/**
 * App wiring: connect, seed, exercise scoreboard, overlays, inspector.
 */

import { Api } from "./api.js";
import { GraphView } from "./graph-view.js";
import { seedDemoNetwork } from "./seed.js";

const $ = (sel) => document.querySelector(sel);

const api = new Api($("#api-base").value);
const view = new GraphView($("#graph-svg"));

const state = {
  connected: false,
  users: new Map(),   // id -> UserPublic
  selected: [],       // [id] or [id, id]
  overlay: "none",
  statuses: new Map(), // exercise key -> "live" | "stub" | "error" | "nodata" | "unknown"
  pollTimer: null,
};

const PALETTE = [
  "#5b8dee", "#ef6f6c", "#41c98e", "#f2a541", "#9b6fe8",
  "#3cbac8", "#e86fb4", "#a3c14a", "#c98041", "#7a8aa8",
];

/** The scoreboard — one probe row per exercise. */
const EXERCISES = [
  { key: "paths",      label: "All paths (DFS)",   ex: "1",  fn: "all_paths",
    probe: (a, b) => api.allPaths(a, b) },
  { key: "path",       label: "Shortest path",     ex: "2",  fn: "bfs_shortest_path",
    probe: (a, b) => api.shortestPath(a, b) },
  { key: "degrees",    label: "Degrees of sep.",   ex: "3",  fn: "degrees_of_separation",
    probe: (a, b) => api.degrees(a, b) },
  { key: "reachable",  label: "Reachable set",     ex: "4",  fn: "reachable_within",
    probe: (a) => api.reachable(a, 2) },
  { key: "mutuals",    label: "Mutual follows",    ex: "5",  fn: "common_neighbors",
    probe: (a, b) => api.mutuals(a, b) },
  { key: "similarity", label: "Jaccard similarity",ex: "6",  fn: "jaccard_similarity",
    probe: (a, b) => api.similarity(a, b) },
  { key: "recs",       label: "Recommendations",   ex: "7",  fn: "recommend_users",
    probe: (a) => api.recommendations(a, 1) },
  { key: "components", label: "Components",        ex: "8",  fn: "connected_components",
    probe: () => api.components() },
  { key: "clustering", label: "Clustering coeff.", ex: "9",  fn: "local_clustering_coefficient",
    probe: (a) => api.clustering(a) },
  { key: "influencers",label: "PageRank",          ex: "10", fn: "pagerank",
    probe: () => api.influencers(1) },
  { key: "communities",label: "Communities",       ex: "11", fn: "detect_communities",
    probe: () => api.communities() },
];

const log = (msg) => { $("#log-line").textContent = msg; };

const displayName = (id) => {
  const u = state.users.get(id);
  return u ? u.username : `#${id}`;
};

// ============================================================================
// connection + graph loading
// ============================================================================

async function connect() {
  api.setBase($("#api-base").value);
  log(`connecting to ${api.base}…`);
  try {
    const res = await api.health();
    if (!res.ok) throw new Error(`health returned ${res.status}`);
  } catch (err) {
    setConnected(false);
    log(`could not reach API at ${api.base} — is uvicorn running? (${err.message})`);
    return;
  }
  setConnected(true);
  log("connected.");
  await refreshGraph();
  await probeAll();
}

function setConnected(on) {
  state.connected = on;
  const pill = $("#conn-status");
  pill.textContent = on ? "connected" : "disconnected";
  pill.className = `conn ${on ? "conn-on" : "conn-off"}`;
  $("#btn-seed").disabled = !on;
  $("#btn-refresh").disabled = !on;
  $("#btn-reset").disabled = !on;
}

/** Load users + follow edges (one /following call per user). */
async function refreshGraph() {
  log("loading graph…");
  const users = await api.allUsers();
  state.users = new Map(users.map((u) => [u.id, u]));

  const edges = [];
  await Promise.all(
    users.map(async (u) => {
      const res = await api.following(u.id);
      if (res.ok) {
        for (const f of res.data) edges.push({ source: u.id, target: f.id });
      }
    })
  );

  view.setData(
    users.map((u) => ({ id: u.id, label: u.username })),
    edges
  );
  $("#stage-empty").style.display = users.length ? "none" : "";
  log(`graph loaded: ${users.length} users, ${edges.length} follow edges.`);
  await applyOverlay(state.overlay);
}

