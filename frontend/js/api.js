/**
 * Tiny API client for the Social Network API.
 *
 * Every call returns { ok, status, notImplemented, data }:
 *   ok             — HTTP 2xx
 *   notImplemented — HTTP 501 (the algorithm is still a stub)
 *   data           — parsed JSON body (or null)
 *
 * Network failures (server down, CORS) throw — callers that probe endpoints
 * should catch and treat that as "disconnected".
 */

export class Api {
  constructor(base = "http://localhost:8000") {
    this.setBase(base);
  }

  setBase(base) {
    this.base = base.replace(/\/+$/, "");
    this.prefix = `${this.base}/api/v1`;
  }

  async request(method, path, { body, token, raw = false } = {}) {
    const headers = {};
    if (body !== undefined) headers["Content-Type"] = "application/json";
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch((raw ? this.base : this.prefix) + path, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    let data = null;
    const text = await res.text();
    if (text) {
      try { data = JSON.parse(text); } catch { data = text; }
    }
    return { ok: res.ok, status: res.status, notImplemented: res.status === 501, data };
  }

  get(path, opts) { return this.request("GET", path, opts); }
  post(path, body, opts = {}) { return this.request("POST", path, { ...opts, body }); }
  delete(path, opts) { return this.request("DELETE", path, opts); }

  // ----- health / auth ------------------------------------------------------
  health() { return this.request("GET", "/health", { raw: true }); }

  register(user) { return this.post("/auth/register", user); }

  async login(username, password) {
    const res = await this.post("/auth/login", { username, password });
    return res.ok ? res.data.access_token : null;
  }

  // ----- users / follows ----------------------------------------------------
  listUsers(limit = 100, offset = 0) {
    return this.get(`/users?limit=${limit}&offset=${offset}`);
  }

  /** All users, paging past the API's max page size of 100. */
  async allUsers() {
    const users = [];
    for (let offset = 0; ; offset += 100) {
      const res = await this.listUsers(100, offset);
      if (!res.ok) break;
      users.push(...res.data);
      if (res.data.length < 100) break;
    }
    return users;
  }

  profile(id) { return this.get(`/users/${id}`); }
  following(id) { return this.get(`/users/${id}/following?limit=100`); }
  follow(id, token) { return this.post(`/users/${id}/follow`, undefined, { token }); }

  // ----- admin ----------------------------------------------------------------
  resetDatabase() { return this.post("/admin/reset"); }

  // ----- graph algorithm endpoints -------------------------------------------
  shortestPath(a, b) { return this.get(`/graph/users/${a}/path/${b}`); }
  degrees(a, b) { return this.get(`/graph/users/${a}/degrees/${b}`); }
  reachable(id, depth = 2) { return this.get(`/graph/users/${id}/reachable?max_depth=${depth}`); }
  allPaths(a, b, depth = 4) { return this.get(`/graph/users/${a}/paths/${b}?max_depth=${depth}`); }
  mutuals(a, b) { return this.get(`/graph/users/${a}/mutuals/${b}`); }
  similarity(a, b) { return this.get(`/graph/users/${a}/similarity/${b}`); }
  recommendations(id, limit = 5) { return this.get(`/graph/users/${id}/recommendations?limit=${limit}`); }
  components() { return this.get(`/graph/components`); }
  clustering(id) { return this.get(`/graph/users/${id}/clustering`); }
  influencers(limit = 100) { return this.get(`/graph/influencers?limit=${limit}`); }
  communities() { return this.get(`/graph/communities`); }
}
