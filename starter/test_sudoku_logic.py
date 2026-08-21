"""
Unit tests for sudoku_logic.py - puzzle generation and validation.
"""
import pytest
import sudoku_logic
from sudoku_app.sudoku.generator import count_solutions


class TestBoardCreation:
    """Tests for board creation utilities."""

    def test_create_empty_board(self):
        """Empty board should be 9x9 grid of zeros."""
        board = sudoku_logic.create_empty_board()
        assert len(board) == 9
        assert all(len(row) == 9 for row in board)
        assert all(board[i][j] == 0 for i in range(9) for j in range(9))

    def test_deep_copy_creates_independent_board(self):
        """Deep copy should create independent board."""
        board1 = sudoku_logic.create_empty_board()
        board1[0][0] = 5
        board2 = sudoku_logic.deep_copy(board1)
        board2[0][0] = 9
        assert board1[0][0] == 5
        assert board2[0][0] == 9


class TestValidation:
    """Tests for Sudoku validation logic (is_safe)."""

    def test_is_safe_empty_cell_with_valid_number(self):
        """Valid number in empty cell should return True."""
        board = sudoku_logic.create_empty_board()
        assert sudoku_logic.is_safe(board, 0, 0, 5) is True

    def test_is_safe_duplicate_in_row(self):
        """Number already in row should return False."""
        board = sudoku_logic.create_empty_board()
        board[0][2] = 7
        assert sudoku_logic.is_safe(board, 0, 0, 7) is False

    def test_is_safe_duplicate_in_column(self):
        """Number already in column should return False."""
        board = sudoku_logic.create_empty_board()
        board[5][0] = 3
        assert sudoku_logic.is_safe(board, 0, 0, 3) is False

    def test_is_safe_duplicate_in_3x3_box(self):
        """Number already in 3x3 box should return False."""
        board = sudoku_logic.create_empty_board()
        board[1][1] = 9
        assert sudoku_logic.is_safe(board, 0, 0, 9) is False

    def test_is_safe_valid_in_different_box(self):
        """Same number in different 3x3 box should be valid."""
        board = sudoku_logic.create_empty_board()
        board[1][1] = 4  # Top-left 3x3
        assert sudoku_logic.is_safe(board, 3, 3, 4) is True  # Middle 3x3

    def test_is_safe_number_range(self):
        """Test edge cases for number ranges."""
        board = sudoku_logic.create_empty_board()
        assert sudoku_logic.is_safe(board, 0, 0, 1) is True
        assert sudoku_logic.is_safe(board, 0, 0, 9) is True
        # Note: is_safe doesn't validate range, but we test it accepts 1-9


class TestFillBoard:
    """Tests for board-filling logic (backtracking solver)."""

    def test_fill_board_completes_empty_board(self):
        """Filling empty board should result in complete valid solution."""
        board = sudoku_logic.create_empty_board()
        result = sudoku_logic.fill_board(board)
        assert result is True
        # All cells should be filled
        assert all(board[i][j] != 0 for i in range(9) for j in range(9))

    def test_fill_board_has_all_digits_in_each_row(self):
        """Filled board should have digits 1-9 in each row."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        for row in board:
            assert sorted(row) == list(range(1, 10))

    def test_fill_board_has_all_digits_in_each_column(self):
        """Filled board should have digits 1-9 in each column."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        for col in range(9):
            column = [board[row][col] for row in range(9)]
            assert sorted(column) == list(range(1, 10))

    def test_fill_board_has_all_digits_in_each_3x3_box(self):
        """Filled board should have digits 1-9 in each 3x3 box."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        for box_row in range(3):
            for box_col in range(3):
                box = []
                for i in range(3):
                    for j in range(3):
                        box.append(board[box_row * 3 + i][box_col * 3 + j])
                assert sorted(box) == list(range(1, 10))


class TestRemoveCells:
    """Tests for puzzle generation (removing cells)."""

    def test_remove_cells_reduces_clues(self):
        """Removing cells should reduce number of clues."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        initial_clues = sum(1 for i in range(9) for j in range(9) if board[i][j] != 0)
        assert initial_clues == 81  # Completely filled
        
        sudoku_logic.remove_cells(board, 35)
        remaining_clues = sum(1 for i in range(9) for j in range(9) if board[i][j] != 0)
        assert remaining_clues == 35

    def test_remove_cells_target_accuracy(self):
        """Removing cells should hit target clue count."""
        for target_clues in [20, 30, 35, 45]:
            board = sudoku_logic.create_empty_board()
            sudoku_logic.fill_board(board)
            sudoku_logic.remove_cells(board, target_clues)
            actual_clues = sum(1 for i in range(9) for j in range(9) if board[i][j] != 0)
            assert actual_clues == target_clues


