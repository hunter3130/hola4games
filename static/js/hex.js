document.addEventListener("DOMContentLoaded", () => {
  // العناصر الأساسية
  const modal = document.getElementById("questionModal");
  const modalLetter = document.getElementById("modal-letter");
  const modalImage = document.getElementById("modal-image");
  const modalQuestion = document.getElementById("modal-question");
  const closeBtn = document.querySelector(".close");
  const timerDisplay = document.getElementById("timer-value");
  const timerContainer = document.getElementById("timer");
  const startTimerBtn = document.getElementById("start-timer");

  // عناصر البازر
  const buzzerResult = document.getElementById("buzzerResult");
  const resetBuzzerBtn = document.getElementById("resetBuzzer");
  const startQuestionBtn = document.getElementById("startQuestion");

  const socket = io();

  // متغيرات اللعبة
  let currentCell = null;
  let timerInterval = null;
  let timeLeft = 5;
  let timerStarted = false;
  const questions = {};
  const boardSize = 5;
  let boardState = Array.from({ length: boardSize }, () =>
    Array(boardSize).fill(null)
  );

  const timeoutSound = new Audio("/static/sounds/timeout.mp3");

  const buzzerButton = document.getElementById("buzzer-button");

  // ========== دوال التحكم الأساسية ==========

  function startTimer() {
    if (timerStarted) return;
    timerStarted = true;
    timeLeft = 5;
    timerDisplay.textContent = timeLeft;
    timerContainer.style.display = "block";
    startTimerBtn.style.display = "none";

    timerInterval = setInterval(() => {
      timeLeft--;
      timerDisplay.textContent = timeLeft;
      if (timeLeft <= 0) {
        clearInterval(timerInterval);
        timeoutSound.play();

        buzzerResult.textContent = "انتهى الوقت، لا يمكن اختيار الفريق الآن.";
        document.getElementById("team1").disabled = true;
        document.getElementById("team2").disabled = true;
      }
    }, 1000);
  }

  function stopTimer() {
    clearInterval(timerInterval);
    timerStarted = false;
    timerContainer.style.display = "none";
    startTimerBtn.style.display = "block";
  }

  function lockAllCells() {
    document.querySelectorAll(".hex").forEach(cell => {
      cell.classList.add("locked");
    });
  }

  // ------ التأكد من الخلايا المختارة------
  socket.emit("get_cells");

  socket.on("cell_states", function(states) {
    for (const cellId in states) {
      const cell = document.querySelector(`[data-cell="${cellId}"]`);
      if (cell) {
        cell.style.backgroundColor = states[cellId].color;
        cell.dataset.team = states[cellId].team;
      }
    }
  });

  function chooseCell(cell) {
    const cellId = cell.dataset.cell;
    const currentTeam = cell.dataset.team || ""; // تعديل: تعريف المتغير الحالي
    const team = currentTeam;
    const color = team === "red" ? "#f00" : "#00f";

    cell.style.backgroundColor = color;
    cell.dataset.team = team;

    socket.emit("update_cell", {
      cellId: cellId,
      state: {
        team: team,
        color: color
      }
    });
  }

  socket.on("cell_updated", function(data) {
    const cell = document.querySelector(`[data-cell="${data.cellId}"]`);
    if (cell) {
      cell.style.backgroundColor = data.state.color;
      cell.dataset.team = data.state.team;
    }
  });

  function showWinnerMessage(teamName) {
    if (document.getElementById("winnerMessage")) return;
    const winnerDiv = document.createElement("div");
    winnerDiv.id = "winnerMessage";
    winnerDiv.classList.add("winner-message");
    winnerDiv.textContent = `الفريق ${teamName} فاز! 🎉`;

    document.body.appendChild(winnerDiv);

    setTimeout(() => {
      if (winnerDiv.parentNode) {
        winnerDiv.parentNode.removeChild(winnerDiv);
      }
    }, 5000);

    lockAllCells();
  }

  function checkWin(teamColor) {
    const visited = Array.from({ length: boardSize }, () =>
      Array(boardSize).fill(false)
    );

    function dfs(row, col) {
      if (
        row < 0 || row >= boardSize ||
        col < 0 || col >= boardSize ||
        visited[row][col] ||
        boardState[row][col] !== teamColor
      ) {
        return false;
      }

      visited[row][col] = true;
      console.log(`زيارتنا للخلية [${row},${col}] للفريق ${teamColor}`);

      if (teamColor === "red" && col === boardSize - 1) {
        console.log("وصل الفريق الأحمر للعمود الأخير!");
        return true;
      }
      if (teamColor === "blue" && row === boardSize - 1) {
        console.log("وصل الفريق الأزرق للصف الأخير!");
        return true;
      }

      const directions = (row % 2 === 0) ?
        [
          [-1, 0], [-1, 1],
          [0, -1], [0, 1],
          [1, 0], [1, 1]
        ] :
        [
          [-1, -1], [-1, 0],
          [0, -1], [0, 1],
          [1, -1], [1, 0]
        ];

      for (const [dr, dc] of directions) {
        if (dfs(row + dr, col + dc)) {
          return true;
        }
      }
      return false;
    }

    if (teamColor === "red") {
      for (let row = 0; row < boardSize; row++) {
        if (boardState[row][0] === "red" && dfs(row, 0)) {
          showWinnerMessage("الأحمر");
          return true;
        }
      }
    } else {
      for (let col = 0; col < boardSize; col++) {
        if (boardState[0][col] === "blue" && dfs(0, col)) {
          showWinnerMessage("الأزرق");
          return true;
        }
      }
    }
    return false;
  }

  function debugBoard() {
    console.log("حالة اللوحة الحالية:");
    for (let row = 0; row < boardSize; row++) {
      console.log(row + ": " + boardState[row].map(c => c ? c[0] : '.').join(' '));
    }
  }

  function enableTeamButtons() {
    document.getElementById("team1").disabled = false;
    document.getElementById("team2").disabled = false;
  }

  function resetModal() {
    buzzerResult.textContent = "";
    enableTeamButtons();
    startTimerBtn.style.display = "block";
    timerContainer.style.display = "none";
  }

  document.querySelectorAll(".hex").forEach(cell => {
    cell.addEventListener("click", () => {
      if (cell.classList.contains("locked")) return;
      currentCell = cell;
      const letter = cell.getAttribute("data-letter");
      console.log("تم الضغط على خلية بحرف:", letter);
      modalLetter.textContent = letter;
      if (questions[letter]) {
        modalImage.src = "/static/imgs/" + questions[letter].image;
      } else {
        modalImage.src = "/static/imgs/notAv.png";
      }

      resetModal();
      modal.style.display = "flex";
      stopTimer();
    });
  });

  document.getElementById("team1").addEventListener("click", () => {
    if (currentCell && !currentCell.classList.contains("locked")) {
      const [row, col] = currentCell.getAttribute("data-cell").split("-").map(Number);
      if (boardState[row][col] === null) {
        boardState[row][col] = "red";
        currentCell.style.backgroundColor = "#ff4d4d";
        currentCell.classList.add("locked");

        socket.emit("update_cell", {
          cellId: `${row}-${col}`,
          state: {
            team: "red",
            color: "#ff4d4d"
          }
        });

        if (checkWin("red")) {
          lockAllCells();
        }
      }
    }
    stopTimer();
    modal.style.display = "none";
    enableTeamButtons();
  });

  document.getElementById("team2").addEventListener("click", () => {
    if (currentCell && !currentCell.classList.contains("locked")) {
      const [row, col] = currentCell.getAttribute("data-cell").split("-").map(Number);
      if (boardState[row][col] === null) {
        boardState[row][col] = "blue";
        currentCell.style.backgroundColor = "#3399ff";
        currentCell.classList.add("locked");

        socket.emit("update_cell", {
          cellId: `${row}-${col}`,
          state: {
            team: "blue",
            color: "#3399ff"
          }
        });

        if (checkWin("blue")) {
          lockAllCells();
        }
      }
    }
    stopTimer();
    modal.style.display = "none";
    enableTeamButtons();
  });

  closeBtn.onclick = () => {
    modal.style.display = "none";
    stopTimer();
    enableTeamButtons();
  };

  window.onclick = (event) => {
    if (event.target === modal) {
      modal.style.display = "none";
      stopTimer();
      enableTeamButtons();
    }
  };

  startTimerBtn.addEventListener("click", startTimer);

  resetBuzzerBtn.addEventListener("click", () => {
    buzzerResult.textContent = "";
    enableTeamButtons();
    stopTimer();
    startTimerBtn.style.display = "block";
    timerContainer.style.display = "none";
  });

  startQuestionBtn.addEventListener("click", () => {
    resetModal();
  });

  socket.on("buzz", data => {
    buzzerResult.textContent = `الفريق ${data.team} ضغط البازر!`;
    stopTimer();
    disableTeamButtons();
  });

  socket.on("initial_state", data => {
    if (data.buzzed_team) {
      buzzerResult.textContent = `الفريق ${data.buzzed_team} ضغط البازر!`;
      disableTeamButtons();
    }
  });

  function disableTeamButtons() {
    document.getElementById("team1").disabled = true;
    document.getElementById("team2").disabled = true;
  }
});
