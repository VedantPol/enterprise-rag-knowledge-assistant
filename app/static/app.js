const healthStatus = document.querySelector("#healthStatus");
const ingestForm = document.querySelector("#ingestForm");
const ingestMessage = document.querySelector("#ingestMessage");
const askForm = document.querySelector("#askForm");
const answer = document.querySelector("#answer");
const citations = document.querySelector("#citations");
const sources = document.querySelector("#sources");

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || `Request failed with ${response.status}`);
  }
  return data;
}

async function loadHealth() {
  try {
    const data = await requestJson("/health");
    healthStatus.textContent = `${data.status.toUpperCase()} - ${data.service}`;
  } catch (error) {
    healthStatus.textContent = error.message;
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
  ingestMessage.textContent = "Indexing PDF...";

  try {
    const formData = new FormData();
    formData.append("file", document.querySelector("#pdfFile").files[0]);
    formData.append("department", document.querySelector("#department").value);
    formData.append("doc_type", document.querySelector("#docType").value);
    const data = await requestJson("/api/ingest", {
      method: "POST",
      body: formData,
    });
    ingestMessage.textContent = `Indexed ${data.chunks_indexed} chunks from ${data.filename}.`;
    ingestForm.reset();
    await loadSources();
  } catch (error) {
    ingestMessage.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

askForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = askForm.querySelector("button");
  button.disabled = true;
  answer.textContent = "Searching sources...";
  citations.innerHTML = "";

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
    answer.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

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

loadHealth();
loadSources();