class TestGeneratePuzzle:
    """Tests for main puzzle generation function."""

    def test_generate_puzzle_returns_tuple(self):
        """generate_puzzle should return (puzzle, solution) tuple."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        assert isinstance(puzzle, list)
        assert isinstance(solution, list)

    def test_generate_puzzle_default_clues(self):
        """Default puzzle should have 35 clues."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        puzzle_clues = sum(1 for i in range(9) for j in range(9) if puzzle[i][j] != 0)
        assert puzzle_clues == 35

    def test_generate_puzzle_default_path_has_unique_solution(self):
        """The default generation path should also preserve a unique solution."""
        puzzle, _ = sudoku_logic.generate_puzzle()
        assert count_solutions(puzzle) == 1

    def test_generate_puzzle_custom_clues(self):
        """Custom clue count should be respected."""
        for clues in [20, 30, 40, 50]:
            puzzle, solution = sudoku_logic.generate_puzzle(clues)
            actual_clues = sum(1 for i in range(9) for j in range(9) if puzzle[i][j] != 0)
            assert actual_clues == clues

    @pytest.mark.parametrize(
        'difficulty, expected_clues',
        [('easy', 45), ('medium', 35), ('hard', 25)],
    )
    def test_generate_puzzle_difficulty_levels(self, difficulty, expected_clues):
        """Each difficulty should target a different clue count."""
        puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)
        actual_clues = sum(1 for i in range(9) for j in range(9) if puzzle[i][j] != 0)
        assert actual_clues == expected_clues

    @pytest.mark.parametrize('difficulty', ['easy', 'medium', 'hard'])
    def test_generate_puzzle_has_unique_solution(self, difficulty):
        """Every generated puzzle should have exactly one valid solution."""
        puzzle, _ = sudoku_logic.generate_puzzle(difficulty=difficulty)
        assert count_solutions(puzzle) == 1

    def test_generate_puzzle_solution_is_complete(self):
        """Solution should have all 81 cells filled."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        solution_clues = sum(1 for i in range(9) for j in range(9) if solution[i][j] != 0)
        assert solution_clues == 81

    def test_generate_puzzle_puzzle_is_subset_of_solution(self):
        """Puzzle clues should match solution at those positions."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    assert puzzle[i][j] == solution[i][j]

    def test_generate_puzzle_solution_is_valid(self):
        """Solution should be a valid Sudoku board."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        # Check each row has 1-9
        for row in solution:
            assert sorted(row) == list(range(1, 10))
        # Check each column has 1-9
        for col in range(9):
            column = [solution[row][col] for row in range(9)]
            assert sorted(column) == list(range(1, 10))
        # Check each 3x3 box has 1-9
        for box_row in range(3):
            for box_col in range(3):
                box = []
                for i in range(3):
                    for j in range(3):
                        box.append(solution[box_row * 3 + i][box_col * 3 + j])
                assert sorted(box) == list(range(1, 10))

    def test_generate_puzzle_independence(self):
        """Multiple puzzle generations should be independent."""
        puzzle1, sol1 = sudoku_logic.generate_puzzle(35)
        puzzle2, sol2 = sudoku_logic.generate_puzzle(35)
        # Puzzles should be different (extremely unlikely to be the same)
        assert puzzle1 != puzzle2
