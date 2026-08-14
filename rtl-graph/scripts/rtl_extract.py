#!/usr/bin/env python3
"""Conservative, dependency-free first-pass RTL inventory; not a full SV parser."""
import argparse
import json
import re
from pathlib import Path

COMMENT_RE = re.compile(r"//.*?$|/\*.*?\*/", re.M | re.S)
MODULE_RE = re.compile(r"\bmodule\s+(\w+)\s*(?:#\s*\(.*?\)\s*)?\((.*?)\)\s*;(.*?)\bendmodule\b", re.S)
PORT_RE = re.compile(r"\b(input|output|inout)\b\s*(?:wire|reg|logic|signed|unsigned|var|tri|\s)*\s*(\[[^\]]+\])?\s*([^;,)]+)", re.I)
INSTANCE_RE = re.compile(r"(?m)^\s*(\w+)\s*(?:#\s*\(.*?\)\s*)?(\w+)\s*\((.*?)\)\s*;", re.S)
CONN_RE = re.compile(r"\.(\w+)\s*\(\s*([^)]*?)\s*\)", re.S)
SKIP_TYPES = {"always", "always_ff", "always_comb", "assign", "if", "for", "while", "case", "module"}

def clean(text):
    return COMMENT_RE.sub("", text)

def parse_ports(header):
    ports = []
    for match in PORT_RE.finditer(header):
        direction, width, names = match.groups()
        for raw in names.split(","):
            name = re.sub(r"\s*=.*$", "", raw).strip()
            name = re.sub(r"\b(?:wire|reg|logic|signed|unsigned|var|tri)\b", "", name).strip()
            if re.fullmatch(r"\w+", name):
                ports.append({"id": name, "direction": direction.lower(), "width": (width or "").strip() or None})
    return ports

def parse_file(path):
    text = clean(path.read_text(encoding="utf-8", errors="replace"))
    modules = []
    for match in MODULE_RE.finditer(text):
        name, header, body = match.groups()
        instances = []
        for inst in INSTANCE_RE.finditer(body):
            module_type, inst_name, connections = inst.groups()
            if module_type.lower() in SKIP_TYPES:
                continue
            instances.append({
                "module": module_type,
                "name": inst_name,
                "connections": {p: re.sub(r"\s+", " ", s).strip() for p, s in CONN_RE.findall(connections)}
            })
        modules.append({"name": name, "file": str(path), "ports": parse_ports(header), "instances": instances})
    return modules

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="RTL files or directories")
    ap.add_argument("-o", "--output", default="rtl-inventory.json")
    args = ap.parse_args()
    files = []
    for value in args.paths:
        path = Path(value)
        files.extend([path] if path.is_file() else sorted(p for p in path.rglob("*") if p.suffix.lower() in {".v", ".sv"}))
    modules = [m for path in files for m in parse_file(path)]
    result = {"modules": modules, "warnings": ["First-pass regex inventory: verify macros, interfaces, generate blocks, and parameterized syntax manually."]}
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"wrote {args.output}: {len(files)} files, {len(modules)} modules")

if __name__ == "__main__":
    main()
