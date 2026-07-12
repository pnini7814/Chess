from texttests.script_parser import ScriptParser

script = ScriptParser().parse("""Board:
. wR .
. . .
. . bK

click 100 0
click 100 200
wait 2000
print board
. . .
. . .
. wR bK
""")
print("board_lines:", script.board_lines)
print("commands:", script.commands)
