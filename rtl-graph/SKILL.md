---
name: rtl-graph
description: Generate, repair, and visually validate concise module-centric RTL data-flow diagrams from Verilog or SystemVerilog without Yosys. Use when a user names a concrete RTL module and wants a draw.io, SVG, or Graphviz diagram focused on how primary data and essential control move between that module and its relevant child-module instances, while omitting routine ports, clocks, resets, configuration, status, and incidental logic.
---

# RTL Graph

Create a restrained data-flow diagram whose scope is one concrete RTL module. Explain the important processing path across relevant module instances, not the complete port list or every connection.

## Non-negotiable default

- Make the user-selected module the single scope boundary and visual focus.
- Show the direct child instances that participate in the primary data path. Omit unrelated instantiated modules.
- Show only boundary ports and internal nets needed to trace primary data from input, through processing modules, to output.
- Show a control signal only when it changes data-path behavior or is required to understand a transfer, such as `valid`, `ready`, `enable`, `select`, `grant`, `flush`, or a write/read qualifier.
- Omit clocks and resets unless the user explicitly asks for timing, CDC, or reset structure.
- Omit routine configuration, debug, scan, status, counters, interrupts, error reporting, and unused sideband signals unless they directly determine the shown data path.
- Prefer one labeled bus edge over multiple related scalar edges. Combine handshake pairs when practical, for example `valid/ready`.
- Do not infer FIFO, FSM, arbiter, mux, pipeline, interface, clock-domain, datapath, or control blocks from `always`, `assign`, signal names, or general RTL behavior.
- Do not add legends, notes boxes, protocol blocks, input/output interface blocks, clock/reset blocks, domain containers, or decorative junctions unless the user explicitly requests them.
- Do not recursively expand grandchildren or show leaf implementation logic by default.
- If the user does not specify a module, ask for the exact module name before drawing.

## Workflow

1. Locate the exact requested module and inspect its declaration, direct instances, net connections, assignments, and mux/enable conditions that determine inter-module data movement.
2. Run `scripts/rtl_extract.py` for a first-pass module/port/instance inventory. Treat its output as a draft: verify parameterized interfaces, interfaces/modports, generate blocks, macros, binds, and implicit connections against source.
3. Trace candidate paths from meaningful module inputs to outputs. Rank signals as `primary-data`, `key-control`, or `omit` using the rules above.
4. Build the normalized JSON described in `references/graph-schema.md`. Include the focus boundary, relevant direct instances, primary-data edges, and the minimum key-control edges needed to explain selection or transfer.
5. Compare every node and edge against source syntax. Remove connections that add completeness but not understanding. Never invent functional blocks.
6. Run `scripts/graph_lint.py graph.json`. Resolve every error and review warnings.
7. Lay out primary data left-to-right. Prefer ELK/ELK.js; otherwise use `scripts/render_dot.py`, or `scripts/render_svg.py` for a small acyclic preview. When draw.io MCP is available, create cells from computed layout rather than improvising coordinates.
8. Render to SVG or PNG and inspect the actual image. Iterate until it passes geometry lint and visual QA.
9. Deliver editable source plus preview. Mention intentionally omitted signal categories, not every omitted signal.

## Layout contract

- Put the selected primary input at the left boundary, processing instances in flow order, and the selected output at the right boundary.
- Use orthogonal edges. Route feedback below the main flow and key control above or below it.
- Align nodes to a grid. Use consistent widths within a semantic tier and at least 40 px node spacing.
- Use at most one focus-module container and one level of direct child instances.
- Replace long cross-page edges with paired named connectors when direct routing harms readability.
- Make primary-data edges visually stronger than key-control edges. Label buses as `name[msb:lsb]`; use thin dashed lines for key control.
- Treat more than 12 child instances as a signal to group or omit details, not to invent higher-level functional blocks.

Read `references/style-guide.md` before styling or reviewing a rendered result.

## Visual QA

Render after every material layout change. Inspect at normal viewing scale and answer all of the following:

- Is the requested module unmistakably the main subject within three seconds?
- Does every non-focus node map to a relevant explicit direct instance in the source?
- Can a reviewer trace the main input-to-output data path without reading the RTL?
- Are only necessary boundary ports, primary-data buses, and key-control signals shown?
- Have clocks, resets, configuration, debug, status, and unrelated sidebands been omitted by default?
- Are any nodes, labels, ports, or arrowheads clipped or overlapping?
- Does any edge cross a node, label, or unrelated container boundary?
- Are avoidable edge crossings, parallel-edge collisions, or ambiguous junctions present?
- Are node sizes, gaps, fonts, line weights, and corner radii consistent?
- Are colors semantic and within the approved palette?
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
- If the diagram remains dense, remove secondary controls and unrelated instances before changing layout or adding pages.
- If source connectivity is ambiguous because of preprocessing, ask for the active define/include configuration or label the uncertain edge.
