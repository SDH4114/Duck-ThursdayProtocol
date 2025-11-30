const consoleEl = document.getElementById("console");
const inputEl = document.getElementById("commandInput");

let history = [];
let historyIndex = -1;

function printLine(text, type) {
  const div = document.createElement("div");
  div.className = "terminal-line";
  if (type) div.classList.add(type);

  // добавляем зелёный префикс "D.O.A.>"
  const prefix = document.createElement("span");
  prefix.className = "prefix";
  prefix.textContent = "D.O.A.>";

  const span = document.createElement("span");
  span.textContent = " " + text;

  div.appendChild(prefix);
  div.appendChild(span);
  consoleEl.appendChild(div);
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

function printRaw(text) {
  const div = document.createElement("div");
  div.className = "terminal-line";
  div.textContent = text;
  consoleEl.appendChild(div);
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

async function handleCommand(cmd) {
  const trimmed = cmd.trim();
  if (!trimmed) return;

  // показываем введённую команду как в терминале
  printRaw("> " + trimmed);

  // локальная команда clear
  if (trimmed === "clear") {
    consoleEl.innerHTML = "";
    return;
  }

  // локальная команда help (подсказка по DOA)
  if (trimmed === "help") {
    printLine(
      "Commands:\n  system.info\n  system.time\n  note.new \"Title\" text\n  note.list\n  ls / pwd / git status\n  clear",
      "info"
    );
    return;
  }

  // отправляем на backend DOA: /command
  try {
    const res = await fetch("/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw: trimmed }),
    });

    if (!res.ok) {
      printLine("[HTTP ERROR] " + res.status, "error");
      return;
    }

    const json = await res.json();

    printLine(json.status.toUpperCase() + ": " + json.message, json.status === "ok" ? "info" : "error");

    if (json.data) {
      // shell-команда
      if (json.data.stdout !== undefined || json.data.stderr !== undefined) {
        if (json.data.stdout) printRaw(json.data.stdout.trimEnd());
        if (json.data.stderr) printLine(json.data.stderr.trimEnd(), "error");
      }
      // список (note.list)
      else if (Array.isArray(json.data)) {
        json.data.forEach((x) => printRaw("- " + x));
      }
      // заметка (note.open)
      else if (json.data.title && json.data.content) {
        printRaw("# " + json.data.title);
        printRaw(json.data.content);
      } else {
        // на всякий случай — показать как JSON
        printRaw(JSON.stringify(json.data, null, 2));
      }
    }
  } catch (err) {
    printLine("[ERROR] " + err, "error");
  }
}

// история + enter
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    const value = inputEl.value;
    inputEl.value = "";
    if (!value.trim()) return;

    history.unshift(value);
    historyIndex = -1;

    handleCommand(value);
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    if (history.length === 0) return;
    if (historyIndex < history.length - 1) historyIndex++;
    inputEl.value = history[historyIndex] || "";
    // ставим курсор в конец
    inputEl.setSelectionRange(inputEl.value.length, inputEl.value.length);
  } else if (e.key === "ArrowDown") {
    e.preventDefault();
    if (historyIndex > 0) {
      historyIndex--;
      inputEl.value = history[historyIndex] || "";
    } else {
      historyIndex = -1;
      inputEl.value = "";
    }
    inputEl.setSelectionRange(inputEl.value.length, inputEl.value.length);
  }
});

// автофокус по клику
document.querySelector(".terminal-window").addEventListener("click", () => {
  inputEl.focus();
});

// приветствие
printLine("DOA Core online. Type `help` for commands.", "info");
inputEl.focus();