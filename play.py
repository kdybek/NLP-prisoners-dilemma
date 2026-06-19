import json
import logging
from pathlib import Path
import os
from absl import app, flags
import numpy as np
import random

from src.game_runner import GameRunner


FLAGS = flags.FLAGS
OLLAMA_BASE_URL = "http://localhost:11434"
flags.DEFINE_string("model", "llama2", "The model to use for the LLM player.")
flags.DEFINE_integer("rounds", 100, "Number of rounds per game.")
flags.DEFINE_integer("games", 30, "Number of games against random opponents of differing hostility.")
flags.DEFINE_string("output_dir", "./results", "Directory to save results.")
flags.DEFINE_string("prompt_file", "prompts.json", "Path to the prompts JSON file.")
flags.DEFINE_integer("prompt_score_multiplier", 1, "Multiplier for the score in the prompt context.")


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(_):
    model = FLAGS.model
    num_rounds = FLAGS.rounds
    num_games = FLAGS.games
    output_dir = FLAGS.output_dir
    prompt_file = FLAGS.prompt_file
    prompt_score_multiplier = FLAGS.prompt_score_multiplier

    random.seed(42)

    logger.info("Starting Prisoner's Dilemma Assessment")
    runner = GameRunner(
        llm_model=model,
        ollama_url=OLLAMA_BASE_URL,
        output_dir=output_dir,
        prompt_file=prompt_file
    )

    if not runner.llm_client.check_connection():
        logger.error("Cannot connect to Ollama. Make sure it's running:")
        logger.error("  ollama serve")
        logger.error("And pull a model:")
        logger.error(f"  ollama pull {model}")
        return

    llm_config = {
            "type": "llm",
            "temperature": 0.7
    }

    random_players = [
        {
            "type": "random",
            "defection_probability": prob
        } for prob in np.linspace(0, 1, num=num_games)
    ]

    matchups = [(llm_config, random_config) for random_config in random_players]

    logger.info(f"Running tournament with {len(matchups)} matchups, {
                num_games} games per matchup")
    results = runner.run_tournament(
        matchups=matchups,
        num_games=1,
        num_rounds=num_rounds,
        verbose=True,
        prompt_score_multiplier=prompt_score_multiplier
    )
    results.update({
        "model": model,
        "prompt_file": prompt_file
    })

    results_file = runner.save_results(results)

    logger.info("\n" + "="*60)
    logger.info("TOURNAMENT SUMMARY")
    logger.info("="*60)

    for i, matchup in enumerate(results["matchups"], 1):
        stats = matchup["stats"]

        logger.info(f"\nMatchup {i}")
        logger.info(f"  A Total Score: {stats['total_score_a']}")
        logger.info(f"  B Total Score: {stats['total_score_b']}")
        logger.info(f"  A Avg Score/Game: {stats['avg_score_per_game_a']:.2f}")
        logger.info(f"  B Avg Score/Game: {stats['avg_score_per_game_b']:.2f}")
        logger.info(f"  A Cooperation Rate: {stats['avg_cooperations_a']:.2f}")
        logger.info(f"  B Cooperation Rate: {stats['avg_cooperations_b']:.2f}")
        logger.info(f"  Wins: A={stats['wins_a']}, B={
                    stats['wins_b']}, Ties={stats['ties']}")

    logger.info(f"\nFull results saved to: {results_file}")


if __name__ == "__main__":
    app.run(main)
