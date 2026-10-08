# td-210 — assembler's independent Tenjin scaling finding

User relayed this finding on 2026-10-07 (America/Los_Angeles). This is steering for the existing td-210 owner, not a new task or environment. Preserve Astra High and the canonical scope/review gates.

The assembler independently measured that **shared materials and cache clearing already work**. The main scaling cost is **5,384 clipped variants expanded into 758,474 triangles**, with approximately **1.43 seconds clipping, 0.86 seconds placing and 0.25 seconds flushing**. Do not assume material duplication is the cause.

Preserve shared full-module geometry with **spatially bounded instancing**, and reserve merged geometry for **unique cropped ends**. Validate the chosen implementation against unchanged reviewed Tenjin handoff `0b2652bc86b6824444af277fdb34af5bdd981066`, runtime `6f7818b45cd09ade3ca621354ce4eb116050a66b`. Keep measured prototype equivalence, stage timings, retained/peak memory and final district deltas explicit.

Do not reduce architecture or art to fit the temporary pack limit. The assembler now owns a **separate bounded larger-build packaging implementation**. td-210 still measures and reports its actual export size/content and preserves required export inclusions; it does not take over distribution implementation.

Commit this feedback with the next ordinary worker checkpoint so it survives the session. Root delivered this file path to the existing worker once; no second implementation owner or external cloud task was created.
