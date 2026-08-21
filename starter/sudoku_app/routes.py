from flask import Blueprint, current_app, jsonify, render_template, request

from .sudoku import SIZE, generate_puzzle

main_blueprint = Blueprint("main", __name__)


def _find_incorrect_cells(board, solution):
    """Return the positions that do not match the current solution."""
    incorrect_cells = []

    for row_index in range(SIZE):
        for col_index in range(SIZE):
            if board[row_index][col_index] != solution[row_index][col_index]:
                incorrect_cells.append([row_index, col_index])

    return incorrect_cells


def _is_complete_solution(board, solution):
    """Return True when the board is fully filled and matches the solution."""
    for row_index in range(SIZE):
        for col_index in range(SIZE):
            if board[row_index][col_index] == 0:
                return False

            if board[row_index][col_index] != solution[row_index][col_index]:
                return False

    return True


def _is_valid_board(board):
    """Return True when board is a valid 9x9 list of integer values."""
    if not isinstance(board, list) or len(board) != SIZE:
        return False

    for row in board:
        if not isinstance(row, list) or len(row) != SIZE:
            return False

        for value in row:
            if not isinstance(value, int) or value < 0 or value > SIZE:
                return False

    return True


@main_blueprint.route("/")
def index():
    """Render the main Sudoku game page."""
    return render_template("index.html")


@main_blueprint.route("/new")
def new_game():
    """Create a new puzzle and store it as the active game."""
    difficulty = request.args.get("difficulty", "").strip().lower()
    clues_param = request.args.get("clues")

    try:
        clues = int(clues_param) if clues_param is not None else 35
    except ValueError:
        return jsonify({"error": "Invalid clue count"}), 400

    puzzle, solution = generate_puzzle(
        clues=clues,
        difficulty=difficulty or None,
    )

    clue_count = sum(
        1
        for row in puzzle
        for cell in row
        if cell != 0
    )

    current_app.CURRENT["puzzle"] = puzzle
    current_app.CURRENT["solution"] = solution

    return jsonify(
        {
            "puzzle": puzzle,
            "difficulty": difficulty or "medium",
            "clues": clue_count,
        }
    )


@main_blueprint.route("/check", methods=["POST"])
def check_solution():
    """Check a submitted board against the active game's solution."""
    data = request.get_json(silent=True) or {}
    board = data.get("board")
    solution = current_app.CURRENT.get("solution")

    if solution is None:
        return jsonify({"error": "No game in progress"}), 400

    if not _is_valid_board(board):
        return jsonify({"error": "Invalid board"}), 400

    # Keep empty cells in the incorrect list when they do not match the
    # solution. This preserves the existing project test behavior.
    incorrect_cells = _find_incorrect_cells(board, solution)

    solved = (
        not incorrect_cells
        and _is_complete_solution(board, solution)
    )

    return jsonify(
        {
            "incorrect": incorrect_cells,
            "solved": solved,
        }
    )


@main_blueprint.route("/hint", methods=["POST"])
def give_hint():
    """Fill exactly one empty cell with the correct solution value."""
    data = request.get_json(silent=True) or {}
    board = data.get("board")
    solution = current_app.CURRENT.get("solution")

    if solution is None:
        return jsonify({"error": "No game in progress"}), 400

    if not _is_valid_board(board):
        return jsonify({"error": "Invalid board"}), 400

    updated_board = [row[:] for row in board]

    for row_index in range(SIZE):
        for col_index in range(SIZE):
            if updated_board[row_index][col_index] == 0:
                updated_board[row_index][col_index] = (
                    solution[row_index][col_index]
                )

                return jsonify(
                    {
                        "hint": {
                            "row": row_index,
                            "col": col_index,
                            "value": solution[row_index][col_index],
                        },
                        "board": updated_board,
                    }
                )

    return jsonify({"error": "No empty cells available"}), 400