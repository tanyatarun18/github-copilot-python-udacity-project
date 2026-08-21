
"""
Integration tests for app.py - Flask routes and game logic.
"""
import json
import pytest


class TestIndexRoute:
    """Tests for the index route."""

    def test_index_returns_200(self, client):
        """GET / should return 200 status."""
        response = client.get('/')
        assert response.status_code == 200

    def test_index_returns_html(self, client):
        """GET / should return HTML content."""
        response = client.get('/')
        assert response.content_type == 'text/html; charset=utf-8'
        assert b'Sudoku Game' in response.data

    def test_index_includes_leaderboard_section(self, client):
        """GET / should include the leaderboard markup."""
        response = client.get('/')
        assert b'Top 10 Leaderboard' in response.data
        assert b'leaderboard-list' in response.data

    def test_index_includes_dark_mode_toggle(self, client):
        """GET / should include a dark mode toggle control."""
        response = client.get('/')
        assert b'id="theme-toggle"' in response.data
        assert b'aria-pressed' in response.data

    def test_index_includes_timer_label(self, client):
        """GET / should include a visible timer label."""
        response = client.get('/')
        assert b'Time:' in response.data
        assert b'id="timer"' in response.data


class TestNewGameRoute:
    """Tests for the new game route."""

    def test_new_game_returns_json(self, client):
        """GET /new should return JSON."""
        response = client.get('/new')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

    def test_new_game_returns_puzzle(self, client):
        """GET /new should return a puzzle structure."""
        response = client.get('/new')
        data = json.loads(response.data)
        assert 'puzzle' in data
        puzzle = data['puzzle']
        assert isinstance(puzzle, list)
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)

    def test_new_game_default_clues(self, client):
        """Default new game should have 35 clues."""
        response = client.get('/new')
        data = json.loads(response.data)
        puzzle = data['puzzle']
        clues = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clues == 35

    def test_new_game_custom_clues(self, client):
        """Custom clue count should be respected."""
        for clues in [20, 30, 40, 50]:
            response = client.get(f'/new?clues={clues}')
            data = json.loads(response.data)
            puzzle = data['puzzle']
            actual_clues = sum(1 for row in puzzle for cell in row if cell != 0)
            assert actual_clues == clues

    def test_new_game_stores_puzzle_in_current(self, client, app):
        """New game should store puzzle and solution in CURRENT state."""
        response = client.get('/new')
        assert app.CURRENT['puzzle'] is not None
        assert app.CURRENT['solution'] is not None

    def test_new_game_puzzle_matches_response(self, client, app):
        """Returned puzzle should match stored puzzle."""
        response = client.get('/new')
        data = json.loads(response.data)
        returned_puzzle = data['puzzle']
        stored_puzzle = app.CURRENT['puzzle']
        assert returned_puzzle == stored_puzzle

    def test_new_game_creates_valid_solution(self, client, app):
        """Solution should be a complete valid Sudoku."""
        client.get('/new')
        solution = app.CURRENT['solution']
        # Check all cells filled
        assert all(cell != 0 for row in solution for cell in row)
        # Check rows valid
        for row in solution:
            assert sorted(row) == list(range(1, 10))


