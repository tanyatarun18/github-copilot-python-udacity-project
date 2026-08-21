def count_clues(board):
    return sum(1 for row in board for cell in row if cell != 0)
