# pi-core

Deterministic, local-only pipeline that discovers a real problem from Hacker News, defines ONE product, generates real files, and packages a sellable template pack. Manual approval and kill switch are mandatory.

## Usage

```bash
scripts/run_demo.sh
```

- UI: http://localhost:7860
- All outputs, logs, and state are local only.

## Requirements
- Python 3.9–3.11
- No cloud, no auth, no payments, no multi-user
- Deterministic output (same input → same output)
- Fail fast; no placeholder logic

See ROADMAP.md for implementation details.
