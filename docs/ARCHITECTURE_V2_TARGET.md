# Nemoclaw Guard — Target Architecture (v2)

This document describes the intended long-term architecture of Nemoclaw Guard.

Nemoclaw Guard is designed as a security guardrails layer for AI agents and automation systems, enforcing policy decisions and human approvals before dangerous system actions are executed.

The system is intentionally designed to be:

- agent-agnostic
- channel-agnostic
- execution-provider based
- policy-driven
- audit-friendly


--------------------------------------------------

CORE ARCHITECTURE

Agent
  ↓
Agent Adapter
  ↓
Nemoclaw Runtime
  ↓
Policy Engine
  ↓
Execution Providers


--------------------------------------------------

1. Agent Adapters

Agent adapters integrate Nemoclaw Guard with different agent frameworks.

Examples:

- OpenClaw plugin
- LangChain middleware
- CLI wrappers
- REST gateways

Responsibilities:

- capture action requests from agents
- normalize requests to Nemoclaw action schema
- forward requests to runtime
- return execution results to the agent

Adapters MUST NOT:

- implement policy logic
- interpret approval decisions
- execute system actions directly


--------------------------------------------------

2. Nemoclaw Runtime

The runtime orchestrates the lifecycle of guarded actions.

Responsibilities:

- action normalization
- risk classification
- approval lifecycle management
- execution routing
- replay protection
- execution receipts
- audit event generation

Key components:

- Action Registry
- Approval Engine
- Execution Router
- Replay Guard
- State Manager


--------------------------------------------------

3. Policy Engine

The policy engine determines whether an action should be:

- allowed
- denied
- require approval

Example rule:

action: file.delete
path: /tmp/*
decision: allow

Example requiring approval:

action: service.stop
decision: approval_required


--------------------------------------------------

4. Approval Lifecycle

Approval lifecycle states:

pending
approved
denied
expired
executed
failed

Approval metadata includes:

- approval_id
- action_id
- created_at
- decided_at
- decided_by
- decision_reason


--------------------------------------------------

5. Execution Providers

Execution providers perform real system actions.

Examples:

- file provider
- system service provider
- docker provider
- git provider
- home assistant provider

Example execution receipt:

{
  "execution_id": "exec_123",
  "action_id": "act_123",
  "status": "executed",
  "provider": "file_provider"
}


--------------------------------------------------

Action Model

Example action request:

{
  "action_id": "act_123",
  "family": "file.delete",
  "target": "/tmp/test.txt",
  "requested_by": {
    "agent": "openclaw"
  },
  "risk_level": "high"
}


--------------------------------------------------

Replay Protection

Execution must never happen twice unintentionally.

Nemoclaw Guard uses execution receipts and action IDs to ensure:

- duplicate executions are prevented
- replay attacks are mitigated
- execution outcomes remain auditable


--------------------------------------------------

Audit Trail

Every guarded action generates a complete audit trail:

- action request
- policy decision
- approval record
- execution receipt

These records enable traceability and forensic debugging.


--------------------------------------------------

Long Term Goals

Future expansions:

- multi-agent integrations
- multi-channel approvals (Slack / WhatsApp / Email / UI)
- policy bundles
- centralized audit services
- provider plugins ecosystem

Nemoclaw Guard aims to become a standard guardrails layer for AI agents and automation systems.

