# include <stdlib.ARKlight>


def shortcuts_panel():
    return Show(
        Predicate.truthy("show_shortcuts"),
        Container(
            Heading("Keyboard shortcuts", level=2, class_name="shortcut-title"),
            Text("V Select  ·  H Pan  ·  R Rectangle  ·  D Diamond  ·  O Ellipse", class_name="shortcut-line"),
            Text("A Arrow  ·  L Line  ·  P Free draw  ·  T Text  ·  E Eraser", class_name="shortcut-line"),
            Text("Ctrl/Cmd+Z Undo  ·  Shift+Ctrl/Cmd+Z Redo  ·  Ctrl/Cmd+D Duplicate", class_name="shortcut-line"),
            Text("Ctrl/Cmd+A Select all  ·  Space+drag Pan  ·  Home Fit scene", class_name="shortcut-line"),
            Button("Close shortcuts", on_click=Action.toggle_bool("show_shortcuts"), class_name="quiet-button"),
            class_name="shortcut-panel",
        ),
    )
