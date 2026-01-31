"""
Minimal Gradio UI for pi-core.
Shows run state, problems, ProductSpec, approval, kill switch.
"""

import gradio as gr
from pathlib import Path
import json
import traceback
from ..config.settings import Settings
from ..control.state import StateManager
from ..control.approvals import ApprovalManager
from ..models.core import RunState

def get_pi_core_root() -> Path:
    return Path(__file__).resolve().parents[3]

def allowed_roots(root: Path) -> list[Path]:
    return [
        root / "data/runs",
        root / "outputs/bundles",
        root / "logs"
    ]

def safe_resolve(path: Path, roots: list[Path]) -> Path | None:
    try:
        if ".." in str(path):
            return None
        resolved = path.resolve()
        for r in roots:
            try:
                if resolved == r or resolved.is_relative_to(r):
                    return resolved
            except Exception:
                # For Python <3.9 compatibility
                try:
                    resolved.relative_to(r)
                    return resolved
                except Exception:
                    continue
        return None
    except Exception:
        return None

def read_text_truncated(path: Path, max_bytes: int = 200_000) -> str:
    try:
        with open(path, "rb") as f:
            data = f.read(max_bytes)
            if f.read(1):
                data += b"\n... [truncated]"
        return data.decode(errors="replace")
    except Exception as e:
        return f"[Error reading file: {e}]"

def tail_text(path: Path, max_lines: int = 200, max_bytes: int = 200_000) -> str:
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            block = min(size, max_bytes)
            f.seek(-block, 2)
            lines = f.read().decode(errors="replace").splitlines()
            return "\n".join(lines[-max_lines:])
    except Exception as e:
        return f"[Error reading log: {e}]"

def list_runs(root: Path) -> list[str]:
    runs_dir = root / "data/runs"
    if not runs_dir.exists():
        return []
    runs = []
    for p in runs_dir.iterdir():
        if p.is_dir() and p.name not in {"KILL", "latest"}:
            runs.append(p.name)
    return sorted(runs, reverse=True)

def list_files_for_run(root: Path, run_id: str) -> list[str]:
    files = []
    # bundle_staging
    staging = root / "data/runs" / run_id / "bundle_staging"
    if staging.exists():
        for f in staging.rglob("*"):
            if f.is_file():
                files.append(str(f.relative_to(root)))
    # outputs/bundles
    bundles = root / "outputs/bundles"
    if bundles.exists():
        for f in bundles.rglob("*"):
            if f.is_file():
                files.append(str(f.relative_to(root)))
    # logs
    logs = root / "logs"
    if logs.exists():
        for f in logs.iterdir():
            if f.is_file():
                files.append(str(f.relative_to(root)))
    return sorted(files)

def get_common_artifacts(root: Path, run_id: str):
    run_dir = root / "data/runs" / run_id
    artifacts = {}
    for fname in ["run_state.json", "problems_ranked.json", "product_spec.json", "approval.json"]:
        f = run_dir / fname
        if f.exists():
            artifacts[fname] = f
    # bundle_manifest.json, listing.md
    # Try to find bundle dir for this run
    bundles = list((root / "outputs/bundles").glob(f"{run_id}*/bundle_manifest.json"))
    if bundles:
        artifacts["bundle_manifest.json"] = bundles[0]
        listing = bundles[0].parent / "listing.md"
        if listing.exists():
            artifacts["listing.md"] = listing
    return artifacts

def get_latest_run_state() -> RunState:
    latest = Settings.LATEST_SYMLINK if Settings.LATEST_SYMLINK.exists() else None
    if not latest:
        return None
    state_path = latest / "run_state.json"
    if not state_path.exists():
        return None
    return StateManager.load(state_path)

def approve_run():
    state = get_latest_run_state()
    if not state:
        return "No run found."
    run_folder = Path(state.paths["run_folder"])
    ApprovalManager.write_approval(run_folder, state.run_id, approved_by="localuser")
    return "Approved. You may now continue the pipeline."

def kill_switch():
    Settings.KILL_FILE.touch()
    return "Kill switch engaged."


