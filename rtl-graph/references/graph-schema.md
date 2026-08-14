# Normalized graph schema

Use this compact JSON contract between RTL inspection and layout:

```json
{
  "title": "top primary data flow",
  "scope": "module",
  "focus_module": "top",
  "view": "module-dataflow",
  "direction": "RIGHT",
  "nodes": [
    {
      "id": "top",
      "label": "top",
      "kind": "module",
      "role": "focus",
      "parent": null,
      "ports": [
        {"id": "data_in", "label": "data_in[7:0]", "direction": "input", "side": "WEST"},
        {"id": "data_out", "label": "data_out[7:0]", "direction": "output", "side": "EAST"}
      ]
    },
    {
      "id": "u_fifo",
      "label": "fifo",
      "module_type": "fifo",
      "instance_name": "u_fifo",
      "kind": "module",
      "role": "instance",
      "parent": "top",
      "ports": [
        {"id": "din", "direction": "input", "side": "WEST"},
        {"id": "dout", "direction": "output", "side": "EAST"}
      ]
    }
  ],
  "edges": [
    {"id": "data_in", "source": "top.data_in", "target": "u_fifo.din", "label": "data_in[7:0]", "kind": "data", "importance": "primary-data", "inferred": false},
    {"id": "data_out", "source": "u_fifo.dout", "target": "top.data_out", "label": "data_out[7:0]", "kind": "data", "importance": "primary-data", "inferred": false}
  ],
  "notes": []
}
```

Required top-level fields: `title`, `scope`, `focus_module`, `view`, `nodes`, and `edges`. The default values are `scope: module` and `view: module-dataflow`.

Exactly one node must have `role: focus`, and its `id` must equal `focus_module`. Other nodes must use `role: instance` and correspond to relevant explicit direct instances. Include only ports referenced by retained edges. Do not list the complete port declaration.

Node `id` values must be unique and stable. A port endpoint is written as `node_id.port_id`; a node-only endpoint is permitted for hierarchy edges.

Every internal instance node must store `module_type` and `instance_name`, but set the visible `label` to `module_type` only. Do not render instance-name prefixes, port lists, signal names, widths, or descriptions inside the box.

Every edge must use `kind: data` and `importance: primary-data`. Data includes payload, address, command, or stored data that moves through the selected module chain. In module scope, every edge must come from explicit source connectivity and use `inferred: false`. Never include valid/ready/control, clock, or reset edges in the default view.

Optional layout fields such as `x`, `y`, `width`, and `height` may be attached after layout. Keep them out of the source-of-truth graph when possible.
