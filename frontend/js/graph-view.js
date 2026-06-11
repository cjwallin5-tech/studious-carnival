/**
 * GraphView — a small hand-rolled force-directed SVG renderer.
 *
 * No dependencies. Designed for classroom-sized graphs (tens of nodes):
 * pairwise repulsion, springs along edges, gentle gravity toward the center,
 * pointer dragging, and an overlay system for recoloring/resizing nodes.
 */

const W = 1000;
const H = 700;
const NODE_R = 14;

export class GraphView {
  constructor(svg) {
    this.svg = svg;
    this.edgesLayer = svg.querySelector("#edges-layer");
    this.nodesLayer = svg.querySelector("#nodes-layer");

    this.nodes = [];          // {id, label, x, y, vx, vy, el, circle, text}
    this.edges = [];          // {source, target, el}  (ids)
    this.byId = new Map();

    this.overlay = new Map(); // id -> {color?, r?}
    this.highlightNodes = new Set();
    this.highlightEdges = new Set(); // "a->b"
    this.selected = [];       // up to 2 ids

    this.onNodeClick = null;  // (id, {shift}) => void

    this.alpha = 0;
    this._raf = null;
    this._drag = null;

    svg.addEventListener("pointermove", (e) => this._onPointerMove(e));
    svg.addEventListener("pointerup", () => this._onPointerUp());
    svg.addEventListener("pointerleave", () => this._onPointerUp());
  }

  /** Replace the graph. nodes: [{id, label}], edges: [{source, target}] */
  setData(nodes, edges) {
    const oldPos = new Map(this.nodes.map((n) => [n.id, n]));
    this.nodes = nodes.map((n, i) => {
      const prev = oldPos.get(n.id);
      const angle = (i / Math.max(nodes.length, 1)) * 2 * Math.PI;
      return {
        ...n,
        x: prev ? prev.x : W / 2 + Math.cos(angle) * 220,
        y: prev ? prev.y : H / 2 + Math.sin(angle) * 220,
        vx: 0,
        vy: 0,
        pinned: false,
      };
    });
    this.byId = new Map(this.nodes.map((n) => [n.id, n]));
    this.edges = edges.filter(
      (e) => this.byId.has(e.source) && this.byId.has(e.target)
    );
    this._build();
    this.reheat();
  }

  setOverlay(overlay) {
    this.overlay = overlay || new Map();
    this._restyle();
  }

  setHighlight(nodeIds = [], edgeKeys = []) {
    this.highlightNodes = new Set(nodeIds);
    this.highlightEdges = new Set(edgeKeys);
    this._restyle();
  }

  setSelected(ids) {
    this.selected = ids.slice(0, 2);
    this._restyle();
  }

  clearMarks() {
    this.highlightNodes.clear();
    this.highlightEdges.clear();
    this.selected = [];
    this._restyle();
  }

  reheat() {
    this.alpha = 1;
    if (!this._raf) this._tick();
  }

  // ----- DOM ----------------------------------------------------------------

  _build() {
    this.edgesLayer.innerHTML = "";
    this.nodesLayer.innerHTML = "";

    for (const e of this.edges) {
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("class", "edge");
      line.setAttribute("marker-end", "url(#arrow)");
      this.edgesLayer.appendChild(line);
      e.el = line;
    }

    for (const n of this.nodes) {
      const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
      g.setAttribute("class", "node");

      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("r", NODE_R);

      const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      text.setAttribute("dy", -NODE_R - 6);
      text.textContent = n.label;

      g.appendChild(circle);
      g.appendChild(text);
      this.nodesLayer.appendChild(g);
      n.el = g;
      n.circle = circle;
      n.text = text;

      g.addEventListener("pointerdown", (e) => {
        e.preventDefault();
        this._drag = { node: n, moved: false };
        n.pinned = true;
        this.reheat();
      });
      g.addEventListener("click", (e) => {
        if (this._lastDragMoved) return; // a drag, not a click
        this.onNodeClick?.(n.id, { shift: e.shiftKey });
      });
    }
    this._restyle();
    this._render();
  }

