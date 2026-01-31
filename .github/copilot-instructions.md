# Copilot Instructions for autopilot-core

## Project Overview
- **autopilot-core** is a deterministic, local-first pipeline for product ideation and prototyping. It pulls data (e.g., from HN/reddit), extracts and ranks problems, defines a product, and packages outputs. All state, logs, and outputs are local.
- The main pipeline is in `pi-core/src/picore/pipeline/` and orchestrated via `run.py` and `steps.py`.
- The UI is a Gradio app in `pi-core/src/picore/ui/app.py`.
- Data connectors (e.g., HN, Reddit, REST) are in `app/connectors/`.
- Models and data objects are in `app/models/` and `pi-core/src/picore/models/`.
- All persistent data, logs, and outputs are under `data/`, `outputs/`, and `logs/`.

## Developer Workflows
- **Python 3.9–3.11 only** (not 3.12+). Use `pyenv` or deadsnakes PPA if needed.
- Create a venv and install dependencies:
  ```bash
  python3.11 -m venv .venv
  source .venv/bin/activate
  pip install -e .
  ```
- Run the demo UI:
  ```bash
  ./scripts/run_demo.sh
  ```
  This launches Gradio at http://localhost:7860 and runs a full pipeline demo.
- All pipeline runs are tracked in `data/runs/`.

## Project Conventions & Patterns
- **Determinism:** All outputs must be reproducible given the same input.
- **No cloud/external state:** All computation and storage is local. No cloud APIs, no user auth, no payments.
- **Fail fast:** Avoid placeholder logic; raise errors on incomplete implementations.
- **Directory structure:**
  - `app/` — legacy and integration code
  - `pi-core/src/picore/` — core pipeline, models, UI, utils
  - `data/`, `outputs/`, `logs/` — all persistent artifacts
- **Pipeline steps:** Each step is a class/function in `pipeline/steps.py` and orchestrated by `run.py`.
- **Approvals:** The pipeline blocks at approval gates; see `control/approvals.py`.
- **Connectors:** Add new data sources by subclassing `app/connectors/base.py`.

## Integration Points
- **UI:** Gradio app in `ui/app.py` interacts with the pipeline.
- **Data connectors:** Implemented in `app/connectors/` and used by pipeline steps.
- **Product packaging:** See `packaging/pack.py` for output bundling.

## Examples
- To add a new data source: subclass `app/connectors/base.py` and register in the pipeline.
- To add a pipeline step: add a class/function in `pipeline/steps.py` and update `run.py`.

---
For more, see `README.md` and `pi-core/README.md`. When in doubt, prefer explicit, deterministic logic and local state.
