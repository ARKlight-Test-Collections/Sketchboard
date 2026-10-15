# include <stdlib.ARKlight>

STYLES = {
    "topbar": {"display": "flex", "align-items": "center", "justify-content": "space-between", "gap": "1rem", "min-height": "4.6rem", "padding": "0.6rem 1rem", "border-bottom": "1px solid #e0e2e6", "background": "#ffffff"},
    "brand-lockup": {"display": "flex", "align-items": "center", "gap": "0.7rem", "min-width": "12rem"},
    "brand-mark": {"display": "grid", "place-items": "center", "width": "2.35rem", "height": "2.35rem", "border-radius": "0.55rem", "background": "#26364b", "color": "#ffffff", "font-family": "Georgia, serif", "font-size": "1.2rem", "font-weight": "700"},
    "brand-lockup-copy": {"display": "flex", "flex-direction": "column", "gap": "0.15rem"},
    "brand-name": {"color": "#202b3a", "font-size": "1rem", "font-weight": "700", "line-height": "1.1"},
    "brand-caption": {"color": "#7b8491", "font-size": "0.58rem", "font-weight": "600"},
    "document-meta": {"display": "flex", "flex-direction": "column", "gap": "0.18rem", "min-width": "8rem", "text-align": "center"},
    "board-title": {"color": "#303b4a", "font-size": "0.78rem", "font-weight": "600"},
    "save-status": {"color": "#89919c", "font-size": "0.62rem"},
    "top-actions": {"display": "flex", "align-items": "center", "justify-content": "end", "gap": "0.45rem"},
    "top-divider": {"width": "1px", "height": "1.7rem", "margin": "0 0.25rem", "background": "#e0e2e6"},
    "icon-button": {"width": "2.2rem", "height": "2.2rem", "padding": "0", "border": "1px solid #e0e2e6", "border-radius": "0.45rem", "background": "#ffffff", "color": "#38465a", "font-size": "1.2rem"},
    "quiet-button": {"height": "2.2rem", "padding": "0 0.75rem", "border": "1px solid #e0e2e6", "border-radius": "0.45rem", "background": "#ffffff", "color": "#38465a", "font-size": "0.7rem", "font-weight": "600"},
    "primary-button": {"height": "2.2rem", "padding": "0 0.85rem", "border": "1px solid #4169e1", "border-radius": "0.45rem", "background": "#4169e1", "color": "#ffffff", "font-size": "0.7rem", "font-weight": "600"},
    "tool-dock": {"display": "flex", "flex-wrap": "wrap", "align-items": "center", "gap": "0.35rem", "min-height": "3.8rem", "padding": "0.45rem 1rem", "border-bottom": "1px solid #e0e2e6", "background": "#ffffff"},
    "tool-button": {"display": "grid", "place-items": "center", "width": "2.55rem", "height": "2.55rem", "padding": "0", "border": "1px solid transparent", "border-radius": "0.5rem", "background": "transparent", "color": "#455267", "font-size": "1.15rem", "font-weight": "500"},
    "tool-text-button": {"height": "2.25rem", "padding": "0 0.65rem", "border": "1px solid #e0e2e6", "border-radius": "0.45rem", "background": "#ffffff", "color": "#536176", "font-size": "0.68rem", "font-weight": "600"},
    "tool-divider": {"width": "1px", "height": "1.8rem", "margin": "0 0.25rem", "background": "#e0e2e6"},
    "app-main": {"display": "flex", "flex-direction": "column", "gap": "0.6rem", "padding": "0.75rem 1rem 0.5rem"},
    "editor-layout": {"display": "flex", "flex-wrap": "wrap", "align-items": "stretch", "gap": "0.75rem", "min-height": "min(68vh, 48rem)"},
    "board-stage": {"position": "relative", "flex": "999 1 42rem", "min-width": "0", "min-height": "min(68vh, 42rem)", "overflow": "hidden", "border": "1px solid #dfe2e7", "border-radius": "0.6rem", "background": "#ffffff"},
    "drawing-host": {"position": "absolute", "inset": "0", "overflow": "hidden", "background-color": "#ffffff", "background-image": "radial-gradient(#dfe3e9 1px, transparent 1px)", "background-size": "22px 22px"},
    "canvas-overlay": {"position": "absolute", "right": "0.7rem", "bottom": "0.65rem", "pointer-events": "none"},
    "canvas-hint": {"padding": "0.35rem 0.55rem", "border": "1px solid #e1e5eb", "border-radius": "0.35rem", "background": "rgba(255, 255, 255, 0.88)", "color": "#7b8491", "font-size": "0.62rem"},
    "properties-rail": {"flex": "1 1 15rem", "max-width": "18rem", "min-width": "14rem"},
    "properties-panel": {"display": "flex", "flex-direction": "column", "gap": "0.8rem", "height": "100%", "padding": "1rem", "border": "1px solid #dfe2e7", "border-radius": "0.6rem", "background": "#ffffff"},
    "panel-title": {"color": "#293548", "font-size": "0.85rem", "font-weight": "700"},
    "field-label": {"color": "#697587", "font-size": "0.67rem", "font-weight": "600"},
    "swatch-row": {"display": "flex", "flex-wrap": "wrap", "gap": "0.5rem"},
    "swatch": {"width": "1.65rem", "height": "1.65rem", "padding": "0", "border": "2px solid #ffffff", "border-radius": "50%", "box-shadow": "0 0 0 1px #d8dde4"},
    "swatch-ink": {"background": "#27364b"},
    "swatch-blue": {"background": "#4169e1"},
    "swatch-rose": {"background": "#df697d"},
    "swatch-green": {"background": "#3a9278"},
    "swatch-amber": {"background": "#d99a32"},
    "swatch-violet": {"background": "#8b6dc1"},
    "field-row": {"display": "flex", "align-items": "center", "justify-content": "space-between", "gap": "0.55rem"},
    "column-field": {"flex-direction": "column", "align-items": "stretch"},
    "color-input": {"width": "2.1rem", "height": "1.8rem", "padding": "0.1rem", "border": "1px solid #dfe2e7", "border-radius": "0.35rem", "background": "#ffffff"},
    "range-input": {"width": "100%", "accent-color": "#4169e1"},
    "range-value": {"color": "#788394", "font-size": "0.65rem", "text-align": "right"},
    "select-input": {"min-width": "7rem", "height": "1.9rem", "padding": "0 0.4rem", "border": "1px solid #dfe2e7", "border-radius": "0.35rem", "background": "#ffffff", "color": "#536176", "font-size": "0.68rem"},
    "small-toggle": {"height": "1.9rem", "padding": "0 0.6rem", "border": "1px solid #dfe2e7", "border-radius": "0.35rem", "background": "#ffffff", "color": "#536176", "font-size": "0.65rem"},
    "selection-actions": {"display": "flex", "flex-direction": "column", "gap": "0.5rem", "margin-top": "auto", "padding-top": "0.8rem", "border-top": "1px solid #edf0f3"},
    "selection-status": {"color": "#89919c", "font-size": "0.67rem"},
    "layer-actions": {"display": "grid", "grid-template-columns": "repeat(2, minmax(0, 1fr))", "gap": "0.35rem"},
    "delete-button": {"height": "2rem", "padding": "0 0.6rem", "border": "1px solid #f0ccd1", "border-radius": "0.35rem", "background": "#fff7f8", "color": "#ba5360", "font-size": "0.67rem"},
    "statusbar": {"display": "flex", "align-items": "center", "justify-content": "space-between", "gap": "0.8rem", "min-height": "2.6rem", "padding": "0 0.25rem", "color": "#7b8491"},
    "status-brand": {"color": "#566174", "font-size": "0.65rem", "font-weight": "700"},
    "status-copy": {"flex": "1", "font-size": "0.65rem"},
    "zoom-control": {"display": "flex", "align-items": "center", "gap": "0.2rem", "padding": "0.15rem", "border": "1px solid #dfe2e7", "border-radius": "0.45rem", "background": "#ffffff"},
    "zoom-button": {"width": "1.75rem", "height": "1.75rem", "padding": "0", "border": "0", "border-radius": "0.3rem", "background": "transparent", "color": "#536176", "font-size": "1rem"},
    "zoom-readout": {"min-width": "3rem", "height": "1.75rem", "padding": "0 0.3rem", "border": "0", "background": "transparent", "color": "#536176", "font-size": "0.65rem"},
    "visually-hidden": {"position": "absolute", "width": "1px", "height": "1px", "padding": "0", "margin": "-1px", "overflow": "hidden", "clip": "rect(0, 0, 0, 0)", "white-space": "nowrap", "border": "0"},
}


def configure_design(site):
    for name, rules in STYLES.items():
        site.style(name, rules)
    site.style_selector(".tool-button:hover, .icon-button:hover, .quiet-button:hover, .zoom-button:hover", {"background": "#f2f5fa"})
    site.style_selector(".tool-button.is-active", {"border-color": "#cbd8ff", "background": "#eaf0ff", "color": "#315bd4"})
    site.style_selector(".swatch.is-selected", {"box-shadow": "0 0 0 2px #4169e1"})
    site.style_selector(".drawing-host > .drawing-surface", {"position": "absolute", "inset": "0", "width": "100%", "height": "100%", "touch-action": "none"})
    site.style_selector(".shortcut-panel", {"display": "grid", "grid-template-columns": "repeat(auto-fit, minmax(min(100%, 14rem), 1fr))", "gap": "0.55rem 1rem", "margin": "0 1rem 0.75rem", "padding": "0.9rem 1rem", "border": "1px solid #dfe2e7", "border-radius": "0.5rem", "background": "#ffffff"})
    site.style("shortcut-title", {"grid-column": "1 / -1", "color": "#293548", "font-size": "0.82rem", "font-weight": "700"})
    site.style("shortcut-line", {"color": "#617084", "font-size": "0.68rem"})
