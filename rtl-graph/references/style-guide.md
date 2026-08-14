# RTL diagram style guide

Use one restrained palette:

| Meaning | Fill | Stroke |
|---|---|---|
| Logic | `#F8FAFC` | `#475569` |
| Storage/FIFO/register | `#DBEAFE` | `#2563EB` |
| Control/FSM | `#FFEDD5` | `#EA580C` |
| External interface | `#DCFCE7` | `#16A34A` |
| Clock/CDC | `#F3E8FF` | `#9333EA` |
| Container | `#FFFFFF` | `#94A3B8` |

Use rounded rectangles for functional blocks, plain containers for hierarchy/clock domains, and at most one alternate shape for explicit junctions. Use a single sans-serif font, 11–12 px labels, 1–1.5 px strokes, and 6–8 px corner radii.

Use dark gray solid lines for data, blue-gray solid lines for control, purple dashed lines for clock/CDC, and red only for a specifically requested error path. Use thicker lines for buses, not additional colors. Avoid gradients, shadows, 3D effects, decorative icons, and per-module colors.

For the default module-dataflow view, emphasize `primary-data` with 2 px solid edges and render `key-control` with 1 px dashed edges. Do not include clock/reset styling unless the user explicitly requests those signals.

Keep edge labels short. Prefer `valid`, `ready`, `addr[31:0]`, or `data[63:0]`; move protocol explanations into notes or a legend.
