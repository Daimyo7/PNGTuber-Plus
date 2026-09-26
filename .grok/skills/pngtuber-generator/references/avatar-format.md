# PNGTuber-Plus avatar format

Written by `main_scenes/main.gd` (`_on_save_dialog_file_selected`) and read by `_on_load_dialog_file_selected`. New files use extension `.pngtuber`. Older `.save` files are the same JSON.

## File

- UTF-8 JSON, one object
- Keys are `"0"`, `"1"`, `"2"`, … (stringified insertion order, not `identification`)
- Each value is one sprite
- Images are PNG bytes in `imageData` (standard Base64). Load tries `path` first, then `imageData`

Godot string forms (must match exactly):

- Vector: `"Vector2(0, 0)"` (space after comma)
- Costume list: `"[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]"` (10 ints, `1` = visible on that costume)
- `parentId`: JSON `null` or an integer
- `toggle`: `"null"` when unused (string, not JSON null)

## Sprite fields

| field | type | meaning |
|---|---|---|
| `type` | string | always `"sprite"` |
| `path` | string | original PNG path (absolute or `user://…`) |
| `imageData` | string | Base64 PNG |
| `identification` | int | unique id; children point here |
| `parentId` | int or null | motion parent `identification`, or `null` for a root (see Layering) |
| `pos` | Vector2 string | node position vs parent |
| `offset` | Vector2 string | sprite draw offset |
| `zindex` | int | global draw order (see Layering) |
| `drag` | number | follow lag; `0` = locked, `1` = typical head |
| `xFrq` `xAmp` `yFrq` `yAmp` | number | idle wobble |
| `rotDrag` | number | tilt from bounce (`rdragStr`) |
| `rLimitMin` `rLimitMax` | number | tilt clamp in degrees, default `-180` / `180` |
| `stretchAmount` | number | squash/stretch from bounce |
| `ignoreBounce` | bool | skip bounce on this sprite |
| `showTalk` | 0 / 1 / 2 | visibility vs mic (see below) |
| `showBlink` | 0 / 1 / 2 | visibility vs blink (see below) |
| `costumeLayers` | string | 10 costume flags (see Costumes) |
| `frames` | int | horizontal strip cell count; `1` = still |
| `animSpeed` | number | strip playback; `0` = off (timer/talk-loop) |
| `talkAnim` | 0 / 1 / 2 | how the strip is driven (see Animation strips). Missing → 0 |
| `clipped` | bool | clip children to this sprite |
| `toggle` | string | hotkey name to hide/show, or `"null"` |

## Talk and blink

From `spriteObject.gd` `talkBlink()`:

| value | `showTalk` | `showBlink` |
|---|---|---|
| 0 | always | always |
| 1 | only when **silent** | only when **not blinking** (open eyes) |
| 2 | only when **talking** | only when **blinking** (closed eyes) |

Closed mouth = `showTalk` 1. Open mouth = `showTalk` 2. Open eyes = `showBlink` 1. Blink = `showBlink` 2.

Two PNG mouths still use that swap. A **mouth strip** (`talkAnim` 1 or 2) should use `showTalk` 0 so the rest frame stays visible when silent.

## Layering

Not a PSD. Each PNG is its own `spriteObject` / `Sprite2D`. Opaque pixels overwrite what is behind; there are no blend modes. Talk/blink and costumes hide sprites — they do not change z.

**Shared canvas.** Same width/height, subject locked in place, empty pixels transparent. Then `pos` stays `Vector2(0, 0)`. A cropped piece needs `pos` / `offset` (the default hat does).

**`parentId` = who you follow.** After spawn, a child reparents onto the parent's `Sprite2D` (`spriteObject.gd` `_ready`). Head drag/bounce/wobble then moves hair, mouth, eyes, hat. Link uses `reparent(newParent.sprite)`; unlink puts the node back on Origin.

**`zindex` = who draws on top.** The `Sprite2D` has `z_as_relative = false`, so z is **global**, not “child of head”. Hair is a **child of head** (follows) with `zindex` **-2** (still behind the face). Default body `-1`, face `0`, hat `2`. Q/E in edit mode change z.

Parents resolve by `identification` group after all sprites spawn; a child may appear before its parent in the JSON.

Default tree:

```
body (root)
  head
    hair          zindex -2
    mouth_closed
    mouth_open
    eyes_open
    eyes_closed
    hat / extras  zindex 2
```

| Want | Use |
|---|---|
| Hair follows head | `parentId` → head |
| Hair behind face | hair `zindex` lower than head |
| Mouth swap | two PNGs, `showTalk` 1 vs 2, same `pos` — or one strip + `talkAnim` |
| Hat only on outfit 2 | same parent/z, `costumeLayers` |
| Children only inside this alpha | `clipped` true (`CLIP_CHILDREN_AND_DRAW`; children's z forced to match) |
| Cropped small PNG | `pos` / `offset`, not z |

## Animation strips

`frames` > 1 means the PNG is a **horizontal** strip. Cell width = `image_width / frames`. Cell height = image height. The editor treats cells as square using the image height, so use square cells.

`talkAnim` (sprite editor: next to frames):

| value | name | behavior |
|---|---|---|
| 0 | loop (idle) | Timer loop while `animSpeed` > 0. Old avatars. Idle FX, not mic. |
| 1 | talk loop | Frame 0 = rest (silent). While `speaking`, loop frames `1..n-1` at `animSpeed`. Two cells → closed/open. |
| 2 | volume frames | Frame index from smoothed `talkLevel` (mic magnitude vs volume slider). Closed → small → wide on one sheet. |

Mouth sheet: left-to-right rest then more-open. Parent to head. Square cells. No visemes.

## Costumes

Ten outfits. Each sprite's `costumeLayers` is ten `0`/`1` flags: `1` means that piece is visible on that costume. Index `0` is costume 1. Body/head/face stay all `1`s so they never vanish; hats and alt clothes are `1` only on the slots they belong to.

**Costume keys** are the keyboard hotkeys that switch those ten slots. They are **app settings**, not avatar data. Stored in `user://settings.pngtp` as `costumeKeys` (default `["1","2","3","4","5","6","7","8","9","0"]` — number row, `0` is costume 10). Remap them in Settings. On key press, `main.gd` finds the key in that list and calls `changeCostume`.

Elgato Stream Deck buttons `1`–`10` switch the same slots and ignore `costumeKeys`. Optional `bounceOnCostumeChange` also lives in settings.

Do not write `costumeKeys` into a `.pngtuber`. Only `costumeLayers` on each sprite.

## Settings (not the avatar)

App settings stay at `user://settings.pngtp` (`costumeKeys`, bounce, mic, window, …). Do not pack those into a `.pngtuber`.
