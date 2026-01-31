"""
Pydantic models for all core data shapes in pi-core.
- Discovery, Product, Generation, Control
- Enums where applicable
"""
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel

# --- Discovery models ---
class SourceRef(BaseModel):
    source_name: str
    source_item_id: str
    source_url: str
    retrieved_at: datetime

class Evidence(BaseModel):
    ref: SourceRef
    quote: str
    signals: Dict[str, float]
    notes: Optional[str] = None

class ProblemStatement(BaseModel):
    problem_id: str
    title: str
    summary: str
    who_is_hurt: str
    why_now: str
    evidence: List[Evidence]
    tags: List[str]
    score: float
    score_breakdown: Dict[str, float]

# --- Product definition models ---
class ProductType(str, Enum):
    template_pack = "template_pack"
    # Only template_pack is implemented for MVP

class ProductSpec(BaseModel):
    product_id: str
    problem_id: str
    product_type: ProductType
    target_user: str
    value_prop: str
    deliverables: List[str]
    non_goals: List[str]
    constraints: List[str]
    acceptance_criteria: List[str]

# --- Generation + packaging models ---
class Artifact(BaseModel):
    path: str
    kind: str
    sha256: str
    bytes: int

class ListingDraft(BaseModel):
    title: str
    short_description: str
    long_description_md: str
    what_you_get: List[str]
    requirements: List[str]
    faq: List[Dict[str, str]]

class PricingSuggestion(BaseModel):
    currency: str  # "USD"
    price: float
    rationale: str

class BundleManifest(BaseModel):
    bundle_id: str
    product_id: str
    created_at: datetime
    artifacts: List[Artifact]
    listing: ListingDraft
    pricing: PricingSuggestion

# --- Control plane models ---
class RunStep(str, Enum):
    pull_raw = "pull_raw"
    derive_candidates = "derive_candidates"
    rank_problems = "rank_problems"
    define_product = "define_product"
    generate_files = "generate_files"
    package_bundle = "package_bundle"

class StepStatus(str, Enum):
    pending = "pending"
    running = "running"
    ok = "ok"
    failed = "failed"
    skipped = "skipped"
    blocked = "blocked"

class RunState(BaseModel):
    run_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    current_step: RunStep
    step_status: Dict[RunStep, StepStatus]
    errors: List[str]
    selected_problem_id: Optional[str] = None
    selected_product_id: Optional[str] = None
    approval_required: bool
    approved: bool
    killed: bool
    paths: Dict[str, str]

class ApprovalRecord(BaseModel):
    run_id: str
    approved_at: datetime
    approved_by: str
    note: Optional[str] = None
