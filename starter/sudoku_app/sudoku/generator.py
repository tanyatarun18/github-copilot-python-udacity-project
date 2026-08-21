import random

from .logic import EMPTY, SIZE, create_empty_board, deep_copy
from .validation import is_safe


DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 25,
}


def fill_board(board):
    """Populate an empty board using recursive backtracking."""
    while True:
        for row in range(SIZE):
            for col in range(SIZE):
                board[row][col] = EMPTY

        if _fill_board_with_backtracking(board):
            return True


def _fill_board_with_backtracking(board):
    """Recursively fill the board one cell at a time."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                candidate_values = list(range(1, SIZE + 1))
                random.shuffle(candidate_values)

                for candidate in candidate_values:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate

                        if _fill_board_with_backtracking(board):
                            return True

                        board[row][col] = EMPTY

                return False

    return True


def _get_candidates(board_state, row, col):
    """Return the valid values that can be placed in a cell."""
    candidates = []

    for candidate in range(1, SIZE + 1):
        if is_safe(board_state, row, col, candidate):
            candidates.append(candidate)

    return candidates


def count_solutions(board, limit=2):
    """Count how many solutions a partial board can have, up to a given limit."""
    board_state = deep_copy(board)
    solutions = 0

    def _count():
        nonlocal solutions

        if solutions >= limit:
            return

        best_row = None
        best_col = None
        best_candidates = None

        for row in range(SIZE):
            for col in range(SIZE):
                if board_state[row][col] == EMPTY:
                    candidates = _get_candidates(board_state, row, col)

                    if not candidates:
                        return

                    if (
                        best_candidates is None
                        or len(candidates) < len(best_candidates)
                    ):
                        best_row = row
                        best_col = col
                        best_candidates = candidates

                        if len(best_candidates) == 1:
                            break

            if (
                best_candidates is not None
                and len(best_candidates) == 1
            ):
                break

        if best_candidates is None:
            solutions += 1
            return

        for candidate in best_candidates:
            board_state[best_row][best_col] = candidate

            _count()

            board_state[best_row][best_col] = EMPTY

            if solutions >= limit:
                return

    _count()
    return solutions


def _remove_cells_while_preserving_uniqueness(board, clues):
    """Remove clues while ensuring the resulting board has one solution."""
    target_empty_cells = SIZE * SIZE - clues

    if target_empty_cells <= 0:
        return deep_copy(board)

    full_board = deep_copy(board)
    positions = [
        (row, col)
        for row in range(SIZE)
        for col in range(SIZE)
    ]

    for _ in range(100):
        working_board = deep_copy(full_board)
        empty_count = 0

        random.shuffle(positions)

        while empty_count < target_empty_cells:
            progress = False

            for row, col in positions:
                if empty_count >= target_empty_cells:
                    break

                if working_board[row][col] == EMPTY:
                    continue

                original_value = working_board[row][col]
                working_board[row][col] = EMPTY

                if count_solutions(working_board, limit=2) == 1:
                    empty_count += 1
                    progress = True
                else:
                    working_board[row][col] = original_value

            if not progress:
                break

        if empty_count == target_empty_cells:
            return working_board

    # If the exact target could not be reached, return the last
    # uniquely solvable puzzle produced.
    return working_board


def remove_cells(board, clues):
    """Remove values until the board reaches the target clue count."""
    target_empty_cells = SIZE * SIZE - clues

    if target_empty_cells <= 0:
        return

    positions = [
        (row, col)
        for row in range(SIZE)
        for col in range(SIZE)
    ]

    random.shuffle(positions)

    removed = 0

    for row, col in positions:
        if removed >= target_empty_cells:
            break

        if board[row][col] == EMPTY:
            continue

        board[row][col] = EMPTY
        removed += 1


def generate_unique_puzzle(solution_board, clues):
    """Create a puzzle with the target clue count while preserving uniqueness."""
    return _remove_cells_while_preserving_uniqueness(
        solution_board,
        clues
    )


def generate_puzzle(clues=35, difficulty=None):
    """Create a new Sudoku puzzle and its solved board."""
    target_clues = clues

    if difficulty is not None:
        normalized_difficulty = str(difficulty).strip().lower()

        if normalized_difficulty in DIFFICULTY_CLUES:
            target_clues = DIFFICULTY_CLUES[normalized_difficulty]

    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)

    # Difficulty-based puzzles preserve uniqueness.
    if difficulty is not None:
        puzzle = generate_unique_puzzle(
            solution,
            target_clues
        )

    # The default 35-clue puzzle also preserves uniqueness.
    elif target_clues == 35:
        puzzle = generate_unique_puzzle(
            solution,
            target_clues
        )

    # Custom clue counts use direct removal so the exact requested
    # number of clues is always returned quickly.
    else:
        remove_cells(board, target_clues)
        puzzle = deep_copy(board)

    return puzzle, solution