"""
Orchestrates full pipeline, stops at approval gate until approved.
"""
import os
from pathlib import Path
from datetime import datetime
from ..config.settings import Settings
from ..models.core import RunState, RunStep, StepStatus
from ..control.state import StateManager
from ..control.kill_switch import KillSwitch
from ..control.approvals import ApprovalManager
from ..sources.hn_algolia import HNAlgoliaAdapter
from ..discovery.extractor import Extractor
from ..discovery.ranker import Ranker
from ..product.define import ProductDefiner
from ..product.generator import TemplatePackGenerator
from ..packaging.pack import Packager

class PipelineRunner:
    def __init__(self):
        Settings.ensure_dirs()
        self.run_id = datetime.utcnow().strftime(Settings.RUN_ID_FORMAT)
        self.run_folder = Settings.RUNS / self.run_id
        self.state_path = self.run_folder / "run_state.json"
        StateManager.ensure_run_folder(self.run_id, Settings.RUNS)
        self.state = RunState(
            run_id=self.run_id,
            started_at=datetime.utcnow(),
            ended_at=None,
            current_step=RunStep.pull_raw,
            step_status={s: StepStatus.pending for s in RunStep},
            errors=[],
            selected_problem_id=None,
            selected_product_id=None,
            approval_required=False,
            approved=False,
            killed=False,
            paths={"run_folder": str(self.run_folder)}
        )
        StateManager.save(self.state, self.state_path)

    def run(self):
        KillSwitch.require_alive()
        # Step A: Pull raw
        raw_path = self.run_folder / "raw.jsonl"
        hn = HNAlgoliaAdapter()
        hits = hn.fetch(out_path=raw_path)
        # Step B: Derive candidates
        KillSwitch.require_alive()
        problems = Extractor.extract_problems(hits)
        # Step C: Rank problems
        KillSwitch.require_alive()
        ranked = Ranker.score_and_rank(problems)
        top_problem = ranked[0]
        self.state.selected_problem_id = top_problem.problem_id
        # Step D: Define product
        KillSwitch.require_alive()
        spec = ProductDefiner.define(top_problem)
        self.state.selected_product_id = spec.product_id
        self.state.approval_required = True
        StateManager.save(self.state, self.state_path)
        # Approval gate
        if not ApprovalManager.is_approved(self.run_folder):
            self.state.step_status[RunStep.define_product] = StepStatus.blocked
            StateManager.save(self.state, self.state_path)
            print("Approval required. Approve via UI to continue.")
            return
        self.state.approved = True
        # Step E: Generate files
        KillSwitch.require_alive()
        bundle_staging = self.run_folder / "bundle_staging"
        artifacts = TemplatePackGenerator.generate(spec, bundle_staging)
        # Step F: Package bundle
        KillSwitch.require_alive()
        from ..models.core import ListingDraft, PricingSuggestion, BundleManifest
        manifest = BundleManifest(
            bundle_id=spec.product_id,
            product_id=spec.product_id,
            created_at=datetime.utcnow(),
            artifacts=artifacts,
            listing=ListingDraft(
                title=spec.value_prop,
                short_description=spec.value_prop,
                long_description_md=spec.value_prop,
                what_you_get=spec.deliverables,
                requirements=[],
                faq=[]
            ),
            pricing=PricingSuggestion(currency="USD", price=19.0, rationale="Flat MVP price.")
        )
        bundle_dir = Settings.BUNDLES / spec.product_id
        Packager.assemble_bundle(bundle_dir, manifest)
        zip_path = Settings.BUNDLES / f"{spec.product_id}.zip"
        Packager.zip_bundle(bundle_dir, zip_path)
        # Finalize
        self.state.ended_at = datetime.utcnow()
        self.state.step_status[RunStep.package_bundle] = StepStatus.ok
        StateManager.save(self.state, self.state_path)
        # Update latest symlink (best effort)
        try:
            if Settings.LATEST_SYMLINK.exists() or Settings.LATEST_SYMLINK.is_symlink():
                Settings.LATEST_SYMLINK.unlink()
            Settings.LATEST_SYMLINK.symlink_to(self.run_folder)
        except Exception:
            pass
        print(f"Run complete. Bundle at {zip_path}")
