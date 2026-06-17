from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class GameState:
    round_number: int = 1
    max_rounds: int = 100
    player_a_score: int = 0
    player_b_score: int = 0
    player_a_cooperations: int = 0
    player_b_cooperations: int = 0
    history: List[Tuple[str, str]] = field(default_factory=list)
    
    def get_last_n_rounds(self, n: int = 5) -> List[Tuple[str, str]]:
        return self.history[-n:] if len(self.history) >= n else self.history
    
    def get_round_payoff(self, action_a: str, action_b: str) -> Tuple[int, int]:
        payoffs = {
            ("Defect", "Defect"): (1, 1),
            ("Defect", "Cooperate"): (5, 0),
            ("Cooperate", "Defect"): (0, 5),
            ("Cooperate", "Cooperate"): (3, 3),
        }
        return payoffs.get((action_a, action_b), (0, 0))


class PrisonersDilemmaGame:
    
    def __init__(self, max_rounds: int = 100):
        self.state = GameState(max_rounds=max_rounds)
        self.round_results: List[Dict] = []
    
    def play_round(self, action_a: str, action_b: str) -> Dict:
        valid_actions = {"Cooperate", "Defect"}
        if action_a not in valid_actions or action_b not in valid_actions:
            logger.error(f"Invalid action: A={action_a}, B={action_b}")
            action_a, action_b = "Cooperate", "Cooperate"
        
        payoff_a, payoff_b = self.state.get_round_payoff(action_a, action_b)
        
        self.state.player_a_score += payoff_a
        self.state.player_b_score += payoff_b
        
        if action_a == "Cooperate":
            self.state.player_a_cooperations += 1
        if action_b == "Cooperate":
            self.state.player_b_cooperations += 1
        
        self.state.history.append((action_a, action_b))
        
        result = {
            "round": self.state.round_number,
            "action_a": action_a,
            "action_b": action_b,
            "payoff_a": payoff_a,
            "payoff_b": payoff_b,
            "total_score_a": self.state.player_a_score,
            "total_score_b": self.state.player_b_score,
        }
        
        self.round_results.append(result)
        
        self.state.round_number += 1
        
        return result
    
    def is_finished(self) -> bool:
        return self.state.round_number > self.state.max_rounds
    
    def get_game_summary(self) -> Dict:
        return {
            "total_rounds": len(self.round_results),
            "player_a_total_score": self.state.player_a_score,
            "player_b_total_score": self.state.player_b_score,
            "player_a_cooperations": self.state.player_a_cooperations,
            "player_b_cooperations": self.state.player_b_cooperations,
            "player_a_defections": len(self.round_results) - self.state.player_a_cooperations,
            "player_b_defections": len(self.round_results) - self.state.player_b_cooperations,
            "winner": "A" if self.state.player_a_score > self.state.player_b_score else ("B" if self.state.player_b_score > self.state.player_a_score else "Tie"),
        }


class GameTournament:
    
    def __init__(self, num_games: int = 5, rounds_per_game: int = 100):
        self.num_games = num_games
        self.rounds_per_game = rounds_per_game
        self.games: List[PrisonersDilemmaGame] = []
        self.tournament_results: List[Dict] = []
    
    def get_tournament_stats(self) -> Dict:
        if not self.tournament_results:
            return {}
        
        total_score_a = sum(r["player_a_total_score"] for r in self.tournament_results)
        total_score_b = sum(r["player_b_total_score"] for r in self.tournament_results)
        avg_cooperations_a = sum(r["player_a_cooperations"] for r in self.tournament_results) / len(self.tournament_results)
        avg_cooperations_b = sum(r["player_b_cooperations"] for r in self.tournament_results) / len(self.tournament_results)
        
        wins_a = sum(1 for r in self.tournament_results if r["winner"] == "A")
        wins_b = sum(1 for r in self.tournament_results if r["winner"] == "B")
        ties = sum(1 for r in self.tournament_results if r["winner"] == "Tie")
        
        return {
            "total_games": len(self.tournament_results),
            "total_score_a": total_score_a,
            "total_score_b": total_score_b,
            "avg_score_per_game_a": total_score_a / len(self.tournament_results),
            "avg_score_per_game_b": total_score_b / len(self.tournament_results),
            "avg_cooperations_a": avg_cooperations_a,
            "avg_cooperations_b": avg_cooperations_b,
            "wins_a": wins_a,
            "wins_b": wins_b,
            "ties": ties,
        }
