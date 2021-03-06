import copy
import logging
import math
import plots
import pprint
import statistics

from generator import Board, Generator
from performance_system import PerformanceSystem
from critic import Critic
from generalizer import Generalizer


def calculate_percentages(p_wins, draws):
    pass


def initial_training(board, generator, generalizer):
    # Winner finals
    for i in range(17):
       board.clear_board()
       if i < 17: 
           x = i
       else: 
           x = i % 17
       final_board = copy.deepcopy(generator.generate_final_board(x + 1, 1))
       logging.debug(pprint.pformat(final_board))
       training_set = [(final_board, 1)]
       generalizer.lms(training_set)
       logging.debug(generalizer.weights)

    # Loser finals
    for i in range(17):
       board.clear_board()
       if i < 17: 
           x = i
       else: 
           x = i % 17
       final_board = copy.deepcopy(generator.generate_final_board(x + 1, 2))
       logging.debug(pprint.pformat(final_board))
       training_set = [(final_board, -1)]
       generalizer.lms(training_set)
       logging.debug((generalizer.weights))


# "Fixed" parameters
mu_factor = 0.8 # Factor para enfriar
enfriamiento_por_ronda = False # Sisi, la unica variable en español. No se como se dice enfriamiento.
use_gamma = True # Si critic usa gamma o no
gamma = 0.9 
use_v = True # Si critic usa v o usa valores 1 y -1
do_initial_training = True
trainings = 1 # Cantidad de entrenamientos
rounds = 20 # Cantidad de rondas por entrenamiento
matches_per_round = 50 # Cantidad de partidas por ronda
draws_limit_movements = 100 # Cantidad de movimientos antes de decir que es empate

# Parameters
initial_mu = 0.1
initial_weights_p1 = [-0.3245326346849934, 0.1693042050134686, 0.16953670371976523, 0.22783655225690969, 0.22793136193535615, 0.3166528358145293, 0.3143485967442448, 0.35530630208678404, 0.3464082778644509]
initial_weights_p2 = [-0.3245326346849934, 0.1693042050134686, 0.16953670371976523, 0.22783655225690969, 0.22793136193535615, 0.3166528358145293, 0.3143485967442448, 0.35530630208678404, 0.3464082778644509]
fixed_weights_p1 = [-0.01870055657485548, 0.03074003071666052, 0.031318934572842926, -0.08270074674927273, -0.07011917467007431, -7.162670732412986e-05, 0.0008689605180341086, -0.002650084442916412, 0.003135239438228969]
# fixed_weights_p1 = [7.308087279196824e-19, 4.3359576646143924e-19, 9.653256598813128e-21, -3.897649336527599e-18, -1.1925632070418126e-18, -1.3520841664501426e-16, -6.603642214072577e-18, -9.353103466343584e-18, -4.790888400942196e-19]
fixed_weights_p2 = [-0.3245326346849934, 0.1693042050134686, 0.16953670371976523, 0.22783655225690969, 0.22793136193535615, 0.3166528358145293, 0.3143485967442448, 0.35530630208678404, 0.3464082778644509]
random_every_x_moves_p1 = 3 # Cada cuantos movimientos el p1 hace uno random (1 = siempre random, 0 = nunca random)
random_every_x_moves_p2 = 0 # Cada cuantos movimientos el p2 hace uno random (1 = siempre random, 0 = nunca random)
player_2_plays = True  # True si jugador 2 juega con sus propios pesos
player_2_change = 50 # Cada cuantas partidas el jugador 2 actualiza sus pesos (brindados por jugador 1), 0 si no utiliza sus pesos
play_with_fixed_weights = True # True si ambos jugadores juegan con pesos fijos

DEBUG = True # Imprime mensajes de debug si está en true
PLOT = True


