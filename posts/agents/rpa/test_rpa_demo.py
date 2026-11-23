from rpa_demo import FakeERP, Invoice, State, TransientUIError, run_invoice

def test_normal_invoice_reaches_done():
    erp = FakeERP()
    result = run_invoice(Invoice("INV-001", 12500, 12500), erp)
    assert result.state is State.DONE
    assert erp.records == {"INV-001": 12500}
    assert erp.post_count == 1

def test_amount_mismatch_is_escalated_without_write():
    erp = FakeERP()
    result = run_invoice(Invoice("INV-002", 12500, 12000), erp)
    assert result.state is State.HUMAN_REVIEW
    assert erp.records == {}
    assert erp.post_count == 0

def test_missing_approval_is_escalated_without_write():
    erp = FakeERP()
    result = run_invoice(Invoice("INV-003", 12500, 12500, approved=False), erp)
    assert result.state is State.HUMAN_REVIEW
    assert erp.records == {}
    assert erp.post_count == 0

def test_lost_ack_after_commit_retries_idempotently():
    erp = FakeERP(timeout_after_commit_once=True)
    result = run_invoice(Invoice("INV-004", 12500, 12500), erp, max_retries=1)
    assert result.state is State.DONE
    assert erp.records == {"INV-004": 12500}
    assert erp.post_count == 1
    assert any(event["state"] == State.WRITE_UNCERTAIN.value for event in result.events)

def test_retry_budget_exhaustion_escalates():
    class AlwaysTimeoutERP(FakeERP):
        def post_invoice(self, invoice_id, amount_cents):
            raise TransientUIError("acknowledgement unavailable")
    erp = AlwaysTimeoutERP()
    result = run_invoice(Invoice("INV-005", 12500, 12500), erp, max_retries=1)
    assert result.state is State.HUMAN_REVIEW
    assert erp.post_count == 0
