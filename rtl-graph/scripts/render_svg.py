#!/usr/bin/env python3
"""Dependency-free SVG preview for small normalized RTL graphs."""
import argparse
import html
import json
from collections import defaultdict, deque
from pathlib import Path

COLORS = {
    "module": ("#F8FAFC", "#334155"),
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
    all_nodes = {n["id"]: n for n in data["nodes"] if n.get("kind") != "container"}
    focus_id = data.get("focus_module")
    module_scope = data.get("scope") == "module" and focus_id in all_nodes
    nodes = {nid: node for nid, node in all_nodes.items() if not module_scope or nid != focus_id}
    if not nodes:
        nodes = all_nodes
        module_scope = False
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
            x_offset = margin + 80 if module_scope else margin
            y_offset = margin + 40 if module_scope else margin
            positions[nid] = (x_offset + level * (width + xgap), y_offset + row * (height + ygap))
    canvas_w = max((x for x, _ in positions.values()), default=0) + width + margin + (80 if module_scope else 0)
    canvas_h = max((y for _, y in positions.values()), default=0) + height + margin
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}">', '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#475569"/></marker></defs>', '<rect width="100%" height="100%" fill="white"/>']
    if module_scope:
        parts.append(f'<rect x="{margin/2}" y="{margin/2}" width="{canvas_w-margin}" height="{canvas_h-margin}" rx="10" fill="#FFFFFF" stroke="#94A3B8" stroke-width="1.5"/>')
        parts.append(f'<text x="{margin}" y="{margin}" font-family="Arial" font-size="13" font-weight="bold" fill="#0F172A">{html.escape(focus_id)}</text>')
    directed_pairs = {(e["source"].split(".")[0], e["target"].split(".")[0]) for e in data["edges"]}
    for edge in data["edges"]:
        src, dst = edge["source"].split(".")[0], edge["target"].split(".")[0]
        if src == focus_id and dst in positions:
            tx, ty = positions[dst]; x1, y1, x2, y2 = margin / 2, ty + height / 2, tx, ty + height / 2
        elif dst == focus_id and src in positions:
            sx, sy = positions[src]; x1, y1, x2, y2 = sx + width, sy + height / 2, canvas_w - margin / 2, sy + height / 2
        elif src in positions and dst in positions:
            sx, sy = positions[src]; tx, ty = positions[dst]
            x1 = sx + width if sx <= tx else sx
            x2 = tx if sx <= tx else tx + width
            y1, y2 = sy + height / 2, ty + height / 2
        else:
            continue
        reverse_pair = src != focus_id and dst != focus_id and (dst, src) in directed_pairs
        lane = (-14 if x1 <= x2 else 14) if reverse_pair else 0
        y1 += lane; y2 += lane
        mid = (x1 + x2) / 2
        dash = ' stroke-dasharray="6 4"' if edge.get("importance") == "key-control" or edge.get("kind") in {"clock", "reset", "cdc"} else ""
        stroke_width = "2" if edge.get("importance") == "primary-data" else "1"
        parts.append(f'<path d="M{x1},{y1} H{mid} V{y2} H{x2}" fill="none" stroke="#475569" stroke-width="{stroke_width}" marker-end="url(#arrow)"{dash}/>' )
        label = html.escape(edge.get("label", ""))
        label_y = min(y1, y2) - 5 if lane <= 0 else max(y1, y2) + 14
        if label: parts.append(f'<text x="{mid}" y="{label_y}" text-anchor="middle" font-family="Arial" font-size="10" fill="#334155">{label}</text>')
    for nid, node in nodes.items():
        x, y = positions[nid]; fill, stroke = COLORS[node.get("kind", "logic")]
        parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x+width/2}" y="{y+height/2+4}" text-anchor="middle" font-family="Arial" font-size="12" fill="#0F172A">{html.escape(node.get("label", nid))}</text>')
    parts.append("</svg>")
    Path(args.output).write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {args.output}")

if __name__ == "__main__":
    main()
