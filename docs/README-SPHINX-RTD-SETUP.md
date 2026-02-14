# Step-by-Step: Sphinx RST + Read the Docs for a GitHub Repo

Follow these steps to get Sphinx (reStructuredText) documentation building on Read the Docs.

---

## 1. Repo layout

Your repo should look like this:

```
your-repo/
├── .readthedocs.yaml          # Read the Docs config (repo root)
├── docs/
│   ├── conf.py                # Sphinx config
│   ├── requirements.txt       # Python deps for the build
│   ├── index.rst              # Required: main/root page
│   └── (other .rst files)     # Your content
```

All RST source files must live **inside** `docs/`. Read the Docs runs Sphinx with `docs/` as the source directory.

---

## 2. Create `.readthedocs.yaml` in the repo root

```yaml
version: 2

build:
  os: "ubuntu-22.04"
  tools:
    python: "3.12"

python:
  install:
    - requirements: docs/requirements.txt

sphinx:
  configuration: docs/conf.py
```

- Do **not** add `formats: - pdf` until HTML builds successfully (PDF needs LaTeX and often causes failures).

---

## 3. Create `docs/requirements.txt`

Keep it minimal so the build is reliable:

```
sphinx>=7.0
sphinx-rtd-theme
```

Add more packages (e.g. `sphinx-design`, `sphinx-copybutton`) only after the basic build works.

---

## 4. Create `docs/conf.py`

Minimal config that works on Read the Docs:

```python
# docs/conf.py
import sphinx_rtd_theme

project = 'Your Project Name'
copyright = '2025, Your Name'
author = 'Your Name'

extensions = [
    'sphinx_rtd_theme',
]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
```

- Do **not** set `html_static_path` or `app.add_css_file(...)` unless you actually add those files under `docs/_static/`. Missing static files can break the build.

---

## 5. Create `docs/index.rst` (required)

Sphinx **requires** a root document. By default it looks for `index.rst` in the source dir (`docs/`).

**Minimum valid `docs/index.rst`:**

```rst
Welcome
======

This is the main page.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   bio-software-knl-training
```

The `toctree` lists other `.rst` files (without the `.rst` extension). Add one line per page. If you only have `index.rst`, you can use:

```rst
Welcome
======

Your content here. No toctree needed if this is the only page.
```

---

## 6. Add your content as `.rst` files in `docs/`

Example: `docs/bio-software-knl-training.rst`. Any `.rst` file in `docs/` can be included in `index.rst` via the toctree.

---

## 7. Ignore build output in Git

In the repo root, create or edit `.gitignore`:

```
docs/_build/
```

Do **not** commit `docs/_build/`; Read the Docs builds it on their servers.

---

## 8. Push to GitHub

```bash
git add .readthedocs.yaml docs/ .gitignore
git commit -m "Add Sphinx docs and Read the Docs config"
git push origin main
```

---

## 9. Connect the repo to Read the Docs

1. Go to [readthedocs.org](https://readthedocs.org) and sign in (GitHub is supported).
2. **Import a project** → select your GitHub repo.
3. Leave the default settings (Read the Docs will use `.readthedocs.yaml`).
4. Click **Build version**. The first build may take a few minutes.

---

## 10. If the build fails

- Open the **Build** tab for your project on Read the Docs and read the **full build log**.
- Typical causes:
  - **No `index.rst`** in `docs/` → add `docs/index.rst` (see step 5).
  - **RST files in the repo root** → move them into `docs/` and list them in the toctree in `index.rst`.
  - **Missing or broken static files** → remove `html_static_path` and `add_css_file` from `conf.py`, or add the missing files under `docs/_static/`.
  - **PDF build failing** → remove `formats: - pdf` from `.readthedocs.yaml` and get HTML working first.
  - **Extension errors** → in `conf.py`, comment out all extensions except `'sphinx_rtd_theme'`, then add them back one by one.

---

## Checklist before pushing

- [ ] `.readthedocs.yaml` is in the **repo root** (not inside `docs/`).
- [ ] `docs/conf.py` exists and has `extensions = ['sphinx_rtd_theme']` (or minimal set).
- [ ] `docs/requirements.txt` exists and includes `sphinx` and `sphinx-rtd-theme`.
- [ ] `docs/index.rst` exists and is the root page (with or without a toctree).
- [ ] All `.rst` content is under `docs/` and (if you use a toctree) listed in `index.rst`.
- [ ] `docs/_build/` is in `.gitignore` and not committed.
