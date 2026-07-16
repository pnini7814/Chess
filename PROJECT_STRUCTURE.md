# Kung Fu Chess - Project Structure and Instructions

## Overview
This is a real-time chess game where pieces move according to chess rules but movement is not instantaneous. Pieces travel toward their destination at a fixed speed, and the logical board updates only when a piece arrives.

## Current Architecture

The project implements a **clean, layered architecture** with the following components:

### 1. **Model Layer** (`models/`)
- `position.py` - Value object representing board cells (row, col)
- `piece.py` - Chess piece with color, kind, and current cell
- `board.py` - Board state: dimensions, piece placement, bounds checking
- `game_state.py` - Game state: board, current time, selection, game-over flag
- `piece_factory.py` - Factory for creating pieces from tokens (e.g., "wR", "bK")

**Responsibilities:**
- Store piece positions and board state
- Validate board bounds
- Track piece lifecycle (placement, removal, capture)

**Does NOT own:** Rendering, movement rules, timing, click handling

### 2. **Rules Layer** (`rules/`)
- `piece_rules.py` - Abstract `PieceRule` interface and concrete implementations:
  - `RookRule`, `BishopRule`, `QueenRule`, `KnightRule`, `KingRule`, `PawnRule`
  - Each rule calculates legal destinations given board state
  - Handles sliding pieces with blocking and capture logic
- `rule_engine.py` - `RuleEngine`: validates move legality before allowing it

**Responsibilities:**
- Calculate legal moves for each piece type
- Validate requested moves against current board state
- Check for friendly-fire, out-of-bounds, blocking, captures

**Does NOT own:** Board mutation, timing, rendering, game-over logic

### 3. **Real-Time Layer** (`realtime/`)
- `motion.py` - `Motion` object: models a piece traveling from source to destination
  - Stores piece, source, destination, start time, arrival time
  - Calculates pixel position at any elapsed time
- `real_time_arbiter.py` - `RealTimeArbiter`: manages active motions and arrival resolution
  - Maintains list of in-flight motions
  - Advances time and resolves arrivals atomically
  - Handles capture logic: removes target piece before placing moving piece
  - Reports king capture with `KingCapturedError`

**Responsibilities:**
- Track moving pieces in flight
- Resolve arrivals atomically (remove source, remove target, place piece)
- Detect and report game-ending captures

**Does NOT own:** Chess legality, click handling, rendering, script parsing

### 4. **Engine Layer** (`engine/`)
- `game_engine.py` - `GameEngine`: application-service coordinator
  - Delegates validation to `RuleEngine`
  - Delegates motion to `RealTimeArbiter`
  - Guards against game-over
  - **NEW:** Guards against `motion_in_progress` (only one motion at a time in common route)
  - Generates `GameSnapshot` for rendering

**Responsibilities:**
- Coordinate board, rules, and real-time arbitration
- Handle public move/wait commands
- Provide game state snapshots for UI rendering
- Enforce game rules (game-over guard, motion blocking)

**Does NOT own:** Piece-specific logic, input parsing, rendering, coordinate mapping

### 5. **Input Layer** (`input/`)
- `board_mapper.py` - `BoardMapper`: converts pixel coordinates to board positions
  - Maps clicks to cells based on board size and cell size
- `controller.py` - `Controller`: click handling
  - Converts on-click events to move requests
  - Manages selection state (selected cell for two-click moves)

**Responsibilities:**
- Translate screen clicks to game commands
- Maintain UI selection state

**Does NOT own:** Chess legality, board mutation, rendering, timing

### 6. **I/O Layer** (`chess_io/`)
- `board_parser.py` - `BoardParser`: parses text board descriptions
  - Extracts board section from text
  - Validates token format and row width
  - Creates Board with pieces from factory
- `board_printer.py` - `BoardPrinter`: outputs board state as text
  - Formats board for text-based tests and debugging

**Responsibilities:**
- Parse textual game descriptions into Board objects
- Serialize Board state back to text

