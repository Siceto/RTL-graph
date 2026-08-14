# Normalized graph schema

Use this compact JSON contract between RTL inspection and layout:

```json
{
  "title": "Top datapath",
  "view": "datapath",
  "direction": "RIGHT",
  "nodes": [
    {
      "id": "fifo",
      "label": "RX FIFO",
      "kind": "storage",
      "parent": null,
      "clock_domain": "rx_clk",
      "ports": [
        {"id": "din", "label": "din[31:0]", "direction": "input", "side": "WEST"},
        {"id": "dout", "label": "dout[31:0]", "direction": "output", "side": "EAST"}
      ]
    }
  ],
  "edges": [
    {
      "id": "packet_data",
      "source": "parser.data",
      "target": "fifo.din",
      "label": "packet_data[31:0]",
      "kind": "data",
      "inferred": false
    }
  ],
  "notes": []
}
```

Required top-level fields: `title`, `view`, `nodes`, `edges`. Valid views are `hierarchy`, `datapath`, `control`, and `clock-reset`.

Node `id` values must be unique and stable. Valid node kinds are `logic`, `storage`, `control`, `interface`, `clock`, and `container`. A port endpoint is written as `node_id.port_id`; a node-only endpoint is permitted for hierarchy edges.

Valid edge kinds are `data`, `control`, `clock`, `reset`, `cdc`, and `hierarchy`. Set `inferred` to true when semantic analysis rather than direct syntax establishes a relationship. Put unresolved details in `notes` instead of guessing.

Optional layout fields such as `x`, `y`, `width`, and `height` may be attached after layout. Keep them out of the source-of-truth graph when possible.
