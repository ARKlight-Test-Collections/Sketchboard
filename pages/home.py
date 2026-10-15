# include <stdlib.ARKlight>

from components.canvas_stage import canvas_stage
from components.header import header
from components.properties_panel import properties_panel
from components.shortcuts_panel import shortcuts_panel
from components.status_bar import status_bar
from components.toolbar import toolbar
from content.site_content import DESCRIPTION, FAVICON, TITLE


def home():
    return Page(
        State("scene_name", "Untitled board", persist=True),
        State("show_shortcuts", False),
        Computed(
            "document_title",
            deps=("scene_name",),
            derive=Derive.format("{name} · Sketchboard", name="scene_name"),
        ),
        header(),
        toolbar(),
        shortcuts_panel(),
        Main(
            Container(
                canvas_stage(),
                properties_panel(),
                class_name="editor-layout",
            ),
            status_bar(),
            class_name="app-main",
        ),
        title=TITLE,
        description=DESCRIPTION,
        favicon=FAVICON,
    )