**Does NOT own:** Movement rules, rendering, game logic

### 7. **View Layer** (`view/`)
- `renderer.py` - Abstract `Renderer` interface and `GameSnapshot` DTO
  - `GameSnapshot`: read-only snapshot of board state (positions, selected cell, game-over)
  - `Renderer`: abstract base for implementations (console, UI, etc.)
- `image_view.py` - Potential image-based renderer

**Responsibilities:**
- Display game state to user
- Convert model snapshots to visual output

**Does NOT own:** Game logic, movement rules, input handling

### 8. **Text Test Framework** (`texttests/`)
- `script_parser.py` - `ScriptParser`: parses test scripts into commands
  - Commands: `Board`, `click`, `wait`, `print board`
- `script_runner.py` - `ScriptRunner`: executes test scripts without UI
  - Drives engine and controller through public API
  - Captures board output and compares to expected

**Responsibilities:**
- Parse textual integration tests
- Execute games without rendering
- Validate output against expectations

**Does NOT own:** Direct board mutation, movement logic, rendering

## Design Rules & Constraints

### Common Route Requirements
These are the current rules implemented:

1. ✅ Board is any rectangular size (inferred from textual description)
2. ✅ Pieces use chess notation: K, Q, R, B, N, P
3. ✅ Color encoded by prefix: wK = white king, bR = black rook
4. ✅ '.' = empty square
5. ✅ No special moves: no check, checkmate, castling, en passant, promotion
6. ✅ King can be captured
7. ✅ Capturing opponent king ends the game (raises `KingCapturedError`)
8. ✅ Piece moves only according to its movement rule
9. ✅ Sliding pieces don't pass through blocking pieces
10. ✅ Movement has fixed speed (defined by `CELL_SIZE` and `Motion.TRAVEL_TIME_MS`)
11. ✅ Tests use fixed cell size in pixels
12. ⚠️ UI rendering available (Pygame-based)
13. ✅ Logical board changes only when moving piece arrives
14. ✅ **Only one active motion at a time** (common route constraint)
    - If a move is requested while another motion is active, `GameEngine.request_move()` returns `motion_in_progress`
15. ✅ Text integration DSL: Board, click, wait, print board
16. ✅ `print board` is the only assertion mechanism

### Dependency Direction Rules
```
Model (depends on nothing)
  ↑
  └── Board, Piece, Position, GameState
  
Rules (depends on Model)
  ↑
  └── RuleEngine, PieceRules
  
RealTime (depends on Model)
  ↑
  └── RealTimeArbiter, Motion
  
Engine (depends on Model, Rules, RealTime)
  ↑
  └── GameEngine
  
Input (depends on Model, Engine)
  ↑
  └── Controller, BoardMapper
  
View (depends on Engine snapshot)
  ↑
  └── Renderer, GameSnapshot
  
IO (depends on Model only)
  └── BoardParser, BoardPrinter
  
TextTests (depends on all public components)
  └── ScriptRunner, ScriptParser
```

**Rule:** Dependencies point upward only. Model never depends on UI. Rules never depend on timing.

### API Boundaries

#### GameEngine.request_move(state, from_pos, to_pos) → MoveResult
- Checks game-over
- **Checks motion_in_progress** (NEW)
- Validates move legality
- Starts motion if valid
- Returns `MoveResult(is_accepted, reason)`

#### GameEngine.wait(state, ms)
- Advances game time
- Resolves arrived motions
- Updates board state atomically

#### RealTimeArbiter.start_motion(piece, from_pos, to_pos, current_time)
- Creates a Motion object
- Adds to active motions list
- No duplicate motions for same piece (guarded by GameEngine)

#### RealTimeArbiter.advance(current_time, board)
- Resolves all motions that have arrived
- Updates board atomically for each arrival
- May raise `KingCapturedError` if king captured

## Key Files and Their Roles

