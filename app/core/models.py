from typing import Annotated, Optional
from pydantic import BaseModel


# ── Per-page classification ──────────────────────────────────────────────────

DOC_TYPES = [
    "claim_forms",
    "cheque_or_bank_details",
    "identity_document",
    "itemized_bill",
    "discharge_summary",
    "prescription",
    "investigation_report",
    "cash_receipt",
    "other",
]

AGENT_DOC_TYPES = {
    "id_agent": ["identity_document", "claim_forms"],
    "discharge_agent": ["discharge_summary"],
    "bill_agent": ["itemized_bill", "cash_receipt"],
}


class PageClassification(BaseModel):
    page_number: int          # 1-indexed
    doc_type: str             # one of DOC_TYPES
    base64_image: str         # page rendered as PNG → base64


# ── Reducer helpers ───────────────────────────────────────────────────────────
# LangGraph requires a reducer for every state key that multiple parallel nodes
# may write to. "last write wins" (_last) is the right semantic here because
# only one agent ever writes each key; we just need to satisfy LangGraph's
# merge requirement.

def _last(a, b):
    """Return the most-recent (rightmost) value — last-write-wins."""
    return b if b is not None else a


def _last_list(a, b):
    """For list fields: prefer the non-empty update."""
    return b if b else a


# ── LangGraph state ──────────────────────────────────────────────────────────

class ClaimState(BaseModel):
    # Use Annotated[T, reducer] so parallel nodes can write without conflict.
    claim_id: Annotated[str, _last]
    pdf_bytes: Annotated[bytes, _last]

    # Populated by segregator — prefer non-empty list
    page_classifications: Annotated[list[PageClassification], _last_list] = []

    # Populated by extraction agents — each written by exactly one agent
    id_data: Annotated[Optional[dict], _last] = None
    discharge_data: Annotated[Optional[dict], _last] = None
    bill_data: Annotated[Optional[dict], _last] = None

    # Final output
    result: Annotated[Optional[dict], _last] = None


# ── Extraction output schemas ─────────────────────────────────────────────────

class IDData(BaseModel):
    patient_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    id_numbers: Optional[list[str]] = None
    policy_number: Optional[str] = None
    patient_id: Optional[str] = None
    contact: Optional[str] = None
    address: Optional[str] = None
    insurance_provider: Optional[str] = None
    group_number: Optional[str] = None


class DischargeData(BaseModel):
    admission_date: Optional[str] = None
    discharge_date: Optional[str] = None
    length_of_stay: Optional[str] = None
    diagnosis: Optional[str] = None
    attending_physician: Optional[str] = None
    hospital: Optional[str] = None
    condition_at_discharge: Optional[str] = None
    discharge_medications: Optional[list[str]] = None
    follow_up: Optional[str] = None


class BillItem(BaseModel):
    description: str
    quantity: Optional[int] = None
    rate: Optional[float] = None
    amount: float


class BillData(BaseModel):
    items: list[BillItem] = []
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total_amount: Optional[float] = None
    insurance_payment: Optional[float] = None
    patient_responsibility: Optional[float] = None
    bill_numbers: Optional[list[str]] = None
