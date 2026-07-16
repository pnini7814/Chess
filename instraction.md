# Kung Fu Chess - Implementation Instructions

> **See `PROJECT_STRUCTURE.md` for detailed architectural documentation and design rules.**

## Quick Start

This is a real-time chess game where pieces move according to chess rules, but movement happens over time (not instantaneously).

**Key Design Principle:** Clean layered architecture where each layer has one responsibility and knows nothing about UI, timing, or rendering details.

## Project Structure

```
models/          → Board, Piece, Position, GameState (core data)
rules/           → RuleEngine, PieceRules (move validation)
realtime/        → RealTimeArbiter, Motion (timing & arrival)
engine/          → GameEngine (application service coordinator)
input/           → Controller, BoardMapper (click handling)
chess_io/        → BoardParser, BoardPrinter (text I/O)
view/            → Renderer, GameSnapshot (abstract view)
texttests/       → ScriptRunner, ScriptParser (text-based tests)
ui/              → Pygame UI (optional)
tests/           → Unit and integration tests
```

## Core Responsibilities

| Layer | Owns | Does NOT Own |
|-------|------|------------|
| **Model** | Board state, piece positions, cell coordinates | Pixels, clicks, rules, timing |
| **Rules** | Move legality, piece movement geometry | Board mutation, rendering, timing |
| **RealTime** | Motion tracking, arrival resolution, captures | Chess rules, rendering, input |
| **Engine** | Coordination, game-over guard, motion blocking | Piece logic, rendering, input parsing |
| **Input** | Click-to-command translation, selection state | Chess rules, board mutation |
| **View** | Visual rendering from snapshots | Game logic, input, board state |
| **IO** | Parsing/serializing board text | Game logic, rendering, rules |
| **TextTests** | Scripted test execution | Direct board mutation, game logic |

## Development Rules

### 1. Always Respect Dependencies
- Model depends on nothing
- Everything eventually depends on Model
- UI never depends on game logic (depends on snapshots only)
- Rules never depend on timing

### 2. One Active Motion at a Time (Common Route)
```python
# GameEngine.request_move() checks this:
if arbiter.has_active_motion():
    return MoveResult(is_accepted=False, reason="motion_in_progress")
```

### 3. Atomic Arrival Resolution
When a piece arrives:
1. Remove piece from source cell
2. Remove enemy piece at destination (if any)
3. Place moving piece at destination
4. Report king capture if applicable

### 4. Test-Driven Development
1. Write failing test first (unit or integration)
2. Implement minimal change to pass
3. Check for responsibility leakage
4. Refactor if needed
5. Commit when tests pass

## Common Tasks

### Adding a New Piece Type

1. Create movement rule in `rules/piece_rules.py`:
```python
class MyPieceRule(PieceRule):
    def legal_destinations(self, board: Board, piece: Piece) -> set[Position]:
        # Return set of valid destinations
```

2. Register in `rules/rule_engine.py` RULE_MAP

3. Register token in `models/piece_factory.py`

4. Write unit tests in `tests/test_pieces.py`

5. Add integration tests as `.kfc` scripts

### Debugging a Move

1. Check layer responsibility - is this a Rules problem or RealTime problem?
2. Write a failing test that reproduces the issue
3. Check the layer's invariants:
   - **Rules:** Does legality check pass? Are pieces on board correct?
   - **RealTime:** Does motion calculate arrival time correctly? Does resolution place piece at destination?
   - **Engine:** Does game-over guard work? Does motion-in-progress guard work?
   - **Controller:** Is click converted to correct position?
4. Add assertions to verify the diagnosis

### Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_pieces.py -v

# Specific test
python -m pytest tests/test_integration.py::TestRuleEngine::test_valid_rook_move -v

# With coverage
python -m pytest tests/ --cov=. --cov-report=term-missing
```

### Running a Game

```bash
# Via text script
python app.py < script.kfc

# Via UI (if implemented)
cd ui
python app.py
```

## Key APIs

### GameEngine
```python
def request_move(state: GameState, from_pos: Position, to_pos: Position) -> MoveResult:
    # Validates, starts motion, returns result

def wait(state: GameState, ms: int) -> None:
    # Advances time, resolves arrivals

def snapshot(state: GameState) -> GameSnapshot:
    # Returns read-only view for rendering
```

### RuleEngine
```python
def validate(board: Board, from_pos: Position, to_pos: Position) -> MoveValidation:
    # Returns is_valid + reason (e.g., "illegal_piece_move")
```

### RealTimeArbiter
```python
def start_motion(piece: Piece, from_pos: Position, to_pos: Position, current_time: int):
    # Starts a motion (or ignores if piece already moving)

def advance(current_time: int, board: Board):
    # Resolves all arrived motions, updates board atomically
    # May raise KingCapturedError
```

## Common Mistakes to Avoid

### ❌ Don't

- **Mutate Board in RuleEngine** - Only validate, don't change state
- **Put timing logic in RealTimeArbiter** - It only tracks motions, not game logic
- **Render directly from Board** - Use GameSnapshot only
- **Handle clicks directly in GameEngine** - Controller's job
- **Block multiple motions in RealTimeArbiter** - GameEngine does that
- **Skip tests** - Write tests before implementation
- **Merge unrelated responsibilities** - If you can't describe a class in one sentence, split it

### ✅ Do

- **Validate before mutating** - RuleEngine validates, GameEngine mutates
- **Use value objects** - Position, MoveResult, GameSnapshot, MoveValidation
- **Test each layer independently** - Mock the layers it depends on
- **Document invariants** - Why does _resolve_arrival look like that?
- **Review diffs carefully** - Does dependency direction stay clean?
- **Commit frequently** - Small, testable changes are easier to review

## Files You'll Edit Most Often

1. `rules/piece_rules.py` - Adding piece movement logic
2. `tests/test_pieces.py` - Writing piece movement tests
3. `models/game_state.py` - Adding game state
4. `engine/game_engine.py` - Coordination logic
5. `texttests/` - Integration test scripts

## Debugging Checklist

- [ ] Is the test failing at the right layer? (Check the stack trace)
- [ ] Does the test have a clear name that explains what it tests?
- [ ] Are you testing the right piece type? (Make sure token is correct)
- [ ] Is the board correctly set up? (Print it before/after)
- [ ] Are coordinates (row, col) correct? (Not mixed up)
- [ ] Does the motion have correct arrival_time? (Check math)
- [ ] Is the piece correctly removed from source before being placed at destination?
- [ ] Are you checking game_over or motion_in_progress guards?

## Next Steps

See `PROJECT_STRUCTURE.md` for:
- Detailed layer responsibilities
- Dependency diagram
- Key classes and their roles
- Known issues and next steps
- Architecture philosophy

---

**Remember:** The real goal is learning clean architecture, not finishing fast. Write tests, respect dependencies, and review your diffs carefully.