| File | Class | Role |
|------|-------|------|
| `models/board.py` | Board | Core board state |
| `models/game_state.py` | GameState | Full game state container |
| `models/position.py` | Position | Board coordinates (value object) |
| `rules/rule_engine.py` | RuleEngine | Move validation service |
| `rules/piece_rules.py` | PieceRule (+ subclasses) | Movement strategy per piece type |
| `realtime/real_time_arbiter.py` | RealTimeArbiter | Motion coordinator |
| `realtime/motion.py` | Motion | A piece in transit |
| `engine/game_engine.py` | GameEngine | Application service & coordinator |
| `input/controller.py` | Controller | Click-to-command translator |
| `input/board_mapper.py` | BoardMapper | Pixel-to-cell coordinate mapper |
| `chess_io/board_parser.py` | BoardParser | Text → Board parser |
| `chess_io/board_printer.py` | BoardPrinter | Board → text serializer |
| `view/renderer.py` | Renderer, GameSnapshot | View abstraction & DTO |
| `texttests/script_runner.py` | ScriptRunner | Integration test executor |

## Development Workflow

When implementing a new feature or fixing a bug:

1. **Identify the layer** - Which layer owns this behavior? (Model, Rules, RealTime, Engine, Input, View, IO, or TextTests?)
2. **Write a failing unit test** first, focused on that layer's responsibility
3. **Implement the minimal change** to make the test pass
4. **Check dependencies** - Does the change respect the dependency hierarchy?
5. **Refactor if needed** - Does the change introduce responsibility leakage?
6. **Add integration tests** if needed (via ScriptRunner)
7. **Commit** when all tests pass

### Example: Adding a new piece type (Knight)

1. Add KnightRule to `rules/piece_rules.py` with legal-move logic
2. Register it in `rules/rule_engine.py`'s RULE_MAP
3. Register "N" token in `models/piece_factory.py`
4. Write unit tests for KnightRule (test jumps, blocking, etc.)
5. Write integration tests in script format
6. Verify no new dependencies were introduced

## Current Status

### ✅ Implemented
- All piece movement rules (Rook, Bishop, Queen, Knight, King, Pawn)
- Board model with bounds checking
- RuleEngine with legality validation
- RealTimeArbiter with atomic arrival resolution
- GameEngine with game-over and motion-in-progress guards
- Controller with selection state
- BoardMapper and coordinate conversion
- BoardParser and BoardPrinter
- GameSnapshot for rendering
- ScriptRunner for text-based integration tests
- Pygame UI (in `ui/` folder)

### ⚠️ Known Issues
1. Some tests reference `request_jump()` which doesn't exist (should use `request_move()`)
2. Test `test_rook_moves_horizontally` fails - board state mismatch after move

### 🔄 To Investigate
1. Why do some integration tests fail while unit tests pass?
2. Is the Motion timing calculation correct?
3. Should there be a UI-specific layer separate from the core game?

## Testing

### Unit Tests
```bash
python -m pytest tests/ -v
```

Location: `tests/` folder
- `test_board_and_state.py` - Board, GameState, BoardParser
- `test_integration.py` - RuleEngine, GameEngine, Controller
- `test_pieces.py` - All piece movement rules

### Integration Tests
Text-based scripts in `tests/integration/scripts/`:
- Each `.kfc` file contains a board setup and sequence of commands
- ScriptRunner executes without UI
- Output validated by comparing board state

## Next Steps

1. **Fix failing integration tests** - Debug board state mismatches
2. **Add more integration test cases** - Cover edge cases (simultaneous motions, collision detection, etc.)
3. **Implement extra route features** if desired (simultaneous motions, cooldown, replay, bot, etc.)
4. **Improve UI** - Add visual feedback, animations, etc.
5. **Document edge cases** - Special moves, error handling, etc.

---

**Architecture Philosophy:** Keep layers thin and focused. Each layer owns one responsibility and knows nothing about UI details, timing details, or rendering details. Test each layer independently before connecting them.
