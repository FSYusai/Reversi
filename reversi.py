import tkinter as tk
from tkinter import messagebox


class ReversiBoard:
    def __init__(self, size=8):
        self.size = size
        self.board = [[' ' for _ in range(size)] for _ in range(size)]
        self.board[size // 2 - 1][size // 2 - 1] = 'W'
        self.board[size // 2 - 1][size // 2] = 'B'
        self.board[size // 2][size // 2 - 1] = 'B'
        self.board[size // 2][size // 2] = 'W'
        self.current_player = 'B'

    def is_valid_move(self, x, y):
        if self.board[x][y] != ' ':
            return False
        return any(self.flips(x, y, dx, dy) for dx, dy in self.directions())

    def place_stone(self, x, y):
        self.board[x][y] = self.current_player  # この行を追加
        flips = [self.flips(x, y, dx, dy) for dx, dy in self.directions()]
        for flip in flips:
            for fx, fy in flip:
                self.board[fx][fy] = self.current_player

    def flips(self, x, y, dx, dy):
        flipped = []
        while True:
            x, y = x + dx, y + dy
            if (x < 0 or x >= self.size or y < 0 or y >= self.size):
                return []
            if self.board[x][y] == ' ':
                return []
            if self.board[x][y] == self.current_player:
                return flipped
            flipped.append((x, y))

    def directions(self):
        return [(dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if (dx, dy) != (0, 0)]

    def is_game_over(self):
        black_stones = sum([row.count('B') for row in self.board])
        white_stones = sum([row.count('W') for row in self.board])

        # どちらかが全ての石を取った場合、または、ボードがいっぱいになった場合
        return black_stones == 0 or white_stones == 0 or black_stones + white_stones == self.size * self.size

    def count_stones(self):
        count = {'B': 0, 'W': 0, ' ': 0}
        for i in range(self.size):
            for j in range(self.size):
                count[self.board[i][j]] += 1
        return count

    def has_valid_move(self, player):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == ' ':
                    tmp_player = self.current_player
                    self.current_player = player
                    if self.is_valid_move(i, j):
                        self.current_player = tmp_player
                        return True
                    self.current_player = tmp_player
        return False

    def heuristic(self):
        score = 0
        total_empty = sum([row.count(' ') for row in self.board])

        # 評価マトリクスの設定
        corner_val = 80
        adjacent_corner = -80  # 価値をさらに低く設定
        edge_connected_to_corner = 15
        other_tiles = 1
        opponent_corner_potential = -60

        # ボードの端と隅の位置を定義
        corners = [(0, 0), (0, self.size - 1), (self.size - 1, 0), (self.size - 1, self.size - 1)]
        edges = [(i, 0) for i in range(1, self.size - 1)] + \
                [(i, self.size - 1) for i in range(1, self.size - 1)] + \
                [(0, i) for i in range(1, self.size - 1)] + \
                [(self.size - 1, i) for i in range(1, self.size - 1)]

        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != ' ':
                    add = other_tiles

                    # 隅の評価
                    if (i, j) in corners:
                        add = corner_val
                    # 隅の斜めに隣接するマスの評価
                    elif (i, j) in [(1, 1), (1, self.size - 2), (self.size - 2, 1), (self.size - 2, self.size - 2)]:
                        add = adjacent_corner
                    # 隅に繋がる辺の評価
                    elif (i, j) in edges and any(self.board[x][y] == self.board[i][j] for x, y in corners):
                        add = edge_connected_to_corner
                    # 隅を取られる可能性のある手の評価
                    elif (i, j) in edges and any(self.board[x][y] == ' ' for x, y in corners):
                        add = opponent_corner_potential

                    if self.board[i][j] == self.current_player:
                        score += add
                    else:
                        score -= add

        # 終盤の評価
        if total_empty <= 10:
            my_stones = sum([row.count(self.current_player) for row in self.board])
            opponent_stones = self.size * self.size - total_empty - my_stones
            score += my_stones - opponent_stones

        return score

    def minimax_alpha_beta(self, depth, alpha, beta, maximizingPlayer):
        if depth == 0 or self.is_game_over():
            return self.heuristic()

        if maximizingPlayer:
            maxEval = float('-inf')
            for i in range(self.size):
                for j in range(self.size):
                    if self.is_valid_move(i, j):
                        temp = self.board[i][j]
                        self.board[i][j] = self.current_player
                        eval = self.minimax_alpha_beta(depth - 1, alpha, beta, False)
                        self.board[i][j] = temp
                        maxEval = max(maxEval, eval)
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break
            return maxEval
        else:
            minEval = float('inf')
            for i in range(self.size):
                for j in range(self.size):
                    if self.is_valid_move(i, j):
                        temp = self.board[i][j]
                        self.board[i][j] = 'W' if self.current_player == 'B' else 'B'
                        eval = self.minimax_alpha_beta(depth - 1, alpha, beta, True)
                        self.board[i][j] = temp
                        minEval = min(minEval, eval)
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
            return minEval

    def get_best_move(self, depth):
        best_score = float('-inf')
        best_move = None

        for i in range(self.size):
            for j in range(self.size):
                if self.is_valid_move(i, j):
                    temp = self.board[i][j]
                    self.board[i][j] = self.current_player
                    current_score = self.minimax_alpha_beta(depth - 1, float('-inf'), float('inf'), False)
                    self.board[i][j] = temp
                    if current_score > best_score:
                        best_score = current_score
                        best_move = (i, j)

        return best_move


class ReversiGUI(tk.Tk):
    def __init__(self, board):
        super().__init__()
        self.board = board
        self.title('Reversi Game')

        self.label = tk.Label(self, text="黒の手番", font=('Arial', 16))
        self.label.pack(pady=10)

        self.canvas = tk.Canvas(self, width=400, height=400, bg='green')
        self.canvas.pack(pady=10)
        self.canvas.bind('<Button-1>', self.on_click)

        self.draw_board()

    def on_click(self, event):
        col = event.x // 50
        row = event.y // 50

        # ユーザー（黒）の手番
        if self.board.current_player == 'B':
            # ユーザーが有効な手を持つ場合
            if self.board.is_valid_move(row, col):
                self.board.place_stone(row, col)
                self.draw_board()
                self.switch_player()

                # ここでCPUの手番の処理を追加
                if self.board.current_player == 'W':
                    if not self.board.has_valid_move('W'):
                        messagebox.showinfo('パス', 'CPUは打てる場所がありません。パスします。')
                        self.switch_player()
                    else:
                        self.after(100, self.cpu_move)

            # ユーザーが有効な手を持たない場合
            elif not self.board.has_valid_move('B'):
                messagebox.showinfo('パス', '打てる場所がありません。パスします。')
                self.switch_player()

                # ここもCPUの手番の処理を追加
                if self.board.current_player == 'W':
                    if not self.board.has_valid_move('W'):
                        messagebox.showinfo('パス', 'CPUは打てる場所がありません。パスします。')
                        self.switch_player()
                    else:
                        self.after(100, self.cpu_move)

    def cpu_move(self):
        move = self.board.get_best_move(7)  # 探索深度を7に設定
        if move:
            x, y = move
            self.board.place_stone(x, y)
            self.draw_board()
            self.switch_player()
            if not self.board.has_valid_move('B'):
                if not self.board.has_valid_move('W'):
                    self.show_result()

    def show_result(self):
        counts = self.board.count_stones()
        if counts['B'] > counts['W']:
            winner = 'B'
            counts['B'] += counts[' ']
        else:
            winner = 'W'
            counts['W'] += counts[' ']
        winner_text = "黒の勝利!" if winner == 'B' else "白の勝利!"
        msg = f"{winner_text}\n\n黒の石: {counts['B']}\n白の石: {counts['W']}"
        messagebox.showinfo('ゲーム終了', msg)
        self.quit()

    def switch_player(self):
        if self.board.current_player == 'B':
            self.board.current_player = 'W'
            self.label.config(text="白の手番")
        else:
            self.board.current_player = 'B'
            self.label.config(text="黒の手番")

    def draw_board(self):
        for i in range(self.board.size):
            for j in range(self.board.size):
                x, y = j * 50, i * 50
                self.canvas.create_rectangle(x, y, x + 50, y + 50, fill='green')
                if self.board.board[i][j] == 'B':
                    self.canvas.create_oval(x + 5, y + 5, x + 45, y + 45, fill='black')
                elif self.board.board[i][j] == 'W':
                    self.canvas.create_oval(x + 5, y + 5, x + 45, y + 45, fill='white')


if __name__ == '__main__':
    board = ReversiBoard()
    app = ReversiGUI(board)
    app.mainloop()
