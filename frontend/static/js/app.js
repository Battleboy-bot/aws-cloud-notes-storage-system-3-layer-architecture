const API_BASE_URL = window.NOTES_CONFIG.API_BASE_URL;

let page = 1;
let pageSize = 10;
let currentSearch = "";

const uploadForm = document.getElementById("uploadForm");
const filesTable = document.getElementById("filesTable");
const alertHost = document.getElementById("alertHost");
const paginationSummary = document.getElementById("paginationSummary");
const prevPage = document.getElementById("prevPage");
const nextPage = document.getElementById("nextPage");
const searchForm = document.getElementById("searchForm");
const resetSearch = document.getElementById("resetSearch");

function showAlert(message, type = "success") {
  alertHost.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `;
}

async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || "Request failed");
  }
  return payload;
}

function renderFiles(payload) {
  const files = payload.items || [];
  filesTable.innerHTML = "";

  if (files.length === 0) {
    filesTable.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-4">No files found</td></tr>`;
  }

  for (const file of files) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(file.title)}</td>
      <td>${escapeHtml(file.filename)}</td>
      <td>${new Date(file.created_at).toLocaleString()}</td>
      <td class="text-end">
        <button class="btn btn-sm btn-outline-primary me-2" data-action="download" data-filename="${escapeHtml(file.filename)}">Download</button>
        <button class="btn btn-sm btn-outline-danger" data-action="delete" data-id="${file.id}">Delete</button>
      </td>
    `;
    filesTable.appendChild(row);
  }

  const pagination = payload.pagination || { total: 0 };
  const start = pagination.total === 0 ? 0 : (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, pagination.total);
  paginationSummary.textContent = `${start}-${end} of ${pagination.total}`;
  prevPage.disabled = page <= 1;
  nextPage.disabled = end >= pagination.total;
}

async function loadFiles() {
  const params = new URLSearchParams({ page, page_size: pageSize });
  const path = currentSearch
    ? `/files/search?title=${encodeURIComponent(currentSearch)}&${params}`
    : `/files?${params}`;
  const payload = await apiFetch(path);
  renderFiles(payload);
}

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(uploadForm);
  try {
    await apiFetch("/files", { method: "POST", body: formData });
    uploadForm.reset();
    page = 1;
    await loadFiles();
    showAlert("File uploaded successfully");
  } catch (error) {
    showAlert(error.message, "danger");
  }
});

filesTable.addEventListener("click", async (event) => {
  const button = event.target.closest("button");
  if (!button) return;

  try {
    if (button.dataset.action === "download") {
      const payload = await apiFetch(`/files/${encodeURIComponent(button.dataset.filename)}`);
      window.open(payload.download_url, "_blank", "noopener");
    }

    if (button.dataset.action === "delete") {
      await apiFetch(`/files/${button.dataset.id}`, { method: "DELETE" });
      await loadFiles();
      showAlert("File deleted successfully");
    }
  } catch (error) {
    showAlert(error.message, "danger");
  }
});

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  currentSearch = document.getElementById("searchTitle").value.trim();
  page = 1;
  await loadFiles();
});

resetSearch.addEventListener("click", async () => {
  currentSearch = "";
  document.getElementById("searchTitle").value = "";
  page = 1;
  await loadFiles();
});

prevPage.addEventListener("click", async () => {
  if (page > 1) {
    page -= 1;
    await loadFiles();
  }
});

nextPage.addEventListener("click", async () => {
  page += 1;
  await loadFiles();
});

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

loadFiles().catch((error) => showAlert(error.message, "danger"));
