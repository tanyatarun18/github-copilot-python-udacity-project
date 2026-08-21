# Copilot Instructions for the Flask Sudoku Project

## Project overview
- This repository contains a Flask-based Sudoku web app with puzzle generation, validation, hints, a timer, difficulty levels, and a browser-based leaderboard.
- The app is organized as a small Flask application with a simple blueprint-based structure and a focused Sudoku logic module.

## Architecture
- Keep the backend modular: route handlers should stay thin, while puzzle generation and validation logic live under the Sudoku package.
- Preserve the current flow of data:
  1. The app creates or loads a puzzle.
  2. The puzzle and solved board are stored as the active game state.
  3. The UI calls the Flask endpoints for checking progress and requesting hints.
- Avoid introducing heavy frameworks or large architectural rewrites unless explicitly requested.

## Folder responsibilities
- starter/app.py: Flask app entry point and app initialization.
- starter/sudoku_app/routes.py: Flask endpoints such as the home page, new game creation, checking the board, and hint generation.
- starter/sudoku_app/sudoku/: core Sudoku logic, including generation, validation, and solving behavior.
- starter/static/: frontend JavaScript and CSS.
- starter/templates/index.html: the main HTML shell for the app UI.
- starter/test_*.py and starter/conftest.py: pytest coverage for game logic and Flask routes.

## Coding style
- Prefer clear, readable Python and JavaScript over clever abstractions.
- Keep functions small and focused; add short docstrings for public or non-obvious behavior.
- Preserve existing naming patterns and existing app behavior unless the task explicitly changes a feature.
- Favor incremental changes over large refactors.
- Before any major refactor, explain the change, the reason for it, and the expected impact.

## Sudoku gameplay rules
- Every generated puzzle must remain uniquely solvable.
- Puzzle generation must preserve the uniqueness rule by ensuring the puzzle still has exactly one valid solution after removing clues.
- Do not weaken the uniqueness constraint when changing puzzle generation logic.
- Difficulty levels should remain consistent with the current clue-count mapping:
  - Easy: 45 clues
  - Medium: 35 clues
  - Hard: 25 clues

## UI and experience requirements
- The UI should remain responsive, accessible, and polished.
- Dark mode must be supported through a theme toggle and persisted in browser storage.
- The board should preserve the current visual structure, including the alternating 3x3 block styling with stronger borders between every third row and column.
- Keep the leaderboard behavior intact and consistent with the existing UI.

## Leaderboard expectations
- The leaderboard should continue to store the top 10 completed runs in browser storage.
- Each entry should include these fields when relevant:
  - playerName
  - completionTime
  - difficulty
  - hintsUsed
  - clueCount
  - completedAt
  - status
- Preserve the current sorting behavior so faster completion times appear first.

## Testing expectations
- When changing game logic, routes, or UI behavior, add or update tests where appropriate.
- Keep the existing pytest suite passing unless a change intentionally alters required behavior.
- Prefer regression tests for bug fixes and feature additions.
- Do not change tests just to mask a bug; fix the underlying behavior.

## Change guidance for Copilot
- Explain the intended change before major refactors, especially when touching puzzle generation, route behavior, or UI structure.
- Summarize the expected impact on gameplay, tests, and user experience.
- Keep changes aligned with the current project scope and avoid unnecessary dependencies.
