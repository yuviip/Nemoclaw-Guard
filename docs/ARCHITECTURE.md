# Nemoclaw Guard Architecture

Nemoclaw Guard implements a lightweight guardrail layer for agent-driven systems.

The architecture separates **capabilities**, **policy**, and **execution**, allowing automation agents to operate safely without embedding security logic inside the agent itself.

Core model:

Agent → Guarded Wrapper → Policy Engine → Decision → Action

---

## Architectural Goals

The system is designed around several core principles:

- agent-agnostic execution
- minimal runtime overhead
- deterministic policy decisions
- human-readable configuration
- minimal LLM involvement
- extensible capability model

Nemoclaw Guard is intentionally simple so it can operate in:

- AI agent runtimes
- DevOps tooling
- automation frameworks
- CI/CD pipelines
- self-hosted infrastructure
- home automation environments

---

## Core Components

### Agent

An AI agent or automation system that wants to perform an action.

Examples:

- OpenClaw
- NVIDIA NemoClaw
- other LLM-driven agents
- CLI automation scripts
- DevOps pipelines

Agents **never execute system actions directly**.

Instead they call guarded wrappers.

---

### Guarded Wrappers

Wrappers are small scripts that perform two tasks:

1. Build a policy request
2. Enforce the policy decision

Example wrapper:

guarded_git_push.sh

Wrappers translate a real system operation into a **policy request**.

Example request:

action: git_push  
resource: repo_name:origin:main  
risk: high  

---

### Policy Engine

The policy engine evaluates whether an action is allowed.

Inputs:

- requester identity
- requester role
- action
- resource
- risk level

Possible outcomes:

ALLOW  
DENY  
REQUIRE_OWNER_CONFIRMATION  
REQUIRE_OWNER_APPROVAL  

Only ALLOW results in execution.

---

### Skills

Skills define what capabilities exist in the system.

Each skill declares:

- action
- resource type
- expected parameters
- default risk

Examples:

ha_control  
git_push  
delete_files  

Skills allow the system to remain **extensible without modifying core logic**.

---

### Policy Configuration

Policies are defined in configuration files.

users.yml  
permissions.yml  

These define:

- identities
- roles
- rule sets
- resource restrictions
- risk escalation rules

Policies are designed to remain:

- human-readable
- auditable
- version controllable

---

## Token Efficiency

Nemoclaw Guard minimizes LLM usage.

Most policy decisions are evaluated locally.

Blocked operations consume **zero tokens**.

Even when used in LLM-driven environments, Nemoclaw Guard prevents unnecessary model calls.

---

## Integration with NemoClaw

Nemoclaw Guard complements NVIDIA NemoClaw by providing a safety layer around agent-driven execution.

NemoClaw provides execution capabilities.

Nemoclaw Guard provides **policy enforcement and guardrails**.

