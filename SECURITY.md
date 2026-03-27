# Security Policy

Nemoclaw Guard is designed as a safety layer for agent-driven systems.

The project focuses on preventing automation agents from performing unsafe or unauthorized actions.

---

## Security Model

The core security model is based on:

RBAC + resource-level policy rules

Each action request contains:

- identity
- role
- action
- resource
- risk level

The policy engine evaluates the request before execution.

Possible decisions:

ALLOW  
DENY  
REQUIRE_OWNER_CONFIRMATION  
REQUIRE_OWNER_APPROVAL  

Only ALLOW results in execution.

---

## Threat Model

Nemoclaw Guard is designed to mitigate risks such as:

- unsafe automation
- accidental infrastructure changes
- unauthorized git pushes
- destructive file operations
- unintended system actions triggered by AI agents

The system assumes:

- the agent environment may be imperfect
- LLM outputs may contain mistakes
- automation pipelines may trigger unexpected actions

Nemoclaw Guard acts as a **deterministic safety layer**.

---

## Responsible Disclosure

If you discover a security issue, please report it responsibly.

Do not publicly disclose vulnerabilities before maintainers have had a chance to investigate and respond.

