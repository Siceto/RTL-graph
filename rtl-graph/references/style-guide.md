# RTL diagram style guide

Use one restrained palette. Color may distinguish broad module functions, but keep the box label equal to the RTL module type name:

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

For the default module-dataflow view, render every retained edge as a 2 px solid data edge. Do not render control, clock, or reset lines.

Keep edge labels short and data-oriented. Prefer `packet`, `pixels`, `samples`, `addr[31:0]`, or `data[63:0]`. Never label an edge `valid`, `ready`, `enable`, or another control signal.