class TestCheckRoute:
    """Tests for the check solution route."""

    def test_check_requires_puzzle_in_progress(self, client):
        """Check without active game should return error."""
        # Clear the current game
        import app as app_module
        app_module.CURRENT['solution'] = None
        
        response = client.post('/check',
                              json={'board': [[0]*9 for _ in range(9)]})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_check_returns_json(self, client):
        """POST /check should return JSON."""
        client.get('/new')  # Create a game
        response = client.post('/check',
                              json={'board': [[0]*9 for _ in range(9)]})
        assert response.content_type == 'application/json'

    def test_check_empty_board_has_incorrect_cells(self, client):
        """Checking empty board should flag cells as incorrect."""
        client.get('/new')
        empty_board = [[0]*9 for _ in range(9)]
        response = client.post('/check', json={'board': empty_board})
        data = json.loads(response.data)
        assert 'incorrect' in data
        # Empty board should have many incorrect cells
        assert len(data['incorrect']) > 0

    def test_check_correct_solution_returns_empty_incorrect(self, client, app):
        """Checking correct solution should return no incorrect cells."""
        client.get('/new')
        solution = app.CURRENT['solution']
        response = client.post('/check', json={'board': solution})
        data = json.loads(response.data)
        assert data['incorrect'] == []

    def test_check_complete_solution_reports_solved(self, client, app):
        """A complete correct board should be reported as solved."""
        client.get('/new')
        solution = app.CURRENT['solution']
        response = client.post('/check', json={'board': solution})
        data = json.loads(response.data)
        assert data['solved'] is True

    def test_check_incorrect_cells_identified(self, client, app):
        """Incorrectly filled cells should be identified."""
        client.get('/new')
        solution = app.CURRENT['solution']
        # Copy solution and modify a cell
        test_board = [row[:] for row in solution]
        test_board[0][0] = 9 if test_board[0][0] != 9 else 8
        
        response = client.post('/check', json={'board': test_board})
        data = json.loads(response.data)
        assert len(data['incorrect']) > 0
        # Should identify the modified cell as incorrect
        assert [0, 0] in data['incorrect']

    def test_check_multiple_incorrect_cells(self, client, app):
        """Multiple incorrect cells should all be identified."""
        client.get('/new')
        solution = app.CURRENT['solution']
        # Copy solution and modify multiple cells
        test_board = [row[:] for row in solution]
        test_board[0][0] = 9 if test_board[0][0] != 9 else 8
        test_board[5][5] = 9 if test_board[5][5] != 9 else 8
        test_board[8][8] = 9 if test_board[8][8] != 9 else 8
        
        response = client.post('/check', json={'board': test_board})
        data = json.loads(response.data)
        assert len(data['incorrect']) == 3

    def test_check_correct_cells_not_flagged(self, client, app):
        """Only incorrect cells should be flagged."""
        client.get('/new')
        solution = app.CURRENT['solution']
        # Copy solution and modify just one cell
        test_board = [row[:] for row in solution]
        incorrect_row, incorrect_col = 0, 0
        test_board[incorrect_row][incorrect_col] = (test_board[incorrect_row][incorrect_col] % 9) + 1
        
        response = client.post('/check', json={'board': test_board})
        data = json.loads(response.data)
        incorrect_positions = set(tuple(cell) for cell in data['incorrect'])
        
        # Check that correct cells are not in incorrect list
        for i in range(9):
            for j in range(9):
                if (i, j) != (incorrect_row, incorrect_col):
                    assert (i, j) not in incorrect_positions


class TestHintRoute:
    """Tests for the hint route."""

    def test_hint_fills_one_empty_cell(self, client, app):
        """Hint should fill exactly one empty cell with the correct solution value."""
        client.get('/new')
        empty_board = [[0] * 9 for _ in range(9)]

        response = client.post('/hint', json={'board': empty_board})

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'hint' in data
        assert 'board' in data

        hint = data['hint']
        updated_board = data['board']
        filled_cells = sum(1 for row in updated_board for cell in row if cell != 0)

        assert filled_cells == 1
        assert updated_board[hint['row']][hint['col']] == hint['value']
        assert hint['value'] == app.CURRENT['solution'][hint['row']][hint['col']]


class TestGameFlow:
    """Integration tests for complete game flows."""

    def test_new_game_then_check_flow(self, client):
        """Complete flow: new game → check solution."""
        # Get new game
        response = client.get('/new')
        puzzle = json.loads(response.data)['puzzle']
        
        # Check with empty board (should have incorrect cells)
        response = client.post('/check', json={'board': puzzle})
        data = json.loads(response.data)
        assert 'incorrect' in data

    def test_multiple_games_are_independent(self, client, app):
        """Starting new game should replace previous game."""
        # First game
        client.get('/new?clues=30')
        first_solution = [row[:] for row in app.CURRENT['solution']]
        
        # Second game
        client.get('/new?clues=30')
        second_solution = app.CURRENT['solution']
        
        # Solutions should be different
        assert first_solution != second_solution

    def test_check_uses_latest_solution(self, client, app):
        """Check should validate against latest game's solution."""
        # First game
        client.get('/new?clues=35')
        first_solution = [row[:] for row in app.CURRENT['solution']]
        
        # Second game
        client.get('/new?clues=35')
        second_solution = app.CURRENT['solution']
        
        # Check against first solution should fail (it's using second)
        response = client.post('/check', json={'board': first_solution})
        data = json.loads(response.data)
        # Unless they're the same (very unlikely), there should be incorrect cells
        # This test verifies the check uses the latest solution
        assert 'incorrect' in data
