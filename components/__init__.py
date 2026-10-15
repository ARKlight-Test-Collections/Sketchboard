"""Reusable pieces shared across pages.

Two kinds live side by side here on purpose -- pick whichever a given
piece needs, and mix them freely:

- a plain function (`footer.py`) -- ordinary Python composition, zero
  setup;
- a registered `@component(...)` (`nav.py`) -- a checked props
  contract and build-time validation instead of a raw `TypeError` if
  it's misused. See docs/Foundational/USER-DEFINED-COMPONENTS.md.
"""
