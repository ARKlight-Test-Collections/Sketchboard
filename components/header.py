# include <stdlib.ARKlight>


def header():
    return Header(
        Container(
            Text("E", class_name="brand-mark"),
            Container(
                Text("Excalidraw", class_name="brand-name"),
                Text("SKETCHBOARD / LOCAL CANVAS", class_name="brand-caption"),
                class_name="brand-lockup-copy",
            ),
            class_name="brand-lockup",
        ),
        Container(
            Input(
                type="text",
                id="board-title",
                name="scene_name",
                aria_label="Scene name",
                bind_value=Bind.model("scene_name"),
                class_name="board-title-input",
            ),
            Text(Bind("document_title"), id="document-title", class_name="document-title"),
            Text("Saved in this browser", id="save-status", class_name="save-status"),
            class_name="document-meta",
        ),
        Container(
            Button("?", id="help-toggle", title="Keyboard shortcuts", aria_label="Keyboard shortcuts", on_click=Action.toggle_bool("show_shortcuts"), class_name="icon-button"),
            Button("↶", id="undo", title="Undo", aria_label="Undo", class_name="icon-button"),
            Button("↷", id="redo", title="Redo", aria_label="Redo", class_name="icon-button"),
            Container(class_name="top-divider"),
            Button("Open", id="open-json", class_name="quiet-button"),
            Button("Save JSON", id="export-json", class_name="quiet-button"),
            Button("Export PNG", id="export-png", aria_label="Export PNG", class_name="primary-button"),
            class_name="top-actions",
        ),
        class_name="topbar",
    )
