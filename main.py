import numpy as np
import pickle as pk
import random
import copy
   
class Agent():
   def __init__(self):
      self.num_weights = 10
      self.weights = np.random.randn(self.num_weights, 1)
      self.trainable = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
      self.weight_to_sq = {0: (0,0), 1: (0,1), 2: (0,2), 3: (0,3), 4: (1,1), 5: (1,2), 6: (1,3), 7: (2,2), 8: (2,3), 9: (3,3)}
      self.weight_mask = [[np.array([0]) for i in range(8)] for j in range(8)]
      for k in range(self.num_weights):
         r = self.weight_to_sq[k][0]
         c = self.weight_to_sq[k][1]
         self.add_to_mask(k, r, c)
         if not r == c:
            r, c = c, r
            self.add_to_mask(k, r, c)
      self.other_token = {'x':'o', 'o':'x'}
      self.temp_board = Board()
      self.age = 0
   
   def add_to_mask(self, k, r, c):
      self.weight_mask[r][c] = self.weights[k]
      self.weight_mask[7-r][c] = self.weights[k]
      self.weight_mask[r][7-c] = self.weights[k]
      self.weight_mask[7-r][7-c] = self.weights[k]
      
   def eval(self, board):
      return np.round(np.sum(np.multiply(board.state, np.array(self.weight_mask).squeeze())), 2)
      
   def set_weights(self, weights):
      for k in range(self.num_weights):
         self.weights[k] = weights[k]
      
class Board:
    def __init__(self):
        self.board = np.array(list('#' * 10 + ('#' + '.' * 8 + '#') * 8 + '#' * 10))
        self.board[44] = 'o'
        self.board[55] = 'o'
        self.board[45] = 'x'
        self.board[54] = 'x'
        self.state = np.zeros((8,8))
        self.state[3][4] = 1
        self.state[4][3] = 1
        self.state[3][3] = -1
        self.state[4][4] = -1
        self.turn = 'x'
        self.dirs = [1, -9, -10, -11, -1, 9, 10, 11]
        self.other_token = {'x':'o', 'o':'x'}
        self.token_int = {'x': 1, 'o': -1}

    def find_moves(self, find_flipped=True):
        moves = []
        valid = [k for k in range(len(self.board)) if self.board[k] == '.']
        for idx in valid:
            legal = False
            flip = []
            valid_dirs = [d for d in self.dirs if not (self.board[idx + d] in [self.turn, '.'])]
            for d in valid_dirs:
                new_idx = idx + d
                sq = []
                while self.board[new_idx] == self.other_token[self.turn]:
                    sq.append(new_idx)
                    new_idx += d
                if self.board[new_idx] == self.turn:
                    legal = True
                    if find_flipped:
                        flip += sq
                    else:
                        break
            if legal:
                if find_flipped:
                   moves.append((idx, set(flip)))
                else:
                   moves.append(idx)
        return moves

    def move(self, idx):
        if idx in range(100):
            for d in self.dirs:
                new_idx = idx + d
                while self.board[new_idx] == self.other_token[self.turn]:
                    new_idx += d
                if self.board[new_idx] == self.turn:
                    while not new_idx == idx:
                        new_idx -= d
                        self.board[new_idx] = self.turn
                        self.state[(new_idx // 10) - 1][(new_idx % 10) - 1] = self.token_int[self.turn]
        else:
            flip = list(idx[1])
            flip.append(idx[0])
            for flip_idx in flip:
                self.board[flip_idx] = self.turn
                self.state[(flip_idx // 10) - 1][(flip_idx % 10) - 1] = self.token_int[self.turn]
        self.turn = self.other_token[self.turn]
   
    def pass_turn(self):
        self.turn = self.other_token[self.turn]
   
    def reset(self):
        self.board = np.array(list('#' * 10 + ('#' + '.' * 8 + '#') * 8 + '#' * 10))
        self.board[44] = 'o'
        self.board[55] = 'o'
        self.board[45] = 'x'
        self.board[54] = 'x'
        self.state = np.zeros((8,8))
        self.state[3][4] = 1
        self.state[4][3] = 1
        self.state[3][3] = -1
        self.state[4][4] = -1
        self.turn = 'x'
      
    def copy_board(self, board):
        self.board = copy.copy(board.board)
        self.state = copy.deepcopy(board.state)
        self.turn = board.turn
   
    def set_board(self, board_str):
        self.turn = board_str[0]
        board_str = board_str[1:]
        self.board = np.array(list(board_str))
        for i in range(8):
            for j in range(8):
                token = self.board[10*(i+1) + j + 1]
                if token == 'x':
                    self.state[i][j] = 1
                elif token == 'o':
                    self.state[i][j] = -1
                else:
                    self.state[i][j] = 0

class Strategy():
    def __init__(self, turn, agent, cutoff_depth):
        self.turn = turn
        self.other_token = {'x':'o', 'o':'x'}
        self.agent = agent
        self.cutoff_depth = cutoff_depth
        self.temp_boards = [Board() for k in range(cutoff_depth)]
   
    def find_best_move(self, board, alpha=float('-inf'), beta=float('inf'), depth=0):
        if depth == self.cutoff_depth:
            return (self.agent.eval(board), None)
        moves = board.find_moves()
        if len(moves) == 0:
            self.temp_boards[depth].copy_board(board)
            self.temp_boards[depth].pass_turn()
            moves = self.temp_boards[depth].find_moves()
            if len(moves) == 0:
                x_count = np.count_nonzero(self.temp_boards[depth].board == 'x')
                o_count = np.count_nonzero(self.temp_boards[depth].board == 'o')
                if x_count > o_count:
                    return (float('inf'), None)
                elif x_count > o_count:
                    return (float('-inf'), None)
                else:
                    return (0, None)
            else:
                value = self.find_best_move(self.temp_boards[depth], alpha, beta, depth+1)[0]
                return (value, None)
        if board.turn == 'x':
            candidate = (float('-inf'), None)
            for move in moves:
                self.temp_boards[depth].copy_board(board)
                self.temp_boards[depth].move(move)
                value = self.find_best_move(self.temp_boards[depth], alpha, beta, depth+1)[0]
                if candidate[1] == None or value > candidate[0]:
                    candidate = (value, move)
                if candidate[0] >= beta:
                    break
                alpha = max(alpha, candidate[0])
        else:
            candidate = (float('inf'), None)
            for move in moves:
                self.temp_boards[depth].copy_board(board)
                self.temp_boards[depth].move(move)
                value = self.find_best_move(self.temp_boards[depth], alpha, beta, depth+1)[0]
                if candidate[1] == None or value < candidate[0]:
                    candidate = (value, move)
                if candidate[0] <= alpha:
                    break
                beta = min(beta, candidate[0])
        return candidate
        
def find_best_move(*args):
    state = Element('state').element.innerHTML
    global_board.set_board(state)
    candidate = strategy.find_best_move(global_board)
    move = candidate[1][0]
    pyscript.write('move', move)
    
def set_strategy(*args):
    global strategy
    ai_turn = Element('ai_turn').element.innerHTML
    if ai_turn == '-':
        strategy = None
    else:
        strategy = Strategy(ai_turn, agent, 4)
        
# Custom AI trained with co-evolutionary genetic algorithm, achieve 60% win rate against SWPC AI
# Planning to use n-tuple networks for better performance
weights = [0.77, -0.08, 0.68, -0.12, -0.51, -0.124, 0.055, 0.06, 0.0, 0.0]
weights = np.array(weights)
weights = np.expand_dims(weights, axis=1)
agent = Agent()
agent.set_weights(weights)
strategy = None
global_board = Board()
