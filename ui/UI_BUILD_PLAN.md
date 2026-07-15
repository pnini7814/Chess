# Kung Fu Chess — UI Build Plan (Adapted to Your Project)

**Date:** July 2026
**Stack:** Python + OpenCV (cv2)
**Game engine:** Iterations 1-10 complete (KungFuArbiter with extra features)
**Graphics base:** `Img` class — thin OpenCV wrapper
**Scope:** UI only (rendering, input, animation, moves log/score)
**Status:** Complete plan prior to coding — every phase below is to be built

---

## 1. What your engine already provides

Your engine is complete with all necessary features:

| Concern | Implementation |
|---|---|
| Board/piece state | `GameEngine.snapshot()` → `GameSnapshot` with all piece positions, states, and metadata |
| Move submission | `GameEngine.request_move(src: Position, dst: Position)` → `MoveResult` |
| Jump submission | `GameEngine.request_jump(pos: Position)` → `MoveResult` (KungFuArbiter extra feature) |
| Click handling | `Controller.on_click(x, y)` — already handles select → move logic |
| Pixel mapping | `BoardMapper.pixel_to_cell(x, y)` — uses `CELL_SIZE = 100` |
| Virtual clock | `GameEngine.wait(ms)` — advances game time deterministically |
| Jump capture | Already in `KungFuArbiter._resolve_arrival` |
| Pawn promotion | Already in `KungFuArbiter._resolve_regular_arrival_with_airborne` |
| Game over | `GameEngine.game_over` set on king capture |

---

## 2. What's missing (UI scope)

- ❌ No rendering/graphics yet (headless text-based only)
- ❌ No real-time game loop (wall-clock driven)
- ❌ No smooth motion interpolation exposed to UI
- ❌ No sprite/animation system (idle/move/jump/long_rest states)
- ❌ No moves log, score display, player names
- ❌ Settlement events not exposed to UI observers

---

## 3. Architecture constraints

1. **All drawing through `Img` class only** — no PyGame, SFML, or other libraries
2. **`Img` is extensible** — add methods like `draw_rect`, `draw_circle`, `new`, `save` as needed
3. **Window/mouse via cv2** — `cv2.imshow`, `cv2.setMouseCallback`, `cv2.waitKey` (not another graphics library)
4. **Read-only snapshots** — all rendering state comes via `GameSnapshot` from engine
5. **No direct engine mutation from UI** — UI only calls public methods

---

## 4. Phased implementation plan

### Phase 0 — Project skeleton (no rendering)

**Goal:** UI package structure and engine wiring ready

**Files to create:**
```
kungfu_chess/ui/
├── __init__.py
├── config.py                 # GameConfig(cell_pixel_size=100, colors, etc.)
├── setup.py                  # Standard 8x8 starting position
├── app.py                    # Composition root & main loop (not yet)
├── rendering/
│   ├── __init__.py
│   ├── board_view.py         # Coordinator (not yet)
│   ├── board_renderer.py     # Background (not yet)
│   ├── piece_renderer.py     # Piece compositing (not yet)
│   └── overlay_renderer.py   # Overlays (not yet)
├── sprites/
│   ├── __init__.py
│   ├── sprite_library.py     # Asset loading Strategy (not yet)
│   ├── sprite_state.py       # State pattern (not yet)
│   └── assets/
│       └── placeholder/      # Generated placeholder sprites
├── events/
│   ├── __init__.py
│   ├── event_bus.py          # Observer/pub-sub (not yet)
│   └── observers/
│       ├── score_observer.py (not yet)
│       └── moves_log_observer.py (not yet)
└── img.py                    # Img class wrapper (not yet)
```

**Exit criteria:** 
- Engine boots via `build_game_engine()`
- `engine.snapshot()` returns standard starting position
- No window opens yet

---

### Phase 1 — Static render

**Goal:** Display board and pieces (no animation)

