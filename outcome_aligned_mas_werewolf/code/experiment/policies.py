"""Condition-specific policy blocks.

Wolf prompts explicitly keep the hidden role and teammate private. The prompt
does not ask Wolves to disclose either fact.
"""

SHARED_OPEN_CONVERSATION = """All living players can hear every public debate statement you make.
Do not assume that a public statement is private. Bids and votes remain private
unless the game rules explicitly reveal them.

You may extract and retain useful information from every completed public debate
round. When using an extracted observation later, distinguish what was directly
said, what you inferred, and how uncertain you are."""

GOOD_FULL_DISCLOSURE = """You are a non-Werewolf and your objective is for the Villagers to win.
Display as much information as you know and are sure about. Cite evidence IDs,
separate direct evidence from inference, and label uncertainty. Do not invent,
exaggerate, or falsely attribute facts."""

GOOD_STRATEGIC_DISCLOSURE = """You are a non-Werewolf and your objective is for the Villagers to win.
Choose what to disclose and when based on the team's chance of winning. You may
withhold true information temporarily, but may not fabricate evidence or state
unsupported claims as certain. You may use private memory from earlier rounds."""

WOLF_STRATEGIC = """You are a Werewolf and your objective is for the Werewolves to win.
Use public conversation strategically and may mislead as allowed by the game.
Your role and your Werewolf teammate's identity are private. Do not reveal or
explicitly confirm either one in public. You may extract information from each
public round and retain it privately."""

WOLF_TRUTH_RESTRICTED = """You are a Werewolf and your objective is for the Werewolves to win.
This instruction is internal: do not reveal or explicitly confirm that you are a
Werewolf, and do not reveal or explicitly confirm your Werewolf teammate.
You may selectively withhold information only when sharing it would clearly help
the Villagers identify a Werewolf. You may not fabricate, distort, or falsely
attribute evidence. Use private memory from every public conversation round."""

POLICIES = {
    "baseline": "",
    "full_disclosure": GOOD_FULL_DISCLOSURE,
    "strategic_disclosure": GOOD_STRATEGIC_DISCLOSURE,
    "strategic": WOLF_STRATEGIC,
    "truth_restricted": WOLF_TRUTH_RESTRICTED,
    "centralized": GOOD_FULL_DISCLOSURE,
}


def policy_text(name: str) -> str:
    try:
        return POLICIES[name]
    except KeyError as exc:
        raise KeyError(f"Unknown coordination policy: {name}") from exc
