# State Machines & Workflow Control

**Stable topic:** `agents/state-machines`

## Scope

Study explicit discrete control models used by protocols, tools, workflows and Agent runtimes:

- state, event, transition, guard, action and terminal-state semantics;
- DFA/NFA, Mealy/Moore machines and transition systems as formal foundations;
- extended finite-state machines, hierarchical statecharts and orthogonal regions;
- safety, liveness, reachability, deadlock and transition-coverage reasoning;
- durable workflow concerns: retries, timeouts, cancellation, idempotency, persistence and concurrent workers.

## Boundaries

- Neural hidden states and State Space Models (SSMs) are not finite-state machines.
- MDPs add probabilistic transitions, actions and rewards; they are decision models, not synonyms for FSMs.
- Event sourcing persists facts and reconstructs state; a state machine specifies legal transitions.
- A workflow engine operationalizes durable execution, timers and retries; it may implement a state machine but is not identical to the abstract model.

## Reading order

1. [Understanding State Machines](../../state-machines/index.html)
2. [Understanding Function Calling](../../function-calling/index.html)
3. [Understanding Harness Engineering](../../harness-engineering/index.html)
4. [Understanding Loop Engineering](../../loop-engineering/index.html)

A topic placeholder is navigation and scope documentation, not a separately published article.
