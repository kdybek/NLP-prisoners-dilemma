from absl import app, flags
import json
from src.analysis_utils.types import Action
import src.analysis_utils.metrics as metrics
import pandas as pd
import os


FLAGS = flags.FLAGS
flags.DEFINE_string('results_dir', 'results/', 'Path to the directory containing the results.')
flags.DEFINE_string('output_file', 'results/analyzed_results.csv', 'Path to the output CSV file for analysis results.')


def analyze_results(input_file):
    with open(input_file, 'r') as f:
        game_data = json.load(f)
        matchups = game_data['matchups']
        records = []
        for i, matchup in enumerate(matchups):
            random_player_defection_prob = matchup['player_b']['defection_probability']
            for j, game in enumerate(matchup['games']):
                history = [(Action.COOPERATE if move['action_a'] == 'Cooperate' else Action.DEFECT,
                            Action.COOPERATE if move['action_b'] == 'Cooperate' else Action.DEFECT) for move in game['round_details']]

                nice_factor = metrics.player1_nice_factor(history)
                forgiving_factor = metrics.player1_forgiving_factor(history)
                retaliatory_factor = metrics.player1_retaliatory_factor(history)
                troublemaking_factor = metrics.player1_troublemaking_factor(history)
                emulative_factor = metrics.player1_emulative_factor(history)

                records.append({
                    'matchup_id': i,
                    'game_id': j,
                    'model': game_data['model'],
                    'prompt_file': game_data['prompt_file'],
                    'random_player_defection_prob': random_player_defection_prob,
                    'nice_factor': nice_factor,
                    'forgiving_factor': forgiving_factor,
                    'retaliatory_factor': retaliatory_factor,
                    'troublemaking_factor': troublemaking_factor,
                    'emulative_factor': emulative_factor,
                    'player_a_total_score': game['player_a_total_score'],
                    'player_b_total_score': game['player_b_total_score'],
                })

        return records


def main(_):
    results_dir = FLAGS.results_dir
    if not results_dir:
        print("Please provide the path to the input file using --input_file flag.")
        return
    all_records = []
    for filename in os.listdir(results_dir):
        if filename.endswith('.json'):
            input_file = os.path.join(results_dir, filename)
            records = analyze_results(input_file)
            all_records.extend(records)

    df = pd.DataFrame(all_records)
    df.to_csv(FLAGS.output_file, index=False)


if __name__ == '__main__':
    app.run(main)
