# Graph Lab — frontend

A zero-build web app for **watching the graph exercises come to life**. Each of
the eleven algorithms in `app/graph/algorithms.py` shows as a **stub** until a
student implements it, then flips to **LIVE** — and the matching visualization
starts working.

Plain HTML + CSS + ES modules. No npm, no bundler, no dependencies.

## Run it

**1. Start the API** (from the project root, schema migrated):

```bash
uvicorn app.main:app --reload     # http://localhost:8000
```

**2. Serve this folder** on a CORS-allowed port (`5173` and `3000` are
pre-allowed in the API's `.env`):

```bash
cd frontend
python -m http.server 5173
```

**3. Open** http://localhost:5173 — it connects to `http://localhost:8000`
automatically.

> Serving on a different port? Add it to `BACKEND_CORS_ORIGINS` in `.env`.

## Using it

0. **Reset database** — wipes every user, post, comment, like, and follow
   (after a confirmation prompt) via `POST /api/v1/admin/reset`, handy for
   starting a demo from a clean slate. Same as `python scripts/reset_db.py`.
1. **Seed demo network** — one click creates 12 users and ~33 follows shaped to
   make every exercise interesting: two clusters, a bridge user, a hub that
   everyone follows, a newcomer with no followers, and one isolated user.
   Idempotent — safe to click repeatedly.
2. **Exercises panel** (left) probes each `/graph` endpoint and shows
   **LIVE** (HTTP 200) or **stub** (HTTP 501 from `NotImplementedError`).
   Check **auto** to re-poll every 5 s — with `uvicorn --reload`, the pill
   flips to LIVE on its own moments after a student saves their implementation.
3. **The graph** (center): an arrow A → B means "A follows B".
   - **Click** a node — inspect that user: reachable set (ex 4, highlighted on
     the graph), recommendations (ex 7), clustering coefficient (ex 9),
     PageRank rank (ex 10).
   - **Shift-click** a second node — compare: shortest path (ex 2, drawn in
     orange), degrees of separation (ex 3), mutual follows (ex 5), Jaccard
     similarity (ex 6).
   - **Drag** nodes to rearrange; click empty space to clear.
4. **Overlays** (above the graph):
   - **influence** — node size ∝ PageRank (ex 10)
   - **communities** — color by detected community (ex 11)
   - **components** — color by connected component (ex 8)

Anything that depends on an unimplemented algorithm simply says
*not implemented yet*, so the whole UI doubles as a progress scoreboard.

## Files

| File | Role |
|------|------|
| `index.html` | Layout |
| `css/styles.css` | Styling |
| `js/api.js` | API client — treats HTTP 501 as "not implemented" |
| `js/graph-view.js` | Hand-rolled force-directed SVG renderer |
| `js/seed.js` | Builds the demo network through the public API |
| `js/app.js` | Scoreboard, overlays, inspector wiring |

## Exercise → endpoint map

| Scoreboard row | Endpoint | Exercise |
|----------------|----------|----------|
| Shortest path | `/graph/users/{a}/path/{b}` | 1 |
| Degrees of sep. | `/graph/users/{a}/degrees/{b}` | 2 |
| Reachable set | `/graph/users/{id}/reachable` | 3 |
| Mutual follows | `/graph/users/{id}/mutuals/{other}` | 4 |
| Jaccard similarity | `/graph/users/{id}/similarity/{other}` | 5 |
| Recommendations | `/graph/users/{id}/recommendations` | 6 |
| Components | `/graph/components` | 7 |
| Clustering coeff. | `/graph/users/{id}/clustering` | 8 |
| PageRank | `/graph/influencers` | 9 |
| Communities | `/graph/communities` | 10 |
