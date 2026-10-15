# include <stdlib.ARKlight>


def canvas_stage():
    return Container(
        Container(
            Container(id="drawing-host", class_name="drawing-host"),
            Container(
                Text("Drag to draw  ·  Space + drag to pan", id="canvas-hint", class_name="canvas-hint"),
                class_name="canvas-overlay",
            ),
            class_name="board-stage",
        ),
        Input(type="file", id="scene-import", accept="application/json,.json,.excalidraw", aria_label="Open a sketchboard or Excalidraw JSON file", class_name="visually-hidden"),
        Input(type="file", id="image-import", accept="image/*", aria_label="Choose an image to place on the board", class_name="visually-hidden"),
    )
