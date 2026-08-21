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

import enum
import copy
import json
import random
from typing import Any, Dict, List, Optional, Tuple, Union

from werewolf.lm import LmLog, generate
from werewolf.prompts import ACTION_PROMPTS_AND_SCHEMAS
from werewolf.utils import Deserializable
from werewolf.config import MAX_DEBATE_TURNS, NUM_PLAYERS

# Role names
VILLAGER = "Villager"
WEREWOLF = "Werewolf"
SEER = "Seer"
DOCTOR = "Doctor"


def group_and_format_observations(observations):
  """Groups observations by round and formats them for output.

  Args:
      observations: A list of strings, where each string starts with "Round X:".

  Returns:
      A list of strings, where each string represents the formatted observations
      for a round.
  """

  grouped = {}
  for obs in observations:
    round_num = int(obs.split(":", 1)[0].split()[1])
    obs_text = obs.split(":", 1)[1].strip().replace('"', "")
    grouped.setdefault(round_num, []).append(obs_text)

  formatted_obs = []
  for round_num, round_obs in sorted(grouped.items()):
    formatted_round = f"Round {round_num}:\n"
    formatted_round += "\n".join(f"   - {obs}" for obs in round_obs)
    formatted_obs.append(formatted_round)

  return formatted_obs


# JSON serializer that works for nested classes
class JsonEncoder(json.JSONEncoder):

  def default(self, o):
    if isinstance(o, enum.Enum):
      return o.value
    if isinstance(o, set):
      return list(o)
    return o.__dict__

def to_dict(o: Any) -> Union[Dict[str, Any], List[Any], Any]:
  return json.loads(JsonEncoder().encode(o))

class GameView:
  """Represents the state of the game for each player."""

  def __init__(
      self,
      round_number: int,
      current_players: List[str],
      other_wolf: Optional[str] = None,
  ):
    self.round_number: int = round_number
    self.current_players: List[str] = current_players
    self.debate: List[tuple[str, str]] = []
    self.public_message_ids: List[str] = []
    self.other_wolf: Optional[str] = other_wolf

  def update_debate(self, author: str, dialogue: str, message_id: Optional[str] = None):
    """Adds a new dialogue entry to the debate."""
    self.debate.append((author, dialogue))
    self.public_message_ids.append(message_id or f"legacy_{len(self.debate)}")

  def clear_debate(self):
    """Clears all entries from the debate."""
    self.debate.clear()
    self.public_message_ids.clear()

  def remove_player(self, player_to_remove: str):
    """Removes a player from the list of current players."""
    if player_to_remove not in self.current_players:
      print(
          f"Player {player_to_remove} not in current players:"
          f" {self.current_players}"
      )
    self.current_players.remove(player_to_remove)

  def to_dict(self) -> Any:
    return to_dict(self)

  @classmethod
  def from_json(cls, data: Dict[Any, Any]):
    view = cls(
        round_number=data.get("round_number", 0),
        current_players=data.get("current_players", []),
        other_wolf=data.get("other_wolf"),
    )
    view.debate = [tuple(turn) for turn in data.get("debate", [])]
    view.public_message_ids = data.get(
        "public_message_ids", [f"legacy_{index}" for index in range(len(view.debate))]
    )
    return view


