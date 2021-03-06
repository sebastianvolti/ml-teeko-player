import copy


class Generalizer(object):
    def __init__(self, board, weights, weights_player2, mu):
        self.board = board
        self.weights = copy.deepcopy(weights)
        self.weights_player2 = copy.deepcopy(weights_player2)
        self.mu = mu

    def lms(self, training_set):
        for board, vt_board in training_set:
            attrs = self.board.get_attrs_from_board(board)

            vop = 0
            for i, attr in enumerate(attrs):
                vop += attr * self.weights[i]
            # vop += self.weights[0]

            for i, weight in enumerate(self.weights):
                # if i==0 :
                #     self.weights[i] = weight + self.mu * (vt_board - vop)
                # else :
                self.weights[i] = weight + self.mu * (vt_board - vop) * attrs[i]

    def v(self, board):
        attrs = self.board.get_attrs_from_board(board)
        weights = copy.deepcopy(self.weights)
        v_res = sum([attr * weight for attr, weight in zip(attrs, weights)])
        return v_res

    def v2(self, board):
        attrs = self.board.get_attrs_from_board(board)
        weights = copy.deepcopy(self.weights_player2)
        v_res = sum([attr * weight for attr, weight in zip(attrs, weights)])
        return v_res

    def change_mu(self,param):
        self.mu = param

    def change_weights_player2(self):
        self.weights_player2 = copy.deepcopy(self.weights)