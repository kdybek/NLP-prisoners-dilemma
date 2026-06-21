"""
Main game runner for prisoner's dilemma tournament
"""
import json
import logging
from typing import Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from src.game import PrisonersDilemmaGame, GameTournament
from src.llm_client import OllamaClient
from src.player import LLMPlayer, Player, RandomPlayer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GameRunner:
    def __init__(
        self,
        llm_model: str,
        ollama_url: str,
        output_dir: str,
        prompt_file: str,
    ):
        self.llm_client = OllamaClient(base_url=ollama_url, model=llm_model)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        with open(prompt_file, "r") as f:
            self.prompts = json.load(f)

    def create_player(
        self,
        config: Dict[str, Any],
    ) -> Player:
        if config["type"] == "random":
            name = "Random Player"
            defection_probability = config["defection_probability"]
            return RandomPlayer(name=name, defection_probability=defection_probability)
        elif config["type"] == "llm":
            name = "LLM"
            temperature = config["temperature"]
            return LLMPlayer(name=name, temperature=temperature, llm_client=self.llm_client, prompts_dict=self.prompts)
        else:
            raise ValueError(f"Unknown player type: {config['type']}")

    def build_game_context(
        self,
        game: PrisonersDilemmaGame,
        round_num: int,
        prompt_score_multiplier: int
    ) -> str:
        if len(game.state.history) == 0:
            return "Current round: 1."

        # Get last 10 rounds for context
        last_rounds = min(10, len(game.state.history))
        context_lines = []

        for i, (action_a, action_b) in enumerate(game.state.history[-last_rounds:],
                                                 start=round_num - last_rounds):
            payoff_a, payoff_b = game.state.get_round_payoff(action_a, action_b)
            payoff_a *= prompt_score_multiplier
            payoff_b *= prompt_score_multiplier
            payoff_a_text = f"{payoff_a} point" if payoff_a == 1 else f"{
                payoff_a} points"
            payoff_b_text = f"{payoff_b} point" if payoff_b == 1 else f"{
                payoff_b} points"
            context_lines.append(
                f'Round {i}: A played "{action_a}" and B played "{action_b}", '
                f'A collected {payoff_a_text} and B collected {payoff_b_text}.'
            )

        if last_rounds == 1:
            context = "The history of the game in the last round is the following:\n"
        else:
            context = f"The history of the game in the last {
                last_rounds} rounds is the following:\n"
        context += "\n".join(context_lines)
        a_cooperations = game.state.player_a_cooperations
        b_cooperations = game.state.player_b_cooperations
        a_defections = len(game.state.history) - a_cooperations
        b_defections = len(game.state.history) - b_cooperations
        a_coop_text = f"{a_cooperations} time" if a_cooperations == 1 else f"{
            a_cooperations} times"
        a_defect_text = f"{a_defections} time" if a_defections == 1 else f"{
            a_defections} times"
        b_coop_text = f"{b_cooperations} time" if b_cooperations == 1 else f"{
            b_cooperations} times"
        b_defect_text = f"{b_defections} time" if b_defections == 1 else f"{
            b_defections} times"
        context += f"\nIn total, A chose \"Cooperate\" {
            a_coop_text} and chose \"Defect\" {a_defect_text}, "
        context += f"B chose \"Cooperate\" {
            b_coop_text} and chose \"Defect\" {b_defect_text}.\n"
        payoff_a_total = game.state.player_a_score * prompt_score_multiplier
        payoff_b_total = game.state.player_b_score * prompt_score_multiplier
        payoff_a_total_text = f"{payoff_a_total} point" if payoff_a_total == 1 else f"{
            payoff_a_total} points"
        payoff_b_total_text = f"{payoff_b_total} point" if payoff_b_total == 1 else f"{
            payoff_b_total} points"
        context += f"In total, A collected {
            payoff_a_total_text} and B collected {payoff_b_total_text}.\n"
        context += f"Current round: {round_num}."

        return context

    def play_game(
        self,
        player_a: Player,
        player_b: Player,
        num_rounds: int,
        independent_payoffs: str,
        verbose: bool = True,
        prompt_score_multiplier: int = 1,
    ) -> Dict[str, Any]:
        game = PrisonersDilemmaGame(max_rounds=num_rounds,
                                    independent_payoffs=independent_payoffs)

        iterator = tqdm(range(num_rounds), desc="Playing game", disable=not verbose)

        for round_num in iterator:
            game_context = self.build_game_context(
                game, round_num + 1, prompt_score_multiplier=prompt_score_multiplier)

            game_state_a = {
                "round": round_num + 1,
                "context": game_context,
                "player": "A"
            }
            game_state_b = {
                "round": round_num + 1,
                "context": game_context,
                "player": "B"
            }

            # Get decisions
            decision_a = player_a.make_decision(game_state_a)
            decision_b = player_b.make_decision(game_state_b)

            action_a = decision_a["action"]
            action_b = decision_b["action"]

            game.play_round(action_a, action_b)

            if verbose and (round_num + 1) % 10 == 0:
                logger.info(f"Round {round_num + 1}: A={action_a}, B={action_b} | "
                            f"Scores: A={game.state.player_a_score}, B={game.state.player_b_score}")

        summary = game.get_game_summary()
        summary["round_details"] = game.round_results

        return summary

    def run_tournament(
        self,
        matchups: list,
        num_games: int,
        num_rounds: int,
        independent_payoffs: str,
        verbose: bool = True,
        prompt_score_multiplier: int = 1
    ) -> Dict[str, Any]:
        tournament_results = {
            "timestamp": datetime.now().isoformat(),
            "num_games_per_matchup": num_games,
            "matchups": []
        }

        for player_a_config, player_b_config in matchups:
            logger.info(f"\n{'='*60}")
            logger.info(f"Matchup: {player_a_config['type']} vs {
                        player_b_config['type']}")
            logger.info(f"{'='*60}")

            matchup_results = {
                "player_a": player_a_config,
                "player_b": player_b_config,
                "games": []
            }

            for game_num in range(num_games):
                logger.info(f"\nGame {game_num + 1}/{num_games}")

                player_a = self.create_player(player_a_config)
                player_b = self.create_player(player_b_config)

                result = self.play_game(player_a,
                                        player_b,
                                        num_rounds=num_rounds,
                                        independent_payoffs=independent_payoffs,
                                        verbose=verbose,
                                        prompt_score_multiplier=prompt_score_multiplier
                                        )
                matchup_results["games"].append(result)

            # Calculate matchup stats
            matchup_results["stats"] = self._calculate_matchup_stats(matchup_results)
            tournament_results["matchups"].append(matchup_results)

        return tournament_results

    def _calculate_matchup_stats(self, matchup: Dict) -> Dict[str, Any]:
        games = matchup["games"]

        total_score_a = sum(g["player_a_total_score"] for g in games)
        total_score_b = sum(g["player_b_total_score"] for g in games)
        avg_cooperations_a = sum(g["player_a_cooperations"] for g in games) / len(games)
        avg_cooperations_b = sum(g["player_b_cooperations"] for g in games) / len(games)

        wins_a = sum(1 for g in games if g["winner"] == "A")
        wins_b = sum(1 for g in games if g["winner"] == "B")
        ties = sum(1 for g in games if g["winner"] == "Tie")

        return {
            "total_score_a": total_score_a,
            "total_score_b": total_score_b,
            "avg_score_per_game_a": total_score_a / len(games),
            "avg_score_per_game_b": total_score_b / len(games),
            "avg_cooperations_a": avg_cooperations_a,
            "avg_cooperations_b": avg_cooperations_b,
            "wins_a": wins_a,
            "wins_b": wins_b,
            "ties": ties,
        }

    def save_results(self, results: Dict[str, Any], filename: str = None) -> Path:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tournament_results_{timestamp}.json"

        filepath = self.output_dir / filename

        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results saved to {filepath}")
        return filepath
