"""Deterministic teaching simulator for an invoice RPA workflow."""
from dataclasses import dataclass, field
from enum import Enum

class State(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    MATCHED = "MATCHED"
    APPROVED = "APPROVED"
    WRITE_UNCERTAIN = "WRITE_UNCERTAIN"
    POSTED = "POSTED"
    VERIFIED = "VERIFIED"
    DONE = "DONE"
    HUMAN_REVIEW = "HUMAN_REVIEW"

class TransientUIError(Exception):
    """The UI acknowledgement was lost; the business write may have committed."""

@dataclass(frozen=True)
class Invoice:
    invoice_id: str
    amount_cents: int
    po_amount_cents: int
    approved: bool = True

class FakeERP:
    """Idempotent adapter keyed by invoice_id."""
    def __init__(self, timeout_after_commit_once: bool = False):
        self.records: dict[str, int] = {}
        self.post_count = 0
        self.timeout_after_commit_once = timeout_after_commit_once

    def post_invoice(self, invoice_id: str, amount_cents: int) -> int:
        if invoice_id in self.records:
            return self.records[invoice_id]
        self.records[invoice_id] = amount_cents
        self.post_count += 1
        if self.timeout_after_commit_once:
            self.timeout_after_commit_once = False
            raise TransientUIError("commit succeeded; acknowledgement lost")
        return amount_cents

    def read_invoice(self, invoice_id: str) -> int | None:
        return self.records.get(invoice_id)

@dataclass
class RunResult:
    state: State
    events: list[dict[str, str]] = field(default_factory=list)

def run_invoice(invoice: Invoice, erp: FakeERP, max_retries: int = 1) -> RunResult:
    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")
    events: list[dict[str, str]] = []
    def emit(state: State, detail: str) -> None:
        events.append({"state": state.value, "detail": detail})
    def review(detail: str) -> RunResult:
        emit(State.HUMAN_REVIEW, detail)
        return RunResult(State.HUMAN_REVIEW, events)

    emit(State.RECEIVED, "case accepted")
    if invoice.amount_cents <= 0:
        return review("amount must be positive")
    emit(State.VALIDATED, "required fields are valid")
    if invoice.amount_cents != invoice.po_amount_cents:
        return review("purchase order amount mismatch")
    emit(State.MATCHED, "invoice matches purchase order")
    if not invoice.approved:
        return review("approval is missing")
    emit(State.APPROVED, "business approval is present")

    for attempt in range(max_retries + 1):
        try:
            erp.post_invoice(invoice.invoice_id, invoice.amount_cents)
            break
        except TransientUIError:
            emit(State.WRITE_UNCERTAIN, "write outcome is uncertain; reconcile before retry")
            if attempt == max_retries:
                return review("retry budget exhausted; manual reconciliation required")

    stored = erp.read_invoice(invoice.invoice_id)
    if stored != invoice.amount_cents:
        return review("read-after-write verification failed")
    emit(State.POSTED, "record exists")
    emit(State.VERIFIED, "persisted amount matches")
    emit(State.DONE, "postconditions satisfied")
    return RunResult(State.DONE, events)
