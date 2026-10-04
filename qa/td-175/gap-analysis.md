# td-175 — Gap analysis: assembled Showa scene vs the 80s-anime cel vision

Date: 2026-10-04. Scene: `godot/scenes/districts/bay_strait.tscn` on main @ 8265a932,
plus minimal toon wiring (sky + ground) done at assembly time.
Screenshots: `wide.png` (elevated establishing), `chase.png` (behind-car).
Benchmarks: `art-reference/showa-benchmark/` (4 canonical images, all opened and studied).

Merged anime work present at assembly: td-155 (bible), td-156 (toon kit),
td-165 (vending/phone booths), td-170 (map framework), td-171 (void purge).
NOT merged (excluded): td-157, td-163, td-164, td-168, td-172.

## The honest verdict

Craig is right: the references and 2D mocks look great, the 3D reads as terrible.
Having the whole scene in front of me, here is why — no sugarcoating.

### Gap 1 — The ground is a black void (scene-killer)
In every night benchmark, the road is the emotional center of the frame: wet
asphalt carrying long vertical streaks of red taillight, warm sodium, and
neon reflections. In our assembled scene the plaza/ground renders essentially
BLACK in both shots. No reflection, no light response, no texture — a hole in
the middle of the frame. The toon ground shader receives almost no light, and
there is no wet-look treatment at all. Until the ground reads as a lit surface,
nothing else matters: the eye falls into the void.

### Gap 2 — The toon kit is merged but unwired (shelfware)
td-156's cel shader kit merged to main, but at assembly time it was applied to
*nowhere* in the scene. The assembly worker had to hand-wire it to sky and
ground only. Every building — ~90% of the pixels — still renders with its baked
GLB StandardMaterial3D: smooth PBR-ish gradient falloff, exactly what the
anime-strokes skill forbids. The intended auto-assign path (td-161 import hook)
is not merged, so the kit cannot reach GLB assets. A merged shader that touches
no geometry is not a visual feature.

### Gap 3 — Zero ink outlines
The single most recognizable anime-strokes signature — crisp, uniform dark
linework on every structural edge — is completely absent. Building edges,
window frames, the car's silhouette, guardrails: all soft anti-aliased edges
with no dark contour. The inverted-hull `Mat_Ink_Outline` pass from the skill
was never applied to any shipped asset. Without ink, flat colors read as
"low-poly 3D" instead of "cel drawing."

### Gap 4 — Street level is empty
The benchmarks are dense at eye level: vertical kanban signs, striped awnings,
utility poles with wire webs, sodium streetlamps, glowing vending banks. Our
scene has two office towers, a distant bridge, 4 vending machines, and 2 phone
booths — then nothing. No signs, no poles, no wires, no awnings, no lamps.
The five still-open tasks (td-157 textures, td-163 poles, td-164 signs,
td-168 furniture, td-172 awnings) are precisely the street-level density work.
The scene cannot read as a Showa street until they land; it currently reads as
two towers in a parking lot at midnight.

### Gap 5 — No night light design
The benchmarks' warmth is deliberate: sodium-vapor practicals with visible
warm pools on the pavement, red/white glow accents, starburst lamp flares.
Our scene has a cool directional key light and darkness. No practical
streetlights are placed, no warm point lights, no emissive glow tuning (the
td-165 light_pool renders as a brown dome under direct light — a real defect
found at assembly). The white chase sedan is lit flat gray with smooth
gradient shading on the body panels — PBR falloff, no cel bands, desaturated.
The hero of a driving game currently looks like an untextured placeholder.

## What actually works
- The toon sky (indigo bands + stars) reads correctly in both shots.
- Building windows as flat lit rectangles (orange/blue) are close to the
  benchmark language — they just need ink frames.
- The td-165 vending bank + phone booths place correctly and read at distance.
- The bridge silhouette in the distance gives the right depth cue.

## Priority order (my take, before Gemini)
1. Ground: lit wet-asphalt treatment (light response + reflection streaks).
2. Wire the toon kit to real geometry (buildings, props, car) — merge the
   GLB auto-assign path or hand-assign; a shelfware shader helps no one.
3. Ink outlines on everything (inverted hull on car + hero props at minimum).
4. Land the street-level density tasks (signs, poles, awnings first — they
   carry the Showa read).
5. Night light design pass: sodium practicals, warm pools, glow tuning,
   and a proper hero-car paint job (saturated color + cel bands).
