import pytest

from examples.agent_state_machine import Context, Event, InvalidTransition, State, run, transition


def test_low_risk_task_skips_approval_and_succeeds():
    state, context = run([Event.SUBMIT, Event.PASS, Event.SUCCESS], Context(requires_approval=False))
    assert state is State.SUCCEEDED
    assert context.attempts == 1


def test_high_risk_task_requires_approval():
    state, context = run([Event.SUBMIT, Event.PASS], Context(requires_approval=True))
    assert state is State.AWAITING_APPROVAL
    state, context = transition(state, Event.APPROVE, context)
    assert state is State.RUNNING
    assert context.attempts == 1


def test_retries_are_bounded_by_attempt_budget():
    state, context = run(
        [Event.SUBMIT, Event.PASS, Event.FAIL, Event.RETRY, Event.TIMEOUT],
        Context(max_attempts=2),
    )
    assert state is State.FAILED
    assert context.attempts == 2


def test_retry_wait_does_not_retry_without_retry_event():
    state, context = run([Event.SUBMIT, Event.PASS, Event.FAIL], Context(max_attempts=3))
    assert state is State.RETRY_WAIT
    with pytest.raises(InvalidTransition):
        transition(state, Event.SUCCESS, context)


def test_invalid_input_and_approval_rejection_are_terminal():
    state, _ = run([Event.SUBMIT, Event.INVALID])
    assert state is State.FAILED
    state, _ = run(
        [Event.SUBMIT, Event.PASS, Event.REJECT],
        Context(requires_approval=True),
    )
    assert state is State.CANCELLED


def test_cancel_is_supported_from_active_execution_states():
    state, context = run([Event.SUBMIT, Event.PASS], Context())
    state, _ = transition(state, Event.CANCEL, context)
    assert state is State.CANCELLED


def test_terminal_reset_starts_a_new_attempt_sequence():
    state, context = run([Event.SUBMIT, Event.PASS, Event.SUCCESS], Context())
    state, context = transition(state, Event.RESET, context)
    assert state is State.IDLE
    assert context.attempts == 0


def test_illegal_event_is_rejected_without_mutating_context():
    context = Context(requires_approval=True)
    with pytest.raises(InvalidTransition):
        transition(State.IDLE, Event.APPROVE, context)
    assert context.attempts == 0


def test_context_rejects_invalid_retry_configuration():
    with pytest.raises(ValueError):
        Context(max_attempts=0)
    with pytest.raises(ValueError):
        Context(attempts=3, max_attempts=2)
