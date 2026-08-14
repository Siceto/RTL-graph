---
name: rtl-graph
description: Generate, repair, and visually validate module-centric RTL data-flow diagrams from Verilog or SystemVerilog without Yosys. Use when a user names a concrete RTL module and wants a draw.io, SVG, or Graphviz diagram that keeps every necessary child module on the main data path, labels boxes with module type names, and shows data movement while omitting port lists, internal signal text, valid/ready/control lines, clocks, resets, and unrelated logic.
---

# RTL Graph

Create a balanced data-flow diagram whose scope is one concrete RTL module. Preserve the necessary chain of child modules that transforms, buffers, routes, or emits the main data; simplify signals, not the module structure.

## Non-negotiable default

- Make the user-selected module the single scope boundary and visual focus.
- Show every direct child module that participates in the primary data path. Do not collapse a multi-module chain into one generic block.
- If a relevant child is only a wrapper and its internal submodules are necessary to understand the data transformation, expand that child by one additional level. Stop when the functional path is understandable.
- Show only boundary ports and internal nets needed to trace primary data from input, through processing modules, to output.
- Draw data edges only. Omit `valid`, `ready`, `enable`, `select`, `grant`, `flush`, read/write qualifiers, FSM transitions, and other control-flow signals.
- Omit clocks and resets unless the user explicitly asks for timing, CDC, or reset structure.
- Omit routine configuration, debug, scan, status, counters, interrupts, error reporting, and unused sideband signals unless they directly determine the shown data path.
- Prefer one data edge per logical payload or bus. Edge labels may name the data object or bus, but keep them short.
- Do not infer FIFO, FSM, arbiter, mux, pipeline, interface, clock-domain, datapath, or control blocks from `always`, `assign`, signal names, or general RTL behavior.
- Do not add legends, notes boxes, protocol blocks, input/output interface blocks, clock/reset blocks, domain containers, or decorative junctions unless the user explicitly requests them.
- Do not recursively expand grandchildren or show leaf implementation logic by default.
- If the user does not specify a module, ask for the exact module name before drawing.

## Workflow

1. Locate the exact requested module and inspect its declaration, direct instances, net connections, assignments, and mux/enable conditions that determine inter-module data movement.
2. Run `scripts/rtl_extract.py` for a first-pass module/port/instance inventory. Treat its output as a draft: verify parameterized interfaces, interfaces/modports, generate blocks, macros, binds, and implicit connections against source.
3. Trace data dependencies from meaningful module inputs to outputs across instance port mappings, assignments, and intermediate nets. Compute the data-path module cone: retain every instantiated module touched by those dependencies.
4. Build the normalized JSON described in `references/graph-schema.md`. Include the focus boundary, all necessary data-path modules, and data edges only.
5. Compare every node and edge against source syntax. Remove connections that add completeness but not understanding. Never invent functional blocks.
6. Run `scripts/graph_lint.py graph.json`. Resolve every error and review warnings.
7. Lay out primary data left-to-right. Prefer ELK/ELK.js; otherwise use `scripts/render_dot.py`, or `scripts/render_svg.py` for a small acyclic preview. When draw.io MCP is available, create cells from computed layout rather than improvising coordinates.
8. Render to SVG or PNG and inspect the actual image. Iterate until it passes geometry lint and visual QA.
9. Deliver editable source plus preview. Mention intentionally omitted signal categories, not every omitted signal.

## Layout contract

- Put the selected primary input at the left boundary, processing instances in flow order, and the selected output at the right boundary.
- Use orthogonal data edges. Route feedback below the main flow.
- Align nodes to a grid. Use consistent widths within a semantic tier and at least 40 px node spacing.
- Use at most one focus-module container and one level of direct child instances.
- Replace long cross-page edges with paired named connectors when direct routing harms readability.
- Use consistent solid data edges. Label only useful data objects or buses such as `pixels`, `packet`, or `data[31:0]`.
- When many instances participate, preserve the end-to-end module chain and group parallel lanes only if their function and ordering remain clear.

Read `references/style-guide.md` before styling or reviewing a rendered result.

## Visual QA

Render after every material layout change. Inspect at normal viewing scale and answer all of the following:

- Is the requested module unmistakably the main subject within three seconds?
- Does every non-focus node map to a relevant explicit direct instance in the source?
- Can a reviewer trace the main input-to-output data path without reading the RTL?
- Are all necessary data-path modules present, with no unexplained jump between distant stages?
- Do internal boxes contain only module type names, with no port lists, signal names, widths, or instance-name prefixes?
- Are only data-flow arrows shown, with no `valid`, `ready`, enable, selection, or other control lines?
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
- If the diagram remains dense, remove signal labels and unrelated instances first; do not remove necessary data-path modules.
- If source connectivity is ambiguous because of preprocessing, ask for the active define/include configuration or label the uncertain edge.
