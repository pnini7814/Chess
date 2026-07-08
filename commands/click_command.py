from commands.command import Command
from game.game_state import GameState


class ClickCommand(Command):

    def __init__(self, parts: list[str], move_validator, move_factory):
        self._row, self._col = self.parse_coords(parts)
        self._validator = move_validator
        self._factory = move_factory

    def execute(self, state: GameState) -> None:
        if not state.is_within_bounds(self._row, self._col):
            return

        if state.has_selection():
            self._handle_destination(state)
        else:
            self._handle_selection(state)

    def _handle_selection(self, state: GameState) -> None:
        cell = state.board[self._row][self._col]
        if cell == "." or state.is_piece_moving(self._row, self._col):
            return
        state.select(self._row, self._col)

    def _handle_destination(self, state: GameState) -> None:
        cell = state.board[self._row][self._col]
        piece = state.board[state.selected_row][state.selected_col]

        if cell == ".":
            self._try_move(state, piece)
        elif piece[0] == cell[0]:
            self._switch_selection_to_ally(state)
        else:
            self._try_capture(state, piece)

    def _try_move(self, state: GameState, piece: str) -> None:
        if not self._validator.is_valid(piece, state.selected_row, state.selected_col,
                                        self._row, self._col, state.board):
            return
        move = self._factory.create(piece, state.selected_row, state.selected_col,
                                    self._row, self._col, state.current_time)
        state.pending_moves.append(move)
        state.deselect()

    def _try_capture(self, state: GameState, piece: str) -> None:
        if not self._validator.is_valid(piece, state.selected_row, state.selected_col,
                                        self._row, self._col, state.board):
            return
        move = self._factory.create(piece, state.selected_row, state.selected_col,
                                    self._row, self._col, state.current_time)
        state.pending_moves.append(move)
        state.deselect()

    def _switch_selection_to_ally(self, state: GameState) -> None:
        if not state.is_piece_moving(self._row, self._col):
            state.select(self._row, self._col)
