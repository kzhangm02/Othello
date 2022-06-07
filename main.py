import numpy as np
import pickle as pk
import random
import copy
   
class Agent():
   def __init__(self):
      self.num_weights = 10
      self.weights = np.random.randn(self.num_weights, 1)
      self.weights[3] = 0
      self.trainable = [0, 1, 2, 4, 5, 6, 7, 8, 9]
      self.weight_to_sq = {0: (0,0), 1: (1,1), 2: (2,2), 3: (3,3), 4: (0,1), 5: (1,2), 6: (2,3), 7: (0,2), 8: (1,3), 9: (0,3)}
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
      return np.sum(np.multiply(board.state, np.array(self.weight_mask).squeeze()))
   
   # def find_best_move(self, board, moves):
      # pairs = []
      # for move in moves:
         # self.temp_board.copy_board(board)
         # self.temp_board.move(move)
         # legal_moves = self.temp_board.find_moves()
         # eval = self.eval(self.temp_board) + len(legal_moves)
         # pairs.append((eval, move))
      # if board.turn == 'x':
         # return max(pairs)
      # return min(pairs)
      
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
        for i in range(1,9):
            for j in range(1,9):
                idx = 10*i + j
                legal = False
                flip = set({})
                if self.board[idx] == '.':
                    for d in self.dirs:
                        sq = set({})
                        new_idx = idx + d
                        if self.board[new_idx] == self.turn or self.board[new_idx] == '.':
                            continue
                        while self.board[new_idx] == self.other_token[self.turn]:
                            sq.add(new_idx)
                            new_idx += d
                        if self.board[new_idx] == self.turn:
                            legal = True
                            flip = flip.union(sq)
                            if not find_flipped:
                                break
                if legal:
                    if find_flipped:
                        moves.append((idx, flip))
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
        self.temp_board = Board()
   
    def find_best_move(self, board, alpha=float('-inf'), beta=float('inf'), depth=0):
        if depth == self.cutoff_depth:
            if self.turn == 'x':
                return (self.agent.eval(board), None)
            return (-1 * self.agent.eval(board), None)
        moves = board.find_moves()
        if len(moves) == 0:
            self.temp_board.copy_board(board)
            self.temp_board.pass_turn()
            moves = self.temp_board.find_moves()
            if len(moves) == 0:
                my_count = board.board.count(self.turn)
                op_count = board.board.count(board.other_token[self.turn])
                if my_count > op_count:
                    return (float('inf'), None)
                elif my_count < op_count:
                    return (float('-inf'), None)
                else:
                    return (0, None)
            else:
                value = self.find_best_move(self.temp_board, alpha, beta, depth+1)[0]
                return (value, None)
        if board.turn == self.turn:
            candidate = (float('-inf'), None)
            for move in moves:
                self.temp_board.copy_board(board)
                self.temp_board.move(move)
                value = self.find_best_move(self.temp_board, alpha, beta, depth+1)[0]
                if candidate[1] == None or value > candidate[0]:
                    candidate = (value, move)
                if candidate[0] >= beta:
                    break
                alpha = max(alpha, candidate[0])
        else:
            candidate = (float('inf'), None)
            for move in moves:
                self.temp_board.copy_board(board)
                self.temp_board.move(move)
                value = self.find_best_move(self.temp_board, alpha, beta, depth+1)[0]
                if candidate[1] == None or value < candidate[0]:
                    candidate = (value, move)
                if candidate[0] <= alpha:
                    break
                beta = min(beta, candidate[0])
        return candidate
        
def find_best_move_unique(*args):
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
        strategy = Strategy(ai_turn, agent, 1)
        
weights = [5.925923040996503, -1.2530656815684476, -0.7442317598865232, 0.0, -2.793126083525491, -2.439215370868367, 0.8114567742238017, 8.363316678824882, 0.0805112529383367, -1.8362651847690366]
weights = np.array(weights)
weights = np.expand_dims(weights, axis=1)
agent = Agent()
agent.set_weights(weights)
strategy = None
global_board = Board()