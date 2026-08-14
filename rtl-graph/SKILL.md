---
name: rtl-graph
description: Generate, repair, and visually validate clean RTL architecture and module block diagrams from Verilog or SystemVerilog without Yosys. Use for RTL hierarchy diagrams, data-flow block diagrams, clock/reset/CDC views, draw.io diagrams, Graphviz diagrams, or when existing RTL diagrams have cluttered shapes, inconsistent colors, poor alignment, overlapping lines, or excessive detail.
---

# RTL Graph

Create readable architecture diagrams from RTL source without requiring synthesis. Treat source-derived connectivity as facts, semantic grouping as inference, and layout as a deterministic geometry problem.

## Workflow

1. Inventory the requested top module and recursively inspect only relevant `.v`, `.sv`, and include files.
2. Run `scripts/rtl_extract.py` for a first-pass module/port/instance inventory. Treat its output as a draft: verify parameterized interfaces, interfaces/modports, generate blocks, macros, binds, and implicit connections against source.
3. Choose exactly one view per diagram:
   - hierarchy: module instances and boundaries;
   - datapath: meaningful registers, memories, FIFOs, muxes, arithmetic blocks, and buses;
   - control: FSMs, enables, handshakes, interrupts, and status;
   - clock-reset: clock domains, resets, synchronizers, and CDC boundaries.
4. Build or refine the normalized JSON described in `references/graph-schema.md`. Collapse implementation detail that does not help the selected view. Preserve uncertainty in `notes`; never invent connectivity.
5. Run `scripts/graph_lint.py graph.json`. Resolve every error and review warnings.
6. Lay out left-to-right with fixed ports. Prefer an available ELK/ELK.js integration. Otherwise run `scripts/render_dot.py graph.json -o graph.dot` and render with Graphviz. For a dependency-free preview, run `scripts/render_svg.py graph.json -o graph.svg`; use it only for small acyclic drafts. When a draw.io MCP is available, create `mxGraphModel` cells from the computed layout instead of asking the model to improvise coordinates.
7. Render the finished diagram to SVG or PNG. Inspect the actual image, not only XML or DOT. Iterate until it passes both geometry lint and the visual checklist below.
8. Deliver the editable source plus a rendered preview. State which relationships were inferred rather than directly parsed.

## Layout contract

- Use left-to-right primary data flow. Put inputs on WEST and outputs on EAST.
- Use orthogonal edges. Route feedback below the main flow and clocks/resets on a top or bottom rail.
- Align nodes to a grid. Use consistent widths within a semantic tier and at least 40 px node spacing.
- Use containers for hierarchy or clock domains, but avoid more than two visible nesting levels.
- Replace long cross-page edges with paired named connectors when direct routing harms readability.
- Bundle related data signals; label buses as `name[msb:lsb]`. Do not draw every bit.
- Split diagrams when there are more than about 20 nodes or 30 visible edges unless the overview remains sparse.

Read `references/style-guide.md` before styling or reviewing a rendered result.

## Visual QA

Render after every material layout change. Inspect at normal viewing scale and answer all of the following:

- Is the primary flow obvious within three seconds?
- Are any nodes, labels, ports, or arrowheads clipped or overlapping?
- Does any edge cross a node, label, or unrelated container boundary?
- Are avoidable edge crossings, parallel-edge collisions, or ambiguous junctions present?
- Are node sizes, gaps, fonts, line weights, and corner radii consistent?
- Are colors semantic and within the approved palette?
- Can clock/reset/CDC paths be distinguished without dominating the datapath?
- Is text legible in the exported image without zooming excessively?

If any answer is unfavorable, change the graph structure or layout constraints before applying cosmetic tweaks. Re-render and inspect again. Do not claim visual validation unless the rendered artifact was actually viewed.

## Tool selection

- Use ELK.js when automatic port-aware layered layout is available. It is optional and may be installed locally with `npm install elkjs`.
- Use Graphviz `dot` as the lightweight deterministic fallback. If unavailable, still emit valid DOT for rendering elsewhere.
- Use `render_svg.py` only as a small-diagram preview fallback; ELK or Graphviz remains preferable for dense or cyclic graphs.
- Use draw.io for editable delivery and final manual adjustment, not for unconstrained automatic layout.
- Do not install or invoke Yosys for this workflow.

## Failure handling

- For unsupported SystemVerilog constructs, record the limitation and verify manually from source.
- If the diagram remains dense after layout tuning, split it by view, hierarchy, pipeline stage, or clock domain.
- If source connectivity is ambiguous because of preprocessing, ask for the active define/include configuration or label the uncertain edge.
