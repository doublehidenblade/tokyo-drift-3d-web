# td-175 — Iteration list: what to fix, in priority order

Source: honest gap analysis (`gap-analysis.md`) + Gemini vision consult 2026-10-04
(Gemini saw wide.png, chase.png, and 2 canonical benchmarks; techniques below
are Gemini's, adapted to Godot 4.7 gl_compatibility / mobile-class).
Ordered by visual impact per unit of work. One defect per follow-up task.

## td-176 — Wet-road ground treatment
**Defect:** Ground renders as a black void; benchmarks' wet asphalt with long
light streaks is the emotional center of every night frame.
**Fix:** Deep slate-indigo albedo (#181a24) + painted lane markings/stop diamonds
in the texture; fake wet reflections via anisotropic specular (low roughness,
tangent along road axis stretches point/spot highlights into vertical smears —
no SSR in gl_compatibility); additive taillight-smear quads behind cars.
**Payoff:** Kills the "floating in space" feel; anchors every night shot.

## td-177 — Ink outlines on everything (inverted hull)
**Defect:** Zero structural linework; scene reads as soft early-2000s low-poly,
not 80s cel.
**Fix:** Inverted-hull `next_pass` material (cull_front, unshaded, vertex extrude
along normal with depth-scaled width ~0.025, dark navy outline color) on hero
car, building shells, street furniture. NOT fullscreen edge-detect (too slow on
mobile gl_compatibility).
**Payoff:** The single most recognizable anime signature, applied everywhere.

## td-178 — Wire the td-156 cel kit to real geometry
**Defect:** td-156 merged but applied to nothing; 90% of pixels still smooth
PBR gradients.
**Fix:** `EditorScenePostImport` script that swaps StandardMaterial3D → cel
shader on GLB import (preserving diffuse/emissive textures); hard-stepped
2-tone lighting (1 shadow band + 1 light band, cool indigo shadow tint).
Unblocks the shelfware kit for every GLB asset, present and future.
**Payoff:** Flat poster-color blocks replace muddy gradients across the scene.

## td-179 — Night light design: sodium practicals
**Defect:** Sterile cool directional key; no warm pools, no streetlamps, broken
td-165 light_pool (brown dome under direct light).
**Fix:** Drop directional to 0.05 (moonlight fill only); reusable StreetLamp
scene — mast + warm sodium OmniLight3D (#FFA030, energy 2.5, range 12m) +
billboarded hand-drawn starburst flare quad at the bulb; fix light_pool.glb
material response.
**Payoff:** The indigo-vs-sodium chromatic contrast that defines Showa night.

## td-180 — Hero car 80s makeover
**Defect:** Rounded modern silver sedan, smooth shading, dark unlit taillights —
a placeholder, not a hero.
**Fix:** Angular 80s wedge silhouette (AE86/Celica XX language, rectangular
tail cluster); saturated paint (blue #1e40aa or classic white) under the td-178
cel shader + td-177 ink hull; pure emissive red taillights (#ff2010) with a
rear-facing red light bouncing off the wet road.
**Payoff:** The gameplay focal point finally signals the era and lights the road.

## td-181 — Street-level density (land td-163/td-164, then wire)
**Defect:** Two towers in an empty corridor; benchmarks are dense at eye level.
**Fix:** Land td-163 (poles) + td-164 (signs) first, then place along curbs every
15–20m; procedural wire generator (sagging catenary ribbons, unshaded charcoal)
between pole crossbars; vertical kanban with emissive faces + ink borders.
**Payoff:** The messy vertical framing that funnels perspective down the street.

## td-182 — Horizon glow + Tokyo Tower landmark
**Defect:** Dead navy-to-black horizon cut; no vanishing-point anchor.
**Fix:** Sky-shader horizon ribbon (warm pink-orange smog bleed via EYEDIR.y
mask); low-poly Tokyo Tower silhouette dead-center on the vanishing point,
2-tone red/white emissive with tip beacons.
**Payoff:** The definitive Showa Tokyo signature; pulls the eye down the road.
