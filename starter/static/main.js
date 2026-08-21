// Client-side rendering and interaction for the Flask-backed Sudoku

const SIZE = 9;

let puzzle = [];
let initialPuzzle = [];
let validationTimeoutId = null;

let timerIntervalId = null;
let elapsedSeconds = 0;

let currentDifficulty = 'medium';
let currentDifficultyLabel = 'Medium';
let currentClueCount = 0;

let hintCount = 0;

// Store ALL hinted cells for the current game.
// A Set lets us remember previous hints so they remain locked
// after the board is rendered again.
const hintedCells = new Set();

const LEADERBOARD_STORAGE_KEY = 'sudoku-leaderboard';
const THEME_STORAGE_KEY = 'sudoku-theme';


function cellKey(row, col) {
  return `${row}:${col}`;
}


function formatTime(seconds) {
  const mins = Math.floor(seconds / 60)
    .toString()
    .padStart(2, '0');

  const secs = (seconds % 60)
    .toString()
    .padStart(2, '0');

  return `${mins}:${secs}`;
}


function updateTimerDisplay() {
  const el = document.getElementById('timer');

  if (el) {
    el.innerText = `Time: ${formatTime(elapsedSeconds)}`;
  }
}


function formatDifficulty(value) {
  if (!value) {
    return 'Unknown';
  }

  return value.charAt(0).toUpperCase() + value.slice(1);
}


// -------------------------
// Leaderboard
// -------------------------

function readLeaderboardEntries() {
  try {
    const raw = window.localStorage.getItem(
      LEADERBOARD_STORAGE_KEY
    );

    return raw ? JSON.parse(raw) : [];
  } catch (error) {
    console.warn(
      'Unable to read leaderboard',
      error
    );

    return [];
  }
}


function writeLeaderboardEntries(entries) {
  try {
    window.localStorage.setItem(
      LEADERBOARD_STORAGE_KEY,
      JSON.stringify(entries)
    );
  } catch (error) {
    console.warn(
      'Unable to write leaderboard',
      error
    );
  }
}


function applyTheme(theme) {
  document.body.dataset.theme = theme;

  const toggle = document.getElementById(
    'theme-toggle'
  );

  if (toggle) {
    const isDark = theme === 'dark';

    toggle.setAttribute(
      'aria-pressed',
      String(isDark)
    );

    toggle.innerHTML = `
      <span aria-hidden="true">
        ${isDark ? '☀️' : '🌙'}
      </span>
      <span>
        ${isDark ? 'Light mode' : 'Dark mode'}
      </span>
    `;
  }
}


function initializeTheme() {
  const storedTheme = window.localStorage.getItem(
    THEME_STORAGE_KEY
  );

  const theme =
    storedTheme === 'dark'
      ? 'dark'
      : 'light';

  applyTheme(theme);
}


function toggleTheme() {
  const nextTheme =
    document.body.dataset.theme === 'dark'
      ? 'light'
      : 'dark';

  window.localStorage.setItem(
    THEME_STORAGE_KEY,
    nextTheme
  );

  applyTheme(nextTheme);
}


