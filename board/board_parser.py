from pieces.piece_factory import PieceFactory


class BoardParser:

    def parse(self, lines: list[str]) -> list[list[str]] | None:
        board = self._extract_board_lines(lines)
        if not board:
            return None
        return board if self._validate(board) else None

    def _extract_board_lines(self, lines: list[str]) -> list[list[str]]:
        board = []
        inside = False
        for line in lines:
            if line == "Board:":
                inside = True
                continue
            if line.startswith("Commands:"):
                break
            if inside:
                board.append(line.split())
        return board

    def _validate(self, board: list[list[str]]) -> bool:
        num_cols = len(board[0])
        valid_symbols = PieceFactory.known_symbols()

        for row in board:
            if len(row) != num_cols:
                print("ERROR ROW_WIDTH_MISMATCH")
                return False
            for token in row:
                if token == ".":
                    continue
                if len(token) != 2 or token[0] not in ("w", "b") or token[1] not in valid_symbols:
                    print("ERROR UNKNOWN_TOKEN")
                    return False
        return True
