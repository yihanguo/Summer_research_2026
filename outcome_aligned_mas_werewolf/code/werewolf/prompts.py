# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

GAME = """You are playing a digital version of the social deduction game Werewolf (also known as Mafia).

GAME RULES:
- Player Roles: {{num_players}} players - 2 Werewolves, 1 Seer, 1 Doctor, {{num_villagers}} Villagers.
- Rounds consist of two phases:
    - Night Phase: Werewolves remove a player. Seer identifies a player's role. Doctor saves a player. If no one is removed, the Doctor saved the Werewolf's target.
    - Day Phase: Players debate and vote to remove one player.
- Winning Conditions: Villagers win by voting out both Werewolves. Werewolves win when they outnumber the Villagers."""

STATE = """GAME STATE:
- It is currently Round {{round}}. {% if round == 0 %}The game has just begun.{% endif %}
- You are {{name}} the {{role}}. {{werewolf_context}}
{% if personality -%}
- Personality: {{ personality }}
{% endif -%}
- Remaining players: {{remaining_players}}"""

OBSERVATIONS = """{% if observations|length -%}YOUR PRIVATE OBSERVATIONS:
{% for turn in observations -%}
{{ turn }}
{% endfor %}
{% endif %}"""

EXPERIMENT_CONTEXT = """{% if private_evidence|length -%}
PRIVATE EVIDENCE AVAILABLE TO YOU:
{% for item in private_evidence -%}
- {{ item.evidence_id }}: {{ item.claim_text }} ({{ item.source_type }}, {{ item.directness }})
{% endfor %}
{% endif -%}
{% if private_round_memory|length -%}
PRIVATE MEMORY EXTRACTED FROM EARLIER PUBLIC ROUNDS:
{% for item in private_round_memory -%}
- {{ item.summary if item.summary is defined else item }}
{% endfor %}
{% endif -%}
{% if coordination_policy -%}
COORDINATION POLICY:
{{ coordination_policy }}
{% endif %}"""

DEBATE_SO_FAR_THIS_ROUND = """\nROUND {{round}} DEBATE:
{% if debate|length -%}
{% for turn in debate -%}
{{ turn }}
{% endfor -%}
{% else -%}
The debate has not begun.{% endif %}\n\n"""

PREFIX = f"""{GAME}

{STATE}

{OBSERVATIONS}

{EXPERIMENT_CONTEXT}
""".strip()

BIDDING = (
    PREFIX
    + DEBATE_SO_FAR_THIS_ROUND
    + """CONTEXT: For the chance to speak next you will place a bid. Highest bidder speaks first.
- BID OPTIONS:
  0: I would like to observe and listen for now.
  1: I have some general thoughts to share with the group.
  2: I have something critical and specific to contribute to this discussion.
  3: It is absolutely urgent for me to speak next.
  4: Someone has addressed me directly and I must respond.
- You have {{debate_turns_left}} chance(s) to speak left.

INSTRUCTIONS:
- Think strategically as {{name}} the {{role}}.
- Prioritize speaking only when you have something impactful to contribute.
- Balance your involvement, especially if you've been very vocal or notably silent.
- Before bidding, report your current private belief state for every other living
  player. These fields are measurement variables and are not automatically shown
  to the other players.
- Use this suspicion scale for every other living player: 0 = strongly believe
  good, 1 = probably good, 2 = uncertain, 3 = probably Werewolf, 4 = strongly
  suspect Werewolf.
- `top_suspect` and `intended_vote` must name another living player.
- Even if evidence is absent or all players are tied, choose one living player.
  Break a tie by choosing the first tied player in the displayed JSON vector.
  Never return none, N/A, unknown, an explanation, or a blank value for either
  field.
- `suspect_confidence_bin` is your confidence in `top_suspect`: 0 = none,
  1 = low, 2 = moderate, 3 = high, 4 = very high.
- `evidence_state` must be one of: none, private_only, public_only,
  corroborated, conflicting.
{% if role == 'Werewolf' -%}
{% if coordination_policy_name == 'truth_restricted' -%}
- Preserve your hidden role and teammate without fabricating, distorting, or falsely attributing evidence.
- You may selectively withhold information only when sharing it would clearly help the Villagers identify a Werewolf.
{% else -%}
- Decide if you want to subtly guide the conversation toward chaos and distrust, sow seeds of doubt about the Villagers, or deflect suspicion from yourself and your pack.
- Silence can be a powerful tactic, but a lack of participation can be suspicious too.
{% endif -%}
{% else -%}
- If the discussion is repetitive or off-track, prepare to steer it towards a more strategic direction.
- If you are under suspicion or the discussion directly involves your role, you should prioritize speaking
- Share information and make accusations strategically, but be aware that doing so can make you a target.
{% endif %}

```json
{
"reasoning": "string",  // How crucial is it for you to contribute to the debate right now? Explain your reasoning in one or two sentences. Avoid using violent or harmful language.
"bid": "string", // Based on your reasoning cast your bid. Response is a single number from: "0" | "1" | "2" | "3" | "4".
"top_suspect": "string",
"suspect_confidence_bin": 0,
"intended_vote": "string",
"evidence_state": "none",
"suspect_levels": [
{% for player in remaining_player_names if player != name -%}
  {"player": "{{player}}", "level": 2}{% if not loop.last %},{% endif %}
{% endfor -%}
]
}
```
"""
)

