import pprint

class Critic(object):
    def __init__(self, board, gamma):
        self.board = board
        self.gamma = gamma
        pass

    def generate_training_set(self, game_history, use_gamma, v=None):
        training_set = []

        # Si no se usa v para calcular los de entrenamiento -> Uso valores 1 y -1
        if not v:
            if self.board.is_final()['winner'] == 1:
                value = 1
            elif self.board.is_final()['winner'] == 2:
                value = -1
            else:
                value = -0.5
            training_set.append((self.board.current_board,value))

        gamma = 1
        base_gamma = self.gamma

        for i, board in enumerate(reversed(game_history)):
            if use_gamma:
                gamma = gamma * base_gamma

            if v:
                value = gamma * v(game_history[i - 1])
            # Si no le paso v -> uso valores 1 y -1
            else:
                value = value*gamma

            # Si es el tablero final -> no le asigno valor porque no tiene sucesor
            if i != 0:
                training_set.append((board,value))

        return training_set
