const $ = (id) => document.getElementById(id);

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { Accept: "application/json", ...(opts.headers || {}) },
    ...opts,
  });
  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = { raw: text };
  }
  if (!res.ok) {
    throw new Error(data.detail || data.raw || res.statusText);
  }
  return data;
}

function show(el, data) {
  el.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
}

async function refreshHealth() {
  const badge = $("health");
  try {
    const h = await api("/api/health");
    badge.textContent = `connected · ${h.repo.split("/").pop()}`;
    badge.className = "badge ok";
  } catch (e) {
    badge.textContent = "API offline";
    badge.className = "badge err";
  }
}

async function loadManifest() {
  try {
    const m = await api("/api/manifest");
    show($("manifest-out"), m);
  } catch (e) {
    show($("manifest-out"), String(e));
  }
}

$("btn-audit").onclick = async () => {
  show($("gov-out"), "Running audit…");
  try {
    show($("gov-out"), await api("/api/audit"));
  } catch (e) {
    show($("gov-out"), String(e));
  }
};

$("btn-validate").onclick = async () => {
  show($("gov-out"), "Validating manifest…");
  try {
    show($("gov-out"), await api("/api/validate-manifest"));
  } catch (e) {
    show($("gov-out"), String(e));
  }
};

$("btn-test").onclick = async () => {
  show($("gov-out"), "Running scenarios…");
  try {
    show($("gov-out"), await api("/api/test"));
  } catch (e) {
    show($("gov-out"), String(e));
  }
};

$("btn-evidence").onclick = async () => {
  show($("gov-out"), "Building evidence…");
  try {
    show($("gov-out"), await api("/api/evidence?environment=staging"));
  } catch (e) {
    show($("gov-out"), String(e));
  }
};

$("btn-promote").onclick = async () => {
  show($("promote-out"), "Dry-run promote…");
  try {
    const data = await api("/api/promote", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        environment: "production",
        sync_from: "staging",
        dry_run: true,
      }),
    });
    show($("promote-out"), data);
  } catch (e) {
    show($("promote-out"), String(e));
  }
};

$("btn-gr-index").onclick = async () => {
  show($("gr-out"), "Indexing (Go stub)…");
  try {
    show($("gr-out"), await api("/api/graphrag/index", { method: "POST" }));
  } catch (e) {
    show($("gr-out"), String(e));
  }
};

$("btn-gr-context").onclick = async () => {
  const q = $("gr-question").value;
  show($("gr-out"), "Loading context…");
  try {
    show($("gr-out"), await api(`/api/graphrag/context?question=${encodeURIComponent(q)}`));
  } catch (e) {
    show($("gr-out"), String(e));
  }
};

$("btn-gr-query").onclick = async () => {
  const question = $("gr-question").value;
  show($("gr-out"), "Querying…");
  try {
    show($("gr-out"), await api("/api/graphrag/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    }));
  } catch (e) {
    show($("gr-out"), String(e));
  }
};

refreshHealth();
loadManifest();
