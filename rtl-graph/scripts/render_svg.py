#!/usr/bin/env python3
"""Dependency-free SVG preview for small normalized RTL graphs."""
import argparse
import html
import json
from collections import defaultdict, deque
from pathlib import Path

COLORS = {
    "logic": ("#F8FAFC", "#475569"), "storage": ("#DBEAFE", "#2563EB"),
    "control": ("#FFEDD5", "#EA580C"), "interface": ("#DCFCE7", "#16A34A"),
    "clock": ("#F3E8FF", "#9333EA"), "container": ("#FFFFFF", "#94A3B8")
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("graph")
    ap.add_argument("-o", "--output", default="rtl-graph.svg")
    args = ap.parse_args()
    data = json.loads(Path(args.graph).read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in data["nodes"] if n.get("kind") != "container"}
    outgoing, indegree = defaultdict(list), {nid: 0 for nid in nodes}
    for edge in data["edges"]:
        src, dst = edge["source"].split(".")[0], edge["target"].split(".")[0]
        if src in nodes and dst in nodes and src != dst:
            outgoing[src].append(dst); indegree[dst] += 1
    levels = {nid: 0 for nid in nodes}
    queue = deque(nid for nid, degree in indegree.items() if degree == 0)
    seen = set()
    while queue:
        nid = queue.popleft(); seen.add(nid)
        for dst in outgoing[nid]:
            levels[dst] = max(levels[dst], levels[nid] + 1)
            indegree[dst] -= 1
            if indegree[dst] == 0: queue.append(dst)
    for nid in nodes.keys() - seen:
        levels[nid] = max(levels.values(), default=0) + 1
    buckets = defaultdict(list)
    for nid, level in levels.items(): buckets[level].append(nid)
    positions = {}
    width, height, xgap, ygap, margin = 170, 72, 90, 45, 45
    for level in sorted(buckets):
        for row, nid in enumerate(sorted(buckets[level])):
            positions[nid] = (margin + level * (width + xgap), margin + row * (height + ygap))
    canvas_w = max((x for x, _ in positions.values()), default=0) + width + margin
    canvas_h = max((y for _, y in positions.values()), default=0) + height + margin
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}">', '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#475569"/></marker></defs>', '<rect width="100%" height="100%" fill="white"/>']
    for edge in data["edges"]:
        src, dst = edge["source"].split(".")[0], edge["target"].split(".")[0]
        if src not in positions or dst not in positions: continue
        sx, sy = positions[src]; tx, ty = positions[dst]
        x1, y1, x2, y2 = sx + width, sy + height / 2, tx, ty + height / 2
        mid = (x1 + x2) / 2
        dash = ' stroke-dasharray="6 4"' if edge.get("kind") in {"clock", "reset", "cdc"} else ""
        parts.append(f'<path d="M{x1},{y1} H{mid} V{y2} H{x2}" fill="none" stroke="#475569" stroke-width="1.5" marker-end="url(#arrow)"{dash}/>' )
        label = html.escape(edge.get("label", ""))
        if label: parts.append(f'<text x="{mid}" y="{min(y1,y2)-5}" text-anchor="middle" font-family="Arial" font-size="10" fill="#334155">{label}</text>')
    for nid, node in nodes.items():
        x, y = positions[nid]; fill, stroke = COLORS[node.get("kind", "logic")]
        parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x+width/2}" y="{y+height/2+4}" text-anchor="middle" font-family="Arial" font-size="12" fill="#0F172A">{html.escape(node.get("label", nid))}</text>')
    parts.append("</svg>")
    Path(args.output).write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {args.output}")

if __name__ == "__main__":
    main()
