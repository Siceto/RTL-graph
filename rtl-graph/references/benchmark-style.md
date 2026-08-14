# Benchmark-derived draw.io style

Use these rules when the user expects a concise engineering block diagram rather than a polished architecture poster.

- Preserve the literal instance topology. Render repeated modules as repeated boxes in stage/index order.
- Use a flat canvas. A chain may have one light dashed/background strip and a plain label; avoid nested swimlanes.
- Put repeated processing stages in one row. Align related context/parity/helper modules directly above the corresponding stage.
- Use one horizontal rail for a shared wide bus and short vertical taps into each stage.
- Use horizontal arrows for stage-to-stage payload/state propagation.
- Put external bus names at the boundary as plain text or a small neutral box.
- Use compact, mostly square-cornered module boxes. Keep same-type instances identical in size and color.
- Limit the palette to roughly three functional colors plus neutral gray.
- Keep module type names inside boxes. Put data-slice labels on edges, never inside boxes.
- Omit control-only muxes, handshake signals, stage badges, multiplicity badges, decorative port dots, and explanatory panels.
- Treat wide state/context/parity buses as data when they are the payload exchanged by functional modules.
- Retain any explicitly instantiated module on the traced payload dependency even if its name suggests configuration, bonding, adaptation, or glue logic.
