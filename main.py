import json
import logging
from pathlib import Path
from dotenv import load_dotenv
import os

from src.game_runner import GameRunner

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    default_model = os.getenv("DEFAULT_MODEL", "llama2")
    num_rounds = int(os.getenv("NUM_ROUNDS", "100"))
    num_games = int(os.getenv("NUM_GAMES", "5"))
    output_dir = os.getenv("OUTPUT_DIR", "./results")
    
    logger.info("Starting Prisoner's Dilemma Assessment")
    logger.info(f"Ollama URL: {ollama_url}")
    logger.info(f"Default Model: {default_model}")
    
    runner = GameRunner(
        llm_model=default_model,
        ollama_url=ollama_url,
        output_dir=output_dir
    )
    
    if not runner.llm_client.check_connection():
        logger.error("Cannot connect to Ollama. Make sure it's running:")
        logger.error("  ollama serve")
        logger.error("And pull a model:")
        logger.error(f"  ollama pull {default_model}")
        return
    
    player_configs = [
        {
            "name": "Baseline Player",
            "model": default_model,
            "company": "Test",
            "persona": "baseline",
            "temperature": 0.7
        },
        {
            "name": "Compassionate Player",
            "model": default_model,
            "company": "Test",
            "persona": "compassionate",
            "temperature": 0.7
        },
        {
            "name": "Narcissistic Player",
            "model": default_model,
            "company": "Test",
            "persona": "narcisstic",
            "temperature": 0.8
        }
    ]
    
    matchups = [
        (player_configs[0], player_configs[1]),  # Baseline vs Compassionate
        (player_configs[0], player_configs[2]),  # Baseline vs Narcissistic
        (player_configs[1], player_configs[2]),  # Compassionate vs Narcissistic
    ]
    
    logger.info(f"Running tournament with {len(matchups)} matchups, {num_games} games per matchup")
    results = runner.run_tournament(
        matchups=matchups,
        num_games=num_games,
        verbose=True
    )
    
    results_file = runner.save_results(results)
    
    logger.info("\n" + "="*60)
    logger.info("TOURNAMENT SUMMARY")
    logger.info("="*60)
    
    for i, matchup in enumerate(results["matchups"], 1):
        player_a_name = matchup["player_a"]["name"]
        player_b_name = matchup["player_b"]["name"]
        stats = matchup["stats"]
        
        logger.info(f"\nMatchup {i}: {player_a_name} vs {player_b_name}")
        logger.info(f"  A Total Score: {stats['total_score_a']}")
        logger.info(f"  B Total Score: {stats['total_score_b']}")
        logger.info(f"  A Avg Score/Game: {stats['avg_score_per_game_a']:.2f}")
        logger.info(f"  B Avg Score/Game: {stats['avg_score_per_game_b']:.2f}")
        logger.info(f"  A Cooperation Rate: {stats['avg_cooperations_a']:.2f}")
        logger.info(f"  B Cooperation Rate: {stats['avg_cooperations_b']:.2f}")
        logger.info(f"  Wins: A={stats['wins_a']}, B={stats['wins_b']}, Ties={stats['ties']}")
    
    logger.info(f"\nFull results saved to: {results_file}")


if __name__ == "__main__":
    main()