class Player(Deserializable):
  """Represents a player in the game."""

  def __init__(
      self,
      name: str,
      role: str,
      model: Optional[str] = None,
      personality: Optional[str] = "",
  ):
    self.name = name
    self.role = role
    self.personality = personality
    self.model = model
    self.observations: List[str] = []
    self.private_evidence: List[Dict[str, Any]] = []
    self.private_round_memory: List[Dict[str, Any]] = []
    self.coordination_policy_name: str = ""
    self.coordination_policy: str = ""
    self.max_debate_turns: int = MAX_DEBATE_TURNS
    self.bidding_rationale = ""
    self.current_belief: Dict[str, Any] = {
        "top_suspect": "not-yet-measured",
        "suspect_confidence_bin": 0,
        "intended_vote": "not-yet-measured",
        "evidence_state": "none",
        "suspect_levels": [],
    }
    self.gamestate: Optional[GameView] = None

  def initialize_game_view(
      self, round_number, current_players, other_wolf=None
  ) -> None:
    self.gamestate = GameView(round_number, current_players, other_wolf)

  def _add_observation(self, observation: str):
    """Adds an observation for the given round."""
    if not self.gamestate:
      raise ValueError(
          "GameView not initialized. Call initialize_game_view() first."
      )

    self.observations.append(
        f"Round {self.gamestate.round_number}: {observation}"
    )

  def _restore_experiment_fields(self, data: Dict[Any, Any]) -> None:
    """Restore optional experiment fields without affecting legacy games."""
    self.private_evidence = data.get("private_evidence", [])
    self.private_round_memory = data.get("private_round_memory", [])
    self.coordination_policy_name = data.get("coordination_policy_name", "")
    self.coordination_policy = data.get("coordination_policy", "")
    self.max_debate_turns = data.get("max_debate_turns", MAX_DEBATE_TURNS)
    self.current_belief = data.get("current_belief", self.current_belief)

  def add_announcement(self, announcement: str):
    """Adds the current game announcement to the player's observations."""
    self._add_observation(f"Moderator Announcement: {announcement}")

  def _get_game_state(self) -> Dict[str, Any]:
    """Gets the current game state from the player's perspective."""
    if not self.gamestate:
      raise ValueError(
          "GameView not initialized. Call initialize_game_view() first."
      )

    remaining_players = [
        f"{player} (You)" if player == self.name else player
        for player in self.gamestate.current_players
    ]
    random.shuffle(remaining_players)
    formatted_debate = [
        f"{author} (You): {dialogue}"
        if author == self.name
        else f"{author}: {dialogue}"
        for author, dialogue in self.gamestate.debate
    ]

    formatted_observations = group_and_format_observations(self.observations)

    return {
        "name": self.name,
        "role": self.role,
        "round": self.gamestate.round_number,
        "observations": formatted_observations,
        "remaining_players": ", ".join(remaining_players),
        "remaining_player_names": list(self.gamestate.current_players),
        "debate": formatted_debate,
        "bidding_rationale": self.bidding_rationale,
        "debate_turns_left": self.max_debate_turns - len(formatted_debate),
        "personality": self.personality,
        "num_players": NUM_PLAYERS,
        "num_villagers": NUM_PLAYERS - 4,
        "private_evidence": self.private_evidence,
        "private_round_memory": self.private_round_memory,
        "coordination_policy_name": self.coordination_policy_name,
        "coordination_policy": self.coordination_policy,
        "current_belief": self.current_belief,
    }

  def _validate_bid_response(self, payload: Any) -> Optional[str]:
    """Validate the complete longitudinal belief panel returned with a bid."""
    if not isinstance(payload, dict):
      return "The response must be a JSON object."
    if not self.gamestate:
      return "Game state is unavailable."
    other_players = {
        name for name in self.gamestate.current_players if name != self.name
    }
    legal_names = sorted(other_players)
    if payload.get("top_suspect") not in other_players:
      return (
          f"top_suspect must be exactly one of {legal_names}; never use "
          "none, N/A, an explanation, or a blank value."
      )
    if payload.get("intended_vote") not in other_players:
      return (
          f"intended_vote must be exactly one of {legal_names}; never use "
          "none, N/A, an explanation, or a blank value."
      )
    confidence = payload.get("suspect_confidence_bin")
    if isinstance(confidence, bool) or not isinstance(confidence, int) or not 0 <= confidence <= 4:
      return "suspect_confidence_bin must be an integer from 0 through 4."
    if payload.get("evidence_state") not in {
        "none", "private_only", "public_only", "corroborated", "conflicting"
    }:
      return "evidence_state is not one of the five allowed categories."
    levels = payload.get("suspect_levels")
    if not isinstance(levels, list):
      return "suspect_levels must be an array."
    level_by_player: Dict[str, int] = {}
    for item in levels:
      if not isinstance(item, dict):
        return "Every suspect_levels item must be an object."
      player = item.get("player")
      level = item.get("level")
      if player in level_by_player:
        return f"suspect_levels repeats {player}."
      if player not in other_players:
        return f"suspect_levels contains a non-living or self player: {player}."
      if isinstance(level, bool) or not isinstance(level, int) or not 0 <= level <= 4:
        return f"Suspicion level for {player} must be an integer from 0 through 4."
      level_by_player[player] = level
    missing = sorted(other_players - set(level_by_player))
    if missing:
      return f"suspect_levels is missing living players: {missing}."
    return None

  def _schema_for_action(
      self,
      action: str,
      response_schema: Dict[str, Any],
      options: Optional[List[str]],
  ) -> Dict[str, Any]:
    """Bind generic schemas to the legal choices in the current game state."""
    schema = copy.deepcopy(response_schema)
    if action == "bid" and self.gamestate:
      legal_names = [
          name for name in self.gamestate.current_players if name != self.name
      ]
      properties = schema["properties"]
      properties["bid"]["enum"] = list(options or [])
      properties["top_suspect"]["enum"] = legal_names
      properties["intended_vote"]["enum"] = legal_names
      levels = properties["suspect_levels"]
      levels["minItems"] = len(legal_names)
      levels["maxItems"] = len(legal_names)
      levels["items"]["properties"]["player"]["enum"] = legal_names
    elif action == "debate":
      expected = [
          str(item["player"])
          for item in self.current_belief.get("suspect_levels", [])
          if isinstance(item, dict) and "player" in item
      ]
      levels = schema["properties"]["public_suspect_levels"]
      levels["minItems"] = len(expected)
      levels["maxItems"] = len(expected)
      if expected:
        levels["items"]["properties"]["player"]["enum"] = expected
    return schema

  @staticmethod
  def _last_invalid_payload(log: LmLog) -> Dict[str, Any]:
    payload = log.metadata.get("last_invalid_result")
    return dict(payload) if isinstance(payload, dict) else {}

  def _repair_bid_response(
      self, log: LmLog, options: List[str]
  ) -> tuple[str, LmLog]:
    """Deterministically repair an exhausted structured bid response.

    Valid model-provided fields are retained. Missing or invalid suspicion
    entries are filled with the neutral level 2, and categorical choices are
    derived from the resulting complete vector. Every repair remains visible in
    the log and downstream belief-snapshot events.
    """
    if not self.gamestate:
      raise ValueError("Cannot repair a bid without an initialized game state.")
    payload = self._last_invalid_payload(log)
    legal_names = [
        name for name in self.gamestate.current_players if name != self.name
    ]
    raw_levels = payload.get("suspect_levels", [])
    observed: Dict[str, int] = {}
    if isinstance(raw_levels, list):
      for item in raw_levels:
        if not isinstance(item, dict):
          continue
        player, level = item.get("player"), item.get("level")
        if (
            player in legal_names
            and player not in observed
            and not isinstance(level, bool)
            and isinstance(level, int)
            and 0 <= level <= 4
        ):
          observed[player] = level
    levels = [
        {"player": name, "level": observed.get(name, 2)} for name in legal_names
    ]
    level_by_name = {item["player"]: item["level"] for item in levels}

    top_suspect = payload.get("top_suspect")
    if top_suspect not in legal_names:
      highest = max(level_by_name.values())
      top_suspect = next(
          name for name in legal_names if level_by_name[name] == highest
      )
    intended_vote = payload.get("intended_vote")
    if intended_vote not in legal_names:
      intended_vote = top_suspect

    confidence = payload.get("suspect_confidence_bin")
    if isinstance(confidence, bool) or not isinstance(confidence, int) or not 0 <= confidence <= 4:
      confidence = max(0, 2 * (level_by_name[top_suspect] - 2))
    evidence_state = payload.get("evidence_state")
    if evidence_state not in {
        "none", "private_only", "public_only", "corroborated", "conflicting"
    }:
      evidence_state = "none"

    bid_value = str(payload.get("bid", ""))
    if bid_value not in options:
      bid_value = "0"
    reasoning = payload.get("reasoning")
    if not isinstance(reasoning, str) or not reasoning.strip():
      reasoning = "Structured belief response repaired after validation retries."
    repaired = {
        "reasoning": reasoning,
        "bid": bid_value,
        "top_suspect": top_suspect,
        "suspect_confidence_bin": confidence,
        "intended_vote": intended_vote,
        "evidence_state": evidence_state,
        "suspect_levels": levels,
    }
    log.result = repaired
    log.metadata["structured_repair"] = True
    log.metadata["structured_repair_kind"] = "bid"
    log.metadata["structured_repair_reason"] = (
        "Model exhausted retries without a fully valid belief snapshot."
    )
    return bid_value, log

  def _repair_debate_response(self, log: LmLog) -> tuple[Dict[str, Any], LmLog]:
    """Publish the measured vector even if the model's debate JSON is invalid."""
    payload = self._last_invalid_payload(log)
    levels = [dict(item) for item in self.current_belief["suspect_levels"]]
    vector = ", ".join(f"{item['player']}={item['level']}" for item in levels)
    required_statement = (
        f"My current suspicion levels are {vector}. "
        f"My top suspect is {self.current_belief['top_suspect']} with confidence "
        f"bin {self.current_belief['suspect_confidence_bin']}; my intended vote is "
        f"{self.current_belief['intended_vote']} and my evidence state is "
        f"{self.current_belief['evidence_state']}."
    )
    say = payload.get("say")
    if not isinstance(say, str) or not say.strip():
      say = required_statement
    else:
      say = f"{say.strip()} {required_statement}"
    reasoning = payload.get("reasoning")
    if not isinstance(reasoning, str) or not reasoning.strip():
      reasoning = "Public belief declaration repaired after validation retries."
    refs = payload.get("evidence_refs", [])
    refs = [str(ref) for ref in refs] if isinstance(refs, list) else []
    confidence = payload.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
      confidence = None
    elif not 0 <= float(confidence) <= 1:
      confidence = None
    repaired = {
        "reasoning": reasoning,
        "say": say,
        "evidence_refs": refs,
        "confidence": confidence,
        "public_suspect_levels": levels,
    }
    log.result = repaired
    log.metadata["structured_repair"] = True
    log.metadata["structured_repair_kind"] = "debate"
    log.metadata["structured_repair_reason"] = (
        "Model exhausted retries without a valid public belief declaration."
    )
    return repaired, log

  def _validate_debate_response(self, payload: Any) -> Optional[str]:
    """Require the speaker to publish the same complete declared vector."""
    if not isinstance(payload, dict):
      return "The response must be a JSON object."
    levels = payload.get("public_suspect_levels")
    if not isinstance(levels, list):
      return "public_suspect_levels must be an array."
    try:
      observed = {str(item["player"]): int(item["level"]) for item in levels}
      expected = {
          str(item["player"]): int(item["level"])
          for item in self.current_belief["suspect_levels"]
      }
    except (KeyError, TypeError, ValueError):
      return "Every public suspicion entry must contain a player and integer level."
    if len(observed) != len(levels):
      return "public_suspect_levels contains a duplicate player."
    if observed != expected:
      return "public_suspect_levels must exactly match the complete bid-time vector."
    say = str(payload.get("say", ""))
    missing_names = [name for name in expected if name.lower() not in say.lower()]
    if missing_names:
      return f"The public say statement must name every rated player: {missing_names}."
    return None

  def _generate_action(
      self,
      action: str,
      options: Optional[List[str]] = None,
  ) -> tuple[Any | None, LmLog]:
    """Helper function to generate player actions."""
    game_state = self._get_game_state()
    if options:
      game_state["options"] = (", ").join(options)
    prompt_template, base_response_schema = ACTION_PROMPTS_AND_SCHEMAS[action]
    response_schema = self._schema_for_action(
        action, base_response_schema, options
    )

    result_key, allowed_values = (
        (action, options)
        if action in ["vote", "remove", "investigate", "protect", "bid"]
        else (None, None)
    )

    # Set temperature based on allowed_values
    temperature = 0.5 if allowed_values else 1.0

    result, log = generate(
        prompt_template,
        response_schema,
        game_state,
        model=self.model,
        temperature=temperature,
        allowed_values=allowed_values,
        result_key=result_key,
        result_validator=(
            self._validate_bid_response
            if action == "bid"
            else self._validate_debate_response
            if action == "debate"
            else None
        ),
    )

    # Keep a malformed model response from aborting an otherwise valid game.
    # The fallback is restricted to the legal choices exposed in the prompt
    # and is recorded separately from the model's raw response.
    if result is None and action == "bid":
      return self._repair_bid_response(log, list(options or []))
    if result is None and action == "debate":
      return self._repair_debate_response(log)
    if result is None and allowed_values:
      result = random.choice(allowed_values)
      log.result = result
      log.metadata["fallback_action"] = True
      log.metadata["fallback_reason"] = (
          "No legal action returned after model retries."
      )

    return result, log

  def vote(self) -> tuple[str | None, LmLog]:
    """Vote for a player."""
    if not self.gamestate:
      raise ValueError(
          "GameView not initialized. Call initialize_game_view() first."
      )
    options = [
        player
        for player in self.gamestate.current_players
        if player != self.name
    ]
    random.shuffle(options)
    vote, log = self._generate_action("vote", options)
    if vote is not None and len(self.gamestate.debate) == self.max_debate_turns:
      self._add_observation(
          f"After the debate, I voted to remove {vote} from the game."
      )
    return vote, log

  def bid(self) -> tuple[int | None, LmLog]:
    """Place a bid."""
    bid, log = self._generate_action("bid", options=["0", "1", "2", "3", "4"])
    if bid is not None:
      bid = int(bid)
      self.bidding_rationale = (
          log.result.get("reasoning", "")
          if isinstance(log.result, dict)
          else ""
      )
      if isinstance(log.result, dict):
        self.current_belief = {
            key: log.result[key]
            for key in (
                "top_suspect",
                "suspect_confidence_bin",
                "intended_vote",
                "evidence_state",
                "suspect_levels",
            )
        }
    return bid, log

  def debate(self) -> tuple[str | None, LmLog]:
    """Engage in the debate."""
    result, log = self._generate_action("debate", [])
    if result is not None:
      say = result.get("say", None)
      return say, log
    return result, log

  def summarize(self) -> tuple[str | None, LmLog]:
    """Summarize the game state."""
    result, log = self._generate_action("summarize", [])
    if result is not None:
      summary = result.get("summary", None)
      if summary is not None:
        summary = summary.strip('"')
        self._add_observation(f"Summary: {summary}")
      return summary, log
    return result, log

  def to_dict(self) -> Any:
    return to_dict(self)

  @classmethod
  def from_json(cls, data: Dict[Any, Any]):
    name = data["name"]
    role = data["role"]
    model = data.get("model", None)
    o = cls(name=name, role=role, model=model)
    o.gamestate = data.get("gamestate", None)
    o.bidding_rationale = data.get("bidding_rationale", "")
    o.current_belief = data.get("current_belief", o.current_belief)
    o.observations = data.get("observations", [])
    o._restore_experiment_fields(data)
    return o


