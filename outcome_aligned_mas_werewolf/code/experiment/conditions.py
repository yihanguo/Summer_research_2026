"""Experiment condition definitions.

The first study keeps the communication topology fixed: every living player
receives every public message. The old agent-full duplicated-evidence arm is
intentionally absent.

The primary conditions use the requested two-sign display labels. The first
sign denotes the good-agent disclosure instruction and the second denotes the
Werewolf truth-restriction instruction. A plus means that instruction is
present. Filesystem-safe slugs and the historical C labels remain accepted so
old artifacts and shell commands continue to work.

This is not a perfectly orthogonal 2 x 2 evidence design: ``-+`` retains the
full complementary evidence fixture used by historical condition C4, whereas
``--`` retains the no-evidence fixture used by C0. That fact is explicit in
every saved manifest.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple


@dataclass(frozen=True)
class Condition:
    condition_id: str
    condition_slug: str
    legacy_id: str
    legacy_full_id: str
    evidence_mode: str
    good_policy: str
    wolf_policy: str
    good_intervention: bool
    wolf_intervention: bool
    public_broadcast: bool = True
    synthetic_votes: bool = False
    max_debate_turns: int = 8
    round_extraction: bool = True

    def __post_init__(self) -> None:
        if not self.public_broadcast:
            raise ValueError("The first experiment requires open public broadcast.")
        if self.evidence_mode not in {"none", "system_full_complementary"}:
            raise ValueError(f"Unsupported evidence mode: {self.evidence_mode}")
        expected_id = (
            ("+" if self.good_intervention else "-")
            + ("+" if self.wolf_intervention else "-")
        )
        if self.condition_id != expected_id:
            raise ValueError(
                f"Condition {self.condition_id} conflicts with intervention flags "
                f"{expected_id}."
            )

    @property
    def evidence_available(self) -> bool:
        return self.evidence_mode != "none"


_PRIMARY_CONDITIONS: Tuple[Condition, ...] = (
    Condition(
        "++",
        "pp",
        "C3",
        "C3_complementary_truth_restricted_wolves",
        "system_full_complementary",
        "full_disclosure",
        "truth_restricted",
        True,
        True,
    ),
    Condition(
        "+-",
        "pm",
        "C1",
        "C1_complementary_full_disclosure",
        "system_full_complementary",
        "full_disclosure",
        "strategic",
        True,
        False,
    ),
    Condition(
        "-+",
        "mp",
        "C4",
        "C4_complementary_baseline_truth_restricted",
        "system_full_complementary",
        "baseline",
        "truth_restricted",
        False,
        True,
    ),
    Condition(
        "--",
        "mm",
        "C0",
        "C0_standard_open_baseline",
        "none",
        "baseline",
        "strategic",
        False,
        False,
    ),
)


_ALIASES: Dict[str, Condition] = {}
for _condition in _PRIMARY_CONDITIONS:
    for _alias in (
        _condition.condition_id,
        _condition.condition_slug,
        _condition.legacy_id,
        _condition.legacy_full_id,
    ):
        _ALIASES[_alias] = _condition


def get_condition(condition_id: str) -> Condition:
    """Return a condition by signs, safe slug, or historical C label."""
    try:
        return _ALIASES[condition_id]
    except KeyError as exc:
        raise KeyError(f"Unknown experiment condition: {condition_id}") from exc


def primary_conditions() -> Tuple[Condition, ...]:
    """Return the primary conditions used in the open-broadcast study."""
    return _PRIMARY_CONDITIONS


def condition_cli_aliases() -> Tuple[str, ...]:
    """Return unambiguous CLI aliases, including shell-safe names."""
    aliases: Iterable[str] = (
        alias for condition in _PRIMARY_CONDITIONS for alias in (
            condition.condition_id,
            condition.condition_slug,
            condition.legacy_id,
            condition.legacy_full_id,
        )
    )
    return tuple(aliases)