def play():
    global initial_weights_p1
    global initial_weights_p2
    ### STATS ###
    draws = []
    p_wins = []

    if (play_with_fixed_weights == True):
        initial_weights_p1 = fixed_weights_p1
        initial_weights_p2 = fixed_weights_p2

    ################## GAME START ##################
    # Para cada entrenamiento
    for x in range(trainings):

        # Instanciar clases básicas
        count_matches = 0
        mu = initial_mu
        board = Board(rows=5, cols=5, pieces=4)
        generator = Generator(board)
        generator.generate_board()
        generalizer = Generalizer(board, initial_weights_p1, initial_weights_p2, mu)
        perf = PerformanceSystem(board, draws_limit_movements, random_every_x_moves_p1, random_every_x_moves_p2)

        # Hacer entrenamiento incial si corresponde
        if do_initial_training:
            initial_training(board, generator, generalizer)

        # Para cada ronda
        for i in range(rounds):
            print("Round Number ", i)
            p_wins.append([0, 0])
            draws.append(0)

            # Para cada partida
            for j in range(matches_per_round):

                # Limpio el tablero
                board.clear_board()
                generator.generate_board()
                # Juego
                game_performance = perf.play(generalizer.v, generalizer.v2, player_2_plays)
                count_matches += 1

                # Si es un empate
                if game_performance['was_draw']:
                    draws[i] += 1
                    logging.debug("------------ It's a draw! ------------")
                else:
                    winner = game_performance['winner']
                    if winner != 0:
                        p_wins[i][winner - 1] += 1
                        logging.debug("------------ The winner is player " + str(winner) + " ------------")

                # Genero el conjunto de entrenamiento
                critic = Critic(board, gamma)

                # Si quiero que los pesos varíen, aplico critic y lms con generalizer
                if not play_with_fixed_weights:
                    v = None
                    if use_v:
                        v = generalizer.v

                    # Genero el conjunto de entrenamiento según si quiero usar v o 1, -1
                    training_set = critic.generate_training_set(game_performance['game_history'], use_gamma, v)

                    # Aplico lms
                    logging.debug("weights_player1 pre-lms:")
                    logging.debug(generalizer.weights)
                    generalizer.lms(training_set)
                    logging.debug("weights_player1 post-lms:")
                    logging.debug(generalizer.weights)

                    if player_2_plays:
                        logging.debug("weights_player2:")
                        logging.debug(generalizer.weights_player2)

                    # Si el jugador 2 no es random -> Actualizo sus pesos
                    if player_2_plays and (count_matches % player_2_change) == 0:
                        generalizer.change_weights_player2()
                    
            if player_2_plays:
                logging.debug("weights_player2:")
                logging.debug(generalizer.weights_player2)

            if enfriamiento_por_ronda:
                mu += mu_factor

            logging.info("------------ Player 1 won " + str(p_wins[i][0]) + " times ------------")
            logging.info("------------ Player 2 won " + str(p_wins[i][1]) + " times ------------")
            logging.info("------------ There where " + str(draws[i]) + " draws ------------")

        logging.info("")

        for i in range(rounds):
            logging.info("")
            logging.info("------------ Player 1 won " + str(p_wins[i][0]) + " times in round " + str(i + 1) + " ------------")
            logging.info("------------ Player 2 won " + str(p_wins[i][1]) + " times in round " + str(i + 1) + " ------------")
            logging.info("------------ There where " + str(draws[i]) + " draws in round " + str(i + 1) + " ------------")

        p1_wins = [sum(x) for x in zip(*p_wins)][0]
        p2_wins = [sum(x) for x in zip(*p_wins)][1]
        total_draws = sum(draws)
        p1_wins_percentage = ((p1_wins / (p1_wins + p2_wins)) * 100) if (p1_wins + p2_wins) != 0 else 0
        p1_wins_percentage_w_draws = (p1_wins / (p1_wins + p2_wins + total_draws)) * 100
        p2_wins_percentage_w_draws = (p2_wins / (p1_wins + p2_wins + total_draws)) * 100
        draws_percentage = (total_draws / (p1_wins + p2_wins + total_draws)) * 100
        logging.info("")
        logging.info("------------ Player 1 won " + str(p1_wins) + " times in total ------------")
        logging.info("------------ Player 2 won " + str(p2_wins) + " times in total ------------")
        logging.info("------------ There where " + str(total_draws) + " draws in total ------------")
        logging.info("------------ Player 1 won " + str(p1_wins_percentage) + "% of the non-drawn games ------------")
        logging.info("------------ Player 1 won " + str(p1_wins_percentage_w_draws) + "% of the games ------------")
        logging.info("------------ Player 2 won " + str(p2_wins_percentage_w_draws) + "% of the games ------------")
        logging.info("------------ There were " + str(draws_percentage) + "% of draws ------------")

    return {}


def main():
    if DEBUG:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    logging.basicConfig(level=logging_level, format='%(message)s')

    results = play()
    import pdb; pdb.set_trace()

    if PLOT:
        pass

if __name__ == '__main__':
    main()