# LLM Prisoner's Dilemma Assessment

Assess how Large Language Models (LLMs) play the iterated prisoner's dilemma game with different personas.

## Quick Start

1. **Install Ollama** (https://ollama.ai) and pull a model:
   ```bash
   ollama pull llama2
   ollama serve
   ```

2. **Setup Python** (in new terminal):
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run Assessment**:
   ```bash
   python main.py
   ```

## What This Does

- Creates LLM-based players with different personas
- Runs multiple games of iterated prisoner's dilemma
- Tracks cooperation rates, scores, and strategy outcomes
- Analyzes how LLMs respond to different game scenarios
- Generates detailed tournament results

## Key Components

| File | Purpose |
|------|---------|
| `src/llm_client.py` | Ollama API communication |
| `src/game.py` | Game logic and state management |
| `src/player.py` | LLM player implementation |
| `src/game_runner.py` | Tournament orchestration |
| `main.py` | Entry point |
| `prompts.json` | Game rules and personas |

## Configuration

Edit `.env` to customize:
- `DEFAULT_MODEL`: Which LLM to use
- `NUM_ROUNDS`: Rounds per game (default: 100)
- `NUM_GAMES`: Games per matchup (default: 5)

## Results

Tournament results saved to `results/` folder as JSON with:
- Round-by-round decisions
- Score breakdowns
- Cooperation statistics
- Win/loss records


## See Also

- [Setup Instructions](setup_instructions.md)
- [Ollama Documentation](https://ollama.ai)
