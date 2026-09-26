---
name: pngtuber-generator
description: >
  Generate PNGTuber-Plus avatars as aligned PNG layers and pack them into a
  .pngtuber file. Use when making a PNGTuber, VTuber PNG avatar, talk/blink
  mouth and eye layers, or when the user runs /pngtuber-generator.
---

# PNGTuber generator

PNGTuber-Plus loads a JSON `.pngtuber` (legacy `.save` still opens) whose sprites are stacked PNGs. The product is a **loadable avatar**, not a pretty composite.

Load `game-asset-core` and `game-character-consistency` before generating art. Load `imagine` when using Grok image tools. Field meanings and PNG layering (`parentId` vs `zindex`) live in `references/avatar-format.md`. Shader candidates live in `references/shader-options.md`. Do not restate those files here.

## Default kit

Unless the user names a different split, generate these layers on **one shared canvas** (same width/height, subject locked in place):

| file | role |
|---|---|
| `body.png` | torso / legs / whatever does not move with the head |
| `head.png` | face base **without** mouth or eyes |
| `hair.png` | hair behind or around the head (omit if hair is baked into head) |
| `mouth_closed.png` | mouth only, silent |
| `mouth_open.png` | mouth only, talking |
| `eyes_open.png` | open eyes only |
| `eyes_closed.png` | closed / blink eyes only |
| extra `.png` | hat, extra costume, props — same canvas |

Do **not** split open-eyes into talking vs silent copies unless the eye art itself changes with the mouth.

Minimum that still talks and blinks: `body`, `head`, `mouth_closed`, `mouth_open`, `eyes_open`, `eyes_closed`.

**Mouth strip (optional):** one `mouth.png` horizontal sheet instead of closed/open files. Frame 0 = rest, later cells more open. `showTalk` 0. `talkAnim` modes (sprite editor labels):

| `talkAnim` | name | use |
|---|---|---|
| 0 | loop (idle) | Timer cycle; not a mouth. Default for old avatars. |
| 1 | talk loop | Rest on silence; chatter frames while speaking. |
| 2 | volume frames | Mic loudness picks the cell (closed → wide). |

Field semantics stay in Animation strips in `references/avatar-format.md`. Example pack: `scripts/example_mouth_strip.json`.

## Art rules

1. **Shared canvas.** Every layer is the full avatar frame. Empty pixels are transparent. `pos` stays `Vector2(0, 0)` so the app does not have to guess offsets. Parenting is motion; `zindex` is draw order — Layering in `references/avatar-format.md`.
2. **True alpha.** Generate on a flat key color `#FF00FF`, then run `scripts/key_background.py`. Do not trust the image model to emit transparency.
3. **No baked scene.** No floor, shadow blob, or background furniture.
4. **Edit-chain.** One assembled canonical image first. Isolate every layer from that image (`image_edit` or equivalent: keep pose, scale, and framing, show only that part, rest of canvas key color). Mouth/eye states are edits of the face, not new characters.
5. **Mouth and eyes do not overlap other face paint.** Head base has blank mouth and eye holes (skin/face color in those holes is OK; do not draw a second mouth on the head).
6. **Pixel-art vs paint.** Match the user's style. This app defaults to unfiltered nearest-neighbor (`textures/canvas_textures/default_texture_filter=0`), so crisp pixels survive; soft paint is fine if requested.
7. **Do not bake shader looks.** No outline, glow, drop shadow, hue wash, or wind lean in the PNG. Those are shader options (`references/shader-options.md`). Motion (bounce, idle wobble, head drag, talk/blink swap) stays in the rig, not in the image.

## Motion defaults (first load should already bounce)

Use the default avatar's rig unless the user asks otherwise:

- `body`: root, `zindex` -1, light idle wobble (`xAmp` 9, `xFrq` 0.004, `yAmp` 11, `yFrq` 0.008), `stretchAmount` 0.25
- `head`: child of body, `drag` 1
- `hair`: child of head, `zindex` -2, `stretchAmount` 2
- mouths / eyes / extras: child of head
- `mouth_closed`: `showTalk` 1
- `mouth_open`: `showTalk` 2
- or one mouth strip: `showTalk` 0, `talkAnim` 1 or 2
- `eyes_open`: `showBlink` 1
- `eyes_closed`: `showBlink` 2
- hats: child of head, small `rotDrag` and tight `rLimitMin`/`rLimitMax` so they tilt, not spin

Costume extras: set `costumeLayers` so the extra is `1` only on the costumes it belongs to; base body/head/face stay all `1`s. Keyboard switching is **costume keys** in app settings, not the avatar file — see Costumes in `references/avatar-format.md`.

## Pipeline

1. Lock a written kit (files + parent + talk/blink + z; `talkAnim` if using a mouth strip).
2. Generate the canonical assembled character (front, stream-cam framing, key-color background).
3. Derive each layer from that canonical image. Verify by compositing in code: body+head+hair+silent mouth+open eyes must match the canonical; swapping mouth/eyes must not shift the face.
4. Key magenta → alpha (`scripts/key_background.py`).
5. Write `layers.json` next to the PNGs (see `scripts/example_layers.json`).
6. Pack:

```
py -3 .grok/skills/pngtuber-generator/scripts/pack_pngtuber.py --layers <dir>/layers.json --out <dir>/<name>.pngtuber
```

7. Tell the user to **Load Avatar** on the `.pngtuber`. Keep the PNG folder; the file embeds copies but the `path` fields still point at those PNGs.

## Verify before handing off

- All PNGs identical size
- Overlay of idle layers matches the canonical (no double-mouth, no holes)
- Open mouth and blink actually change those features only
- Packed file is JSON with `imageData` on every sprite
- `parentId` of every child matches an `identification` that exists