class Villager(Player):
  """Represents a Villager in the game."""

  def __init__(
      self,
      name: str,
      model: Optional[str] = None,
      personality: Optional[str] = None,
  ):
    super().__init__(
        name=name, role=VILLAGER, model=model, personality=personality
    )

  @classmethod
  def from_json(cls, data: dict[Any, Any]):
    name = data["name"]
    model = data.get("model", None)
    o = cls(name=name, model=model)
    o.gamestate = data.get("gamestate", None)
    o.bidding_rationale = data.get("bidding_rationale", "")
    o.observations = data.get("observations", [])
    o._restore_experiment_fields(data)
    return o


class Werewolf(Player):
  """Represents a Werewolf in the game."""

  def __init__(
      self,
      name: str,
      model: Optional[str] = None,
      personality: Optional[str] = None,
  ):
    super().__init__(
        name=name, role=WEREWOLF, model=model, personality=personality
    )

  def _get_game_state(self, **kwargs) -> Dict[str, Any]:
    """Gets the current game state, including werewolf-specific context."""
    state = super()._get_game_state(**kwargs)
    state["werewolf_context"] = self._get_werewolf_context()
    return state

  def eliminate(self) -> tuple[str | None, "LmLog"]:
    """Choose a player to eliminate."""
    if not self.gamestate:
      raise ValueError(
          "GameView not initialized. Call initialize_game_view() first."
      )

    options = [
        player
        for player in self.gamestate.current_players
        if player != self.name and player != self.gamestate.other_wolf
    ]
    random.shuffle(options)
    eliminate, log = self._generate_action("remove", options)
    return eliminate, log

  def _get_werewolf_context(self):
    if not self.gamestate:
      raise ValueError(
          "GameView not initialized. Call initialize_game_view() first."
      )

    if self.gamestate.other_wolf in self.gamestate.current_players:
      context = f"\n- The other Werewolf is {self.gamestate.other_wolf}."
    else:
      context = (
          f"\n- The other Werewolf, {self.gamestate.other_wolf}, was exiled by"
          " the Villagers. Only you remain."
      )

    return context

  @classmethod
  def from_json(cls, data: dict[Any, Any]):
    name = data["name"]
    model = data.get("model", None)
    o = cls(name=name, model=model)
    o.gamestate = data.get("gamestate", None)
    o.bidding_rationale = data.get("bidding_rationale", "")
    o.observations = data.get("observations", [])
    o._restore_experiment_fields(data)
    return o