function renderLeaderboard() {
  const tableBody = document.getElementById(
    'leaderboard-list'
  );

  if (!tableBody) {
    return;
  }

  const entries = readLeaderboardEntries()
    .slice()
    .sort(
      (a, b) =>
        a.completionTime - b.completionTime ||
        new Date(a.completedAt) -
          new Date(b.completedAt)
    )
    .slice(0, 10);

  if (entries.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="8">
          No completed runs yet.
        </td>
      </tr>
    `;

    return;
  }

  tableBody.innerHTML = entries
    .map((entry, index) => {
      const completedAt = new Date(
        entry.completedAt
      );

      const completedLabel =
        completedAt.toLocaleDateString(
          undefined,
          {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
          }
        );

      return `
        <tr>
          <td>${index + 1}</td>
          <td>
            ${entry.playerName || 'Anonymous'}
          </td>
          <td>
            ${formatDifficulty(entry.difficulty)}
          </td>
          <td>
            ${formatTime(entry.completionTime)}
          </td>
          <td>
            ${entry.hintsUsed ?? 0}
          </td>
          <td>
            ${entry.clueCount ?? 0}
          </td>
          <td>
            ${completedLabel}
          </td>
          <td>
            ${entry.status || 'Completed'}
          </td>
        </tr>
      `;
    })
    .join('');
}


function saveLeaderboardEntry(
  playerName,
  completionTime,
  difficulty,
  hintsUsed,
  clueCount
) {
  const entries = readLeaderboardEntries();

  const record = {
    playerName:
      playerName.trim() || 'Anonymous',
    completionTime,
    difficulty,
    hintsUsed,
    clueCount,
    completedAt: new Date().toISOString(),
    status: 'Completed'
  };

  entries.push(record);

  const topEntries = entries
    .sort(
      (a, b) =>
        a.completionTime - b.completionTime ||
        new Date(a.completedAt) -
          new Date(b.completedAt)
    )
    .slice(0, 10);

  writeLeaderboardEntries(topEntries);

  renderLeaderboard();
}


function handleGameSolved() {
  stopTimer();

  const playerName = window.prompt(
    'Enter your name for the leaderboard:',
    'Anonymous'
  );

  saveLeaderboardEntry(
    playerName || 'Anonymous',
    elapsedSeconds,
    currentDifficulty,
    hintCount,
    currentClueCount
  );
}


// -------------------------
// Timer
// -------------------------

function startTimer() {
  stopTimer();

  timerIntervalId = window.setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}


function stopTimer() {
  if (timerIntervalId) {
    window.clearInterval(
      timerIntervalId
    );

    timerIntervalId = null;
  }
}


function resetTimer() {
  stopTimer();

  elapsedSeconds = 0;

  updateTimerDisplay();
}


// -------------------------
// Board helpers
// -------------------------

function getBoardState() {
  const boardDiv =
    document.getElementById('sudoku-board');

  const inputs =
    boardDiv.getElementsByTagName('input');

  const board = [];

  for (let i = 0; i < SIZE; i++) {
    board[i] = [];

    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;

      const val = inputs[idx].value;

      board[i][j] = val
        ? parseInt(val, 10)
        : 0;
    }
  }

  return {
    board,
    inputs
  };
}


// -------------------------
// Validation
// -------------------------

function applyValidationResult(
  inputs,
  incorrect
) {
  const incorrectSet = new Set(
    incorrect.map(
      (cell) =>
        cell[0] * SIZE + cell[1]
    )
  );

  for (
    let idx = 0;
    idx < inputs.length;
    idx++
  ) {
    const inp = inputs[idx];

    // Do not mark locked cells as incorrect.
    if (inp.disabled) {
      continue;
    }

    if (incorrectSet.has(idx)) {
      inp.classList.add('incorrect');
    } else {
      inp.classList.remove('incorrect');
    }
  }
}


function updateValidationMessage(data) {
  const msg =
    document.getElementById('message');

  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;

    return;
  }

  const incorrect =
    data.incorrect || [];

  if (data.solved) {
    msg.style.color = '#388e3c';

    msg.innerText =
      `Congratulations! You solved it in ` +
      `${formatTime(elapsedSeconds)} ` +
      `(${currentDifficultyLabel}).`;

  } else if (incorrect.length === 0) {
    msg.style.color = '#388e3c';

    msg.innerText =
      'Board looks correct so far.';

  } else {
    msg.style.color = '#d32f2f';

    msg.innerText =
      'Some cells are incorrect.';
  }
}


async function validateBoard() {
  try {
    const { board, inputs } =
      getBoardState();

    const res = await fetch(
      '/check',
      {
        method: 'POST',

        headers: {
          'Content-Type':
            'application/json'
        },

        body: JSON.stringify({
          board
        })
      }
    );

    const data =
      await res.json();

    if (data.error) {
      updateValidationMessage(data);

      return;
    }

    applyValidationResult(
      inputs,
      data.incorrect || []
    );

    updateValidationMessage(data);

    if (data.solved) {
      handleGameSolved();
    }

  } catch (error) {
    console.error(
      'Validation failed:',
      error
    );
  }
}


function scheduleValidation() {
  if (validationTimeoutId) {
    window.clearTimeout(
      validationTimeoutId
    );
  }

  validationTimeoutId =
    window.setTimeout(() => {
      void validateBoard();
    }, 180);
}


// -------------------------
// Board rendering
// -------------------------

function createBoardElement() {
  const boardDiv =
    document.getElementById(
      'sudoku-board'
    );

  boardDiv.innerHTML = '';

  for (let i = 0; i < SIZE; i++) {
    const rowDiv =
      document.createElement('div');

    rowDiv.className =
      'sudoku-row';

    for (let j = 0; j < SIZE; j++) {
      const input =
        document.createElement('input');

      input.type = 'text';

      input.maxLength = 1;

      const regionClass =
        (
          (
            Math.floor(i / 3) +
            Math.floor(j / 3)
          ) %
          2
        ) === 0
          ? 'region-light'
          : 'region-dark';

      input.className =
        `sudoku-cell ${regionClass}`;

      input.dataset.row = i;

      input.dataset.col = j;

      input.addEventListener(
        'input',
        (event) => {
          const val =
            event.target.value
              .replace(/[^1-9]/g, '')
              .slice(0, 1);

          event.target.value = val;

          scheduleValidation();
        }
      );

      rowDiv.appendChild(input);
    }

    boardDiv.appendChild(rowDiv);
  }
}


function renderBoard(board) {
  puzzle = board;

  createBoardElement();

  const boardDiv =
    document.getElementById(
      'sudoku-board'
    );

  const inputs =
    boardDiv.getElementsByTagName(
      'input'
    );

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx =
        i * SIZE + j;

      const val =
        board[i][j];

      const inp =
        inputs[idx];

      const regionClass =
        (
          (
            Math.floor(i / 3) +
            Math.floor(j / 3)
          ) %
          2
        ) === 0
          ? 'region-light'
          : 'region-dark';

      const isPrefilled =
        initialPuzzle[i] &&
        initialPuzzle[i][j] !== 0;

      // Check whether this cell was hinted
      // at any point during the current game.
      const isHinted =
        hintedCells.has(
          cellKey(i, j)
        );

      if (isPrefilled || isHinted) {
        inp.value = val;

        inp.disabled = true;

        inp.readOnly = true;

        if (isHinted) {
          inp.className =
            `sudoku-cell ${regionClass} hint`;
        } else {
          inp.className =
            `sudoku-cell ${regionClass} prefilled`;
        }

      } else if (val !== 0) {
        inp.value = val;

        inp.disabled = false;

        inp.readOnly = false;

        inp.className =
          `sudoku-cell ${regionClass}`;

      } else {
        inp.value = '';

        inp.disabled = false;

        inp.readOnly = false;

        inp.className =
          `sudoku-cell ${regionClass}`;
      }
    }
  }
}


function renderPuzzle(puz) {
  renderBoard(puz);
}


// -------------------------
// New game
// -------------------------

async function newGame() {
  try {
    const difficultySelector =
      document.getElementById(
        'difficulty-selector'
      );

    const difficulty =
      difficultySelector.value;

    // Reset hint information for the new game.
    hintCount = 0;

    hintedCells.clear();

    const res = await fetch(
      `/new?difficulty=${encodeURIComponent(
        difficulty
      )}`
    );

    const data =
      await res.json();

    if (data.error) {
      document.getElementById(
        'message'
      ).innerText = data.error;

      return;
    }

    initialPuzzle =
      data.puzzle.map(
        (row) => row.slice()
      );

    currentDifficulty =
      difficulty;

    currentDifficultyLabel =
      difficulty.charAt(0)
        .toUpperCase() +
      difficulty.slice(1);

    currentClueCount =
      data.clues ||
      data.puzzle
        .flat()
        .filter(
          (cell) => cell !== 0
        ).length;

    renderPuzzle(data.puzzle);

    document.getElementById(
      'game-meta'
    ).innerText =
      `${currentDifficultyLabel} • ` +
      `${currentClueCount} clues`;

    document.getElementById(
      'message'
    ).innerText = '';

    resetTimer();

    startTimer();

  } catch (error) {
    console.error(
      'Unable to start new game:',
      error
    );

    document.getElementById(
      'message'
    ).innerText =
      'Unable to start a new game.';
  }
}


// -------------------------
// Check button
// -------------------------

async function checkSolution() {
  try {
    const { board, inputs } =
      getBoardState();

    const res = await fetch(
      '/check',
      {
        method: 'POST',

        headers: {
          'Content-Type':
            'application/json'
        },

        body: JSON.stringify({
          board
        })
      }
    );

    const data =
      await res.json();

    if (data.error) {
      updateValidationMessage(data);

      return;
    }

    applyValidationResult(
      inputs,
      data.incorrect || []
    );

    updateValidationMessage(data);

    if (data.solved) {
      handleGameSolved();
    }

  } catch (error) {
    console.error(
      'Check failed:',
      error
    );

    document.getElementById(
      'message'
    ).innerText =
      'Unable to check the board.';
  }
}


// -------------------------
// Hint button
// -------------------------

async function useHint() {
  try {
    const { board } =
      getBoardState();

    const res = await fetch(
      '/hint',
      {
        method: 'POST',

        headers: {
          'Content-Type':
            'application/json'
        },

        body: JSON.stringify({
          board
        })
      }
    );

    const data =
      await res.json();

    if (data.error) {
      document.getElementById(
        'message'
      ).innerText =
        data.error;

      return;
    }

    // Remember this hint permanently
    // for the current game.
    if (data.hint) {
      hintedCells.add(
        cellKey(
          data.hint.row,
          data.hint.col
        )
      );
    }

    hintCount += 1;

    // Render the updated board.
    // renderBoard() checks the hintedCells Set,
    // so ALL previous hints remain locked.
    renderBoard(data.board);

    document.getElementById(
      'message'
    ).innerText =
      'Hint added.';

  } catch (error) {
    console.error(
      'Hint failed:',
      error
    );

    document.getElementById(
      'message'
    ).innerText =
      'Unable to get a hint.';
  }
}


// -------------------------
// Wire buttons
// -------------------------

window.addEventListener(
  'load',
  () => {
    document
      .getElementById('new-game')
      .addEventListener(
        'click',
        newGame
      );

    document
      .getElementById('hint')
      .addEventListener(
        'click',
        useHint
      );

    document
      .getElementById('check-solution')
      .addEventListener(
        'click',
        checkSolution
      );

    const themeToggle =
      document.getElementById(
        'theme-toggle'
      );

    if (themeToggle) {
      themeToggle.addEventListener(
        'click',
        toggleTheme
      );
    }

    initializeTheme();

    renderLeaderboard();

    newGame();
  }
);