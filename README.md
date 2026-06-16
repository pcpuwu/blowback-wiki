# Blowback — Listening Companion

An unofficial read-along wiki for the [Blowback](https://blowback.show) podcast:
per-episode narration-order notes (with `[hh:mm:ss]` jump points and cited
sources) plus full transcripts, across all 6 seasons.

Built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

## Rebuild & publish
```bash
uv venv && uv pip install -r requirements.txt
.venv/bin/python build_docs.py     # regenerate docs/ + mkdocs.yml from source notes
.venv/bin/mkdocs serve             # preview at http://127.0.0.1:8000
.venv/bin/mkdocs gh-deploy --force # publish to GitHub Pages
```
Source notes live in the private `poopie` workspace; `build_docs.py` reads them.
