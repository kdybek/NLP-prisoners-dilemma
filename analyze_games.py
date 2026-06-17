from absl import app, flags
import json
from utils.types import Action
import utils.metrics as metrics
import pandas as pd


FLAGS = flags.FLAGS
flags.DEFINE_string('input_file', None, 'Path to the input file containing game data.')
flags.DEFINE_string('output_file', 'analysis_results.csv', 'Path to the output CSV file for analysis results.')


def main(_):
    input_file = FLAGS.input_file
    if not input_file:
        print("Please provide the path to the input file using --input_file flag.")
        return
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
                    'emulative_factor': emulative_factor
                })

    df = pd.DataFrame(records)
    df.to_csv(FLAGS.output_file, index=False)


if __name__ == '__main__':
    app.run(main)