  _restyle() {
    const dim = this.highlightNodes.size > 0;
    for (const n of this.nodes) {
      const o = this.overlay.get(n.id) || {};
      n.circle.setAttribute("r", o.r ?? NODE_R);
      n.circle.style.fill = o.color ?? "";
      n.el.classList.toggle("hot", this.highlightNodes.has(n.id));
      n.el.classList.toggle("dim", dim && !this.highlightNodes.has(n.id));
      n.el.classList.toggle("selected", this.selected.includes(n.id));
    }
    for (const e of this.edges) {
      const hot = this.highlightEdges.has(`${e.source}->${e.target}`);
      e.el.classList.toggle("hot", hot);
      e.el.setAttribute("marker-end", hot ? "url(#arrow-hot)" : "url(#arrow)");
      e.el.classList.toggle("dim", this.highlightEdges.size > 0 && !hot);
    }
  }

  // ----- simulation -----------------------------------------------------------

  _tick() {
    this._raf = requestAnimationFrame(() => this._tick());
    if (this.alpha < 0.002) {
      cancelAnimationFrame(this._raf);
      this._raf = null;
      return;
    }
    this.alpha *= this._drag ? 1 : 0.985;
    this._step();
    this._render();
  }

  _step() {
    const a = this.alpha;
    const nodes = this.nodes;

    // pairwise repulsion
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const n1 = nodes[i], n2 = nodes[j];
        let dx = n1.x - n2.x, dy = n1.y - n2.y;
        let d2 = dx * dx + dy * dy;
        if (d2 < 1) { dx = (Math.sin(i * 7 + j) || 0.1); dy = 0.1; d2 = 1; }
        const f = Math.min((9000 / d2) * a, 12);
        const d = Math.sqrt(d2);
        const fx = (dx / d) * f, fy = (dy / d) * f;
        n1.vx += fx; n1.vy += fy;
        n2.vx -= fx; n2.vy -= fy;
      }
    }

    // springs along edges
    for (const e of this.edges) {
      const s = this.byId.get(e.source), t = this.byId.get(e.target);
      const dx = t.x - s.x, dy = t.y - s.y;
      const d = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
      const f = (d - 130) * 0.03 * a;
      const fx = (dx / d) * f, fy = (dy / d) * f;
      s.vx += fx; s.vy += fy;
      t.vx -= fx; t.vy -= fy;
    }

    // gravity + integrate
    for (const n of nodes) {
      n.vx += (W / 2 - n.x) * 0.004 * a;
      n.vy += (H / 2 - n.y) * 0.004 * a;
      if (!n.pinned) {
        n.vx *= 0.85; n.vy *= 0.85;
        n.x += n.vx; n.y += n.vy;
      } else {
        n.vx = 0; n.vy = 0;
      }
      n.x = Math.max(30, Math.min(W - 30, n.x));
      n.y = Math.max(30, Math.min(H - 30, n.y));
    }
  }

  _render() {
    for (const n of this.nodes) {
      n.el.setAttribute("transform", `translate(${n.x},${n.y})`);
    }
    for (const e of this.edges) {
      const s = this.byId.get(e.source), t = this.byId.get(e.target);
      // shorten the line so the arrowhead lands on the circle's rim
      const dx = t.x - s.x, dy = t.y - s.y;
      const d = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
      const rT = Number(t.circle.getAttribute("r")) + 3;
      const rS = Number(s.circle.getAttribute("r"));
      e.el.setAttribute("x1", s.x + (dx / d) * rS);
      e.el.setAttribute("y1", s.y + (dy / d) * rS);
      e.el.setAttribute("x2", t.x - (dx / d) * rT);
      e.el.setAttribute("y2", t.y - (dy / d) * rT);
    }
  }

  // ----- dragging --------------------------------------------------------------

  _svgPoint(e) {
    const pt = this.svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    return pt.matrixTransform(this.svg.getScreenCTM().inverse());
  }

  _onPointerMove(e) {
    if (!this._drag) return;
    const p = this._svgPoint(e);
    this._drag.node.x = p.x;
    this._drag.node.y = p.y;
    this._drag.moved = true;
    this.alpha = Math.max(this.alpha, 0.3);
    this._render();
  }

  _onPointerUp() {
    if (!this._drag) return;
    this._lastDragMoved = this._drag.moved;
    setTimeout(() => (this._lastDragMoved = false), 0);
    this._drag.node.pinned = false;
    this._drag = null;
  }
}