class Seer(Player):
  """Represents a Seer in the game."""

  def __init__(
      self,
      name: str,
      model: Optional[str] = None,
      personality: Optional[str] = None,
  ):
    super().__init__(name=name, role=SEER, model=model, personality=personality)
    self.previously_unmasked: Dict[str, str] = {}

  def unmask(self) -> tuple[str | None, LmLog]:
    """Choose a player to unmask."""
    if not self.gamestate:
      raise ValueError(
          "GameView not initialized. Call initialize_game_view() first."
      )

    options = [
        player
        for player in self.gamestate.current_players
        if player != self.name and player not in self.previously_unmasked.keys()
    ]
    random.shuffle(options)
    return self._generate_action("investigate", options)

  def reveal_and_update(self, player, role):
    self._add_observation(
        f"During the night, I decided to investigate {player} and learned they are a {role}."
    )
    self.previously_unmasked[player] = role

  @classmethod
  def from_json(cls, data: dict[Any, Any]):
    name = data["name"]
    model = data.get("model", None)
    o = cls(name=name, model=model)
    o.previously_unmasked = data.get("previously_unmasked", {})
    o.gamestate = data.get("gamestate", None)
    o.bidding_rationale = data.get("bidding_rationale", "")
    o.observations = data.get("observations", [])
    o._restore_experiment_fields(data)
    return o


