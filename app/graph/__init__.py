"""In-memory graph package.

- `graph.py`      — the `DirectedGraph` data structure (a reference implementation
                    students can read to see how a graph is actually stored).
- `builder.py`    — turns rows in the database (the `follows` table) into a
                    `DirectedGraph` the algorithms can run on.
- `algorithms.py` — STUBBED graph algorithms. This is where students implement
                    BFS, PageRank, community detection, recommendations, etc.

See `app/graph/EXERCISES.md` for the list of algorithms to implement.
"""

from app.graph.graph import DirectedGraph

__all__ = ["DirectedGraph"]
