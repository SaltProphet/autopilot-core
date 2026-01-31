"""
Minimal Gradio UI for pi-core.
Shows run state, problems, ProductSpec, approval, kill switch.
"""
import gradio as gr
from pathlib import Path
from ..config.settings import Settings
from ..control.state import StateManager
from ..control.approvals import ApprovalManager
from ..models.core import RunState

RUNS_DIR = Settings.RUNS

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

def ui():
    with gr.Blocks() as demo:
        gr.Markdown("# pi-core MVP UI")
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
    demo.launch()

if __name__ == "__main__":
    ui()