class Doctor(Player):
  """Represents a Doctor in the game."""

  def __init__(
      self,
      name: str,
      model: Optional[str] = None,
      personality: Optional[str] = None,
  ):
    super().__init__(
        name=name, role=DOCTOR, model=model, personality=personality
    )

  def save(self) -> tuple[str | None, LmLog]:
    """Choose a player to protect."""
    if not self.gamestate:
      raise ValueError(
          "GameView not initialized. Call initialize_game_view() first."
      )

    options = list(self.gamestate.current_players)
    random.shuffle(options)
    protected, log = self._generate_action("protect", options)
    if protected is not None:
      self._add_observation(f"During the night, I chose to protect {protected}")
    return protected, log

  @classmethod
  def from_json(cls, data: dict[Any, Any]):
    name = data["name"]
    model = data.get("model", None)
    o = cls(name=name, model=model)
    o.gamestate = data.get("gamestate", None)
    o.bidding_rationale = data.get("bidding_rationale", "")
    o.observations = data.get("observations", [])
    o._restore_experiment_fields(data)
    return o


class Round(Deserializable):
  """Represents a round of gameplay in Werewolf.

  Attributes:
    players: List of player names in this round.
    eliminated: Who the werewolves killed during the night phase.
    unmasked: Who the Seer unmasked during the night phase.
    protected: Who the Doctor saved during the night phase.
    exiled: Who the players decided to exile after the debate.
    debate: List of debate tuples of player name and what they said during the
      debate.
    votes:  Who each player voted to exile after each line of dialogue in the
      debate.
    bids: What each player bid to speak next during each turn in the debate.
    success (bool): Indicates whether the round was completed successfully.

  Methods:
    to_dict: Returns a dictionary representation of the round.
  """

  def __init__(self):
    self.players: List[str] = []
    self.eliminated: str | None = None
    self.unmasked: str | None = None
    self.protected: str | None = None
    self.exiled: str | None = None
    self.debate: List[Tuple[str, str]] = []
    self.votes: List[Dict[str, str]] = []
    self.bids: List[Dict[str, int]] = []
    self.belief_snapshots: List[List[Dict[str, Any]]] = []
    self.success: bool = False

  def to_dict(self):
    return to_dict(self)

  @classmethod
  def from_json(cls, data: Dict[Any, Any]):
    o = cls()
    o.players = data["players"]
    o.eliminated = data.get("eliminated", None)
    o.unmasked = data.get("unmasked", None)
    o.protected = data.get("protected", None)
    o.exiled = data.get("exiled", None)
    o.debate = data.get("debate", [])
    o.votes = data.get("votes", [])
    o.bids = data.get("bids", [])
    o.belief_snapshots = data.get("belief_snapshots", [])
    o.success = data.get("success", False)
    return o


