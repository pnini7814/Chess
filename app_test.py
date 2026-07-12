from app import run

failures = run("""Board:
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
print("failures:", repr(failures))

failures2 = run("""Board:
wR . . .
. . . .
. . . .
. . . wK

click 0 0
click 300 0
wait 500
print board
wR . . .
. . . .
. . . .
. . . wK
wait 3000
print board
. . . wR
. . . .
. . . .
. . . wK
""")
print("timing failures:", repr(failures2))
