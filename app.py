from rules.rule_engine import RuleEngine
from realtime.real_time_arbiter import RealTimeArbiter
from engine.game_engine import GameEngine
from input.board_mapper import BoardMapper
from input.controller import Controller
from texttests.script_runner import ScriptRunner


def run(input_text: str) -> list[str]:
    rule_engine = RuleEngine()
    arbiter = RealTimeArbiter()
    engine = GameEngine(rule_engine, arbiter)

    from chess_io.board_parser import BoardParser
    from texttests.script_parser import ScriptParser
    script = ScriptParser().parse(input_text)
    board = BoardParser().parse(["Board:"] + list(script.board_lines))
    if board is None:
        print("ERROR: invalid board")
        return ["ERROR: invalid board"]

    mapper = BoardMapper(rows=board.rows, cols=board.cols)
    controller = Controller(engine, mapper)
    runner = ScriptRunner(engine, controller)

    return runner.run(input_text)


if __name__ == "__main__":
    import sys
    lines = []
    for line in sys.stdin:
        if line.strip() == "END":
            break
        lines.append(line.rstrip("\n"))


    run("\n".join(lines))
