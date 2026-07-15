from dataclasses import dataclass


@dataclass(frozen=True)
class ClickCommand:
    x: int
    y: int


@dataclass(frozen=True)
class WaitCommand:
    ms: int


@dataclass(frozen=True)
class PrintBoardCommand:
    expected_lines: tuple[str, ...]


ScriptCommand = ClickCommand | WaitCommand | PrintBoardCommand


@dataclass(frozen=True)
class ParsedScript:
    board_lines: tuple[str, ...]
    commands: tuple[ScriptCommand, ...]


class ScriptParser:

    def parse(self, text: str) -> ParsedScript:
        lines = text.strip().splitlines()
        board_lines, rest = self._extract_board(lines)
        commands = self._extract_commands(rest)
        return ParsedScript(board_lines=tuple(board_lines), commands=tuple(commands))

    def _extract_board(self, lines: list[str]) -> tuple[list[str], list[str]]:
        board_lines = []
        i = 0
        while i < len(lines) and lines[i].strip() != "Board:":
            i += 1
        i += 1
        while i < len(lines) and lines[i].strip() not in ("click", "wait", "print") \
                and not lines[i].strip().startswith(("click ", "wait ", "print ")):
            board_lines.append(lines[i].strip())
            i += 1
        board_lines = [l for l in board_lines if l]
        return board_lines, lines[i:]

    def _extract_commands(self, lines: list[str]) -> list[ScriptCommand]:
        commands = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("click "):
                parts = line.split()
                commands.append(ClickCommand(x=int(parts[1]), y=int(parts[2])))
            elif line.startswith("wait "):
                commands.append(WaitCommand(ms=int(line.split()[1])))
            elif line == "print board":
                expected = []
                i += 1
                while i < len(lines) and lines[i].strip() and \
                        not lines[i].strip().startswith(("click ", "wait ", "print ")):
                    expected.append(lines[i].strip())
                    i += 1
                commands.append(PrintBoardCommand(expected_lines=tuple(expected)))
                continue
            i += 1
        return commands