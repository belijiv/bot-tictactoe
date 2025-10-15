class TicTacToeGame:
    def __init__(self, player_x_id: int, player_o_id: int):
        self.player_x = player_x_id
        self.player_o = player_o_id
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_player = player_x_id
        self.winner = None
        self.game_over = False

    def _is_board_full(self) -> bool:
        for row in self.board:
            if ' ' in row:
                return False
        return True

    def _check_winner(self, symbol: str) -> bool:
        board = self.board
        for i in range(3):
            if all(board[i][j] == symbol for j in range(3)):
                return True
            if all(board[j][i] == symbol for j in range(3)):
                return True
        if all(board[i][i] == symbol for i in range(3)):
            return True
        if all(board[i][2 - i] == symbol for i in range(3)):
            return True
        return False

    def make_move(self, player_id: int, row: int, col: int) -> bool:
        if self.game_over or self.current_player != player_id:
            return False
        if row not in range(3) or col not in range(3):
            return False
        if self.board[row][col] != ' ':
            return False

        symbol = 'X' if player_id == self.player_x else 'O'
        self.board[row][col] = symbol

        if self._check_winner(symbol):
            self.winner = player_id
            self.game_over = True
        elif self._is_board_full():
            self.game_over = True
        else:
            self.current_player = self.player_x if player_id == self.player_o else self.player_o
        return True
