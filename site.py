# include <stdlib.ARKlight>

from components.site_design import configure_design
from components.sketchboard_runtime import SketchboardRuntime
from pages.home import home

site = Site(
    name="Excalidraw Sketchboard",
    max_width="100%",
    bg="#f2f3f5",
    font_family="'Avenir Next', 'Trebuchet MS', sans-serif",
    button_text="#ffffff",
)

configure_design(site)
site.register_script_extension(SketchboardRuntime)


@site.page("/")
def home_page():
    return home()
