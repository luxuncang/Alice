# -*- coding: utf-8 -*-
"""
human VS AI models
Input your move in the format: 2,3

@author: Junxiao Song
"""

from __future__ import print_function
import os
import pickle
from .game import Board, Game
from .mcts_pure import MCTSPlayer as MCTS_Pure
from .mcts_alphaZero import MCTSPlayer
from .policy_value_net_numpy import PolicyValueNetNumpy


class Human(object):
    """
    human player
    """

    def __init__(self):
        self.player = None

    def set_player_ind(self, p):
        self.player = p

    # def get_action(self, board):
    #     try:
    #         location = input("Your move: ")
    #         if isinstance(location, str):  # for python3
    #             location = [int(n, 10) for n in location.split(",")]
    #         move = board.location_to_move(location)
    #     except Exception as e:
    #         move = -1
    #     if move == -1 or move not in board.availables:
    #         print("invalid move")
    #         move = self.get_action(board)
    #     return move
    
    def get_actionx(self, board, x, y):
        try:
            move = board.location_to_move([x, y])
        except Exception as e:
            move = -1
        if move == -1 or move not in board.availables:
            print("invalid move")
            return False
            # move = self.get_action(board)
        return move

    def __str__(self):
        return f"Human {self.player}"


def run():
    n = 5
    width, height = 8, 8
    model_file = os.path.join(os.path.split(__file__)[0], 'best_policy_8_8_5.model')
    try:
        board = Board(width=width, height=height, n_in_row=n)
        game = Game(board)
        try:
            policy_param = pickle.load(open(model_file, 'rb'))
        except:
            policy_param = pickle.load(open(model_file, 'rb'),
                                       encoding='bytes')  # To support python3
        best_policy = PolicyValueNetNumpy(width, height, policy_param)
        mcts_player = MCTSPlayer(best_policy.policy_value_fn,
                                 c_puct=5,
                                 n_playout=400)  # set larger n_playout for better performance

        # human player, input your move in the format: 2,3
        human = Human()

        # set start_player=0 for human first
        game.start_play(human, mcts_player, start_player=0, is_shown=1)
    except KeyboardInterrupt:
        print('\n\rquit')

class AlphaZero:
    w = [
    ['┌', '┬', '┬', '┬', '┬', '┬', '┬', '┐'],
    ['├', '┼', '┼', '┼', '┼', '┼', '┼', '┤'],
    ['├', '┼', '┼', '┼', '┼', '┼', '┼', '┤'],
    ['├', '┼', '┼', '┼', '┼', '┼', '┼', '┤'],
    ['├', '┼', '┼', '┼', '┼', '┼', '┼', '┤'],
    ['├', '┼', '┼', '┼', '┼', '┼', '┼', '┤'],
    ['├', '┼', '┼', '┼', '┼', '┼', '┼', '┤'],  
    ['└', '┴', '┴', '┴', '┴', '┴', '┴', '┘'],       
    ]

    x = '○'
    y = '●'

    def __init__(self) -> None:
        n = 5
        width, height = 8, 8
        model_file = os.path.join(os.path.split(__file__)[0], 'best_policy_8_8_5.model')
        board = Board(width=width, height=height, n_in_row=n)
        self.game = Game(board)
        try:
            policy_param = pickle.load(open(model_file, 'rb'))
        except:
            policy_param = pickle.load(open(model_file, 'rb'),
                                    encoding='bytes')  # To support python3
        best_policy = PolicyValueNetNumpy(width, height, policy_param)
        self.mcts_player = MCTSPlayer(best_policy.policy_value_fn,
                                c_puct=5,
                                n_playout=400)  # set larger n_playout for better performance
        self.human = Human()
        self.game.start_play(self.human, self.mcts_player, start_player=0, is_shown=1)
        # game.start_play(human, mcts_player, start_player=1, is_shown=1)

    def ai(self, x, y):
        r1 = self.game.ai(x, y)
        if isinstance(r1, (str, bool)):
            return r1
        r2 = self.game.ai(x, y)
        if isinstance(r2, (str, bool)):
            return r2
        for h,i in enumerate(list(zip(*r2))):
            for l,j in enumerate(i):
                if j == 'O':
                    self.w[h][l] = self.x
                elif j == 'X':
                    self.w[h][l] = self.y
        return self.get_str()

    def get_str(self):
        return '\n'.join([str(7-i)+j for i,j in enumerate(list(map(lambda x: ''.join(x), self.w)))])

# w = [
#     ['┌', '┬', '┬', '┬', '┬', '┬', '┬', '┐'],
#     ['├', '┼', '┼', '┼', '┼', '┼', '┼', '┤'],
#     ['├', '┼', '┼', '┼', '┼', '┼', '┼', '┤'],
#     ['├', '┼', '┼', '┼', '┼', '┼', '┼', '┤'],
#     ['├', '┼', '┼', '┼', '┼', '┼', '┼', '┤'],
#     ['├', '┼', '┼', '┼', '┼', '┼', '┼', '┤'],
#     ['├', '┼', '┼', '┼', '┼', '┼', '┼', '┤'],  
#     ['└', '┴', '┴', '┴', '┴', '┴', '┴', '┘'],       
# ]

# if __name__ == '__main__':
#     # run()
#     a = Al()
#     a.ai(3, 3)
#     print(a.ai(0, 1))
    # a.ai(0, 2)
    # print('\n'.join(map(lambda x: '─'.join(x), w)))

# '''
# 7┌─┬─┬─┬─┬─┬─┬─┐
# 6├─┼─┼─┼─┼─┼─┼─┤
# 5├─┼─┼─┼─┼─┼─┼─┤
# 4├─┼─┼─┼─┼─┼─┼─┤
# 3├─┼─┼─┼─┼─┼─┼─┤
# 2├─┼─┼─┼─┼─┼─┼─┤
# 1├─┼─┼─┼─┼─┼─┼─┤
# 0└─┴─┴─┴─┴─┴─┴─┘
#  0 1 2 3 4 5 6 7
#        ●┼┼┼┼┼┼┼┼●●┼●●┼┼┼┼ ├ ┼┼┼┼┼┼●┼┼●┼┼┼ ├┼○○┼┼┼●┼┼┼●┼┼ ├○┼┼○○●○○○●●●┼ ├○┼┼○○┼┼┼○┼┼●┼ ├┼○○┼○┼┼┼○┼┼●┼ ├┼┼┼┼○┼┼┼○○○●●●
# '''

# '''

# '''