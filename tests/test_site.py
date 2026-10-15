"""Build smoke tests. Run with `pytest` (`pip install pytest` first).

They build the real site into a temp directory, so a broken import, a
misspelled component, a missing required prop, or an undeclared state
name fails here in milliseconds instead of at deploy time. Add a route
to site.py -> add its output file to ROUTES.
"""

from pathlib import Path

import pytest

from arklight.compiler.pipeline import build

SITE = Path(__file__).resolve().parent.parent / "site.py"

# route -> the file `arklight build` writes for it
ROUTES = {"/": "index.html"}


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out_dir = tmp_path_factory.mktemp("ARK")
    build(SITE, out_dir)
    return out_dir


@pytest.mark.parametrize("output_file", ROUTES.values())
def test_every_route_builds(built, output_file):
    assert (built / output_file).exists()


def test_board_shell_has_tool_dock_and_main_landmark(built):
    html = (built / "index.html").read_text(encoding="utf-8")
    assert 'class="tool-dock"' in html
    assert 'id="tool-selection"' in html
    assert "<main" in html


def test_assets_are_copied_into_the_build(built):
    assert (built / "assets" / "icon.svg").exists()


def test_board_controls_and_canvas_host_render(built):
    html = (built / "index.html").read_text(encoding="utf-8")
    assert 'id="drawing-host"' in html
    assert 'aria-label="Export PNG"' in html
    assert "Properties" in html


def test_pointer_runtime_is_appended_by_script_extension(built):
    runtime = (built / "arklight.js").read_text(encoding="utf-8")
    assert "pointerdown" in runtime
    assert "pointermove" in runtime
    assert "localStorage" in runtime
    assert "toBlob" in runtime
    assert "resizeElementTo" in runtime
    assert "normalizeScene" in runtime
    assert 'type: "excalidraw"' in runtime
    assert "groupSelection" in runtime
    assert "groupIds" in runtime
    assert "ScriptExtension: SketchboardRuntime" in runtime


def test_editor_exposes_transform_style_and_image_controls(built):
    html = (built / "index.html").read_text(encoding="utf-8")
    assert 'id="duplicate-selection"' in html
    assert 'id="group-selection"' in html
    assert 'id="ungroup-selection"' in html
    assert 'id="element-opacity"' in html
    assert 'id="line-style"' in html
    assert 'id="image-import"' in html
    assert 'id="grid-toggle"' in html