BIDDING_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "bid": {"type": "string"},
        "top_suspect": {"type": "string"},
        "suspect_confidence_bin": {"type": "integer", "minimum": 0, "maximum": 4},
        "intended_vote": {"type": "string"},
        "evidence_state": {
            "type": "string",
            "enum": ["none", "private_only", "public_only", "corroborated", "conflicting"],
        },
        "suspect_levels": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "player": {"type": "string"},
                    "level": {"type": "integer", "minimum": 0, "maximum": 4},
                },
                "required": ["player", "level"],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "reasoning",
        "bid",
        "top_suspect",
        "suspect_confidence_bin",
        "intended_vote",
        "evidence_state",
        "suspect_levels",
    ],
    "additionalProperties": False,
}

DEBATE = PREFIX + DEBATE_SO_FAR_THIS_ROUND + """INSTRUCTIONS:
- You are speaking next in the debate as {{name}} the {{role}}.
- Your thoughts on speaking next: {{bidding_rationale}}
- Keep your public statement consistent with your current structured belief:
  top suspect {{current_belief.top_suspect}}, confidence bin
  {{current_belief.suspect_confidence_bin}}, intended vote
  {{current_belief.intended_vote}}, and evidence state
  {{current_belief.evidence_state}}.
- Explicitly discuss who you currently suspect and how confident you are.
- Your public `say` statement must briefly report your 0--4 suspicion level for
  every other living player, using a compact form such as `Name=level`.
- Copy the same complete vector into `public_suspect_levels`. It must exactly
  match the structured vector you submitted with your bid. These are declared
  suspicions; Werewolves may still reason strategically about what to declare.
- Do not reveal private evidence or a hidden role unless your strategy calls
  for it.
{% if role == 'Werewolf' -%}
{% if coordination_policy_name == 'truth_restricted' -%}
- Preserve your hidden role and teammate while remaining accurate about evidence.
- You may selectively withhold information only when sharing it would clearly help the Villagers identify a Werewolf.
{% else -%}
- Your goal is to sow chaos and evade detection.
- Cast suspicion on Villagers. Make them doubt each other.
- Steer the conversation away from yourself and your fellow Werewolves.
- Appear helpful while undermining the Villagers' efforts.
- Deception is your greatest weapon. For example, you could claim a special role and falsely accuse a Villager or fabricate inconsistencies to sow confusion. Use these powerful tactics sparingly to avoid suspicion.
{% endif -%}
{% else -%}
- Your goal is to uncover the Werewolves and protect the Village.
- Scrutinize every accusation, expose inconsistencies, and call out suspicious behavior or unusally quite players. Don't hesitate to make bold accusations!
- Emphasize teamwork and propose strategies to expose the Werewolves. Working together will be key to identifying the Werewolves.
{% if role == 'Villager' -%}
- If someone reveals themselves as the Seer or Doctor, try and corroborate their information with what you know.
{% elif role in ['Seer', 'Doctor'] -%}
- Sharing your role can be powerful, but it also makes you a target. The dilemma: continue to help the Village in secret, or reveal information only you have for potentially greater impact? Choose your moment wisely.
{% endif -%}
{% endif %}

```json
{
  "reasoning": "string", // Based on the game's current state and your role's objectives, outline your strategy. What do you want to achieve? What type of message can help you get there? Avoid using violent or harmful language.
  "say": "string", // Your public statement in the debate. Be concise and persuasive. Respond directly to what the other players have said. Avoid simply repeating what others have said or regurgitating the instructions above.
  "evidence_refs": ["string"], // Optional evidence IDs supporting the statement.
  "confidence": 0.0, // Optional confidence from 0 to 1.
  "public_suspect_levels": [
{% for item in current_belief.suspect_levels -%}
    {"player": "{{item.player}}", "level": {{item.level}}}{% if not loop.last %},{% endif %}
{% endfor -%}
  ]
}
"""

DEBATE_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "say": {"type": "string"},
        "evidence_refs": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number"},
        "public_suspect_levels": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "player": {"type": "string"},
                    "level": {"type": "integer", "minimum": 0, "maximum": 4},
                },
                "required": ["player", "level"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["reasoning", "say", "public_suspect_levels"],
}

