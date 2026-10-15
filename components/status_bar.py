# include <stdlib.ARKlight>


def status_bar():
    return Container(
        Text("Sketchboard", class_name="status-brand"),
        Text("Select a tool, then draw on the canvas", id="tool-status", class_name="status-copy"),
        Container(
            Button("−", id="zoom-out", title="Zoom out", aria_label="Zoom out", class_name="zoom-button"),
            Button("100%", id="zoom-fit", title="Fit scene", aria_label="Fit scene", class_name="zoom-readout"),
            Button("+", id="zoom-in", title="Zoom in", aria_label="Zoom in", class_name="zoom-button"),
            class_name="zoom-control",
        ),
        class_name="statusbar",
    )
