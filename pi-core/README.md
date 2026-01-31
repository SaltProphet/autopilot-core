# pi-core

Deterministic, local-only pipeline that discovers a real problem from Hacker News, defines ONE product, generates real files, and packages a sellable template pack. Manual approval and kill switch are mandatory.


## Quickstart

**Python version required:** 3.9, 3.10, or 3.11 (NOT 3.12+)

### 1. Ensure correct Python version

- On Ubuntu 24.04+ or if `python3.11` is not available:
	- **Recommended:** Use [pyenv](https://github.com/pyenv/pyenv) to install Python 3.11 locally:
		```bash
		curl https://pyenv.run | bash
		export PATH="$HOME/.pyenv/bin:$PATH"
		eval "$(pyenv init -)"
		pyenv install 3.11.7
		pyenv local 3.11.7
		```
	- Or, try the deadsnakes PPA (if supported):
		```bash
		sudo apt install software-properties-common
		sudo add-apt-repository ppa:deadsnakes/ppa
		sudo apt update
		sudo apt install python3.11 python3.11-venv python3.11-distutils
		```
	- Or, use Python 3.10 if available:
		```bash
		sudo apt install python3.10 python3.10-venv python3.10-distutils
		```

### 2. Create and activate a virtual environment
```bash
python3.11 -m venv .venv  # or python3.10 if that's what you installed
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -e .
```

### 4. Run the demo UI
```bash
./scripts/run_demo.sh
```

- The UI will open locally (Gradio) at http://localhost:7860
- Start a run to pull HN data, extract and rank problems, and define a product.
- The pipeline will block at the approval gate. Approve to generate and package the product.
- All outputs, logs, and run state are under `data/`, `outputs/`, and `logs/`.


## Requirements
- Python 3.9–3.11 (not 3.12+)
- No cloud, no auth, no payments, no multi-user
- Deterministic output (same input → same output)
- Fail fast; no placeholder logic

## Troubleshooting

- **Python version errors:** If you see errors about Python 3.12, you must use Python 3.9, 3.10, or 3.11. See above for install instructions.
- **Import errors:** Ensure you are in the `.venv` and have run `pip install -e .`.
- **PYTHONPATH issues:** The demo script sets `PYTHONPATH` for you. If running manually, ensure `src/` is in your `PYTHONPATH`.
- **All steps are atomic and deterministic.** If a step is not implemented, the run will fail with an explicit error.
- **Evidence URLs are always included in outputs.**
- **Approval bypass is impossible by design.**
- **All file writes are atomic to prevent partial files.**
- **The kill switch is checked before and after every pipeline step.**

See ROADMAP.md for implementation details.
