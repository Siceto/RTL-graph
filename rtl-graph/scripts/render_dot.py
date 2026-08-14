#!/usr/bin/env python3
"""Render normalized RTL graph JSON as deterministic Graphviz DOT."""
import argparse
import json
from pathlib import Path

COLORS = {
    "module": ("#F8FAFC", "#334155"),
    "logic": ("#F8FAFC", "#475569"), "storage": ("#DBEAFE", "#2563EB"),
    "control": ("#FFEDD5", "#EA580C"), "interface": ("#DCFCE7", "#16A34A"),
    "clock": ("#F3E8FF", "#9333EA"), "container": ("#FFFFFF", "#94A3B8")
}
EDGE = {"data": "#475569", "control": "#64748B", "clock": "#9333EA", "reset": "#9333EA", "cdc": "#9333EA", "hierarchy": "#94A3B8"}

def q(value):
    return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"') + '"'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("graph")
    ap.add_argument("-o", "--output", default="rtl-graph.dot")
    args = ap.parse_args()
    data = json.loads(Path(args.graph).read_text(encoding="utf-8"))
    lines = ["digraph rtl {", "  graph [rankdir=LR, splines=ortho, nodesep=0.55, ranksep=0.9, bgcolor=white];", "  node [shape=box, style=\"rounded,filled\", fontname=Arial, fontsize=11, margin=\"0.15,0.10\"];", "  edge [fontname=Arial, fontsize=9, arrowsize=0.7];"]
    for node in data["nodes"]:
        fill, stroke = COLORS[node.get("kind", "logic")]
        lines.append(f"  {q(node['id'])} [label={q(node.get('label', node['id']))}, fillcolor={q(fill)}, color={q(stroke)}];")
    for edge in data["edges"]:
        kind = edge.get("kind", "data")
        importance = edge.get("importance")
        style = "dashed" if importance == "key-control" or kind in {"clock", "reset", "cdc"} else "solid"
        penwidth = "2.0" if importance == "primary-data" else "1.0"
        source, target = edge["source"].split(".")[0], edge["target"].split(".")[0]
        lines.append(f"  {q(source)} -> {q(target)} [label={q(edge.get('label', ''))}, color={q(EDGE[kind])}, style={q(style)}, penwidth={q(penwidth)}];")
    lines.append("}")
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")

if __name__ == "__main__":
    main()