async function resetDatabase() {
  const ok = window.confirm(
    "Delete ALL data — every user, post, comment, like, and follow?\nThis cannot be undone."
  );
  if (!ok) return;

  $("#btn-reset").disabled = true;
  try {
    const res = await api.resetDatabase();
    if (!res.ok) {
      log(`reset failed (HTTP ${res.status})`);
      return;
    }
    const total = Object.values(res.data.deleted).reduce((a, b) => a + b, 0);
    log(`database reset: ${total} rows deleted.`);
    clearInspector();
    await refreshGraph();
    await probeAll();
  } finally {
    $("#btn-reset").disabled = !state.connected;
  }
}

async function seed() {
  $("#btn-seed").disabled = true;
  try {
    await seedDemoNetwork(api, log);
    await refreshGraph();
    await probeAll();
  } catch (err) {
    log(err.message);
  } finally {
    $("#btn-seed").disabled = !state.connected;
  }
}

// ============================================================================
// exercise scoreboard
// ============================================================================

/** Pick two distinct probe users, preferring a connected pair so the
 *  pairwise endpoints exercise something real. */
function probeIds() {
  const ids = [...state.users.keys()].sort((x, y) => x - y);
  if (ids.length === 0) return [];
  if (ids.length === 1) return [ids[0]];
  const edge = view.edges[0];
  return edge ? [edge.source, edge.target] : [ids[0], ids[1]];
}

async function probeAll() {
  if (!state.connected) return;
  const [a, b] = probeIds();

  await Promise.all(
    EXERCISES.map(async (ex) => {
      const needs = ex.probe.length; // how many user ids the probe takes
      if ((needs >= 1 && a === undefined) || (needs >= 2 && b === undefined)) {
        state.statuses.set(ex.key, { status: "nodata" });
        return;
      }
      try {
        const res = await ex.probe(a, b);
        state.statuses.set(ex.key, {
          status: res.notImplemented ? "stub" : res.ok ? "live" : "error",
          // the 501 body says exactly what's missing, e.g.
          // "Graph step 01: implement add_node" — surface it as a tooltip
          detail: res.notImplemented ? res.data?.detail : undefined,
        });
      } catch {
        state.statuses.set(ex.key, { status: "unknown" });
      }
    })
  );
  renderScoreboard();
}

function renderScoreboard() {
  const list = $("#exercise-list");
  list.innerHTML = "";
  let done = 0;
  const total = EXERCISES.length;

  for (const ex of EXERCISES) {
    const { status, detail } = state.statuses.get(ex.key) ?? { status: "unknown" };
    if (status === "live") done += 1;

    const li = document.createElement("li");
    li.className = `exercise status-${status}`;
    if (detail) li.title = detail;
    li.innerHTML = `
      <span class="ex-num">${ex.ex}</span>
      <span class="ex-name">${ex.label}<code>${ex.fn}</code></span>
      <span class="pill pill-${status}">${
        { live: "LIVE", stub: "stub", error: "error", nodata: "no data", unknown: "?" }[status]
      }</span>`;
    list.appendChild(li);
  }

  $("#progress-fill").style.width = total ? `${(done / total) * 100}%` : "0";
  $("#progress-label").textContent = `${done} / ${total} implemented`;
}

function setAutoPoll(on) {
  clearInterval(state.pollTimer);
  state.pollTimer = null;
  if (on) state.pollTimer = setInterval(probeAll, 5000);
}

// ============================================================================
// overlays
// ============================================================================

