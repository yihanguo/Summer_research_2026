"""Deterministic fake model used for offline pipeline tests and pilots."""

from dataclasses import dataclass
from typing import Dict, List, Sequence

from .conditions import Condition
from .evidence import EvidenceItem


@dataclass
class FakeResponseProvider:
    """A transparent policy engine, not a performance benchmark."""

    target: str

    def debate(
        self,
        *,
        name: str,
        role: str,
        evidence: Sequence[EvidenceItem],
        turn: int,
        condition: Condition,
    ) -> Dict[str, object]:
        if role == "Werewolf":
            if condition.wolf_policy == "truth_restricted":
                text = "We should compare the public evidence carefully before voting."
            else:
                text = "The discussion is becoming too certain; question the leading claim."
            return {"say": text, "evidence_refs": [], "confidence": 0.45}

        if condition.good_policy in {"full_disclosure", "centralized"}:
            refs = [item.evidence_id for item in evidence]
            claims = " ".join(item.claim_text for item in evidence)
            text = claims or "I have no injected evidence; I will track the public claims."
            return {"say": text, "evidence_refs": refs, "confidence": 0.8}

        if condition.good_policy == "strategic_disclosure":
            selected = [evidence[turn % len(evidence)]] if evidence else []
            return {
                "say": selected[0].claim_text if selected else "I will wait for more evidence.",
                "evidence_refs": [item.evidence_id for item in selected],
                "confidence": 0.6,
            }

        return {"say": "I will evaluate the public discussion before committing.", "evidence_refs": []}

    def extract(
        self, *, name: str, source_message_ids: Sequence[str], evidence_refs: Sequence[str]
    ) -> Dict[str, object]:
        claims = [f"I retained public evidence {ref}." for ref in sorted(set(evidence_refs))]
        return {
            "summary": " ".join(claims) or "I retained the public discussion without a structured evidence claim.",
            "extracted_claims": claims,
            "confidence": 0.7 if claims else 0.35,
            "source_message_ids": list(source_message_ids),
        }

    def vote(self, *, name: str, role: str, condition: Condition, options: Sequence[str]) -> str:
        if role == "Werewolf":
            return options[0]
        return self.target if self.target in options else options[0]
