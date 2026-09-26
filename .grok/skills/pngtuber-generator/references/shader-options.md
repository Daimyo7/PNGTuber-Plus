# Shader options

PNGTuber-Plus does **motion in GDScript** (`xAmp`/`yAmp`, bounce, squash, `rotDrag`, talk/blink). Shaders are for **look**. `canvas_item` on a sprite, or one pass on the stacked avatar.

None of these are in the `.pngtuber` format yet. Do not invent save fields. When generating art today, bake only what the PNG must contain; leave outline/glow/tint/wind as shader candidates.

Existing shaders (not on live sprites): `shader/wobble.gdshader` (noise UV), `ui_scenes/selectedSprite/outline.gdshader` and `ui_scenes/spriteEditMenu/chain.gdshader` (palette scroll), `ui_scenes/spriteEditMenu/sprite_viewer.gdshader` (outline). Renderer is `gl_compatibility`.

## First five (if adding a per-sprite slot)

1. Outline (color + width)
2. Hue / saturation / value
3. Palette swap (1D gradient, same idea as the UI outline shaders)
4. Glow / talk emission (drive from `Global.speaking` or mic level)
5. Wind sway (UV offset stronger toward the top — hair, cloth)

## Per sprite

| Shader | What |
|---|---|
| Hue / saturation / brightness | Recolor without a new PNG |
| Palette swap | Luminance → 1D gradient; pixel-art costumes |
| Outline / glow | Expand alpha, tint rim |
| Drop shadow | Offset alpha duplicate |
| Inner shadow / bevel | Darken opaque edges |
| Color overlay / multiply | Tint × alpha |
| Gradient map / duotone | Two-color grade |
| HSV shift over time | Slow rainbow |
| Opacity pulse | Sin-wave alpha |
| Chromatic aberration | RGB split |
| Dither / posterize | Quantize color |
| Sharpen / contrast | Local contrast on soft layers |

## Distortion

Keep amounts small so they do not fight script wobble/bounce.

| Shader | What |
|---|---|
| Noise wobble | Unused `wobble.gdshader`: UV jitter — slime, fire, cloth |
| Wind sway | Horizontal UV offset growing toward the top |
| Jelly / squash UV | Extra squash on bounce |
| Ripple | Radial UV sine |
| Pixelate | Snap UVs to a grid |
| CRT / scanlines | Lines + roll |
| Glitch slices | Random horizontal UV strips |
| 2D dissolve | Noise vs threshold, optional edge color |

## Mic- and blink-reactive

Uniforms from `Global.speaking`, `Global.blink`, and the existing volume/sense sliders.

| Shader | Trigger |
|---|---|
| Talk glow | Rim/emission while speaking |
| Talk squash | Extra Y-stretch on mouth/head while mic is hot |
| Volume-driven hue | Color or outline width from mic level |
| Blink shine | Specular on open-eye layers |
| Anger shake | Noise UV above a volume threshold |

## Whole avatar / screen

Viewport, `BackBufferCopy`, or full-screen ColorRect — not every sprite.

| Shader | What |
|---|---|
| Chroma key polish | Spill kill on green/magenta |
| Bloom | Soft glow of bright pixels |
| Drop-shadow pass | One shadow for the stacked avatar |
| Outline pass | One silhouette around the composite |
| Background blur | Only if compositing a captured desktop |
| Vignette / color grade | Whole-output mood |

## Particle-like

| Shader | What |
|---|---|
| Sparkle overlay | Stars on bright pixels or a mask |
| Scrolling overlay | Second texture clipped to sprite alpha |
| Aura | Soft dilated alpha behind the character |
| Afterimage | Trail of poses (needs a viewport) |

## Do not shader

Already in script or a bad fit: idle float/bounce, head `drag`, talk/blink hide, horizontal `frames`/`animSpeed`, heavy 3D lighting.