class State(Deserializable):
  """Represents a game session.

  Attributes:
    session_id: Unique identifier for the game session.
    players: List of players in the game.
    seer: The player with the seer role.
    doctor: The player with the doctor role.
    villagers: List of players with the villager role.
    werewolves: List of players with the werewolf role.
    rounds: List of Rounds in the game.
    error_message: Contains an error message if the game failed during
      execution.
    winner: Villager or Werewolf

  Methods:
    to_dict: Returns a dictionary representation of the game.
  """

  def __init__(
      self,
      session_id: str,
      seer: Seer,
      doctor: Doctor,
      villagers: List[Villager],
      werewolves: List[Werewolf],
  ):
    self.session_id: str = session_id
    self.seer: Seer = seer
    self.doctor: Doctor = doctor
    self.villagers: List[Villager] = villagers
    self.werewolves: List[Werewolf] = werewolves
    self.players: Dict[str, Player] = {
        player.name: player
        for player in self.villagers
        + self.werewolves
        + [self.doctor, self.seer]
    }
    self.rounds: List[Round] = []
    self.error_message: str = ""
    self.winner: str = ""

  def to_dict(self):
    return to_dict(self)

  @classmethod
  def from_json(cls, data: Dict[Any, Any]):
    werewolves = []
    for w in data.get("werewolves", []):
      werewolves.append(Werewolf.from_json(w))

    villagers = []
    for v in data.get("villagers", []):
      villagers.append(Villager.from_json(v))

    doctor = Doctor.from_json(data.get("doctor"))
    seer = Seer.from_json(data.get("seer"))

    players = {}
    for p in werewolves + villagers + [doctor, seer]:
      players[p.name] = p

    o = cls(
        data.get("session_id", ""),
        seer,
        doctor,
        villagers,
        werewolves,
    )
    rounds = []
    for r in data.get("rounds", []):
      rounds.append(Round.from_json(r))

    o.rounds = rounds
    o.error_message = data.get("error_message", "")
    o.winner = data.get("winner", "")
    return o


