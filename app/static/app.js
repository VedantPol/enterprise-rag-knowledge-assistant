const healthStatus = document.querySelector("#healthStatus");
const ingestForm = document.querySelector("#ingestForm");
const ingestMessage = document.querySelector("#ingestMessage");
const askForm = document.querySelector("#askForm");
const answer = document.querySelector("#answer");
const citations = document.querySelector("#citations");
const sources = document.querySelector("#sources");
const sampleTopic = document.querySelector("#sampleTopic");
const samplePrompts = document.querySelector("#samplePrompts");
const themeToggle = document.querySelector("#themeToggle");
const themeIcon = document.querySelector("#themeIcon");
const progressWrap = document.querySelector("#progressWrap");
const progressTitle = document.querySelector("#progressTitle");
const progressPercent = document.querySelector("#progressPercent");
const progressFill = document.querySelector("#progressFill");
const progressDetail = document.querySelector("#progressDetail");

let progressTimer;

const askStages = [
  { pct: 18, text: "Packaging your question for the retrieval API..." },
  { pct: 38, text: "Searching embeddings and metadata filters..." },
  { pct: 58, text: "Reranking the strongest source chunks..." },
  { pct: 78, text: "Hitting the Gemini API and waiting for a grounded answer..." },
  { pct: 92, text: "Formatting citations and answer text..." },
];

const ingestStages = [
  { pct: 18, text: "Uploading the PDF to the FastAPI backend..." },
  { pct: 36, text: "Parsing pages and extracting text..." },
  { pct: 58, text: "Chunking content for retrieval..." },
  { pct: 78, text: "Creating embeddings and updating the vector index..." },
  { pct: 92, text: "Refreshing indexed source metadata..." },
];

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || `Request failed with ${response.status}`);
  }
  return data;
}

function initTheme() {
  const stored = localStorage.getItem("rag-theme") || "dark";
  document.documentElement.dataset.theme = stored;
  themeIcon.textContent = stored === "dark" ? "D" : "L";
}

themeToggle.addEventListener("click", () => {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  localStorage.setItem("rag-theme", next);
  themeIcon.textContent = next === "dark" ? "D" : "L";
});

async function loadHealth() {
  try {
    const data = await requestJson("/health");
    healthStatus.textContent = `${data.status.toUpperCase()} - ${data.service}`;
  } catch (error) {
    healthStatus.textContent = error.message;
  }
}

async function loadSample() {
  try {
    const data = await requestJson("/api/sample");
    sampleTopic.textContent = data.topic;
    samplePrompts.innerHTML = data.prompts
      .map((prompt) => `<button class="prompt-button" type="button">${escapeHtml(prompt)}</button>`)
      .join("");
    samplePrompts.querySelectorAll("button").forEach((button) => {
      button.addEventListener("click", () => {
        document.querySelector("#question").value = button.textContent;
        document.querySelector("#question").focus();
      });
    });
  } catch (error) {
    sampleTopic.textContent = error.message;
  }
}

async function loadSources() {
  try {
    const docs = await requestJson("/api/documents");
    if (!docs.length) {
      sources.innerHTML = '<p class="message">No documents indexed yet.</p>';
      return;
    }
    sources.innerHTML = docs
      .map(
        (doc) => `
        <div class="source">
          <strong>${escapeHtml(doc.filename)}</strong>
          <p>${doc.chunks} chunks - ${escapeHtml(formatMetadata(doc.metadata))}</p>
        </div>
      `,
      )
      .join("");
  } catch (error) {
    sources.innerHTML = `<p class="message">${escapeHtml(error.message)}</p>`;
  }
}

ingestForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = ingestForm.querySelector("button");
  button.disabled = true;
  ingestMessage.textContent = "";
  startProgress("Indexing document", ingestStages);

  try {
    const formData = new FormData();
    formData.append("file", document.querySelector("#pdfFile").files[0]);
    formData.append("department", document.querySelector("#department").value);
    formData.append("doc_type", document.querySelector("#docType").value);
    const data = await requestJson("/api/ingest", {
      method: "POST",
      body: formData,
    });
    finishProgress("Indexed and ready for questions.");
    ingestMessage.textContent = `Indexed ${data.chunks_indexed} chunks from ${data.filename}.`;
    ingestForm.reset();
    await loadSources();
  } catch (error) {
    failProgress(error.message);
  } finally {
    button.disabled = false;
  }
});

askForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = askForm.querySelector("button");
  button.disabled = true;
  citations.innerHTML = "";
  answer.textContent = "";
  startProgress("Building answer", askStages);

  try {
    const data = await requestJson("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: document.querySelector("#question").value,
        department: document.querySelector("#filterDepartment").value || null,
        doc_type: document.querySelector("#filterDocType").value || null,
      }),
    });
    finishProgress(data.used_llm ? "Answer generated with Gemini." : "Relevant passages retrieved.");
    answer.textContent = data.answer;
    citations.innerHTML = data.citations
      .map(
        (citation, index) => `
        <div class="citation">
          <strong>[${index + 1}] ${escapeHtml(citation.source)}${citation.page ? `, page ${citation.page}` : ""}</strong>
          <p>${escapeHtml(citation.snippet)}</p>
        </div>
      `,
      )
      .join("");
  } catch (error) {
    failProgress(error.message);
    answer.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

function startProgress(title, stages) {
  clearInterval(progressTimer);
  progressWrap.classList.remove("hidden");
  progressTitle.textContent = title;
  setProgress(8, "Preparing request...");

  let index = 0;
  progressTimer = setInterval(() => {
    const stage = stages[index] || stages[stages.length - 1];
    setProgress(stage.pct, stage.text);
    index = Math.min(index + 1, stages.length - 1);
  }, 1200);
}

function finishProgress(message) {
  clearInterval(progressTimer);
  setProgress(100, message);
}

function failProgress(message) {
  clearInterval(progressTimer);
  progressWrap.classList.remove("hidden");
  progressTitle.textContent = "Request stopped";
  setProgress(100, message);
}

function setProgress(percent, detail) {
  progressPercent.textContent = `${percent}%`;
  progressFill.style.width = `${percent}%`;
  progressDetail.textContent = detail;
}

function formatMetadata(metadata) {
  const parts = Object.entries(metadata || {}).map(([key, value]) => `${key}: ${value}`);
  return parts.length ? parts.join(", ") : "no metadata";
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

initTheme();
loadHealth();
loadSample();
loadSources();
