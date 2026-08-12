# Project Guidelines

## Scope

- Read [README.md](README.md) for the user-facing project map and [docs/00-overview.md](docs/00-overview.md) for the lecture's concepts and evidence standards.
- Keep changes focused on the relevant challenge or document. Do not turn the toy examples into claims about real-world lifecycle impacts without adding evidence and stating the boundary.

## Architecture

- Each directory under `challenges/` is a self-contained interactive exercise.
- Keep each challenge's CSV data, browser assets, and local Python modules beside the entry point that loads them. Apps resolve data with paths relative to `__file__`, not the repository root.
- Challenge 03 shares calculations in `model.py` between its Streamlit and Gradio UIs. Challenge 04 shares audit rules in `card.py`; Challenge 05 shares policy-stage logic in `coverage.py`. Update and check every UI that uses a shared module.
- Lecture notes and the source PDF belong under `docs/`; runnable exercises belong under `challenges/`.

## Run And Test

From the repository root, install the example dependencies:

```text
python -m pip install streamlit pandas numpy gradio
```

Run an interactive exercise with:

```text
python -m streamlit run challenges/<challenge-directory>/app.py
```

Challenge 03 also supports `python challenges/03-rebound-loop/gradio_app.py`. Challenges 02 and 04 include standalone HTML entry points; open those files directly in a browser.

There is currently no test suite, build configuration, or lint configuration. For logic changes, run a focused Python check for the affected functions and start the affected UI when practical. For shared modules, check both supported entry points.

## Conventions

- Use four-space indentation and preserve the existing small-function, module-level-constant style in the Python challenges.
- Keep Streamlit widgets and presentation in `app.py`; put reusable calculations or schemas in the challenge's local module when that pattern already exists.
- Keep assumptions visible in the UI and documentation. Distinguish modeled potential reductions from realized, additional, or net reductions.
- Keep water withdrawal, consumption, and discharge distinct in new content. Verify policy and regulatory details against current primary sources before presenting them as current.
- Update links when moving documentation, and keep the root limited to project metadata, `README.md`, `docs/`, and `challenges/`.