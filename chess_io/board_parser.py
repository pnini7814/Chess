from models.board import Board
from models.piece_factory import PieceFactory
from models.position import Position


class BoardParser:

    def parse(self, lines: list[str]) -> Board | None:
        raw = self._extract_rows(lines)
        if not raw:
            return None
        if not self._validate(raw):
            return None
        return self._build_board(raw)

    def _extract_rows(self, lines: list[str]) -> list[list[str]]:
        rows = []
        inside = False
        for line in lines:
            if line.strip() == "Board:":
                inside = True
                continue
            if line.startswith("Commands:"):
                break
            if inside:
                rows.append(line.split())
        return rows

    def _validate(self, rows: list[list[str]]) -> bool:
        num_cols = len(rows[0])
        valid_symbols = PieceFactory.known_symbols()
        for row in rows:
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

    def _build_board(self, rows: list[list[str]]) -> Board:
        board = Board(rows=len(rows), cols=len(rows[0]))
        for r, row in enumerate(rows):
            for c, token in enumerate(row):
                if token != ".":
                    piece = PieceFactory.from_token(token, Position(r, c))
                    board.add_piece(piece)
        return board
