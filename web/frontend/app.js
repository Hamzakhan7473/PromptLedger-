const $ = (id) => document.getElementById(id);

let verticals = [];
let currentId = "legal";
let accent = "#6366f1";

const envByVertical = {
  legal: "contract_review",
  fintech: "financial_modeling",
  healthcare: "legal",
  general: "research",
};

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
  if (!res.ok) throw new Error(data.detail || data.error || data.raw || res.statusText);
  return data;
}

function setAccent(color) {
  accent = color || "#6366f1";
  document.documentElement.style.setProperty("--accent", accent);
}

function setSteps(state) {
  document.querySelectorAll(".step").forEach((el) => {
    const key = el.dataset.step;
    el.classList.remove("active", "done");
    if (state[key] === "active") el.classList.add("active");
    if (state[key] === "done") el.classList.add("done");
  });
}

function setStatus(text, kind = "") {
  const el = $("demo-status");
  el.textContent = text;
  el.className = "status-badge " + kind;
}

async function refreshHealth() {
  try {
    await api("/api/health");
    $("health").textContent = "API connected";
    $("health").className = "health-pill ok";
  } catch {
    $("health").textContent = "API offline";
    $("health").className = "health-pill";
  }
}

function renderNav() {
  const nav = $("vertical-nav");
  nav.innerHTML = "";
  verticals.forEach((v) => {
    const btn = document.createElement("button");
    btn.className = "vert-btn" + (v.id === currentId ? " active" : "");
    const icon = v.icon ? `<span class="vert-icon">${v.icon}</span>` : "";
    btn.innerHTML = `${icon}<span>${v.label}<small>${v.prompt_id}</small></span>`;
    btn.onclick = () => selectVertical(v.id);
    nav.appendChild(btn);
  });
}

async function loadVerticalDetail(id) {
  const data = await api(`/api/demo/vertical/${id}`);
  $("hero-title").textContent = data.headline;
  $("hero-desc").textContent = data.description;
  setAccent(data.accent);

  const checks = $("checks-list");
  checks.innerHTML = "";
  (data.checks || []).forEach((c) => {
    const li = document.createElement("li");
    li.textContent = c;
    checks.appendChild(li);
  });

  const p = data.preview || {};
  $("preview-system").textContent = p.system || "—";
  $("preview-user").textContent = p.user || "—";
}

async function selectVertical(id) {
  currentId = id;
  renderNav();
  setStatus("Ready");
  $("demo-out").textContent = `Selected ${id}. Click “Run full demo pipeline”.`;
  $("graphrag-panel").hidden = true;
  setSteps({});
  try {
    await loadVerticalDetail(id);
  } catch (e) {
    $("hero-desc").textContent = String(e);
  }
}

async function init() {
  await refreshHealth();
  const data = await api("/api/demo/verticals");
  verticals = data.verticals || [];
  if (verticals.length) currentId = verticals[0].id;
  renderNav();
  await selectVertical(currentId);
}

function animatePipelineWhile(promise) {
  const order = ["audit", "test", "manifest", "promote", "graphrag"];
  let idx = 0;
  const tick = () => {
    const state = {};
    order.forEach((step, i) => {
      if (i < idx) state[step] = "done";
      else if (i === idx) state[step] = "active";
    });
    setSteps(state);
    idx = Math.min(idx + 1, order.length - 1);
  };
  tick();
  const timer = setInterval(tick, 700);
  return promise.finally(() => clearInterval(timer));
}

$("btn-run-demo").onclick = async () => {
  setStatus("Running pipeline…", "running");
  $("demo-out").textContent = "Executing audit → scenarios → manifest → promote → GraphRAG…";
  setSteps({ audit: "active" });
  try {
    const result = await animatePipelineWhile(
      api(`/api/demo/run/${currentId}`, { method: "POST" }),
    );
    setSteps({
      audit: result.audit?.passed ? "done" : "active",
      test: result.scenarios?.passed ? "done" : "active",
      manifest: result.manifest?.passed ? "done" : "active",
      promote: "done",
      graphrag: result.graphrag?.indexed ? "done" : "active",
    });
    const allOk =
      result.audit?.passed &&
      result.scenarios?.passed &&
      result.manifest?.passed &&
      result.pack?.passed;
    setStatus(allOk ? "All checks passed" : "Review findings", allOk ? "pass" : "fail");
    $("demo-out").textContent = JSON.stringify(result, null, 2);
    const gr = result.graphrag?.context_preview;
    const grPanel = $("graphrag-panel");
    if (gr) {
      grPanel.hidden = false;
      $("graphrag-preview").textContent = gr;
    } else {
      grPanel.hidden = true;
    }
  } catch (e) {
    setStatus("Demo failed", "fail");
    $("demo-out").textContent = String(e);
    setSteps({});
  }
};

$("btn-agent-run").onclick = async () => {
  const env = envByVertical[currentId] || "research";
  const task = `Demo task for ${currentId} vertical`;
  setStatus("Running agent…", "running");
  $("agent-panel").hidden = false;
  $("agent-out").textContent = "Orchestrator → tools → reward…";
  try {
    const result = await api("/api/agent/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ environment: env, task }),
    });
    setStatus(`Agent reward ${result.reward?.total ?? "—"}`, "pass");
    $("agent-out").textContent = JSON.stringify(result, null, 2);
  } catch (e) {
    setStatus("Agent failed", "fail");
    $("agent-out").textContent = String(e);
  }
};

$("btn-export-evidence").onclick = async () => {
  setStatus("Exporting…", "running");
  try {
    const data = await api("/api/evidence?environment=staging");
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `promptledger-evidence-${currentId}.json`;
    a.click();
    setStatus("Evidence downloaded", "pass");
  } catch (e) {
    setStatus("Export failed", "fail");
    alert(e);
  }
};

init().catch((e) => {
  $("hero-title").textContent = "Demo unavailable";
  $("hero-desc").textContent = String(e);
});
