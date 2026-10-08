# td-210 — protected AnimeLook scope response

The worker found that AnimeLook._toon_tree mutates MultiMesh.mesh material surfaces for each node, so sharing one mutable mesh across cells repeats toon conversion. The proposed per-traversal seen-mesh dictionary is a concrete potential fix, but Craig explicitly excludes AnimeLook changes and another owner is investigating it. Root has not authorized that edit.

First measure an in-scope placement alternative: one mesh resource per bounded module/tint cell, shared by all repeated instances within that cell, while retaining canonical source/module arrays and shared source materials during construction. This keeps module geometry instanced instead of expanded per building. The prototype's two-cell example would still store approximately two copies rather than 24; actual native memory, array bytes, startup and material conversions must be measured, not assumed. Do not alter palette, globals, visibility or source art.

Keep the all-cells-shared prototype as a valid geometry-storage experiment, clearly distinguish the shipping-compatible topology, and verify exactly one toon conversion per cell resource, baked ink, retained material references and native/browser appearance. Avoid one mesh per placement. Unique cropped ends can retain the merged backend.

If this bounded alternative has demonstrated unacceptable costs or cannot preserve intended output, report measured evidence and a precise reviewable minimal AnimeLook diff to root before editing protected code; the explicit scope exception would require Craig's decision. Continue independent in-scope work meanwhile. This is not an independent acceptance verdict.
