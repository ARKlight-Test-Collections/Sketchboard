# Sketchboard

An Excalidraw-inspired, local-first drawing board authored with ARKlight.
It supports selection, marquee/multi-select, move/resize/rotate, grouping,
hand-pan, freehand, rectangle, diamond, ellipse, line, arrow, text, image
insertion, erasing, duplicate and layer order, undo/redo, zoom-to-scene,
grid/snap, stroke/fill/opacity controls, JSON import/export, PNG export, and
local autosave.

## Build and run

```sh
arklight build site.py -o ARK
arklight live-streaming --subscribe site.py --port 8348 -o ARK
```

Run `pytest` for compiler/output smoke tests. Keyboard shortcuts include
`V` select, `H` hand, `R` rectangle, `D` diamond, `O` ellipse, `A` arrow,
`L` line, `P` free draw, `T` text, and `E` eraser. `Ctrl/Cmd+Z`,
`Ctrl/Cmd+Shift+Z`, `Ctrl/Cmd+C/V/D`, `Ctrl/Cmd+A`, `Delete`, `Space`, and
`Home` provide common editing actions.

## ARKlight boundary

The page, controls, layout, and stylesheet use ARKlight's stable component
and style APIs. Pointer events and canvas rendering are not in its stable
action vocabulary, so the isolated browser interaction layer uses the
experimental `ScriptExtension` API. ARKlight warns on every build; the
extension's JavaScript is not validated by the compiler.

The app imports and exports the supported subset of Excalidraw's version-2
scene format. It is not a complete Excalidraw port: collaboration, libraries,
crop editing, alignment/distribution, and unsupported element types are not
implemented. Images are embedded as data URLs, so large scenes can exceed
browser localStorage quotas; JSON export is the durable backup path.
