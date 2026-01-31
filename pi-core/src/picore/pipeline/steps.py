"""
Step wrappers: kill switch, state update, fail-fast.
"""
from pathlib import Path
from ..control.kill_switch import KillSwitch
from ..control.state import StateManager
from ..models.core import RunState, RunStep, StepStatus

class Stepper:
    @staticmethod
    def run_step(step_func, state: RunState, state_path: Path, *args, **kwargs):
        KillSwitch.require_alive()
        state.current_step = step_func.__name__
        state.step_status[RunStep[state.current_step]] = StepStatus.running
        StateManager.save(state, state_path)
        try:
            result = step_func(*args, **kwargs)
            state.step_status[RunStep[state.current_step]] = StepStatus.ok
            StateManager.save(state, state_path)
            KillSwitch.require_alive()
            return result
        except Exception as e:
            state.step_status[RunStep[state.current_step]] = StepStatus.failed
            state.errors.append(str(e))
            StateManager.save(state, state_path)
            raise
