from typing import Optional
from types import GameHistory, Action


def player1_nice_factor(history: GameHistory) -> float:
    for action1, action2 in history:
        if action1 == Action.DEFECT:
            return 0.0
        elif action2 == Action.DEFECT:
            return 1.0

    return 1.0


def player1_forgiving_factor(history: GameHistory) -> Optional[float]:
    forgiven_defections = 0
    opponent_defections = 0
    penalties = 0
    unforgiven_opponent_defection = False
    opponent_seeking_forgiveness = False

    for i in range(len(history)):
        player1_action, player2_action = history[i]
        if player1_action == Action.DEFECT:
            if opponent_seeking_forgiveness:
                penalties += 1
        else:  # player1_action == Action.COOPERATE
            if unforgiven_opponent_defection:
                forgiven_defections += 1
                unforgiven_opponent_defection = False
                opponent_seeking_forgiveness = False

        if i == len(history) - 1:
            break  # Not checking the last action of player2, as it cannot be forgiven

        if player2_action == Action.DEFECT:
            opponent_defections += 1
            unforgiven_opponent_defection = True
            opponent_seeking_forgiveness = False
        else:  # player2_action == Action.COOPERATE
            if unforgiven_opponent_defection:
                opponent_seeking_forgiveness = True

    if opponent_defections + penalties == 0:
        return None

    return forgiven_defections / (opponent_defections + penalties)


def player1_retaliatory_factor(history: GameHistory) -> Optional[float]:
    reactions = 0
    provocations = 0

    hist_aux = [(Action.COOPERATE, Action.COOPERATE)] + history

    for i in range(len(hist_aux) - 2):
        player1_action1 = hist_aux[i][0]
        player2_action2 = hist_aux[i + 1][1]
        player1_action3 = hist_aux[i + 2][0]

        if player1_action1 == Action.COOPERATE and player2_action2 == Action.DEFECT:
            provocations += 1
            if player1_action3 == Action.DEFECT:
                reactions += 1

    if provocations == 0:
        return None

    return reactions / provocations


def player1_troublemaking_factor(history: GameHistory) -> Optional[float]:
    uncalled_defections = 0
    occasions_to_provoke = 0

    hist_aux = [(Action.COOPERATE, Action.COOPERATE)] + history

    for i in range(len(hist_aux) - 1):
        player2_action1 = hist_aux[i][1]
        player1_action2 = hist_aux[i + 1][0]

        if player2_action1 == Action.COOPERATE:
            occasions_to_provoke += 1
            if player1_action2 == Action.DEFECT:
                uncalled_defections += 1

    if occasions_to_provoke == 0:
        return None

    return uncalled_defections / occasions_to_provoke


def player1_emulative_factor(history: GameHistory) -> Optional[float]:
    N = len(history)
    emulations = 0

    for i in range(N - 1):
        player2_action1 = history[i][1]
        player1_action2 = history[i + 1][0]

        if player2_action1 == player1_action2:
            emulations += 1

    if N < 2:
        return None

    return emulations / (N - 1)




