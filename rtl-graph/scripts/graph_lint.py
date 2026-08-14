#!/usr/bin/env python3
"""Validate normalized RTL graph structure and optional node geometry."""
import argparse
import json
import sys
from pathlib import Path

VALID_VIEWS = {"module-dataflow", "module", "hierarchy", "datapath", "control", "clock-reset"}
VALID_KINDS = {"module", "logic", "storage", "control", "interface", "clock", "container"}
VALID_EDGES = {"data", "control", "clock", "reset", "cdc", "hierarchy"}

def endpoint_exists(endpoint, nodes):
    node_id, _, port_id = endpoint.partition(".")
    if node_id not in nodes:
        return False
    return not port_id or port_id in {p.get("id") for p in nodes[node_id].get("ports", [])}

def overlaps(a, b):
    keys = {"x", "y", "width", "height"}
    if not keys <= a.keys() or not keys <= b.keys():
        return False
    return a["x"] < b["x"] + b["width"] and a["x"] + a["width"] > b["x"] and a["y"] < b["y"] + b["height"] and a["y"] + a["height"] > b["y"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("graph")
    args = ap.parse_args()
    data = json.loads(Path(args.graph).read_text(encoding="utf-8"))
    errors, warnings = [], []
    for key in ("title", "scope", "focus_module", "view", "display_mode", "layout_mode", "nodes", "edges"):
        if key not in data:
            errors.append(f"missing top-level field: {key}")
    if data.get("view") not in VALID_VIEWS:
        errors.append(f"invalid view: {data.get('view')}")
    if data.get("scope") == "module" and data.get("display_mode") != "expanded-instances":
        errors.append("module-dataflow requires display_mode=expanded-instances")
    if data.get("scope") == "module" and data.get("layout_mode") != "flat-rails":
        errors.append("module-dataflow requires layout_mode=flat-rails")
    nodes = {}
    for node in data.get("nodes", []):
        nid = node.get("id")
        if not nid or nid in nodes:
            errors.append(f"missing or duplicate node id: {nid}")
        else:
            nodes[nid] = node
        if node.get("kind") not in VALID_KINDS:
            errors.append(f"node {nid}: invalid kind {node.get('kind')}")
        port_ids = [p.get("id") for p in node.get("ports", [])]
        if len(port_ids) != len(set(port_ids)):
            errors.append(f"node {nid}: duplicate port id")
    if data.get("scope") == "module":
        focus = [n for n in nodes.values() if n.get("role") == "focus"]
        if len(focus) != 1:
            errors.append("module scope requires exactly one focus node")
        elif focus[0].get("id") != data.get("focus_module"):
            errors.append("focus node id must equal focus_module")
        for node in nodes.values():
            if node.get("role") not in {"focus", "instance"}:
                errors.append(f"node {node.get('id')}: module scope allows only focus or instance roles")
            if node.get("role") == "instance" and node.get("kind") in {"interface", "clock", "container"}:
                errors.append(f"node {node.get('id')}: auxiliary interface/clock/container nodes are forbidden in module scope")
            if node.get("role") == "instance":
                if not node.get("module_type") or not node.get("instance_name"):
                    errors.append(f"node {node.get('id')}: instance requires module_type and instance_name metadata")
                if node.get("label") != node.get("module_type"):
                    errors.append(f"node {node.get('id')}: visible label must equal module_type")
                for forbidden in ("count", "multiplicity", "badge"):
                    if forbidden in node:
                        errors.append(f"node {node.get('id')}: aggregated instance field {forbidden} is forbidden")
    edge_ids = set()
    for edge in data.get("edges", []):
        eid = edge.get("id")
        if not eid or eid in edge_ids:
            errors.append(f"missing or duplicate edge id: {eid}")
        edge_ids.add(eid)
        if edge.get("kind") not in VALID_EDGES:
            errors.append(f"edge {eid}: invalid kind {edge.get('kind')}")
        if data.get("scope") == "module" and edge.get("inferred") is not False:
            errors.append(f"edge {eid}: module scope requires inferred=false")
        if data.get("scope") == "module" and edge.get("importance") != "primary-data":
            errors.append(f"edge {eid}: module scope requires primary-data importance")
        if data.get("scope") == "module" and edge.get("kind") != "data":
            errors.append(f"edge {eid}: module-dataflow allows data edges only")
        for key in ("source", "target"):
            if not endpoint_exists(str(edge.get(key, "")), nodes):
                errors.append(f"edge {eid}: unknown {key} {edge.get(key)}")
    visible = [n for n in nodes.values() if n.get("kind") != "container"]
    for i, first in enumerate(visible):
        for second in visible[i + 1:]:
            if overlaps(first, second):
                errors.append(f"geometry overlap: {first['id']} and {second['id']}")
    if data.get("scope") == "module" and len(nodes) > 13:
        warnings.append("module-centric diagram has more than 12 direct instances; consider showing fewer children")
    control_names = {"valid", "ready", "enable", "en", "grant", "select", "sel", "flush"}
    for edge in data.get("edges", []):
        label_tokens = set(str(edge.get("label", "")).lower().replace("/", "_").split("_"))
        if label_tokens & control_names:
            errors.append(f"edge {edge.get('id')}: control-oriented label is forbidden in module-dataflow")
    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARN: {message}")
    print(f"checked {len(nodes)} nodes and {len(data.get('edges', []))} edges: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
