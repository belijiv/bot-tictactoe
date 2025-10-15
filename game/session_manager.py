from .game_logic import TicTacToeGame  # Используем относительный импорт


class GameSessionsManager:
    def __init__(self):
        self.pending_players = list()
        self.active_games = dict()

    def _generate_game_id(self) -> str:
        import uuid
        return str(uuid.uuid4())[:8]

    def add_to_queue(self, player_id: int) -> str | None:
        if player_id in self.pending_players:
            return None
        if self.pending_players:
            opponent_id = self.pending_players.pop(0)
            game_id = self._generate_game_id()
            new_game = TicTacToeGame(player_x_id=opponent_id, player_o_id=player_id)
            self.active_games[game_id] = new_game
            return game_id
        else:
            self.pending_players.append(player_id)
            return None

    def remove_from_queue(self, player_id: int) -> bool:
        if player_id in self.pending_players:
            self.pending_players.remove(player_id)
            return True
        return False

    def get_game(self, game_id: str) -> TicTacToeGame:
        return self.active_games.get(game_id)

    def del_game(self, game_id: str):
        if game_id in self.active_games:
            del self.active_games[game_id]