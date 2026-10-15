# include <stdlib.ARKlight>

TOOLS = [
    ("selection", "Select", "↖"),
    ("hand", "Pan canvas", "✋"),
    ("rectangle", "Rectangle", "▭"),
    ("diamond", "Diamond", "◇"),
    ("ellipse", "Ellipse", "◯"),
    ("arrow", "Arrow", "↗"),
    ("line", "Line", "／"),
    ("freedraw", "Free draw", "⌁"),
    ("text", "Text", "T"),
    ("image", "Insert image", "▧"),
    ("eraser", "Eraser", "⌫"),
]


def tool_button(tool, label, icon):
    return Button(
        icon,
        id=f"tool-{tool}",
        title=label,
        aria_label=label,
        aria_pressed="true" if tool == "selection" else "false",
        class_name="tool-button is-active" if tool == "selection" else "tool-button",
    )


def toolbar():
    return Container(
        *[tool_button(*tool) for tool in TOOLS],
        Container(class_name="tool-divider"),
        Button("New", id="clear-scene", class_name="tool-text-button"),
        class_name="tool-dock",
    )
