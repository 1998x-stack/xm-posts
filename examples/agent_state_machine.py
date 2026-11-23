"""A small, deterministic Agent task EFSM used by the article.

This is a teaching model, not a durable workflow engine.
"""
from dataclasses import dataclass, replace
from enum import Enum


class State(str, Enum):
    IDLE = "idle"
    VALIDATING = "validating"
    AWAITING_APPROVAL = "awaiting_approval"
    RUNNING = "running"
    RETRY_WAIT = "retry_wait"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Event(str, Enum):
    SUBMIT = "submit"
    PASS = "pass"
    INVALID = "invalid"
    APPROVE = "approve"
    REJECT = "reject"
    SUCCESS = "success"
    FAIL = "fail"
    TIMEOUT = "timeout"
    RETRY = "retry"
    CANCEL = "cancel"
    RESET = "reset"


TERMINAL_STATES = frozenset({State.SUCCEEDED, State.FAILED, State.CANCELLED})


@dataclass(frozen=True)
class Context:
    requires_approval: bool = False
    attempts: int = 0
    max_attempts: int = 2

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least one")
        if not 0 <= self.attempts <= self.max_attempts:
            raise ValueError("attempts must be within the configured retry budget")


class InvalidTransition(ValueError):
    """Raised when an event is not legal in the current state."""


def transition(state: State, event: Event, context: Context) -> tuple[State, Context]:
    """Apply exactly one legal event; return the next state and context."""
    if state is State.IDLE and event is Event.SUBMIT:
        return State.VALIDATING, replace(context, attempts=0)

    if state is State.VALIDATING and event is Event.PASS:
        if context.requires_approval:
            return State.AWAITING_APPROVAL, context
        return State.RUNNING, replace(context, attempts=1)

    if state is State.VALIDATING and event is Event.INVALID:
        return State.FAILED, context

    if state is State.AWAITING_APPROVAL and event is Event.APPROVE:
        return State.RUNNING, replace(context, attempts=1)

    if state is State.AWAITING_APPROVAL and event in {Event.REJECT, Event.CANCEL}:
        return State.CANCELLED, context

    if state is State.RUNNING and event is Event.SUCCESS:
        return State.SUCCEEDED, context

    if state is State.RUNNING and event in {Event.FAIL, Event.TIMEOUT}:
        next_state = State.RETRY_WAIT if context.attempts < context.max_attempts else State.FAILED
        return next_state, context

    if state is State.RETRY_WAIT and event is Event.RETRY:
        return State.RUNNING, replace(context, attempts=context.attempts + 1)

    if state in {State.RUNNING, State.RETRY_WAIT} and event is Event.CANCEL:
        return State.CANCELLED, context

    if state in TERMINAL_STATES and event is Event.RESET:
        return State.IDLE, replace(context, attempts=0)

    raise InvalidTransition(f"{event.value!r} is not valid while {state.value!r}")


def run(events: list[Event], context: Context | None = None) -> tuple[State, Context]:
    """Run a sequence of events and return its final state/context."""
    state = State.IDLE
    current = context or Context()
    for event in events:
        state, current = transition(state, event, current)
    return state, current