1. **Implement `Img` class:**
   - `read(path, size=(100,100), keep_aspect=True)` — load image
   - `draw_on(target, x, y)` — alpha-blend onto another image
   - `put_text(text, x, y, ...)` — render text
   - `draw_rect(x1, y1, x2, y2, color)` — draw rectangle
   - `draw_circle(x, y, radius, color)` — draw circle
   - `new(width, height, color)` — blank canvas
   - `save(path)` — write to disk
   - `show()` — cv2.imshow (for checks only, not per-frame)

2. **Generate placeholder assets:**
   - Checkerboard background (800×800 for 8×8 board)
   - Circular piece sprites: white/black × K/Q/R/B/N/P (100×100 each)
   - All in BGRA (4-channel) for proper alpha blending
   - Via script: `scripts/generate_placeholder_assets.py`

3. **Implement `BoardRenderer`:**
   - Load board background once
   - Convert to BGRA immediately
   - `fresh_frame()` returns copy each call

4. **Implement `PieceRenderer`:**
   - Load sprites per (color, kind)
   - `draw(frame, snapshot)` — draw each piece at pixel position

5. **Implement `BoardView` coordinator:**
   - Hold `BoardRenderer`, `PieceRenderer`, `OverlayRenderer`
   - `render(snapshot)` → call each in order

6. **Test:**
   - `board_view.render(engine.snapshot())` → window shows starting position

**Exit criteria:** Starting position renders, pieces on squares, no artifacts

---

### Phase 2 — Real-time loop

**Goal:** Clock advances, moves settle visibly

1. **Real-time loop in `app.py`:**
   ```python
   import time
   last_time = time.time()
   while True:
       dt_ms = (time.time() - last_time) * 1000
       last_time = time.time()
       
       engine.wait(int(dt_ms))
       snapshot = engine.snapshot()
       frame = board_view.render(snapshot)
       cv2.imshow("Kung Fu Chess", frame.img)
       cv2.waitKey(1)
   ```

2. **Test with hardcoded moves:**
   - Submit test moves via code (not yet mouse input)
   - Observe piece slides ~1000ms per square

**Exit criteria:** Pieces move smoothly, window responsive, clock advances

---

### Phase 3 — Mouse input

**Goal:** Click piece → click destination → move happens

1. **Register mouse callback:**
   ```python
   def mouse_handler(event, x, y, flags, param):
       if event == cv2.EVENT_LBUTTONDOWN:
           controller.on_click(x, y)
   
   cv2.setMouseCallback("Kung Fu Chess", mouse_handler)
   ```

2. **Test window resizing (empirically):**
   - If coordinates scale correctly: calculate scale factor
   - If not: lock window size via `cv2.WINDOW_AUTOSIZE`

3. **Add `OverlayRenderer` debug markers:**
   - Circle at cursor position
   - Different marker on click
   - Helps verify coordinate mapping

**Exit criteria:** Click piece → click destination → piece moves, mapping verified

---

### Phase 4 — Smooth motion & sprite animation

**Goal:** Pieces animate between states, smooth glide between cells

1. **Add `motion_progress` to engine's `PieceSnapshot`:**
   - Engine computes this (0.0 = start, 1.0 = settled)
   - UI reads directly, no extra query

2. **Implement sprite state machine:**
   - `SpriteState` class (idle/move/jump/long_rest)
   - `config.json` per state: `name`, `frames_per_sec`, `is_loop`, `next_state_when_finished`
   - `AnimatedSprite` transitions between states

3. **Update `PieceRenderer`:**
   - Use `motion_progress` to interpolate position
   - Render current frame from `AnimatedSprite`

4. **Sprite JSON configs:**
   ```json
   {
     "name": "move",
     "frames_per_sec": 12,
     "is_loop": false,
     "next_state_when_finished": "idle"
   }
   ```

**Exit criteria:** Pieces glide smoothly, breathe when idle, all motions smooth

---

### Phase 5 — Moves log, score, player names

**Goal:** Side panel with live updates

1. **Implement `EventBus` (Observer pattern):**
   - Engine publishes `MoveResolvedEvent`, `CaptureEvent`, `JumpResolvedEvent`
   - UI observers subscribe once at startup