async function applyOverlay(name) {
  state.overlay = name;
  document.querySelectorAll(".overlay-btn").forEach((b) =>
    b.classList.toggle("active", b.dataset.overlay === name)
  );
  const note = $("#overlay-note");
  note.textContent = "";
  view.setOverlay(new Map());
  if (!state.connected || name === "none") return;

  const overlay = new Map();

  if (name === "influence") {
    const res = await api.influencers(100);
    if (!res.ok) return noteStub(note, res, "pagerank (Exercise 10)");
    const scores = res.data.map((r) => r.score);
    const max = Math.max(...scores, 1e-9);
    for (const { user, score } of res.data) {
      overlay.set(user.id, { r: 8 + 22 * Math.sqrt(score / max) });
    }
    note.textContent = "node size ∝ PageRank";
  } else if (name === "communities") {
    const res = await api.communities();
    if (!res.ok) return noteStub(note, res, "detect_communities (Exercise 11)");
    res.data.forEach((group, i) => {
      for (const m of group.members) {
        overlay.set(m.id, { color: PALETTE[i % PALETTE.length] });
      }
    });
    note.textContent = `${res.data.length} communities`;
  } else if (name === "components") {
    const res = await api.components();
    if (!res.ok) return noteStub(note, res, "connected_components (Exercise 8)");
    res.data.forEach((comp, i) => {
      for (const u of comp) {
        overlay.set(u.id, { color: PALETTE[i % PALETTE.length] });
      }
    });
    note.textContent = `${res.data.length} component${res.data.length === 1 ? "" : "s"}`;
  }

  view.setOverlay(overlay);
}

function noteStub(noteEl, res, what) {
  noteEl.textContent = res.notImplemented
    ? `${what} is not implemented yet`
    : `request failed (${res.status})`;
}

// ============================================================================
// inspector
// ============================================================================

function clearInspector() {
  state.selected = [];
  view.clearMarks();
  $("#inspector-title").textContent = "Inspector";
  $("#inspector-body").innerHTML =
    `<p class="hint">Click a node to inspect a user. Shift-click a second node to compare two users.</p>`;
}

function handleNodeClick(id, { shift }) {
  if (shift && state.selected.length >= 1 && state.selected[0] !== id) {
    state.selected = [state.selected[0], id];
  } else {
    state.selected = [id];
  }
  view.setSelected(state.selected);
  view.setHighlight([], []);
  if (state.selected.length === 2) {
    inspectPair(state.selected[0], state.selected[1]);
  } else {
    inspectUser(id);
  }
}

/** Render one result block; `render(data)` returns innerHTML for the body. */
function block(title, res, render) {
  const body = res.notImplemented
    ? `<span class="stub-note">not implemented yet</span>`
    : !res.ok
      ? `<span class="stub-note">error ${res.status}</span>`
      : render(res.data);
  return `<div class="block"><h3>${title}</h3>${body}</div>`;
}

const userChip = (u) =>
  `<span class="chip" data-id="${u.id}">${u.username}</span>`;

async function inspectUser(id) {
  $("#inspector-title").textContent = `@${displayName(id)}`;
  const bodyEl = $("#inspector-body");
  bodyEl.innerHTML = `<p class="hint">loading…</p>`;

  const [profile, reachable, recs, clustering, influencers] = await Promise.all([
    api.profile(id),
    api.reachable(id, 2),
    api.recommendations(id, 5),
    api.clustering(id),
    api.influencers(100),
  ]);

  let html = "";
  if (profile.ok) {
    const p = profile.data;
    html += `<div class="block profile">
      <div>${p.full_name ?? ""} <span class="dim">${p.bio ?? ""}</span></div>
      <div class="counts">
        <span><b>${p.followers_count}</b> followers</span>
        <span><b>${p.following_count}</b> following</span>
      </div>
    </div>`;
  }

  html += block("Reachable ≤ 2 hops <span class='ex-tag'>ex 4</span>", reachable, (rows) => {
    const within = rows.filter((r) => r.depth > 0);
    return within.length
      ? within.map((r) => `${userChip(r.user)}<small class="dim">d${r.depth}</small>`).join(" ")
      : `<span class="dim">no one</span>`;
  });

  html += block("People you may know <span class='ex-tag'>ex 7</span>", recs, (rows) =>
    rows.length
      ? rows.map((r) => `${userChip(r.user)}<small class="dim">score ${r.score}</small>`).join(" ")
      : `<span class="dim">no candidates</span>`
  );

  html += block("Clustering coefficient <span class='ex-tag'>ex 9</span>", clustering, (d) =>
    `<b>${d.clustering_coefficient.toFixed(3)}</b> <span class="dim">how interconnected this user's circle is</span>`
  );

  html += block("Influence <span class='ex-tag'>ex 10</span>", influencers, (rows) => {
    const idx = rows.findIndex((r) => r.user.id === id);
    return idx === -1
      ? `<span class="dim">not ranked</span>`
      : `PageRank rank <b>#${idx + 1}</b> of ${rows.length} <span class="dim">(score ${rows[idx].score.toFixed(4)})</span>`;
  });

  bodyEl.innerHTML = html;
  wireChips(bodyEl);

  // highlight the reachable set on the graph
  if (reachable.ok) {
    view.setHighlight(reachable.data.map((r) => r.user.id), []);
  }
}