class VoteLog(Deserializable):

  def __init__(self, player: str, voted_for: str, log: LmLog):
    self.player = player
    self.voted_for = voted_for
    self.log = log

  def to_dict(self):
    return to_dict(self)

  @classmethod
  def from_json(cls, data: Dict[Any, Any]):
    player = data.get("player", None)
    voted_for = data.get("voted_for", None)
    log = LmLog.from_json(data.get("log", None))
    return cls(player, voted_for, log)


class RoundLog(Deserializable):
  """Represents the logs of a round of gameplay in Werewolf.

  Attributes:
    eliminate: Logs from the eliminate action taken by werewolves.
    investigate: Log from the invesetigate action taken by the seer.
    protect: Log from the protect action taken by the doctor.
    bid: Logs from the bidding actions. The 1st element in the list is the bidding logs
      for the 1st debate turn, the 2nd element is the logs for the 2nd debate
      turn, and so on. Every player bids to speak on every turn, so the element
      is a list too. The tuple contains the name of the player and the log of
      their bidding.
    debate: Logs of the debates. Each round has multiple debate turbns, so it's a
      list. Each element is a tuple - the 1st element is the name of the player
      who spoke at this turn, and the 2nd element is the log.
    vote: Log of the votes. A list of logs, one for every player who voted. The
      1st element of the tuple is the name of the player, and the 2nd element is
      the log.
    summaries: Logs from the summarize step. Every player summarizes their
      observations at the end of a round before they vote. Each element is a
      tuple where the 1st element is the name of the player, and the 2nd element
      is the log
  """

  def __init__(self):
    self.eliminate: LmLog | None = None
    self.investigate: LmLog | None = None
    self.protect: LmLog | None = None
    self.bid: List[List[Tuple[str, LmLog]]] = []
    self.debate: List[Tuple[str, LmLog]] = []
    self.votes: List[List[VoteLog]] = []
    self.summaries: List[Tuple[str, LmLog]] = []

  def to_dict(self):
    return to_dict(self)

  @classmethod
  def from_json(cls, data: Dict[Any, Any]):
    o = cls()

    eliminate = data.get("eliminate", None)
    investigate = data.get("investigate", None)
    protect = data.get("protect", None)

    if eliminate:
      o.eliminate = LmLog.from_json(eliminate)
    if investigate:
      o.investigate = LmLog.from_json(investigate)
    if protect:
      o.protect = LmLog.from_json(protect)

    for votes in data.get("votes", []):
      v_logs = []
      o.votes.append(v_logs)
      for v in votes:
        v_logs.append(VoteLog.from_json(v))

    for r in data.get("bid", []):
      r_logs = []
      o.bid.append(r_logs)
      for player in r:
        r_logs.append((player[0], LmLog.from_json(player[1])))

    for player in data.get("debate", []):
      o.debate.append((player[0], LmLog.from_json(player[1])))

    for player in data.get("summaries", []):
      o.summaries.append((player[0], LmLog.from_json(player[1])))

    return o
