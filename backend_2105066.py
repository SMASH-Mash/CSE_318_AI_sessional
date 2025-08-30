import math

ROWS, COLS = 9, 6

class Cell:
 def __init__(self, owner=None, count=0):
        self.owner = owner
        self.count = count

class Board:
   def __init__(self):
        self.rows = ROWS
        self.cols = COLS
        self.grid = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]

   def clone(self):
        new_board = Board()
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                new_board.grid[r][c].owner = cell.owner
                new_board.grid[r][c].count = cell.count
        return new_board

   def is_valid_move(self, row, col, player):
        cell = self.grid[row][col]
        return cell.owner is None or cell.owner == player

   def get_valid_moves(self, player):
        moves = []
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell.owner is None or cell.owner == player:
                    moves.append((r, c))
        return moves

   def apply_move(self, row, col, player):
        cell = self.grid[row][col]
        cell.count += 1
        cell.owner = player
        self._resolve_chain_reactions(row, col)

   def _resolve_chain_reactions(self, row, col):
        changed = True
        while changed and not self.is_game_over():
            changed = False
            to_explode = []
            for r in range(self.rows):
                for c in range(self.cols):
                    cell = self.grid[r][c]
                    if cell.count > self._critical_mass(r, c):
                        to_explode.append((r, c, cell.owner))
            for r, c, owner in to_explode:
                self.grid[r][c].count -= self._critical_mass(r, c) + 1
                if self.grid[r][c].count <= 0:
                    self.grid[r][c].owner = None
                    self.grid[r][c].count = 0
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self.grid[nr][nc].count += 1
                        self.grid[nr][nc].owner = owner
                changed = True

   def _critical_mass(self, row, col):
        edges = 0
        if row == 0 or row == self.rows-1: edges += 1
        if col == 0 or col == self.cols-1: edges += 1
        return 1 + (2 - edges)

   def is_game_over(self):
        owners = set()
        for row in self.grid:
            for cell in row:
                if cell.owner is not None:
                    owners.add(cell.owner)
        return len(owners) <= 1 and any(cell.owner is not None for row in self.grid for cell in row)

   def get_winner(self):
        for row in self.grid:
            for cell in row:
                if cell.owner is not None:
                    return cell.owner
        return None

   def count_orbs(self, player):
        return sum(cell.count for row in self.grid for cell in row if cell.owner == player)
 

def simple_heuristic(board, player, opponent):
    player_orbs = board.count_orbs(player)
    opponent_orbs = board.count_orbs(opponent)
    player_cells = sum(1 for row in board.grid for cell in row if cell.owner == player)
    opponent_cells = sum(1 for row in board.grid for cell in row if cell.owner == opponent)
    return (player_orbs - opponent_orbs) + 0.5 * (player_cells - opponent_cells)

def cell_control_heuristic(board, player, opponent):
    player_cells = sum(1 for row in board.grid for cell in row if cell.owner == player)
    opponent_cells = sum(1 for row in board.grid for cell in row if cell.owner == opponent)
    return player_cells - opponent_cells

def edge_priority_heuristic(board, player, opponent):
    score = 0
    for r in range(board.rows):
        for c in range(board.cols):
            cell = board.grid[r][c]
            if cell.owner == player:
                if (r in [0, board.rows-1] and c in [0, board.cols-1]):
                    score += 3
                elif r in [0, board.rows-1] or c in [0, board.cols-1]:
                    score += 2
                else:
                    score += 1
            elif cell.owner == opponent:
                if (r in [0, board.rows-1] and c in [0, board.cols-1]):
                    score -= 3
                elif r in [0, board.rows-1] or c in [0, board.cols-1]:
                    score -= 2
                else:
                    score -= 1
    return score

def critical_mass_heuristic(board, player, opponent):
    def cell_score(cell, r, c, owner):
        if cell.owner != owner:
            return 0
        return cell.count / (board._critical_mass(r, c) + 1)
    player_score = sum(cell_score(board.grid[r][c], r, c, player)
                       for r in range(board.rows) for c in range(board.cols))
    opponent_score = sum(cell_score(board.grid[r][c], r, c, opponent)
                         for r in range(board.rows) for c in range(board.cols))
    return player_score - opponent_score

def aggressive_heuristic(board, player, opponent):
    player_orbs = board.count_orbs(player)
    opponent_orbs = board.count_orbs(opponent)
    return 2 * player_orbs - 3 * opponent_orbs

HEURISTICS = {
    1: simple_heuristic,
    2: cell_control_heuristic,
    3: edge_priority_heuristic,
    4: critical_mass_heuristic,
    5: aggressive_heuristic
}

def minimax(board, depth, alpha, beta, maximizing, player, opponent, no_moves, heuristic_func):
    if depth == 0 or (no_moves > 1 and board.is_game_over()):
        return heuristic_func(board, player, opponent), None

    valid_moves = board.get_valid_moves(player if maximizing else opponent)
    valid_moves.sort(key=lambda move: board.grid[move[0]][move[1]].count, reverse=maximizing)

    if not valid_moves:
        return heuristic_func(board, player, opponent), None
    best_move = None
    if maximizing:
        max_eval = -math.inf
        for move in valid_moves:
            new_board = board.clone()
            new_board.apply_move(*move, player)
            eval, _ = minimax(new_board, depth-1, alpha, beta, False, player, opponent, no_moves, heuristic_func)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break 
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in valid_moves:
            new_board = board.clone()
            new_board.apply_move(*move, opponent)
            eval, _ = minimax(new_board, depth-1, alpha, beta, True, player, opponent, no_moves, heuristic_func)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break 
        return min_eval, best_move