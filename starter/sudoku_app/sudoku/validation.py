from .logic import SIZE


def is_safe(board, row, col, num):
    """Return True when placing num at the given location doesn't break Sudoku rules."""
    for index in range(SIZE):
        if board[row][index] == num or board[index][col] == num:
            return False

    start_row = row - row % 3
    start_col = col - col % 3
    for box_row in range(3):
        for box_col in range(3):
            if board[start_row + box_row][start_col + box_col] == num:
                return False
    return True
