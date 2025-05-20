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

        // إظهار رسالة انتهاء الوقت
        buzzerResult.textContent = "انتهى الوقت، لا يمكن اختيار الفريق الآن.";

        // قفل أزرار الفريق مؤقتًا لمنع الاختيار بعد انتهاء الوقت
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

  // دالة عرض رسالة الفوز في منتصف الشاشة بشكل واضح
  function showWinnerMessage(teamName) {
    if (document.getElementById("winnerMessage")) return; // تمنع الرسالة من الظهور أكثر من مرة
    const winnerDiv = document.createElement("div");
    winnerDiv.id = "winnerMessage";
    winnerDiv.classList.add("winner-message");
    winnerDiv.textContent = `الفريق ${teamName} فاز! 🎉`;

    document.body.appendChild(winnerDiv);

    // تختفي بعد 5 ثواني
    setTimeout(() => {
      if (winnerDiv.parentNode) {
        winnerDiv.parentNode.removeChild(winnerDiv);
      }
    }, 5000);

    // قفل الخلايا ومنع التفاعل
    lockAllCells();
  }

  // ========== دالة الفوز المحسنة مع أخذ إزاحة الصف في الحسبان ==========

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

      // اتجاهات الجيران تعتمد على إذا كان الصف فردي أو زوجي
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

  // ========== دالة مساعدة لعرض اللوحة ==========

  function debugBoard() {
    console.log("حالة اللوحة الحالية:");
    for (let row = 0; row < boardSize; row++) {
      console.log(row + ": " + boardState[row].map(c => c ? c[0] : '.').join(' '));
    }
  }

  // ========== أسئلة اللعبة ==========

  const questions = {
    "أ": { image: "أ.png", question: "اذكر شيئًا يبدأ بحرف الألف" },
    "ب": { image: "ب.png", question: "اذكر شيئًا يبدأ بحرف الباء" },
    "ت": { image: "ت.png", question: "اذكر شيئًا يبدأ بحرف التاء" },
    "ث": { image: "ث.png", question: "اذكر شيئًا يبدأ بحرف الثاء" },
    "ج": { image: "notAv.png", question: "لا يوجد سؤال لهذا الحرف" },
    // ... باقي الحروف
    "ي": { image: "notAv.png", question: "لا يوجد سؤال لهذا الحرف" },
  };

  // ========== دوال المساعدة لتفعيل وتعطيل أزرار الفريق ==========

  function enableTeamButtons() {
    document.getElementById("team1").disabled = false;
    document.getElementById("team2").disabled = false;
  }

  // إعادة ضبط المودال (عند فتح السؤال الجديد)
  function resetModal() {
    buzzerResult.textContent = "";
    enableTeamButtons();
    startTimerBtn.style.display = "block";
    timerContainer.style.display = "none";
  }

  // ========== معالجة النقر على الخلايا ==========

  document.querySelectorAll(".hex").forEach(cell => {
    cell.addEventListener("click", () => {
      if (cell.classList.contains("locked")) return;
      currentCell = cell;
      const letter = cell.getAttribute("data-letter");

      // عرض الحرف والسؤال في المودال
      modalLetter.textContent = letter;
      if (questions[letter]) {
        modalImage.src = "/static/imgs/" + questions[letter].image;
        modalQuestion.textContent = questions[letter].question || "سؤال غير متاح.";
      } else {
        modalImage.src = "/static/imgs/notAv.png";
        modalQuestion.textContent = "سؤال غير متاح لهذا الحرف.";
      }

      resetModal();
      modal.style.display = "flex";
      stopTimer();

      // ======= تم تعطيل إرسال حدث buzz عند فتح الخلية =======
      // socket.emit("buzz", { team: "المتسابق" });
    });
  });

  // ========== معالجة أحداث اختيار الفرق ==========

  document.getElementById("team1").addEventListener("click", () => {
    if (currentCell && !currentCell.classList.contains("locked")) {
      const [row, col] = currentCell.getAttribute("data-cell").split("-").map(Number);

      if (boardState[row][col] === null) {
        // تعيين اللون الأحمر
        currentCell.style.backgroundColor = "#ff4d4d";
        currentCell.classList.add("locked");
        boardState[row][col] = "red";

        console.log(`تم تعيين أحمر في [${row},${col}]`);
        debugBoard();

        // التحقق من الفوز
        if (checkWin("red")) {
          lockAllCells();
        }
      } else {
        console.warn("الخلية محجوزة بالفعل!", row, col);
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
        // تعيين اللون الأزرق
        currentCell.style.backgroundColor = "#3399ff";
        currentCell.classList.add("locked");
        boardState[row][col] = "blue";

        console.log(`تم تعيين أزرق في [${row},${col}]`);
        debugBoard();

        // التحقق من الفوز
        if (checkWin("blue")) {
          lockAllCells();
        }
      } else {
        console.warn("الخلية محجوزة بالفعل!", row, col);
      }
    }
    stopTimer();
    modal.style.display = "none";
    enableTeamButtons();
  });

  // ========== إغلاق المودال ==========

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

  // ========== زر بدء المؤقت ==========

  startTimerBtn.addEventListener("click", startTimer);

  // ========== إعادة ضبط البازر ==========

  resetBuzzerBtn.addEventListener("click", () => {
    buzzerResult.textContent = "";
    enableTeamButtons();
    stopTimer();
    startTimerBtn.style.display = "block";
    timerContainer.style.display = "none";
  });

  // ========== زر بدء السؤال ==========

  startQuestionBtn.addEventListener("click", () => {
    // أعد ضبط المودال والمؤقت والبازر للبدء بسؤال جديد
    resetModal();
  });

  // ========== استقبال حدث البازر من السيرفر ==========

  socket.on("buzz", data => {
    buzzerResult.textContent = `الفريق ${data.team} ضغط البازر!`;
    stopTimer();
    disableTeamButtons();
  });

  // دالة تعطيل أزرار الفريق بعد البازر
  function disableTeamButtons() {
    document.getElementById("team1").disabled = true;
    document.getElementById("team2").disabled = true;
  }
});
