# Configuration file for the Sphinx documentation builder.
# Full reference: https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
project   = "OPTIC"
author    = "Fukatsu et al. (Wake Lab, Nagoya University)"
copyright = "2026, Wake Lab, Nagoya University"
release   = "0.1"

# -- General configuration ---------------------------------------------------
extensions = [
    "myst_parser",         # Markdown support
    "sphinx_copybutton",   # copy button on code blocks
]

source_suffix = {
    ".md":  "markdown",
    ".rst": "restructuredtext",
}

# Allow useful MyST features inside .md files (e.g. ::: fences, task lists, auto-linkified URLs).
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
    "linkify",
    "fieldlist",
    "attrs_inline",
]

# Auto-generate header anchors for h1-h4 so cross-page links to "#### Subsection" work.
myst_heading_anchors = 4

templates_path   = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    # TIFStackExplorer is not part of the documented app set yet.
    "TIFStackExplorer/**",
    "CheckMultiSessionROICoordinates/**",
]

# -- HTML output -------------------------------------------------------------
html_theme       = "furo"
html_title       = "OPTIC documentation"
html_static_path = ["_static"]


# -- Per-app asset copy ------------------------------------------------------
# The tutorials use raw HTML <img src="images/foo.png"> tags inside Markdown
# (because of side-by-side <table> layouts). Sphinx passes the HTML through
# as-is but does NOT track or copy the referenced image files. Without help,
# every <img> would 404 in the built site.
#
# Sphinx-native solutions (![]() Markdown syntax, .. image:: directive) would
# require rewriting every tutorial. Instead, we copy the per-app images/ and
# movies/ folders verbatim into the corresponding output subdirectory after
# each build.
def _copy_app_assets(app, exception):
    if exception is not None:
        return
    import os, shutil
    src_root = app.srcdir
    out_root = app.outdir
    for app_dir in ("OpticROICuration", "OpticROITracking", "OpticRawTracking"):
        for sub in ("images", "movies"):
            src = os.path.join(src_root, app_dir, sub)
            dst = os.path.join(out_root, app_dir, sub)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)


def setup(app):
    app.connect("build-finished", _copy_app_assets)
