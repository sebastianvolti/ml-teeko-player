import random

from critic import Critic
from generator import Board, Generator
from generalizer import Generalizer


class PerformanceSystem(object):
    def __init__(self, board, movements_limit, random_every_x_moves_p1, random_every_x_moves_p2):
        self.board = board
        self.movements_limit = movements_limit # This counts only player 1 movements
        self.random_every_x_moves_p1 = random_every_x_moves_p1
        self.random_every_x_moves_p2 = random_every_x_moves_p2

    def choose_move(self, movements, v):
        current_max = v(movements[0])
        max_board = movements[0]

        for movement in movements:
            v_movement = v(movement)
            if v_movement > current_max:
                current_max = v_movement
                max_board = movement

        return max_board

    def choose_random_move(self, movements):
        return random.choice(movements)

    def play(self, v, v2, player_2_plays):
        game_history = []
        draw = False
        movements_count = 0
        
        if self.board.is_final()['is_final']:
            game_history.append(self.board.current_board)

        while not self.board.is_final()['is_final']:

            # Player 1 turn
            movements = self.board.possible_movements(1)
            if self.random_every_x_moves_p1 and (movements_count % self.random_every_x_moves_p1) == 0:
                movement = self.choose_random_move(movements)
            else:
                movement = self.choose_move(movements, v)
                
            self.board.update_board(movement, 1)
            game_history.append(movement)
            movements_count += 1

            # Player 2 turn
            if not self.board.is_final()['is_final']:
                movements = self.board.possible_movements(2)
                # If player 2 is random
                if not player_2_plays:
                    movement = self.choose_random_move(movements)
                else:
                    if self.random_every_x_moves_p2 and (movements_count % self.random_every_x_moves_p2) == 0:
                        movement = self.choose_random_move(movements)
                    else:
                        movement = self.choose_move(movements, v2)

                self.board.update_board(movement, 2)

            # If it's a draw -> break while
            if movements_count > self.movements_limit:
                draw = True
                break

        return {'was_draw': draw, 'winner': self.board.is_final()['winner'], 'game_history': game_history}
  
    def pprint_current(self):
        print('[', end="")

        for i, row in enumerate(self.board.current_board):
            print(' [' if i != 0 else '[', end='')
            for j, player_number in enumerate(row):
                if player_number == 1:
                    color = '1;31'
                elif player_number == 2:
                    color = '1;34'
                else:
                    color = '0;00'

                if (i, j) in self.board.last_move:
                    print('\033[1;33m' + str(player_number) + '\033[0m' + (', ' if j < self.board.rows - 1 else ''), end="")
                else:
                    print('\033[' + color + 'm' + str(player_number) + '\033[0m' + (', ' if j < self.board.rows - 1 else ''), end="")
            print('],' if i < self.board.cols else ']')
        print(']')
