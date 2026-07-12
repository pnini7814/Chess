from board.board_parser import BoardParser
from commands.command_factory import CommandFactory
from moves.move_validator import StandardMoveValidator
from moves.move_factory import MoveFactory
from moves.move_scheduler import MoveScheduler
from game.game_engine import GameEngine


def run(input_text: str) -> None:
    lines = input_text.strip().splitlines()
    board = BoardParser().parse(lines)
    if board is None:
        print("ERROR: invalid board")
        return
    engine = GameEngine(CommandFactory(StandardMoveValidator(), MoveFactory(), MoveScheduler()))
    engine.run(lines, board)


if __name__ == "__main__":
    print("Enter input (type END on a new line to finish):")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    run("\n".join(lines))
