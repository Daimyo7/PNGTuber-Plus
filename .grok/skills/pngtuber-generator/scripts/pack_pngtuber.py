#!/usr/bin/env python3
"""Pack PNG layers + layers.json into a PNGTuber-Plus .pngtuber file."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

AVATAR_EXT = ".pngtuber"

DEFAULTS = {
    "type": "sprite",
    "offset": "Vector2(0, 0)",
    "pos": "Vector2(0, 0)",
    "parentId": None,
    "zindex": 0,
    "drag": 0,
    "xFrq": 0,
    "xAmp": 0,
    "yFrq": 0,
    "yAmp": 0,
    "rotDrag": 0,
    "showTalk": 0,
    "showBlink": 0,
    "rLimitMin": -180,
    "rLimitMax": 180,
    "costumeLayers": "[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]",
    "stretchAmount": 0,
    "ignoreBounce": False,
    "frames": 1,
    "animSpeed": 0,
    "talkAnim": 0,
    "clipped": False,
    "toggle": "null",
}


def vec(value) -> str:
    if isinstance(value, str) and value.startswith("Vector2"):
        return value
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return f"Vector2({value[0]}, {value[1]})"
    raise SystemExit(f"pos/offset must be Vector2(...) or [x, y], got {value!r}")


def costumes(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list) and len(value) == 10:
        return "[" + ", ".join(str(int(v)) for v in value) + "]"
    raise SystemExit("costumeLayers must be 10 ints or a Godot array string")


def pack_layer(layer: dict, folder: Path, index: int) -> dict:
    file_name = layer.get("file")
    if not file_name:
        raise SystemExit(f"layer {index} missing 'file'")
    png_path = (folder / file_name).resolve()
    if not png_path.is_file():
        raise SystemExit(f"missing PNG: {png_path}")

    ident = layer.get("identification", 1000 + index)
    out = dict(DEFAULTS)
    out["path"] = str(png_path)
    out["imageData"] = base64.b64encode(png_path.read_bytes()).decode("ascii")
    out["identification"] = int(ident)
    out["parentId"] = layer.get("parentId", DEFAULTS["parentId"])
    if out["parentId"] is not None:
        out["parentId"] = int(out["parentId"])

    for key in (
        "zindex",
        "drag",
        "xFrq",
        "xAmp",
        "yFrq",
        "yAmp",
        "rotDrag",
        "showTalk",
        "showBlink",
        "rLimitMin",
        "rLimitMax",
        "stretchAmount",
        "ignoreBounce",
        "frames",
        "animSpeed",
        "talkAnim",
        "clipped",
        "toggle",
        "type",
    ):
        if key in layer:
            out[key] = layer[key]

    if "pos" in layer:
        out["pos"] = vec(layer["pos"])
    if "offset" in layer:
        out["offset"] = vec(layer["offset"])
    if "costumeLayers" in layer:
        out["costumeLayers"] = costumes(layer["costumeLayers"])
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layers", required=True, help="Path to layers.json")
    parser.add_argument("--out", required=True, help="Output .pngtuber path")
    args = parser.parse_args()

    layers_path = Path(args.layers).resolve()
    spec = json.loads(layers_path.read_text(encoding="utf-8"))
    layer_list = spec["layers"] if isinstance(spec, dict) else spec
    if not layer_list:
        raise SystemExit("layers.json has no layers")

    folder = layers_path.parent
    packed = {}
    ids = []
    for i, layer in enumerate(layer_list):
        sprite = pack_layer(layer, folder, i)
        packed[str(i)] = sprite
        ids.append(sprite["identification"])

    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate identification values")
    id_set = set(ids)
    for sprite in packed.values():
        parent = sprite["parentId"]
        if parent is not None and parent not in id_set:
            raise SystemExit(f"parentId {parent} has no matching identification")

    out_path = Path(args.out)
    if out_path.suffix.lower() != AVATAR_EXT:
        out_path = out_path.with_suffix(AVATAR_EXT)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(packed, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {out_path} ({len(packed)} sprites)")


if __name__ == "__main__":
    main()