def outputs_tab():
    root = get_pi_core_root()
    allowed = allowed_roots(root)

    def refresh_all():
        runs = list_runs(root)
        latest = None
        latest_txt = root / "data/runs/LATEST.txt"
        if latest_txt.exists():
            try:
                latest = latest_txt.read_text().strip()
            except Exception:
                pass
        return runs, latest

    def get_artifact_content(run_id, artifact):
        artifacts = get_common_artifacts(root, run_id)
        if artifact not in artifacts:
            return f"[File {artifact} not found]"
        path = artifacts[artifact]
        if not safe_resolve(path, allowed):
            return "[Access denied]"
        try:
            if artifact.endswith(".json"):
                data = json.loads(read_text_truncated(path))
                return json.dumps(data, indent=2)
            elif artifact.endswith(".md"):
                return read_text_truncated(path)
            else:
                return read_text_truncated(path)
        except Exception as e:
            return f"[Error: {e}]"

    def get_file_content(rel_path):
        try:
            path = root / rel_path
            if not safe_resolve(path, allowed):
                return "[Access denied]"
            if not path.exists():
                return "[File not found]"
            if path.suffix == ".json":
                data = json.loads(read_text_truncated(path))
                return json.dumps(data, indent=2)
            elif path.suffix == ".md":
                return read_text_truncated(path)
            else:
                return read_text_truncated(path)
        except Exception as e:
            return f"[Error: {e}]"

    def get_log_tail():
        log_path = root / "logs/picore.log"
        if not safe_resolve(log_path, allowed):
            return "[Access denied]"
        if not log_path.exists():
            return "[Log file not found]"
        return tail_text(log_path)

    with gr.Blocks() as tab:
        gr.Markdown("## Outputs & Logs Viewer")
        runs, latest = refresh_all()
        run_id = gr.State(runs[0] if runs else "")
        run_list = gr.Dropdown(choices=runs, value=(runs[0] if runs else None), label="Select Run ID", interactive=True)
        if not runs:
            gr.Markdown("No runs found.")
        else:
            if latest and latest in runs:
                gr.Markdown(f"**Latest run:** {latest}")
        # Common artifacts
        artifact_choices = ["run_state.json", "problems_ranked.json", "product_spec.json", "approval.json", "bundle_manifest.json", "listing.md"]
        artifact = gr.Dropdown(choices=artifact_choices, value=artifact_choices[0], label="Quick View Artifact", interactive=True)
        artifact_content = gr.Textbox(label="Artifact Content", lines=20)
        def update_artifact(run_id, artifact):
            return get_artifact_content(run_id, artifact)
        artifact_btn = gr.Button("Show Artifact")
        artifact_btn.click(update_artifact, inputs=[run_list, artifact], outputs=artifact_content)

        # File browser
        file_list = gr.Dropdown(choices=list_files_for_run(root, run_list.value) if runs else [], label="Browse Files", interactive=True)
        file_content = gr.Textbox(label="File Content", lines=20)
        def update_file_content(rel_path):
            return get_file_content(rel_path)
        file_btn = gr.Button("Show File")
        file_btn.click(update_file_content, inputs=file_list, outputs=file_content)

        # Log tail
        log_tail = gr.Textbox(label="Log Tail (last 200 lines)", lines=10)
        log_btn = gr.Button("Refresh Log Tail")
        log_btn.click(lambda: get_log_tail(), None, log_tail)

        # Refresh button
        def do_refresh():
            runs, latest = refresh_all()
            files = list_files_for_run(root, runs[0]) if runs else []
            return gr.Dropdown.update(choices=runs, value=(runs[0] if runs else None)), gr.Dropdown.update(choices=files, value=(files[0] if files else None)), "", "", get_log_tail()
        refresh_btn = gr.Button("Refresh All")
        refresh_btn.click(do_refresh, None, [run_list, file_list, artifact_content, file_content, log_tail])

    return tab

if __name__ == "__main__":

    def ui():
        with gr.Blocks() as demo:
            gr.Markdown("# pi-core MVP UI")
            with gr.Tab("Pipeline"):
                state = get_latest_run_state()
                if state:
                    gr.Markdown(f"## Run State\n\nStep: {state.current_step}\n\nErrors: {state.errors}")
                    gr.Markdown(f"### Approval Required: {state.approval_required}")
                    if state.selected_problem_id:
                        gr.Markdown(f"**Selected Problem ID:** {state.selected_problem_id}")
                    if state.selected_product_id:
                        gr.Markdown(f"**Selected Product ID:** {state.selected_product_id}")
                else:
                    gr.Markdown("No run found.")
                gr.Button("Approve Run").click(approve_run, None, None)
                gr.Button("Engage Kill Switch").click(kill_switch, None, None)
            with gr.Tab("Outputs"):
                outputs_tab()
        demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
