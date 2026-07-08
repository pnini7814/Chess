class MoveScheduler:

    def resolve(self, current_time: int, pending_moves: list[dict],
                board: list[list[str]], game_over: bool) -> tuple[list[dict], bool]:
        if not pending_moves:
            return [], game_over

        pending_moves.sort(key=lambda m: m["arrival_time"])
        remaining = []

        for move in pending_moves:
            if game_over:
                continue
            if current_time >= move["arrival_time"]:
                game_over = self._apply_move(move, pending_moves, board, current_time, game_over)
            else:
                remaining.append(move)

        return remaining, game_over

    def _apply_move(self, move: dict, pending_moves: list[dict],
                    board: list[list[str]], current_time: int, game_over: bool) -> bool:
        if move.get("is_jump"):
            return game_over

        from_r, from_c = move["from_row"], move["from_col"]
        to_r, to_c = move["to_row"], move["to_col"]
        piece = move["piece"]

        if board[from_r][from_c] != piece:
            return game_over

        if self._is_airborne_capture(move, pending_moves, current_time):
            board[from_r][from_c] = "."
            return game_over

        target = board[to_r][to_c]
        if target != "." and target[1] == "K":
            game_over = True

        board[to_r][to_c] = self._resolve_promotion(piece, to_r, board)
        board[from_r][from_c] = "."

        return game_over

    def _is_airborne_capture(self, arriving_move: dict, pending_moves: list[dict],
                              current_time: int) -> bool:
        to_r = arriving_move["to_row"]
        to_c = arriving_move["to_col"]
        arriving_piece = arriving_move["piece"]

        for jump in pending_moves:
            if not jump.get("is_jump"):
                continue
            if jump["from_row"] != to_r or jump["from_col"] != to_c:
                continue
            if current_time <= jump["arrival_time"] and jump["piece"][0] != arriving_piece[0]:
                return True

        return False

    def _resolve_promotion(self, piece: str, to_row: int, board: list[list[str]]) -> str:
        if piece[1] != "P":
            return piece
        if piece[0] == "w" and to_row == 0:
            return piece[0] + "Q"
        if piece[0] == "b" and to_row == len(board) - 1:
            return piece[0] + "Q"
        return piece