async function inspectPair(a, b) {
  $("#inspector-title").textContent = `@${displayName(a)} → @${displayName(b)}`;
  const bodyEl = $("#inspector-body");
  bodyEl.innerHTML = `<p class="hint">loading…</p>`;

  const [path, degrees, mutuals, similarity] = await Promise.all([
    api.shortestPath(a, b),
    api.degrees(a, b),
    api.mutuals(a, b),
    api.similarity(a, b),
  ]);

  let html = "";
  html += block("Shortest follow-path <span class='ex-tag'>ex 2</span>", path, (d) =>
    d.connected
      ? `<div class="path-row">${d.path.map(userChip).join('<span class="arrow">→</span>')}</div>`
      : `<span class="dim">not connected</span>`
  );

  html += block("Degrees of separation <span class='ex-tag'>ex 3</span>", degrees, (d) =>
    d.connected
      ? `<b>${d.degrees}</b> <span class="dim">hop${d.degrees === 1 ? "" : "s"} on the shortest follow-path</span>`
      : `<span class="dim">not connected</span>`
  );

  html += block("Both follow <span class='ex-tag'>ex 5</span>", mutuals, (rows) =>
    rows.length ? rows.map(userChip).join(" ") : `<span class="dim">no one in common</span>`
  );

  html += block("Jaccard similarity <span class='ex-tag'>ex 6</span>", similarity, (d) => {
    const pct = (d.similarity * 100).toFixed(0);
    return `<div class="sim-bar"><div style="width:${pct}%"></div></div>
            <b>${d.similarity.toFixed(3)}</b> <span class="dim">overlap in who they follow</span>`;
  });

  bodyEl.innerHTML = html;
  wireChips(bodyEl);

  // draw the path on the graph
  if (path.ok && path.data.connected) {
    const ids = path.data.path.map((u) => u.id);
    const edgeKeys = ids.slice(1).map((id, i) => `${ids[i]}->${id}`);
    view.setHighlight(ids, edgeKeys);
  }
}

function wireChips(root) {
  root.querySelectorAll(".chip[data-id]").forEach((chip) => {
    chip.addEventListener("click", (e) =>
      handleNodeClick(Number(chip.dataset.id), { shift: e.shiftKey })
    );
  });
}

// ============================================================================
// events
// ============================================================================

$("#btn-connect").addEventListener("click", connect);
$("#btn-seed").addEventListener("click", seed);
$("#btn-reset").addEventListener("click", resetDatabase);
$("#btn-refresh").addEventListener("click", async () => {
  await refreshGraph();
  await probeAll();
});
$("#api-base").addEventListener("keydown", (e) => {
  if (e.key === "Enter") connect();
});
$("#auto-poll").addEventListener("change", (e) => setAutoPoll(e.target.checked));
document.querySelectorAll(".overlay-btn").forEach((b) =>
  b.addEventListener("click", () => applyOverlay(b.dataset.overlay))
);
view.onNodeClick = (id, mods) => handleNodeClick(id, mods);

$("#graph-svg").addEventListener("click", (e) => {
  if (e.target === e.currentTarget) clearInspector();
});

renderScoreboard();
connect();
