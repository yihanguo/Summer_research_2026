"""Offline analysis of completed Werewolf Arena artifacts.

The primary rows are built from public messages before the current round's
vote.  RoundExtractionEvent records are intentionally not used as predictors
for the same round because they are emitted after voting and can leak the
outcome.  The claim parser is conservative and transparent: ambiguous text is
marked unresolved rather than delegated to an LLM during this offline pass.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import json
import re
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .information_metrics import (
    conditional_mutual_information,
    median_pairwise_synergy,
    permutation_null,
    roundwise_rjig,
)


LABEL_POSITIVE = "positive_task_info"
LABEL_NEUTRAL = "neutral_task_info"
LABEL_MISLEADING = "misleading_info"
LABEL_UNRESOLVED = "unresolved"
SCORES = {
    LABEL_POSITIVE: 1.0,
    LABEL_NEUTRAL: 0.25,
    LABEL_MISLEADING: -1.0,
}

_ROLE_WORDS = {
    "seer": "Seer",
    "doctor": "Doctor",
    "villager": "Villager",
    "werewolf": "Werewolf",
    "wolf": "Werewolf",
}
_SUSPICION_WORDS = re.compile(
    r"\b(?:suspicious|suspicion|suspect(?:s|ed|ing)?|accus(?:e|ed|ation|ing)|"
    r"vote(?:d|ing)?\s+(?:out|for)|remove|removed|eliminat(?:e|ed|ing)?|"
    r"red\s+flag|deflect(?:s|ed|ing)?|mislead(?:s|ing)?|dangerous|threat|"
    r"dishonest|lying|deception)\b",
    re.IGNORECASE,
)
_WOLF_WORDS = re.compile(r"\b(?:werewolf|wolves?|wolf)\b", re.IGNORECASE)
_CLEAR_WORDS = re.compile(
    r"\b(?:villager|cleared|safe|trustworthy|trusted|ally|confirmed)\b",
    re.IGNORECASE,
)
_NEGATED_SUSPICION = re.compile(
    r"\b(?:not|no|never|without)\b[^.!?]{0,35}\b(?:suspicious|suspect|wolf|werewolf)\b",
    re.IGNORECASE,
)
_ROLE_CLAIM = re.compile(
    r"\b(?:claim(?:s|ed)?\s+to\s+be|is\s+(?:the|a|an)?|identified\s+as|"
    r"confirmed\s+as|i\s+am|i'm)\s+(?:the\s+)?(?:a\s+)?"
    r"(seer|doctor|villager|werewolf|wolf)\b",
    re.IGNORECASE,
)
_EVIDENCE_ID = re.compile(r"\bE\d{1,3}\b", re.IGNORECASE)


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def source_column(name: str, label: str) -> str:
    return f"x_{_slug(name)}_{label}"


def _sentences(text: str) -> List[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]


def _mentioned_names(text: str, names: Sequence[str]) -> List[str]:
    found = []
    for name in sorted(names, key=len, reverse=True):
        if re.search(rf"(?<!\w){re.escape(name)}(?!\w)", text, re.IGNORECASE):
            found.append(name)
    return found


def _role_claims(sentence: str, speaker: str, names: Sequence[str]) -> List[Tuple[str, str]]:
    """Return (claimant, claimed role) without judging truthfulness."""
    claims: List[Tuple[str, str]] = []
    for match in _ROLE_CLAIM.finditer(sentence):
        role = _ROLE_WORDS[match.group(1).lower()]
        prefix = sentence[: match.start()]
        claimant = speaker if re.search(r"\b(?:i\s+am|i'm)\b", match.group(0), re.I) else None
        if claimant is None:
            candidates = _mentioned_names(prefix, names)
            claimant = candidates[-1] if candidates else None
        if claimant and (claimant, role) not in claims:
            claims.append((claimant, role))
    return claims


def _has_targeted_suspicion(sentence: str, name: str) -> bool:
    lower = sentence.lower()
    if _NEGATED_SUSPICION.search(sentence):
        return False
    name_pattern = re.escape(name)
    direct_patterns = (
        rf"\b{name_pattern}\b.{{0,70}}\b(?:werewolf|wolf|suspicious|suspect|"
        rf"accus|target|vote|remove|eliminat|red\s+flag|deflect|mislead|"
        rf"dangerous|threat)\b",
        rf"\b(?:accus|suspect|target|vote|remove|eliminat|red\s+flag|deflect|"
        rf"mislead|dangerous|threat)\b.{{0,70}}\b{name_pattern}\b",
    )
    if not any(re.search(pattern, sentence, re.I) for pattern in direct_patterns):
        return False
    # Do not interpret generic statements such as “wolves may target X” as an
    # accusation against X.
    if re.search(
        rf"\b(?:werewolves?|wolves?)\b.{{0,25}}\b(?:may|might|could|will)\b.{{0,15}}"
        rf"\b(?:target|attack|remove|kill)\b.{{0,25}}\b{name_pattern}\b",
        sentence,
        re.I,
    ):
        return False
    return True


def _has_targeted_clearance(sentence: str, name: str) -> bool:
    name_pattern = re.escape(name)
    patterns = (
        rf"\b{name_pattern}\b.{{0,70}}\b(?:villager|cleared|safe|trustworthy|"
        rf"trusted|ally)\b",
        rf"\b(?:villager|cleared|safe|trustworthy|trusted|ally)\b.{{0,70}}"
        rf"\b{name_pattern}\b",
        rf"\bnot\b.{{0,30}}\b(?:wolf|werewolf)\b.{{0,30}}\b{name_pattern}\b",
    )
    return any(re.search(pattern, sentence, re.I) for pattern in patterns)


def _label_for_direction(direction: str, target_role: str) -> str:
    is_wolf = target_role == "Werewolf"
    if direction == "suspicion":
        return LABEL_POSITIVE if is_wolf else LABEL_MISLEADING
    if direction == "clearance":
        return LABEL_NEUTRAL if not is_wolf else LABEL_MISLEADING
    return LABEL_UNRESOLVED


@dataclass(frozen=True)
class ClaimRecord:
    episode_id: str
    provider: str
    condition_id: str
    seed: int
    round: int
    message_id: str
    speaker: str
    speaker_role: str
    target: Optional[str]
    target_role: Optional[str]
    claim_type: str
    label: str
    score: Optional[float]
    role_concealment: bool
    evidence_refs: Tuple[str, ...]
    text: str
    parser_reason: str

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["evidence_refs"] = list(self.evidence_refs)
        return result


def _record(
    *,
    episode_id: str,
    provider: str,
    condition_id: str,
    seed: int,
    round_number: int,
    message_id: str,
    speaker: str,
    speaker_role: str,
    target: Optional[str],
    target_role: Optional[str],
    claim_type: str,
    label: str,
    role_concealment: bool,
    evidence_refs: Sequence[str],
    text: str,
    parser_reason: str,
) -> ClaimRecord:
    return ClaimRecord(
        episode_id=episode_id,
        provider=provider,
        condition_id=condition_id,
        seed=seed,
        round=round_number,
        message_id=message_id,
        speaker=speaker,
        speaker_role=speaker_role,
        target=target,
        target_role=target_role,
        claim_type=claim_type,
        label=label,
        score=SCORES.get(label),
        role_concealment=role_concealment,
        evidence_refs=tuple(evidence_refs),
        text=text,
        parser_reason=parser_reason,
    )


def parse_public_message(
    message: Mapping[str, Any],
    *,
    manifest: Mapping[str, Any],
    evidence_by_id: Mapping[str, Mapping[str, Any]],
    provider: str,
    episode_id: str,
) -> List[ClaimRecord]:
    """Extract conservative role/suspicion claims from one public message."""
    names = list(manifest.get("player_names", []))
    roles = dict(manifest.get("role_assignment", {}))
    speaker = str(message.get("speaker", ""))
    speaker_role = roles.get(speaker, "Unknown")
    text = str(message.get("dialogue", ""))
    refs = tuple(message.get("evidence_refs", []) or [])
    normalized_evidence_ids = []
    evidence_targets: List[str] = []
    for ref in refs:
        match = _EVIDENCE_ID.search(str(ref))
        evidence_id = match.group(0).upper() if match else str(ref)
        normalized_evidence_ids.append(evidence_id)
        item = evidence_by_id.get(evidence_id)
        target = item.get("target_hypothesis") if item else None
        if target in names and target not in evidence_targets:
            evidence_targets.append(target)

    claims: List[ClaimRecord] = []
    seen = set()
    for sentence in _sentences(text):
        mentioned = _mentioned_names(sentence, names)
        sentence_role_claims = _role_claims(sentence, speaker, names)
        if not mentioned and not sentence_role_claims:
            continue
        if not mentioned:
            mentioned = list(dict.fromkeys(claimant for claimant, _ in sentence_role_claims))

        # Role identity is logged separately. A false role claim is permitted
        # as strategic concealment and is not automatically a bad information
        # claim.
        for claimant, claimed_role in sentence_role_claims:
            actual_role = roles.get(claimant)
            concealment = actual_role is not None and actual_role != claimed_role
            key = (sentence, claimant, "role_identity")
            if key not in seen:
                seen.add(key)
                claims.append(
                    _record(
                        episode_id=episode_id,
                        provider=provider,
                        condition_id=manifest["condition_id"],
                        seed=int(manifest["seed"]),
                        round_number=int(message["round"]),
                        message_id=str(message["event_id"]),
                        speaker=speaker,
                        speaker_role=speaker_role,
                        target=claimant,
                        target_role=actual_role,
                        claim_type="role_identity",
                        label=LABEL_UNRESOLVED,
                        role_concealment=concealment,
                        evidence_refs=normalized_evidence_ids,
                        text=sentence,
                        parser_reason=f"role_claim={claimed_role}",
                    )
                )

        directed_targets = set()
        for name in mentioned:
            if _has_targeted_suspicion(sentence, name):
                directed_targets.add(name)
                direction = "suspicion"
            elif _has_targeted_clearance(sentence, name):
                directed_targets.add(name)
                direction = "clearance"
            else:
                continue
            target_role = roles.get(name)
            if target_role is None:
                continue
            label = _label_for_direction(direction, target_role)
            claim_type = "wolf_status" if _WOLF_WORDS.search(sentence) else direction
            key = (sentence, name, claim_type, label)
            if key in seen:
                continue
            seen.add(key)
            claims.append(
                _record(
                    episode_id=episode_id,
                    provider=provider,
                    condition_id=manifest["condition_id"],
                    seed=int(manifest["seed"]),
                    round_number=int(message["round"]),
                    message_id=str(message["event_id"]),
                    speaker=speaker,
                    speaker_role=speaker_role,
                    target=name,
                    target_role=target_role,
                    claim_type=claim_type,
                    label=label,
                    role_concealment=False,
                    evidence_refs=normalized_evidence_ids,
                    text=sentence,
                    parser_reason=f"direction={direction}",
                )
            )

        # If a message cites a structured evidence item without naming a
        # candidate in a directed claim, use the evidence target. This is safe
        # for the synthetic evidence contract and is kept separate from free
        # text interpretation.
        if evidence_targets and not directed_targets:
            for target in evidence_targets:
                target_role = roles.get(target)
                label = LABEL_POSITIVE if target_role == "Werewolf" else LABEL_MISLEADING
                key = (sentence, target, "evidence_support", label)
                if key in seen:
                    continue
                seen.add(key)
                claims.append(
                    _record(
                        episode_id=episode_id,
                        provider=provider,
                        condition_id=manifest["condition_id"],
                        seed=int(manifest["seed"]),
                        round_number=int(message["round"]),
                        message_id=str(message["event_id"]),
                        speaker=speaker,
                        speaker_role=speaker_role,
                        target=target,
                        target_role=target_role,
                        claim_type="evidence_support",
                        label=label,
                        role_concealment=False,
                        evidence_refs=normalized_evidence_ids,
                        text=sentence,
                        parser_reason="structured_evidence_target",
                    )
                )
    return claims


def _bin_count(value: int) -> str:
    if value <= 0:
        return "0"
    if value == 1:
        return "1"
    return "2+"


def _message_count_bin(value: int) -> str:
    if value <= 4:
        return "0-4"
    if value <= 8:
        return "5-8"
    return "9+"


def load_completed_episodes(roots: Sequence[str | Path]) -> List[Dict[str, Any]]:
    """Load complete game states, manifests, events, and evidence only."""
    episodes: List[Dict[str, Any]] = []
    for root in roots:
        root_path = Path(root)
        for manifest_path in sorted(root_path.glob("**/manifest.json")):
            directory = manifest_path.parent
            state_path = directory / "game_complete.json"
            events_path = directory / "events.jsonl"
            if not state_path.exists() or not events_path.exists():
                continue
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            state = json.loads(state_path.read_text(encoding="utf-8"))
            events = [
                json.loads(line)
                for line in events_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            evidence_path = directory / "evidence.json"
            evidence = json.loads(evidence_path.read_text(encoding="utf-8")) if evidence_path.exists() else []
            model_ids = manifest.get("model_ids", {})
            provider = "deepseek" if any("deepseek" in str(v).lower() for v in model_ids.values()) else "openai"
            episode_id = f"{root_path.name}/{manifest['condition_id']}/seed_{manifest['seed']}"
            episodes.append({
                "episode_id": episode_id,
                "root": str(root_path),
                "directory": str(directory),
                "provider": provider,
                "manifest": manifest,
                "state": state,
                "events": events,
                "evidence": evidence,
            })
    return episodes


def build_episode_rows(episode: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], List[ClaimRecord]]:
    """Create candidate-level rows from pre-vote public messages."""
    manifest = episode["manifest"]
    state = episode["state"]
    events = episode["events"]
    evidence_by_id = {
        str(item.get("evidence_id", "")).upper(): item
        for item in episode.get("evidence", [])
    }
    messages = [event for event in events if event.get("event_type") == "public_message"]
    claims: List[ClaimRecord] = []
    for message in messages:
        claims.extend(
            parse_public_message(
                message,
                manifest=manifest,
                evidence_by_id=evidence_by_id,
                provider=episode["provider"],
                episode_id=episode["episode_id"],
            )
        )

    messages_by_round: Dict[int, List[Mapping[str, Any]]] = defaultdict(list)
    for message in messages:
        messages_by_round[int(message["round"])].append(message)

    roles = manifest["role_assignment"]
    rows: List[Dict[str, Any]] = []
    for game_round, round_state in enumerate(state.get("rounds", [])):
        event_round = game_round + 1
        round_messages = messages_by_round.get(event_round, [])
        active_players = list(round_state.get("players", []))
        good_sources = [name for name in active_players if roles.get(name) != "Werewolf"]
        round_claims = [claim for claim in claims if claim.round == event_round]
        counts: Dict[Tuple[str, str, str], int] = Counter()
        content_counts: Dict[Tuple[str, str, str], int] = Counter()
        for claim in round_claims:
            if claim.target is None or claim.speaker not in good_sources:
                continue
            if claim.claim_type in {"suspicion", "wolf_status", "evidence_support"}:
                content_counts[(claim.speaker, claim.target, "suspicion")] += 1
            elif claim.claim_type == "clearance":
                content_counts[(claim.speaker, claim.target, "clearance")] += 1
            if claim.label not in {LABEL_POSITIVE, LABEL_NEUTRAL, LABEL_MISLEADING}:
                continue
            counts[(claim.speaker, claim.target, claim.label)] += 1

        message_bin = _message_count_bin(len(round_messages))
        for candidate in active_players:
            row: Dict[str, Any] = {
                "episode_id": episode["episode_id"],
                "provider": episode["provider"],
                "condition_id": manifest["condition_id"],
                "seed": int(manifest["seed"]),
                "round": event_round,
                "candidate": candidate,
                "candidate_role": roles.get(candidate, "Unknown"),
                "y_role": int(roles.get(candidate) == "Werewolf"),
                "y_decision": int(round_state.get("exiled") == candidate),
                "game_winner": state.get("winner", ""),
                "public_message_count_bin": message_bin,
                "active_player_count": len(active_players),
            }
            for source in roles:
                positive = counts[(source, candidate, LABEL_POSITIVE)]
                neutral = counts[(source, candidate, LABEL_NEUTRAL)]
                misleading = counts[(source, candidate, LABEL_MISLEADING)]
                suspicion = content_counts[(source, candidate, "suspicion")]
                clearance = content_counts[(source, candidate, "clearance")]
                row[source_column(source, "positive")] = _bin_count(positive)
                row[source_column(source, "nm")] = _bin_count(positive + neutral)
                row[source_column(source, "misleading")] = _bin_count(misleading)
                row[source_column(source, "suspicion")] = _bin_count(suspicion)
                row[source_column(source, "clearance")] = _bin_count(clearance)

            for label, field in (
                (LABEL_POSITIVE, "x_group_positive"),
                (LABEL_MISLEADING, "x_group_misleading"),
            ):
                total = sum(counts[(source, candidate, label)] for source in good_sources)
                row[field] = _bin_count(total)
            total_nm = sum(
                counts[(source, candidate, LABEL_POSITIVE)]
                + counts[(source, candidate, LABEL_NEUTRAL)]
                for source in good_sources
            )
            row["x_group_nm"] = _bin_count(total_nm)
            row["x_group_suspicion"] = _bin_count(
                sum(content_counts[(source, candidate, "suspicion")] for source in good_sources)
            )
            row["x_group_clearance"] = _bin_count(
                sum(content_counts[(source, candidate, "clearance")] for source in good_sources)
            )
            rows.append(row)
    return rows, claims


def _claim_summary(claims: Sequence[ClaimRecord], *, good_only: bool = True) -> Dict[str, Any]:
    selected = [
        claim
        for claim in claims
        if not good_only or claim.speaker_role != "Werewolf"
    ]
    counts = Counter(claim.label for claim in selected)
    scored = [claim.score for claim in selected if claim.score is not None]
    return {
        "claims": len(selected),
        "positive": counts[LABEL_POSITIVE],
        "neutral": counts[LABEL_NEUTRAL],
        "misleading": counts[LABEL_MISLEADING],
        "unresolved": counts[LABEL_UNRESOLVED],
        "role_concealment": sum(claim.role_concealment for claim in selected),
        "positive_rate": counts[LABEL_POSITIVE] / len(selected) if selected else 0.0,
        "neutral_rate": counts[LABEL_NEUTRAL] / len(selected) if selected else 0.0,
        "misleading_rate": counts[LABEL_MISLEADING] / len(selected) if selected else 0.0,
        "unresolved_rate": counts[LABEL_UNRESOLVED] / len(selected) if selected else 0.0,
        "signed_task_information_score": mean(scored) if scored else None,
    }


def _pearson(x_values: Sequence[float], y_values: Sequence[float]) -> Optional[float]:
    if len(x_values) != len(y_values) or len(x_values) < 3:
        return None
    x_mean = mean(x_values)
    y_mean = mean(y_values)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    x_variance = sum((x - x_mean) ** 2 for x in x_values)
    y_variance = sum((y - y_mean) ** 2 for y in y_values)
    denominator = (x_variance * y_variance) ** 0.5
    return numerator / denominator if denominator else None


def episode_outcome_associations(
    episodes: Sequence[Mapping[str, Any]], claims: Sequence[ClaimRecord]
) -> List[Dict[str, Any]]:
    """Summarize exploratory episode-level associations with village wins."""
    winners = {
        str(episode["episode_id"]): int(episode["state"].get("winner") == "Villagers")
        for episode in episodes
    }
    grouped: Dict[Tuple[str, str, str], List[ClaimRecord]] = defaultdict(list)
    for claim in claims:
        if claim.speaker_role != "Werewolf":
            grouped[(claim.provider, claim.condition_id, claim.episode_id)].append(claim)

    by_group: Dict[Tuple[str, str], List[Dict[str, float]]] = defaultdict(list)
    for (provider, condition, episode_id), episode_claims in grouped.items():
        labels = Counter(claim.label for claim in episode_claims)
        scored = [claim.score for claim in episode_claims if claim.score is not None]
        total = len(episode_claims)
        by_group[(provider, condition)].append({
            "win": float(winners.get(episode_id, 0)),
            "positive_rate": labels[LABEL_POSITIVE] / total if total else 0.0,
            "misleading_rate": labels[LABEL_MISLEADING] / total if total else 0.0,
            "signed_score": mean(scored) if scored else 0.0,
        })

    result: List[Dict[str, Any]] = []
    for (provider, condition), rows in sorted(by_group.items()):
        wins = [row["win"] for row in rows]
        result.append({
            "provider": provider,
            "condition_id": condition,
            "episodes": len(rows),
            "correlation_signed_score_with_village_win": _pearson(
                [row["signed_score"] for row in rows], wins
            ),
            "correlation_positive_rate_with_village_win": _pearson(
                [row["positive_rate"] for row in rows], wins
            ),
            "correlation_misleading_rate_with_village_win": _pearson(
                [row["misleading_rate"] for row in rows], wins
            ),
        })
    return result


def _source_columns(rows: Sequence[Mapping[str, Any]], label: str) -> List[str]:
    prefix = f"x_"
    suffix = f"_{label}"
    return sorted(
        {
            key
            for row in rows
            for key in row
            if key.startswith(prefix) and key.endswith(suffix) and not key.startswith("x_group_")
        }
    )


def _metric_block(
    rows: Sequence[Mapping[str, Any]],
    *,
    group_source: str,
    individual_sources: Sequence[str],
    target: str,
    conditioning: Sequence[str],
    include_null: bool,
) -> Dict[str, Any]:
    result = roundwise_rjig(
        rows, group_source, individual_sources, target, conditioning
    )
    pairs = median_pairwise_synergy(
        rows, individual_sources, target, conditioning
    )
    result["pid_syn_mmi_proxy_median_bits"] = pairs["median_synergy_bits"]
    result["pid_pair_count"] = pairs["pair_count"]
    if include_null:
        result["permutation_null"] = permutation_null(
            rows,
            group_source,
            target,
            conditioning,
            permutations=50,
            seed=17,
        )
    return result


def analyze_rows(
    rows: Sequence[Mapping[str, Any]],
    claims: Sequence[ClaimRecord],
) -> List[Dict[str, Any]]:
    """Compute per-provider/condition/round information summaries."""
    grouped: Dict[Tuple[str, str, str], List[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["provider"]), str(row["condition_id"]), str(row["round"]))].append(row)

    output: List[Dict[str, Any]] = []
    group_keys = sorted(grouped)
    # Add the pre-registered early-round aggregate when both rounds exist.
    for provider, condition, _ in sorted(set((p, c, r) for p, c, r in group_keys)):
        if (provider, condition, "1") in grouped and (provider, condition, "2") in grouped:
            grouped[(provider, condition, "early_1_2")] = (
                grouped[(provider, condition, "1")]
                + grouped[(provider, condition, "2")]
            )

    for (provider, condition, round_key), group_rows in sorted(grouped.items()):
        conditioning = ["candidate", "public_message_count_bin"]
        if round_key == "early_1_2":
            conditioning = ["round", "candidate", "public_message_count_bin"]
        group_claims = [
            claim
            for claim in claims
            if claim.provider == provider
            and claim.condition_id == condition
            and (
                round_key == "early_1_2"
                and claim.round in {1, 2}
                or round_key != "early_1_2"
                and str(claim.round) == round_key
            )
        ]
        claim_summary = _claim_summary(group_claims)
        summary: Dict[str, Any] = {
            "provider": provider,
            "condition_id": condition,
            "round": round_key,
            "episodes": len({row["episode_id"] for row in group_rows}),
            "candidate_rows": len(group_rows),
            "claim_summary": claim_summary,
            "targets": {},
        }
        episode_winners = {
            str(row["episode_id"]): str(row.get("game_winner", ""))
            for row in group_rows
        }
        summary["good_team_win_rate"] = (
            sum(winner == "Villagers" for winner in episode_winners.values())
            / len(episode_winners)
            if episode_winners
            else 0.0
        )
        for label_name, group_field, individual_label in (
            ("positive", "x_group_positive", "positive"),
            ("admissible_nonmisleading", "x_group_nm", "nm"),
            ("misleading", "x_group_misleading", "misleading"),
            ("content_suspicion", "x_group_suspicion", "suspicion"),
            ("content_clearance", "x_group_clearance", "clearance"),
        ):
            individual_sources = _source_columns(group_rows, individual_label)
            summary["targets"][label_name] = {}
            for target in ("y_role", "y_decision"):
                block = _metric_block(
                    group_rows,
                    group_source=group_field,
                    individual_sources=individual_sources,
                    target=target,
                    conditioning=conditioning,
                    include_null=label_name == "positive" and target == "y_role",
                )
                summary["targets"][label_name][target] = block
        output.append(summary)
    return output


def _markdown_report(
    episodes: Sequence[Mapping[str, Any]],
    summaries: Sequence[Mapping[str, Any]],
    associations: Sequence[Mapping[str, Any]],
) -> str:
    lines = [
        "# Completed-game positive-channel information analysis",
        "",
        "This report uses only directories containing `game_complete.json`.",
        "Primary predictors are pre-vote public messages; post-vote round extractions are excluded to avoid target leakage.",
        "The claim labels come from a conservative rule-based parser, so this is a preliminary offline analysis rather than a semantic-judge result.",
        "",
        "## Coverage",
        "",
        f"Completed episodes analyzed: **{len(episodes)}**",
        "",
        "| Provider | Condition | Completed episodes | Village win rate | Round | Positive rate | Neutral rate | Misleading rate | Signed score | I+ role bits | RJIG+ role bits | PID-Syn+ bits |",
        "|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for summary in summaries:
        if summary["round"] != "early_1_2":
            continue
        positive_role = summary["targets"]["positive"]["y_role"]
        claim = summary["claim_summary"]
        lines.append(
            "| {provider} | {condition} | {episodes} | {win_rate:.3f} | {round} | {positive_rate:.3f} | {neutral_rate:.3f} | {misleading_rate:.3f} | {score} | {group:.4f} | {rjig:.4f} | {syn:.4f} |".format(
                provider=summary["provider"],
                condition=summary["condition_id"],
                episodes=summary["episodes"],
                win_rate=summary["good_team_win_rate"],
                round=summary["round"],
                positive_rate=claim["positive_rate"],
                neutral_rate=claim["neutral_rate"],
                misleading_rate=claim["misleading_rate"],
                score=(f"{claim['signed_task_information_score']:.3f}" if claim["signed_task_information_score"] is not None else "NA"),
                group=positive_role["group_information_bits"],
                rjig=positive_role["rjig_bits"],
                syn=positive_role["pid_syn_mmi_proxy_median_bits"],
            )
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- `I+ role bits` is CMI between the pooled good-agent positive channel and the actual wolf-status target, conditional on candidate and public-message-count bins.",
        "- `RJIG+` is pooled positive-channel information minus the strongest individual good-agent source.",
        "- `PID-Syn+` is the MMI-style pairwise synergy proxy, not a full Williams-Beer `I_min` estimate.",
        "- A zero misleading-channel contribution to the primary positive metric is implemented by filtering misleading claims out of `X+`; misleading-channel diagnostics remain in the JSON output.",
        "- The current `I+` result is oracle-filtered with hidden roles and is therefore an exploratory upper bound, not a leakage-free predictive estimate. The JSON also contains target-independent `content_suspicion` and `content_clearance` channels, conditional on the good-agent coalition.",
        "- Calibrated `DRIG` is not estimated because completed logs do not contain pre/post belief probabilities; causal `DeltaU` is not estimated because these games were not matched keep/block interventions.",
        "- These are observational, parser-based results. They do not estimate the causal `DeltaU` intervention effect.",
        "",
        "## Exploratory episode-level associations",
        "",
        "These correlations use each completed episode once. They are descriptive, not significance tests, and should not be interpreted across providers as a controlled comparison.",
        "",
        "| Provider | Condition | Episodes | Corr(signed score, village win) | Corr(positive rate, village win) | Corr(misleading rate, village win) |",
        "|---|---|---:|---:|---:|---:|",
    ])
    for association in associations:
        def fmt(value: Any) -> str:
            return "NA" if value is None else f"{value:.3f}"

        lines.append(
            f"| {association['provider']} | {association['condition_id']} | {association['episodes']} | "
            f"{fmt(association['correlation_signed_score_with_village_win'])} | "
            f"{fmt(association['correlation_positive_rate_with_village_win'])} | "
            f"{fmt(association['correlation_misleading_rate_with_village_win'])} |"
        )
    lines.extend([
        "",
        "## Reproducibility",
        "",
        "The JSON output contains claim records, candidate-level information rows, estimator settings, and null summaries.",
    ])
    return "\n".join(lines) + "\n"


def run_analysis(roots: Sequence[str | Path], output_dir: str | Path) -> Dict[str, Any]:
    """Run the complete-games analysis and write JSONL/JSON/Markdown outputs."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    episodes = load_completed_episodes(roots)
    all_rows: List[Dict[str, Any]] = []
    all_claims: List[ClaimRecord] = []
    for episode in episodes:
        rows, claims = build_episode_rows(episode)
        all_rows.extend(rows)
        all_claims.extend(claims)

    summaries = analyze_rows(all_rows, all_claims)
    associations = episode_outcome_associations(episodes, all_claims)
    with (output / "claim_records.jsonl").open("w", encoding="utf-8") as handle:
        for claim in all_claims:
            handle.write(json.dumps(claim.to_dict(), sort_keys=True) + "\n")
    with (output / "information_rows.jsonl").open("w", encoding="utf-8") as handle:
        for row in all_rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    result = {
        "roots": [str(root) for root in roots],
        "completed_episodes": len(episodes),
        "claim_records": len(all_claims),
        "information_rows": len(all_rows),
        "summaries": summaries,
        "episode_outcome_associations": associations,
        "parser": {
            "name": "rule_based_public_message_parser",
            "uses_hidden_roles_for_offline_label_join": True,
            "uses_round_extractions_as_predictors": False,
            "primary_channel": "positive_task_info_only",
            "positive_channel_is_oracle_filtered": True,
            "target_independent_content_channels": ["content_suspicion", "content_clearance"],
            "content_channels_conditioned_on_good_agent_coalition": True,
            "drig_estimated": False,
            "delta_u_estimated": False,
            "permutation_count": 50,
        },
    }
    (output / "information_summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    (output / "information_report.md").write_text(
        _markdown_report(episodes, summaries, associations), encoding="utf-8"
    )
    return result
