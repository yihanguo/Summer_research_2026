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

"""Werewolf game."""

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import random
from typing import Any, List, Optional

import tqdm

from werewolf.model import Round, RoundLog, State, VoteLog
from werewolf.config import MAX_DEBATE_TURNS, RUN_SYNTHETIC_VOTES

def get_max_bids(d):
  """Gets all the keys with the highest value in the dictionary."""
  max_value = max(d.values())
  max_keys = [key for key, value in d.items() if value == max_value]
  return max_keys


class GameMaster:

  def __init__(
      self,
      state: State,
      num_threads: int = 1,
      event_sink: Optional[Any] = None,
      run_synthetic_votes: Optional[bool] = None,
      max_debate_turns: Optional[int] = None,
  ) -> None:
    """Initialize the Werewolf game.

    Args:
    """
    self.state = state
    self.current_round_num = len(self.state.rounds) if self.state.rounds else 0
    self.num_threads = num_threads
    self.event_sink = event_sink
    self.run_synthetic_votes = (
        RUN_SYNTHETIC_VOTES if run_synthetic_votes is None else run_synthetic_votes
    )
    self.max_debate_turns = (
        MAX_DEBATE_TURNS if max_debate_turns is None else max_debate_turns
    )
    if self.max_debate_turns < 1:
      raise ValueError("max_debate_turns must be positive")
    for player in self.state.players.values():
      player.max_debate_turns = self.max_debate_turns
    self.logs: List[RoundLog] = []

  @property
  def this_round(self) -> Round:
    return self.state.rounds[self.current_round_num]

  @property
  def this_round_log(self) -> RoundLog:
    return self.logs[self.current_round_num]

  def eliminate(self):
    """Werewolves choose a player to eliminate."""
    werewolves_alive = [
        w for w in self.state.werewolves if w.name in self.this_round.players
    ]
    wolf = random.choice(werewolves_alive)
    eliminated, log = wolf.eliminate()
    self.this_round_log.eliminate = log
    if eliminated is not None:
      self.this_round.eliminated = eliminated
      tqdm.tqdm.write(f"{wolf.name} eliminated {eliminated}")
      for wolf in werewolves_alive:
        wolf._add_observation(
            "During the"
            f" night, {'we' if len(werewolves_alive) > 1 else 'I'} decided to"
            f" eliminate {eliminated}."
        )
    else:
      raise ValueError("Eliminate did not return a valid player.")

  def protect(self):
    """Doctor chooses a player to protect."""
    if self.state.doctor.name not in self.this_round.players:
      return  # Doctor no longer in the game

    protect, log = self.state.doctor.save()
    self.this_round_log.protect = log

    if protect is not None:
      self.this_round.protected = protect
      tqdm.tqdm.write(f"{self.state.doctor.name} protected {protect}")
    else:
      raise ValueError("Protect did not return a valid player.")

  def unmask(self):
    """Seer chooses a player to unmask."""
    if self.state.seer.name not in self.this_round.players:
      return  # Seer no longer in the game

    unmask, log = self.state.seer.unmask()
    self.this_round_log.investigate = log

    if unmask is not None:
      self.this_round.unmasked = unmask
      self.state.seer.reveal_and_update(unmask, self.state.players[unmask].role)
    else:
      raise ValueError("Unmask function did not return a valid player.")

  def _get_bid(self, player_name):
    """Gets the bid for a specific player."""
    player = self.state.players[player_name]
    bid, log = player.bid()
    if bid is None:
      raise ValueError(
          f"{player_name} did not return a valid bid. Find the raw response"
          " in the `bid` field in the log"
      )
    if bid > 1:
      tqdm.tqdm.write(f"{player_name} bid: {bid}")
    return bid, log

  def get_next_speaker(self, turn_number: int):
    """Measure every living player's beliefs, then select an eligible speaker."""
    previous_speaker, previous_dialogue = (
        self.this_round.debate[-1] if self.this_round.debate else (None, None)
    )

    with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
      player_bids = {
          player_name: executor.submit(self._get_bid, player_name)
          for player_name in self.this_round.players
      }

      bid_log = []
      bids = {}
      try:
        for player_name, bid_task in player_bids.items():
          bid, log = bid_task.result()
          bids[player_name] = bid
          bid_log.append((player_name, log))
      except TypeError as e:
        print(e)
        raise e

    self.this_round.bids.append(bids)
    self.this_round_log.bid.append(bid_log)

    snapshots = []
    for player_name, log in bid_log:
      payload = log.result
      if not isinstance(payload, dict):
        raise ValueError(f"{player_name} produced no structured belief snapshot.")
      snapshot = {
          "round": self.current_round_num + 1,
          "turn": turn_number,
          "player": player_name,
          "living_players": list(self.this_round.players),
          "source_message_ids": list(
              self.state.players[player_name].gamestate.public_message_ids
              if self.state.players[player_name].gamestate else []
          ),
          "bid": int(payload["bid"]),
          "speaker_eligible": player_name != previous_speaker,
          "top_suspect": payload["top_suspect"],
          "suspect_confidence_bin": int(payload["suspect_confidence_bin"]),
          "intended_vote": payload["intended_vote"],
          "evidence_state": payload["evidence_state"],
          "suspect_levels": [dict(item) for item in payload["suspect_levels"]],
          "structured_repair": bool(log.metadata.get("structured_repair", False)),
          "structured_repair_reason": log.metadata.get(
              "structured_repair_reason", ""
          ),
      }
      snapshots.append(snapshot)
      if self.event_sink:
        self.event_sink.record_belief_snapshot(
            event_id=f"r{self.current_round_num + 1}_t{turn_number}_belief_{player_name}",
            round_number=snapshot["round"],
            turn_number=snapshot["turn"],
            player=snapshot["player"],
            living_players=snapshot["living_players"],
            source_message_ids=snapshot["source_message_ids"],
            bid=snapshot["bid"],
            speaker_eligible=snapshot["speaker_eligible"],
            top_suspect=snapshot["top_suspect"],
            suspect_confidence_bin=snapshot["suspect_confidence_bin"],
            intended_vote=snapshot["intended_vote"],
            evidence_state=snapshot["evidence_state"],
            suspect_levels=snapshot["suspect_levels"],
            structured_repair=snapshot["structured_repair"],
            structured_repair_reason=snapshot["structured_repair_reason"],
            prompt_policy=self.state.players[player_name].coordination_policy,
        )
    self.this_round.belief_snapshots.append(snapshots)

    eligible_bids = {
        player: bid for player, bid in bids.items() if player != previous_speaker
    }
    potential_speakers = get_max_bids(eligible_bids)
    # Prioritize mentioned speakers if there's previous dialogue
    if previous_dialogue:
      potential_speakers.extend(
          [name for name in potential_speakers if name in previous_dialogue]
      )

    random.shuffle(potential_speakers)
    return random.choice(potential_speakers)

  def run_summaries(self):
    """Collect summaries from players after the debate."""

    with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
      player_summaries = {
          name: executor.submit(self.state.players[name].summarize)
          for name in self.this_round.players
      }

      for player_name, summary_task in player_summaries.items():
        summary, log = summary_task.result()
        tqdm.tqdm.write(f"{player_name} summary: {summary}")
        self.this_round_log.summaries.append((player_name, log))
        player = self.state.players[player_name]
        source_message_ids = (
            list(player.gamestate.public_message_ids)
            if player.gamestate else []
        )
        extracted_claims = []
        memory_refs = []
        confidence = None
        if isinstance(log.result, dict):
          extracted_claims = list(log.result.get("extracted_claims", []))
          memory_refs = list(log.result.get("memory_refs", []))
          confidence = log.result.get("confidence")
        player.private_round_memory.append({
            "round": self.current_round_num + 1,
            "source_message_ids": memory_refs or source_message_ids,
            "summary": summary or "",
            "extracted_claims": extracted_claims,
            "confidence": confidence,
        })
        if self.event_sink:
          self.event_sink.record_round_extraction(
              event_id=f"r{self.current_round_num + 1}_extract_{player_name}",
              round_number=self.current_round_num + 1,
              player=player_name,
              source_message_ids=memory_refs or source_message_ids,
              extracted_claims=extracted_claims,
              summary=summary or "",
              confidence=confidence,
          )

  def run_day_phase(self):
    """Run the day phase which consists of the debate and voting."""

    for idx in range(self.max_debate_turns):
      next_speaker = self.get_next_speaker(idx + 1)
      if not next_speaker:
        raise ValueError("get_next_speaker did not return a valid player.")

      player = self.state.players[next_speaker]
      dialogue, log = player.debate()
      if dialogue is None:
        raise ValueError(
            f"{next_speaker} did not return a valid dialouge from debate()."
        )

      self.this_round_log.debate.append((next_speaker, log))
      self.this_round.debate.append([next_speaker, dialogue])
      tqdm.tqdm.write(f"{next_speaker} ({player.role}): {dialogue}")

      message_id = f"r{self.current_round_num + 1}_t{idx + 1}_{next_speaker}"
      evidence_refs = []
      confidence = None
      public_suspect_levels = []
      if isinstance(log.result, dict):
        evidence_refs = list(log.result.get("evidence_refs", []))
        confidence = log.result.get("confidence")
        public_suspect_levels = list(log.result.get("public_suspect_levels", []))
      if self.event_sink:
        self.event_sink.record_public_message(
            event_id=message_id,
            round_number=self.current_round_num + 1,
            turn_number=idx + 1,
            speaker=next_speaker,
            recipients=list(self.this_round.players),
            dialogue=dialogue,
            evidence_refs=evidence_refs,
            confidence=confidence,
            public_suspect_levels=public_suspect_levels,
            structured_repair=bool(log.metadata.get("structured_repair", False)),
            structured_repair_reason=log.metadata.get(
                "structured_repair_reason", ""
            ),
            prompt_policy=player.coordination_policy,
        )

      for name in self.this_round.players:
        player = self.state.players[name]
        if player.gamestate:
          player.gamestate.update_debate(next_speaker, dialogue, message_id)
        else:
          raise ValueError(f"{name}.gamestate needs to be initialized.")

      if idx == self.max_debate_turns - 1 or self.run_synthetic_votes:
        votes, vote_logs = self.run_voting()
        self.this_round.votes.append(votes)
        self.this_round_log.votes.append(vote_logs)

    for player, vote in self.this_round.votes[-1].items():
      tqdm.tqdm.write(f"{player} voted to remove {vote}")

  def run_voting(self):
    """Conduct a vote among players to exile someone."""
    vote_log = []
    votes = {}

    with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
      player_votes = {
          name: executor.submit(self.state.players[name].vote)
          for name in self.this_round.players
      }

      for player_name, vote_task in player_votes.items():
        vote, log = vote_task.result()
        vote_log.append(VoteLog(player_name, vote, log))

        if vote is not None:
          votes[player_name] = vote
        else:
          self.this_round.votes.append(votes)
          self.this_round_log.votes.append(vote_log)
          raise ValueError(f"{player_name} vote did not return a valid player.")

    return votes, vote_log

  def exile(self):
    """Exile the player who received the most votes."""

    most_voted, vote_count = Counter(
        self.this_round.votes[-1].values()
    ).most_common(1)[0]

    if vote_count > len(self.this_round.players) / 2:
      self.this_round.exiled = most_voted

    if self.this_round.exiled is not None:
      exiled_player = self.this_round.exiled
      self.this_round.players.remove(exiled_player)
      announcement = (
          f"The majority voted to remove {exiled_player} from the game."
      )
    else:
      announcement = (
          "A majority vote was not reached, so no one was removed from the"
          " game."
      )

    for name in self.this_round.players:
      player = self.state.players[name]
      if player.gamestate and self.this_round.exiled is not None:
        player.gamestate.remove_player(self.this_round.exiled)
      player.add_announcement(announcement)

    tqdm.tqdm.write(announcement)

  def resolve_night_phase(self):
    """Resolve elimination and protection during the night phase."""
    removed_player = None
    if self.this_round.eliminated != self.this_round.protected:
      eliminated_player = self.this_round.eliminated
      self.this_round.players.remove(eliminated_player)
      removed_player = eliminated_player
      announcement = (
          f"The Werewolves removed {eliminated_player} from the game during the"
          " night."
      )
    else:
      announcement = "No one was removed from the game during the night."
    tqdm.tqdm.write(announcement)

    for name in self.this_round.players:
      player = self.state.players[name]
      if player.gamestate and removed_player is not None:
        player.gamestate.remove_player(removed_player)
      player.add_announcement(announcement)

  def run_round(self):
    """Run a single round of the game."""
    self.state.rounds.append(Round())
    self.logs.append(RoundLog())

    self.this_round.players = (
        list(self.state.players.keys())
        if self.current_round_num == 0
        else self.state.rounds[self.current_round_num - 1].players.copy()
    )

    for action, message in [
        (
            self.eliminate,
            "The Werewolves are picking someone to remove from the game.",
        ),
        (self.protect, "The Doctor is protecting someone."),
        (self.unmask, "The Seer is investigating someone."),
        (self.resolve_night_phase, ""),
        (self.check_for_winner, "Checking for a winner after Night Phase."),
        (self.run_day_phase, "The Players are debating and voting."),
        (self.exile, ""),
        (self.check_for_winner, "Checking for a winner after Day Phase."),
        (self.run_summaries, "The Players are summarizing the debate."),
    ]:
      tqdm.tqdm.write(message)
      action()

      if self.state.winner:
        tqdm.tqdm.write(f"Round {self.current_round_num} is complete.")
        self.this_round.success = True
        return

    tqdm.tqdm.write(f"Round {self.current_round_num} is complete.")
    self.this_round.success = True

  def get_winner(self) -> str:
    """Determine the winner of the game."""
    active_wolves = set(self.this_round.players) & set(
        w.name for w in self.state.werewolves
    )
    active_villagers = set(self.this_round.players) - active_wolves
    if len(active_wolves) >= len(active_villagers):
      return "Werewolves"
    return "Villagers" if not active_wolves else ""

  def check_for_winner(self):
    """Check if there is a winner and update the state accordingly."""
    self.state.winner = self.get_winner()
    if self.state.winner:
      tqdm.tqdm.write(f"The winner is {self.state.winner}!")

  def run_game(self) -> str:
    """Run the entire Werewolf game and return the winner."""
    while not self.state.winner:
      tqdm.tqdm.write(f"STARTING ROUND: {self.current_round_num}")
      self.run_round()
      for name in self.this_round.players:
        if self.state.players[name].gamestate:
          self.state.players[name].gamestate.round_number = (
              self.current_round_num + 1
          )
          self.state.players[name].gamestate.clear_debate()
      self.current_round_num += 1

    tqdm.tqdm.write("Game is complete!")
    return self.state.winner
