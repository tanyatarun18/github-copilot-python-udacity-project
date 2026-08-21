# Sudoku Flask — Refactor & Feature Project

This repository contains a simple Sudoku web app built with Flask. The starter project is intended for practicing refactoring, adding features, and improving user experience using GitHub Copilot.

## Project Overview

- **App:** Web-based Sudoku game with puzzle generation, validation, hints, timer, and difficulty levels.
- **Backend:** Flask app in the `starter` folder that serves the UI and puzzle logic.
- **Frontend:** Static assets and templates under `starter/static` and `starter/templates`.
- **Tests:** Unit tests located in the `starter` folder use `pytest`.

## Features

- Generate valid Sudoku puzzles with a unique solution.
- Difficulty selector (Easy / Medium / Hard).
- Timer to track solve time.
- Hints and step-by-step assistance.
- Real-time input validation and puzzle checking.
- Save Top 10 scores in Local Storage with player name, time, hints used, and difficulty.
- Responsive UI for desktop and mobile.

## Setup

Prerequisites:

- Python 3.8+ installed
- A modern web browser (Chrome, Firefox, Edge)

Install and run locally:

```bash
# from repository root
cd starter
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open the app at http://127.0.0.1:5000

Notes:

- The main Flask app is `starter/app.py`.
- Puzzle generation and logic live under `starter/sudoku_app/sudoku` (see `generator.py`, `logic.py`, `validation.py`).

## Testing

Run the test suite with `pytest` from the `starter` directory:

```bash
cd starter
pytest -q
```

You can run specific tests or markers, for example:

```bash
pytest -q test_sudoku_logic.py::test_generate_puzzle
pytest -q -k "unique_solution"
```

If tests fail locally, run them again and inspect failing traces in the test output.

## Submission: Required Screenshots

When preparing the project for submission, include the following screenshots in the `screenshots/` directory (PNG or JPG):

- `home_page.png` — The app home page with the board visible and controls (difficulty, new puzzle, timer).
- `playing_board.png` — A partially filled board showing input validation (invalid cell highlighted).
- `hint_shown.png` — A screenshot showing a hint revealed on the board.
- `puzzle_solved.png` — The congratulatory message after solving a puzzle (time and hints used visible).
- `top10_scores.png` — The Top 10 scores UI displayed with at least one saved score.

Include these in your submission ZIP or GitHub repo so reviewers can quickly verify UI features.

## Submission Checklist

- [ ] All tests pass (`pytest -q`).
- [ ] Required screenshots are in the `screenshots/` folder.
- [ ] README updated with setup and testing instructions (this file).
- [ ] UI is responsive and accessible.

## Where to look in the code

- Flask entry: `starter/app.py`
- Frontend assets: `starter/static/` and `starter/templates/index.html`
- Sudoku logic & generator: `starter/sudoku_app/sudoku/`
- Tests: `starter/test_sudoku_logic.py`, `starter/test_app.py`

If you want, I can also run the test suite and attach the failing output or fix small issues. Would you like me to run `pytest` now?
