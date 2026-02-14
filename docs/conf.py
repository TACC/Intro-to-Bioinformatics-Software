# Configuration file for the Sphinx documentation builder.
# Minimal config for Read the Docs. See docs/README-SPHINX-RTD-SETUP.md for full guide.

import sphinx_rtd_theme

project = 'Intro to Bioinformatics Software'
copyright = '2026, Texas Advanced Computing Center'
author = 'Texas Advanced Computing Center'

extensions = [
    'sphinx_rtd_theme',
]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
