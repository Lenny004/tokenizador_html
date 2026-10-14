const statusNode = document.querySelector("#runtime-status");
const codeInput = document.querySelector("#code-input");
const editorHighlight = document.querySelector("#editor-highlight");
const messages = document.querySelector("#messages");
let pyodide;
let latestResult = null;

const addMessage = (text, assistant = true) => {
  const node = document.createElement("div");
  node.className = `message${assistant ? " message--assistant" : ""}`;
  node.innerHTML = `<span class="message__label">${assistant ? "asistente" : "tú"}</span><p class="message__text"></p>`;
  node.querySelector(".message__text").textContent = text;
  messages.append(node);
  messages.scrollTop = messages.scrollHeight;
};

async function loadPython() {
  try {
    const { loadPyodide } = await import("https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.mjs");
    pyodide = await loadPyodide();
    pyodide.FS.mkdir("/home/pyodide/html_analyzer");
    const files = ["__init__.py", "lexer.py", "parser.py", "rules.py", "analyzer.py"];
    for (const file of files) {
      const response = await fetch(`html_analyzer/${file}`);
      pyodide.FS.writeFile(`/home/pyodide/html_analyzer/${file}`, await response.text());
    }
    statusNode.textContent = "Python listo · Pyodide";
  } catch (error) {
    statusNode.textContent = "Modo local no disponible";
    addMessage("No se pudo cargar Pyodide. Revisa la conexión y vuelve a intentar.");
    console.error(error);
  }
}

function updateEditorMeta() {
  const lines = codeInput.value.split("\n").length;
  document.querySelector("#line-count").textContent = `${lines.toLocaleString("es")} ${lines === 1 ? "línea" : "líneas"}`;
}

function offsetAt(line, column) {
  const rows = codeInput.value.split("\n");
  return rows.slice(0, line - 1).reduce((total, row) => total + row.length + 1, 0) + column - 1;
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (character) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[character]));
}

function updateHighlight(findings = []) {
  const source = codeInput.value;
  const marks = findings.map((finding) => ({
    start: offsetAt(finding.line, finding.column),
    end: offsetAt(finding.line, finding.end_column ?? finding.column + 1),
    layer: finding.layer,
  })).filter((mark) => mark.start < mark.end);
  marks.sort((left, right) => left.start - right.start || right.end - left.end);
  let html = "";
  let cursor = 0;
  for (const mark of marks) {
    if (mark.start < cursor) continue;
    html += escapeHtml(source.slice(cursor, mark.start));
    html += `<mark class="editor__mark editor__mark--${mark.layer}">${escapeHtml(source.slice(mark.start, mark.end))}</mark>`;
    cursor = mark.end;
  }
  editorHighlight.innerHTML = `${html}${escapeHtml(source.slice(cursor))}`;
  syncEditorScroll();
}

function syncEditorScroll() {
  editorHighlight.scrollTop = codeInput.scrollTop;
  editorHighlight.scrollLeft = codeInput.scrollLeft;
}

async function analyzeCode() {
  if (!pyodide) { addMessage("El runtime de Python aún está cargando."); return; }
  const source = JSON.stringify(codeInput.value);
  const output = await pyodide.runPythonAsync(`import json\nfrom html_analyzer import analyze\njson.dumps(analyze(${source}).as_dict(), ensure_ascii=False)`);
  latestResult = JSON.parse(output);
  updateHighlight(latestResult.findings);
  document.querySelector("#token-count").textContent = `${latestResult.tokens.toLocaleString("es")} tokens · ${latestResult.elapsed_ms} ms`;
  messages.querySelectorAll(".finding").forEach((node) => node.remove());
  const summary = latestResult.summary;
  addMessage(`Análisis completo: ${summary.total} hallazgo${summary.total === 1 ? "" : "s"}. Estructura ${summary.structure}, sintaxis ${summary.syntax}, lógica ${summary.logic}.`);
  latestResult.findings.forEach((finding) => {
    const node = document.createElement("div");
    node.className = `finding finding--${finding.layer}`;
    node.dataset.line = finding.line;
    node.dataset.column = finding.column;
    node.tabIndex = 0;
    node.setAttribute("role", "button");
    node.innerHTML = `<span class="finding__badge">L${finding.line}:C${finding.column}</span><span class="finding__message"></span>`;
    node.querySelector(".finding__message").textContent = finding.message;
    const selectFinding = () => {
      const start = offsetAt(finding.line, finding.column);
      codeInput.focus();
      const end = offsetAt(finding.line, finding.end_column ?? finding.column + 1);
      codeInput.setSelectionRange(start, Math.max(start + 1, end));
      const lineHeight = parseFloat(getComputedStyle(codeInput).lineHeight);
      codeInput.scrollTop = Math.max(0, (finding.line - 1) * lineHeight - codeInput.clientHeight / 3);
      syncEditorScroll();
    };
    node.addEventListener("click", selectFinding);
    node.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); selectFinding(); } });
    messages.append(node);
  });
  messages.scrollTop = messages.scrollHeight;
}

document.querySelector("#analyze-button").addEventListener("click", analyzeCode);
codeInput.addEventListener("input", () => { updateEditorMeta(); updateHighlight(); });
codeInput.addEventListener("scroll", syncEditorScroll);
document.querySelector("#file-input").addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (file) { codeInput.value = await file.text(); updateEditorMeta(); updateHighlight(); addMessage(`Cargué ${file.name}. Pulsa “Analizar código” para recorrerlo.`); }
});
document.querySelector("#example-button").addEventListener("click", async () => {
  const response = await fetch("ejemplo_prueba.html");
  codeInput.value = await response.text(); updateEditorMeta(); updateHighlight(); addMessage("Cargué el ejemplo sembrado con errores de las tres capas.");
});
document.querySelector("#chat-button").addEventListener("click", () => {
  const input = document.querySelector("#chat-input");
  if (!input.value.trim()) return;
  addMessage(input.value, false);
  const total = latestResult?.summary.total ?? 0;
  addMessage(`El último análisis tiene ${total} hallazgo${total === 1 ? "" : "s"}. Las tarjetas indican capa, línea y columna; vuelve a analizar después de editar.`);
  input.value = "";
});
document.querySelector("#theme-button").addEventListener("click", () => {
  document.documentElement.dataset.theme = document.documentElement.dataset.theme === "light" ? "" : "light";
});
updateEditorMeta();
updateHighlight();
loadPython();
