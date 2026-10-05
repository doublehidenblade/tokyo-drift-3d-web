# td-glowup — Gemini consult (brief section "Learn from the industry")

Date: 2026-10-05 ~01:58Z. Model: `gemini-3.5-flash` via the generativelanguage API.
The brief's `~/workspace/skills/gemini-consult/` is not present in this cloud
container; `gemini-2.5-pro` is retired for new users and `gemini-3.1-pro-preview`
exceeded the egress proxy's 30 s limit twice with four images, so the flash model
was used with 540 px images. This consult ran late, after the main pass had been
built from td-175's earlier Gemini fix order (`godot/qa/td-175/iteration-list.md`).

Inputs: our AFTER frames `after/bridge_midpoint-portrait.jpg` and
`after/commercial_arrival-portrait.jpg` (source 074cf53) beside the targets
`night-bridge-driving.jpg` and `night-highway-driving.jpg`.

## Question (summary)

A) Which Spider-Verse / Borderlands / Kaido Genkai / NFS Unbound techniques survive
Godot 4 Compatibility on mobile-class GPUs, and what are the cheapest fakes for those
that don't? B) The 5 most visible remaining differences (ours vs target), ranked by
impact per unit of work, each with a concrete cheap Compatibility-renderer fix (no
fullscreen post, no SSR). Full prompt text: the request body is not committed (it
embeds the images); the wording is reproduced in the A/B summary above.

## Answer (verbatim)

### A) Industry Techniques & Mobile GLES3 Adaptation

#### 1. Spider-Verse (Line Work, Halftones, Stepped Frame Rate, Chromatic Aberration)
*   **How they do it:** Screen-space Sobel/Laplacian filters for lines; screen-space light-attenuated halftone pattern projections; animating rigs on "twos" or "threes" (12/8 fps); screen-space multi-tap chromatic aberration.
*   **Mobile GLES3 Survival:** **No.** Screen-space halftones and multi-tap aberration will tank fill rate on mid-range mobile GPUs.
*   **Cheapest Fake:** 
    *   *Halftones:* Bake the halftone pattern directly into the dark band of your Toon Shader’s 1D ramp texture.
    *   *Stepped Frame Rate:* **Free.** Run a simple script on your `AnimationPlayer` or vertex shader that snaps the time variable or playback step: `floor(time * 12.0) / 12.0`.
    *   *Chromatic Aberration:* Skip screen-space. Bake static red/cyan offsets directly into the UI textures and far-plane background cards.

#### 2. Borderlands (Thick Outlines, Flat Fills, Hand-Painted Details)
*   **How they do it:** Screen-space depth/normal edge detection post-process combined with highly detailed, hand-drawn PBR textures (cross-hatching in the Albedo and Detail maps).
*   **Mobile GLES3 Survival:** **Partial.** The hand-painted textures survive perfectly (texture memory is cheap); the screen-space outline post-pass does not.
*   **Cheapest Fake:** Keep your current inverted-hull approach for dynamic cars. For static environment assets (buildings, barriers), completely eliminate runtime outlines. Instead, **bake all interior ink lines, window frames, and cross-hatching directly into the Albedo textures**.

#### 3. Kaido Genkai / Inertial Drift (Anime Drift, Night Neon, Stylized Smoke)
*   **How they do it:** Heavy HDR bloom passes, custom camera-aligned vertex-sheared smoke meshes, and custom road shaders calculating real-time anisotropic specular reflections.
*   **Mobile GLES3 Survival:** **No.** True HDR bloom and complex real-time anisotropic calculations are too expensive for WebGL2/GLES3.
*   **Cheapest Fake:**
    *   *Neon Glow:* Place additive, unshaded, camera-facing billboard quads with soft-gradient textures over emissive sources (lamps, taillights).
    *   *Stylized Smoke:* Use low-poly, unshaded, hand-painted 3D mesh "puffs" that scale up and fade out via vertex color alpha, avoiding alpha-sorting issues of dense particle systems.

#### 4. NFS Unbound (Cel-Shaded Graffiti, 2D Elements in 3D)
*   **How they do it:** 2D hand-drawn vector/sprite animations attached to 3D bone sockets, spawned dynamically based on physics events (drift angle, nitro).
*   **Mobile GLES3 Survival:** **Yes.** This is highly performant.
*   **Cheapest Fake:** Spawn simple unshaded quad meshes with 2D spritesheet flipbook animations at the car's wheel sockets when drift threshold is met. Keep texture sizes small ($256 \times 256$ sheets).

---

### B) Critique & 5 High-Impact Fixes (Image 1 vs 2, Image 3 vs 4)