VOTE = PREFIX + DEBATE_SO_FAR_THIS_ROUND + """INSTRUCTIONS:
- Think strategically as {{name}} the {{role}} and decide who to vote out.
- Your vote will not be revealed to the other players, it will remain private.
- Scrutinize accusations, analyze behavior, and consider previous patterns.
{% if role == 'Werewolf' -%}
- Target Villagers who are disrupting your plans, particularly those who seem to hold influence, might be the Doctor or Seer, or pose a threat to you and your fellow Werewolf.
- If the Villagers begin to suspect one of their own, join the chorus of doubt, and vote out the unlucky Villager already facing suspicion.
{% else -%}
- To find the likely Werewolves, look for inconsistencies in their stories, attempts to deflect blame, a tendency to sow discord among other Villagers, or unusually quiet players.
{% endif -%}
- You must choose someone.

```json
{
  "reasoning": "string", // Explain your reasoning about who you should vote out. Avoid using violent or harmful language.
  "vote": "string" // Name of the player. Choose from: {{options}}
}"""

VOTE_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "vote": {"type": "string"},
    },
    "required": ["reasoning", "vote"],
}

INVESTIGATE = PREFIX + """INSTRUCTIONS:
- It is the Night Phase of Round {{round}}. As {{name}} the {{role}} choose the most suspicious player to investigate.
{% if round == 0 -%}
- There is no information is available in the first round, so choose someone at random.
{% else -%}
- Look for behavior that deviates from typical villager behavior.
- Focus on influential players.
- You must choose someone.
{% endif %}

```json
{
"reasoning": "string", //  Analyze the evidence and justify your decision for who you want to investigate.
"investigate": "string" // Name of the player. Choose from: {{options}}
}
"""

INVESTIGATE_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "investigate": {"type": "string"},
    },
    "required": ["reasoning", "investigate"],
}

ELIMINATE = PREFIX + """INSTRUCTIONS:
- It is the Night Phase of Round {{round}}. As {{name}} the {{role}} choose the most strategic player to remove.
{% if round == 0 -%}
- There is no information is available in the first round, so choose someone at random.
{% else -%}
- Analyze accusations and identify influential Villagers who threaten your anonymity.
- Consider players' behavior and the risks of removing them.
- You must choose someone.
{% endif %}

```json
{
"reasoning": "string", //  Explain your reasoning step-by-step for who you want to remove from the game and why. Avoid using violent or harmful language.
"remove": "string" // Name of the player. Choose from: {{options}}
}
"""

ELIMINATE_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "remove": {"type": "string"},
    },
    "required": ["reasoning", "remove"],
}

PROTECT = PREFIX + """INSTRUCTIONS:
- It is the Night Phase of Round {{round}}. As {{name}} the {{role}} choose the most vulnerable player to protect.
{% if round == 0 -%}
- There is no information is available in the first round, so choose someone at random.
{% else -%}
- Consider who the Werewolves might target.
- Prioritize players with crucial roles like the Seer and yourself.
- You must choose someone.
{% endif %}

```json
{
"reasoning": "string", // Analyze the evidence and justify your decision for who you want to protect.
"protect": "string" // Name of the player. Choose from: {{options}}
}
"""

PROTECT_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "protect": {"type": "string"},
    },
    "required": ["reasoning", "protect"],
}

SUMMARIZE = PREFIX + DEBATE_SO_FAR_THIS_ROUND + """INSTRUCTIONS:
- Reflect on the round's debate as {{name}} the {{role}}.
- Summarize the key points and strategic implications.
{% if role == 'Werewolf' -%}
- Pay attention to accusations against you and your allies.
- Identify sympathetic or easily influenced players.
- Identify key roles for potential elimination.
{% else -%}
- When a player makes a significant statement or shares information, carefully consider its credibility. Does it align with what you already know?
- Analyze how others participate in the debate. Are there any contradictions in their words? Hidden motives behind their actions? Unusually quiet players?
- Based on the debate, can you identify potential allies, trustworthy players, or those who might be the Seer or Doctor?
{% endif %}

```json
{
"reasoning": "string", // Your reasoning about what you should remember from this debate and why this information is important.
"summary": "string", // Summarize the key points and noteworthy observations from the debate in a few sentences. Aim to make notes on as many players as you can — even seemingly insignificant details might become relevant in later rounds. Be specific. Remember, you are {{name}}. Write your summary from their point of view using "I" and "me.",
"memory_refs": ["string"], // Optional public message IDs used for this private extraction.
"extracted_claims": ["string"] // Optional claims retained in private memory.
} """

SUMMARIZE_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "summary": {"type": "string"},
        "memory_refs": {"type": "array", "items": {"type": "string"}},
        "extracted_claims": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["reasoning", "summary"],
}

ACTION_PROMPTS_AND_SCHEMAS = {
    "bid": (BIDDING, BIDDING_SCHEMA),
    "debate": (DEBATE, DEBATE_SCHEMA),
    "vote": (VOTE, VOTE_SCHEMA),
    "investigate": (INVESTIGATE, INVESTIGATE_SCHEMA),
    "remove": (ELIMINATE, ELIMINATE_SCHEMA),
    "protect": (PROTECT, PROTECT_SCHEMA),
    "summarize": (SUMMARIZE, SUMMARIZE_SCHEMA),
}
