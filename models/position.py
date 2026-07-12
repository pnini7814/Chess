from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    row: int
    col: int

    def __repr__(self) -> str:
        return f"Position(row={self.row}, col={self.col})"
