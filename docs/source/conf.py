# -*- coding: utf-8 -*-
# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../..'))


# -- Project information -----------------------------------------------------

project = 'sdypy-view'
copyright = '2024, Klemen Zaletelj, Janko Slavič, Domen Gorjup'
author = 'Klemen Zaletelj, Janko Slavič, Domen Gorjup'

# The short X.Y version
version = '0.2'
# The full version, including alpha/beta/rc tags
release = '0.2.0'


# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_copybutton',
]

# Mock heavy optional dependencies so autodoc works without Qt installed.
autodoc_mock_imports = ["PyQt6", "pyvistaqt"]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

language = 'en'

exclude_patterns = []

pygments_style = None


# -- Options for HTML output -------------------------------------------------

html_theme = 'pydata_sphinx_theme'

html_static_path = []

html_theme_options = {
    "show_nav_level": 2,
}


# -- Options for HTMLHelp output ---------------------------------------------

htmlhelp_basename = 'sdypy_view_doc'


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {}

latex_documents = [
    (master_doc, 'sdypy_view.tex', 'sdypy-view Documentation',
     'Klemen Zaletelj, Janko Slavič, Domen Gorjup', 'manual'),
]


# -- Options for manual page output ------------------------------------------

man_pages = [
    (master_doc, 'sdypy_view', 'sdypy-view Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

texinfo_documents = [
    (master_doc, 'sdypy-view', 'sdypy-view Documentation',
     author, 'sdypy-view', 'Visualization of SDyPy models and results.',
     'Miscellaneous'),
]


# -- Options for Epub output -------------------------------------------------

epub_title = project
epub_exclude_files = ['search.html']