2. **Implement `ScoreObserver`:**
   - Piece values: **Pawn=1, Knight=3, Bishop=3, Rook=5, Queen=9** ✓ CONFIRMED
   - Updates per-side totals on capture

3. **Implement `MovesLogObserver`:**
   - Appends `(time, move_text)` for each side

4. **Update `OverlayRenderer`:**
   - Draw score and moves log on right side
   - Use `Img.put_text` for all text
   - Separate pass so slow observer doesn't stall animation

**Exit criteria:** Full board + live score + moves log, no animation lag

---

### Phase 6 — Polish (one at a time, after 1-5 solid)

1. Show `MoveResult` rejection reasons ("motion_in_progress" flash, etc.)
2. Full UI layout polish (board + panels fit together)
3. Additional sprite sets as available
4. Sound hooks (move/capture/jump)
5. Real player names (future: multiplayer)

---

## 5. Key locked decisions

| Item | Decision |
|---|---|
| **Observer pattern** | Engine will publish `SettlementEvent` to subscribers (Phase 5) |
| **motion_progress field** | `PieceSnapshot` gains optional `motion_progress: float = 1.0` field |
| **Starting position** | Hardcoded standard 8×8 in `ui/setup.py` |
| **Piece values** | P=1, N/B=3, R=5, Q=9 |
| **Window sizing** | Test empirically in Phase 3; fixed-size or resizable as result shows |
| **Drawing library** | All via `Img` only, no PyGame/SFML |

---

## 6. Integration with your existing code

| Your component | How UI uses it |
|---|---|
| `GameEngine` | `.snapshot()`, `.request_move()`, `.request_jump()`, `.wait()` |
| `Controller` | `.on_click(x, y)` — UI calls directly |
| `BoardMapper` | Already used by Controller, UI doesn't call directly |
| `KungFuArbiter` | Transparent to UI (engine handles settling) |
| `GameSnapshot` | Primary data source for rendering (read-only) |

**No engine code changes needed for Phases 0-3.** Phases 4+ need two small additive hooks (event publishing, `motion_progress` field), both backward compatible.

---

## 7. Testing strategy (headless in CI)

Every rendering class takes dependencies as constructor arguments (Protocol-typed), never imports `cv2` directly:

```python
def test_board_view_composites_pieces():
    fake_board = FakeBoardRenderer()
    fake_pieces = FakePieceRenderer()
    fake_overlay = FakeOverlayRenderer()
    
    board_view = BoardView(fake_board, fake_pieces, fake_overlay)
    frame = board_view.render(fake_snapshot, fake_input_state)
    
    assert fake_pieces.draw_call_count == 1
    # No cv2.imshow, no window, no monkeypatching
```

All tests in `tests/ui/` run headless in CI.

---

## 8. What's complete vs. remaining

✅ **Complete:**
- Engine (Iterations 1-10)
- Text-based integration tests
- Common route (RealTimeArbiter)
- Extra features (KungFuArbiter, promotion, jump, airborne capture)
- Test framework and scoring

❌ **Remaining:**
- UI (this plan, Phases 0-6)
- Board/piece art assets (if using real images)
- Sprite/animation JSON configs

---

## 9. Next steps

1. **Create `/ui` package structure** with Phase 0 skeleton
2. **Generate placeholder assets** or prepare real board/piece images
3. **Begin Phase 1** once assets exist or placeholders are generated
4. **Follow phases 1-6 in order** — each builds on previous

---

## 10. Timeline estimate

- **Phase 0:** 1-2 hours (skeleton + imports)
- **Phase 1:** 4-6 hours (rendering setup)
- **Phase 2:** 2-3 hours (real-time loop)
- **Phase 3:** 2-3 hours (mouse input)
- **Phase 4:** 4-6 hours (animation)
- **Phase 5:** 3-4 hours (observers + UI)
- **Phase 6:** 2-4 hours (polish, per task)

**Total:** ~20-30 hours for full implementation

---

**This document is the complete, decisions-locked blueprint for the UI.**  
**Nothing is implemented yet — ready to code once we start Phase 0.**
