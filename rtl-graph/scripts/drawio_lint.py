#!/usr/bin/env python3
"""Lint draw.io XML for flat, instance-faithful RTL data-flow style."""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

def style_map(raw):
    out = {}
    for item in (raw or "").split(";"):
        if "=" in item:
            key, value = item.split("=", 1); out[key] = value
        elif item:
            out[item] = "1"
    return out

def plain(raw):
    return re.sub(r"<[^>]+>", " ", raw or "").strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("diagram")
    ap.add_argument("--graph", help="normalized graph JSON for topology/count checks")
    args = ap.parse_args()
    root = ET.parse(args.diagram).getroot()
    cells = {c.get("id"): c for c in root.findall(".//mxCell")}
    errors, warnings = [], []
    swimlanes = []
    ellipses = 0
    colors = set()
    sizes = defaultdict(set)
    visible_box_texts = []
    for cell in cells.values():
        style = style_map(cell.get("style"))
        text = plain(cell.get("value"))
        if "swimlane" in style:
            swimlanes.append(cell)
            parent = cells.get(cell.get("parent"))
            if parent is not None and "swimlane" in style_map(parent.get("style")):
                errors.append(f"nested swimlane is forbidden: {text or cell.get('id')}")
        if "ellipse" in style:
            ellipses += 1
        for key in ("fillColor", "strokeColor"):
            value = style.get(key)
            if value and value not in {"none", "#FFFFFF", "#ffffff"}:
                colors.add(value.lower())
        if cell.get("vertex") == "1" and re.fullmatch(r"(?:×|x)\s*\d+", text, re.I):
            errors.append(f"multiplicity badge is forbidden: {text}")
        if re.fullmatch(r"STAGE\s*\d+", text, re.I):
            warnings.append(f"stage tag is usually unnecessary: {text}")
        if cell.get("vertex") == "1" and text and "edgeLabel" not in style and "text" not in style and "swimlane" not in style:
            geom = cell.find("mxGeometry")
            if geom is not None and geom.get("width") and geom.get("height"):
                width, height = float(geom.get("width")), float(geom.get("height"))
                sizes[text].add((width, height))
                if "ellipse" not in style and height > 12 and width > 20:
                    visible_box_texts.append(text)
                    if width > 260 or height > 110:
                        warnings.append(f"functional box is oversized: {text} {width:g}x{height:g}")
                if re.search(r"(?:mux|arbiter|selector|fsm)", text, re.I):
                    warnings.append(f"control-helper block needs data-path justification: {text}")
        if cell.get("edge") == "1":
            tokens = set(re.split(r"[_/\W]+", text.lower()))
            if tokens & {"valid", "ready", "enable", "grant", "select", "flush"}:
                errors.append(f"control edge is forbidden: {text}")
    if len(swimlanes) > 1:
        warnings.append(f"flat-rails style expects at most one container; found {len(swimlanes)} swimlanes")
    if ellipses > 4:
        warnings.append(f"decorative/tap dots are excessive: {ellipses} ellipses")
    if len(colors) > 8:
        warnings.append(f"palette is complex: {len(colors)} non-neutral fill/stroke colors")
    for label, variants in sizes.items():
        if len(variants) > 1:
            warnings.append(f"same module label has inconsistent sizes: {label} {sorted(variants)}")
    if args.graph:
        graph = json.loads(open(args.graph, encoding="utf-8").read())
        expected = Counter(n.get("module_type") for n in graph.get("nodes", []) if n.get("role") == "instance")
        actual = Counter(visible_box_texts)
        for module_type, count in expected.items():
            found = actual.get(module_type, 0)
            if found != count:
                errors.append(f"module count mismatch for {module_type}: expected {count}, found {found}")
    for message in errors: print(f"ERROR: {message}")
    for message in warnings: print(f"WARN: {message}")
    print(f"checked draw.io: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
