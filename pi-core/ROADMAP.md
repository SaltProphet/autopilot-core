# pi-core MVP Implementation Roadmap

## 1. Config & Paths
- Centralized config (paths, env, HN query)
- Deterministic, local-only

## 2. Data Models (Pydantic)
- All core models/enums in one file
- Discovery, Product, Generation, Control

## 3. State Management
- Atomic RunState load/save
- Per-run folder handling

## 4. Kill Switch
- File-based, checked before/after every step

## 5. Approval Gating
- ApprovalRecord persistence
- Block generation/packaging unless approved

## 6. Source Adapter Protocol
- Abstract base for all sources

## 7. HN Algolia Adapter
- Fetch bounded, deterministic results
- Persist raw snapshots

## 8. Discovery Extractor
- Deterministic heuristics: raw → ProblemStatements
- Attach Evidence (URL, excerpt)

## 9. Problem Ranker
- Score + rank problems
- Explicit breakdown, select top 1

## 10. Product Definition
- Map ProblemStatement → ProductSpec
- Fail if required fields missing

## 11. Product Generator
- Implement template_pack only
- Generate real files, hash, atomic writes

## 12. Packaging
- Assemble bundle, manifest, ZIP output

## 13. Pipeline Steps
- Step wrappers: kill switch, state update, fail-fast

## 14. Pipeline Orchestrator
- Full pipeline, stops at approval gate

## 15. Minimal Gradio UI
- Show run state, problems, ProductSpec, approval, kill switch

## 16. Entrypoint Script
- One command to start UI and pipeline
