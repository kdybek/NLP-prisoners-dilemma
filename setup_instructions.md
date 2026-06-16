# Prisoner's Dilemma LLM Assessment - Setup Instructions

## Setup Steps

### 1. Install Ollama
**Linux Installation:**
```bash
# Download and install
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version
```

### 2. Pull a Language Model
```bash
# Pull the default model (llama2)
ollama pull llama2

# Or try other models:
ollama pull mistral
ollama pull neural-chat
ollama pull orca-mini
```

### 3. Start Ollama Server
```bash
ollama serve
```
This will start the Ollama API on `http://localhost:11434`

### 4. Setup Python Environment
In a new terminal:
```bash

python -m venv venv

source venv/bin/activate 

pip install -r requirements.txt
```

### 5. Run the Assessment
```bash
# Make sure venv is activated and Ollama is running, then:
python main.py
```

## Project Structure
```
.
├── main.py                 # Entry point
├── prompts.json            # Game prompts and personas
├── requirements.txt        # Python dependencies
├── .env.example            # Environment configuration template
├── setup_instructions.md   # This file
├── src/
│   ├── game.py            # Game logic (PrisonersDilemmaGame)
│   ├── game_runner.py     # Tournament orchestration
│   ├── llm_client.py      # Ollama API client
│   └── player.py          # LLM player implementation
└── results/               # Tournament results (created on first run)
```

## Usage

### Running Default Tournament
```bash
python main.py
```
This runs 3 matchups with 5 games each using the default model.

### Custom Configuration
Edit `.env` file:
```env
DEFAULT_MODEL=mistral          # Change model
NUM_ROUNDS=50                  # Change rounds per game
NUM_GAMES=3                    # Change games per matchup
```

### Analyzing Results
Results are saved to `results/` folder as JSON files with timestamps.
You can analyze them with Python:

```python
import json

with open("results/tournament_results_20250616_120000.json") as f:
    results = json.load(f)

# Examine matchup results
for matchup in results["matchups"]:
    print(f"{matchup['player_a']['name']} vs {matchup['player_b']['name']}")
    print(f"Stats: {matchup['stats']}")
```

## Understanding the Output

### Game State Context
The LLM receives context about:
- Last 5 rounds of actions
- Cooperation/defection counts
- Current scores
- Round number

### Player Personas
1. **Baseline**: Neutral player following the rules
2. **Compassionate**: Inspired by Mother Theresa, cooperative nature
3. **Narcissistic**: Inspired by Julius Caesar, self-interested

### Payoff Matrix
- Both Cooperate: 3 points each
- Both Defect: 1 point each
- A Defects, B Cooperates: A gets 5, B gets 0
- A Cooperates, B Defects: A gets 0, B gets 5


### Custom Matchups
Edit `player_configs` in `main.py` to create custom player combinations.

## Performance Notes
- First run downloads model (may take time)
- Each game generates multiple LLM API calls
- Default settings (5 games × 100 rounds = 1000 rounds per matchup)
- Estimated runtime: 10-30 minutes depending on model and hardware

## Next Steps
1. Run the default tournament and examine results
2. Try different models
3. Add custom personas
4. Create statistical analysis script
5. Visualize results with matplotlib/plotly