```
Ranked by Visual Impact per Unit of Work (Highest to Lowest)
```

#### 1. Stylized Puddle Reflections (Road Surface)
*   **Difference:** Image 1 has blurry, straight vertical streaks (Ward specular). Images 2 and 4 have highly stylized, hand-painted, horizontally-rippled red and yellow reflection shapes that perfectly match the puddle contours.
*   **Cheap Fix:** Ditch complex real-time reflection shaders. Attach a flat, horizontal quad mesh hovering $1\text{cm}$ above the road directly to the rear of the player/NPC cars. Apply an unshaded, additive material to this quad with a hand-painted, rippled taillight reflection texture. Use a simple vertex shader to gently wave/jitter the vertices horizontally over time:
    ```glsl
    VERTEX.x += sin(TIME * 10.0 + VERTEX.y) * 0.05;
    ```

#### 2. Retro Anime Starburst Flares
*   **Difference:** Image 1 uses soft, circular, fuzzy starbursts. Images 2 and 4 feature extremely sharp, 4-point and 8-point retro anime starbursts with long, thin vertical and horizontal spikes.
*   **Cheap Fix:** Replace the current billboard textures on the streetlamps and Tokyo Tower with a high-contrast, hand-painted 8-point starburst texture. Set the material to **Unshaded, Additive, with Alpha Cutoff** to keep the edges razor-sharp without relying on expensive alpha blending.

#### 3. Sky Depth & Layered Clouds
*   **Difference:** Image 1's sky is a flat, empty purple-to-blue gradient. Image 4 features a rich indigo-to-orange horizon gradient layered with soft, flat-shaded, hand-painted dark clouds.
*   **Cheap Fix:** Do not use a procedural sky. Use a low-resolution, hand-painted 2D Panorama Sky texture. To add parallax depth cheaply, place 2 or 3 flat, semi-transparent horizontal "cards" (quads) in the far distance with stylized cloud silhouettes painted on them, moving them slowly across the screen.

#### 4. Bridge Suspension Cables
*   **Difference:** Image 1 is missing the iconic diagonal suspension cables of the Rainbow Bridge, leaving the upper screen empty. Image 2 has clean, dark, hand-drawn diagonal cables draping from the towers.
*   **Cheap Fix:** Do not model these as 3D cylinders. Place two flat, double-sided 2D planes running along the sides of the bridge. Apply an unshaded, alpha-tested texture of the diagonal cables with baked black ink outlines. This adds massive structural composition for virtually zero rendering cost.

#### 5. Environment Linework & Foliage Style
*   **Difference:** Image 3's buildings lack internal details, and the trees are generic low-poly 3D blobs. Image 4's buildings have dense, hand-drawn window grids, and the trees have distinct, illustrated anime silhouettes.
*   **Cheap Fix:** 
    *   *Buildings:* Re-author the building textures to include baked-in black window frames and panel lines directly in the Albedo map.
    *   *Trees:* Replace the 3D tree meshes with flat, intersecting 2D "cross-billboard" cards featuring hand-illustrated retro anime trees with thick ink outlines. This simultaneously reduces primitive count and aligns perfectly with the 1980s cel aesthetic.

## Evaluation — what was adopted

| Gemini item | Verdict | Why / what was done |
|---|---|---|
| B1 reflections should follow puddle contours, broken horizontal ripples | **Adopted** | Taillight streaks sample the road's own puddle noise in world space: strong in wet patches, faint on dry asphalt, horizontal ripple gaps and a slow wobble. |
| B2 sharper 4/8-point starbursts with long thin spikes | **Adopted** | Flare shader: tighter core, thinner/longer cardinal spikes, short diagonals, weaker halo. |
| B3 clouds in the sky | Deferred | Only the night-street target has clouds; the hero bridge target is clear and starry. Follow-up. |
| B4 "missing bridge cables" | Rejected (incorrect) | Main catenary cables and hangers exist; they are thin dark lines that vanish at the 540 px images sent. |
| B5 tree blobs need ink | **Adopted (cheap form)** | Rim ink on the batched foliage spheres (view-angle silhouette darkening) instead of re-authoring trees as cards. |
| B5 bake window frames into albedo | Already covered | Procedural fwidth edge ink already frames every window pane. |
| A: Ward anisotropic "too expensive" | Rejected (measured) | The per-light Ward lobe on road sections measured within noise on llvmpipe (`profile-frame-cost.txt`). |
| A: stepped frame rate, halftone in shadow band, NFS-style 2D drift sprites | Follow-up | Gameplay-feel changes outside the brief's visual priority list; logged for a later task. |
