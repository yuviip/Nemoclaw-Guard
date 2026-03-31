# Nemoclaw Guard — Plugin / Runtime Boundary

This document defines the intended boundary between:

- agent adapters (such as the OpenClaw plugin)
- the Nemoclaw Guard runtime

The goal is to keep agent-specific logic thin and move security logic into the runtime.


--------------------------------------------------

High Level Model

Agent
↓
Agent Adapter (plugin)
↓
Nemoclaw Runtime
↓
Execution Providers


--------------------------------------------------

1. Responsibilities of the Agent Adapter

Agent adapters integrate Nemoclaw Guard with agent frameworks.

Examples:

- OpenClaw plugin
- LangChain middleware
- CLI wrappers
- REST gateways


Adapter responsibilities:

- intercept agent action requests
- normalize requests into Nemoclaw action objects
- forward requests to the runtime
- deliver runtime responses back to the agent


Adapters should also handle:

- agent session correlation
- chat/session mapping
- transport of approval requests and responses


--------------------------------------------------

2. Responsibilities of the Runtime

The Nemoclaw runtime is responsible for all guardrail logic.

Runtime responsibilities include:

- action normalization
- policy evaluation
- approval lifecycle management
- approval resolution
- execution routing
- replay protection
- audit logging


The runtime decides whether an action is:

- allowed
- denied
- requires approval


--------------------------------------------------

3. What Must Not Live in the Adapter

Adapters should remain thin.

Adapters should NOT implement:

- policy logic
- approval resolution
- approval lifecycle state machines
- execution logic
- replay protection logic


These responsibilities must live in the runtime.


--------------------------------------------------

4. Current Transitional State

The current OpenClaw plugin still performs some responsibilities
that should eventually move into the runtime.

Examples include:

- partial approval orchestration
- runtime invocation logic
- duplicate execution suppression tied to the plugin state


These areas are transitional and expected to evolve.


--------------------------------------------------

5. Target Direction

The intended direction is:

- plugin becomes a thin adapter
- runtime owns the security model
- execution providers handle real system operations
- adapters simply transport requests and responses

This separation allows Nemoclaw Guard to support:

- multiple agent frameworks
- multiple communication channels
- multiple execution providers

without duplicating security logic.
