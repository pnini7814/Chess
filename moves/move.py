from dataclasses import dataclass, field


@dataclass
class Move:
    piece: str
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    arrival_time: int
    is_jump: bool = False

    def to_dict(self) -> dict:
        return {
            "piece": self.piece,
            "from_row": self.from_row,
            "from_col": self.from_col,
            "to_row": self.to_row,
            "to_col": self.to_col,
            "arrival_time": self.arrival_time,
            "is_jump": self.is_jump,
        }

    @staticmethod
    def from_dict(d: dict) -> "Move":
        return Move(
            piece=d["piece"],
            from_row=d["from_row"],
            from_col=d["from_col"],
            to_row=d["to_row"],
            to_col=d["to_col"],
            arrival_time=d["arrival_time"],
            is_jump=d.get("is_jump", False),
        )
