# include <stdlib.ARKlight>


def properties_panel():
    return Aside(
        Container(
            Text("Properties", class_name="panel-title"),
            Text("Stroke", class_name="field-label"),
            Container(
                Button("", id="stroke-ink", title="Ink", aria_label="Ink", class_name="swatch swatch-ink is-selected"),
                Button("", id="stroke-blue", title="Blue", aria_label="Blue", class_name="swatch swatch-blue"),
                Button("", id="stroke-rose", title="Rose", aria_label="Rose", class_name="swatch swatch-rose"),
                Button("", id="stroke-green", title="Green", aria_label="Green", class_name="swatch swatch-green"),
                Button("", id="stroke-amber", title="Amber", aria_label="Amber", class_name="swatch swatch-amber"),
                Button("", id="stroke-violet", title="Violet", aria_label="Violet", class_name="swatch swatch-violet"),
                class_name="swatch-row",
            ),
            Container(
                Label("Custom color", for_="stroke-color", class_name="field-label"),
                Input(type="color", id="stroke-color", value="#27364b", aria_label="Custom stroke color", class_name="color-input"),
                class_name="field-row",
            ),
            Container(
                Label("Fill", for_="fill-color", class_name="field-label"),
                Input(type="color", id="fill-color", value="#dbeafe", aria_label="Shape fill color", class_name="color-input"),
                Button("No fill", id="fill-toggle", aria_pressed="false", class_name="small-toggle"),
                class_name="field-row",
            ),
            Container(
                Label("Stroke width", for_="stroke-width", class_name="field-label"),
                Input(type="range", id="stroke-width", min="1", max="6", value="2", aria_label="Stroke width", class_name="range-input"),
                Text("2 px", id="stroke-width-value", class_name="range-value"),
                class_name="field-row column-field",
            ),
            Container(
                Label("Opacity", for_="element-opacity", class_name="field-label"),
                Input(type="range", id="element-opacity", min="10", max="100", value="100", aria_label="Element opacity", class_name="range-input"),
                Text("100%", id="opacity-value", class_name="range-value"),
                class_name="field-row column-field",
            ),
            Container(
                Label("Line style", for_="line-style", class_name="field-label"),
                Select(
                    Option("Solid", value="solid"),
                    Option("Dashed", value="dashed"),
                    Option("Dotted", value="dotted"),
                    id="line-style",
                    aria_label="Line style",
                    class_name="select-input",
                ),
                class_name="field-row",
            ),
            Container(
                Label("Text size", for_="font-size", class_name="field-label"),
                Input(type="range", id="font-size", min="12", max="48", value="20", aria_label="Text size", class_name="range-input"),
                Text("20 px", id="font-size-value", class_name="range-value"),
                class_name="field-row column-field",
            ),
            Container(
                Label("Canvas", for_="background-color", class_name="field-label"),
                Input(type="color", id="background-color", value="#ffffff", aria_label="Canvas background color", class_name="color-input"),
                class_name="field-row",
            ),
            Container(
                Button("Snap to grid", id="snap-toggle", aria_pressed="false", class_name="small-toggle"),
                Button("Show grid", id="grid-toggle", aria_pressed="true", class_name="small-toggle"),
                class_name="field-row",
            ),
            Container(
                Text("No selection", id="selection-status", class_name="selection-status"),
                Container(
                    Button("Duplicate", id="duplicate-selection", class_name="small-toggle"),
                    Button("Group", id="group-selection", class_name="small-toggle"),
                    Button("Ungroup", id="ungroup-selection", class_name="small-toggle"),
                    Button("Send back", id="send-backward", class_name="small-toggle"),
                    Button("Bring forward", id="bring-forward", class_name="small-toggle"),
                    class_name="layer-actions",
                ),
                Button("Delete selection", id="delete-selection", class_name="delete-button"),
                class_name="selection-actions",
            ),
            class_name="properties-panel",
        ),
        class_name="properties-rail",
    )
