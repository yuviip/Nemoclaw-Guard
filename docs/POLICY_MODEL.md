# Policy Model

Nemoclaw Guard implements a lightweight **RBAC + Resource Policy model** designed for AI agents and automation systems.

RBAC = Role-Based Access Control.

In addition to roles, Nemoclaw Guard evaluates **resources and risk levels**.

---

## Core Request Structure

Every request evaluated by the policy engine contains:

identity
role
action
resource
risk_level

Example:

action = git_push
resource = repo:origin:main
risk_level = high

---

## Roles

Roles group users by permission level.

Examples:

owner
family
guest
operator
admin
devops

Roles are defined in:

permissions.yml

---

## Users

Users are defined in:

users.yml

Example:

Example configuration:

```yaml
users:
  - id: owner
    aliases:
      - admin
    role: owner
```

Aliases allow mapping external identities to internal policy users.

---

## Rules

Rules define permissions.

Example rule:

- subject: role:family
  action: git_push
  resource: "*:*:*"
  effect: DENY

Each rule defines:

subject
action
resource
effect

---

## Effects

Possible effects:

ALLOW
DENY

The policy engine can also return:

REQUIRE_OWNER_CONFIRMATION
REQUIRE_OWNER_APPROVAL

These decisions depend on risk configuration.

---

## Resource Model

Resources are strings representing system objects.

Examples:

repo:origin:main
light.turn_on:light.kitchen
/tmp/example/file.txt

Each wrapper defines its own resource format.

---

## Why Resource Policies Matter

Traditional RBAC only controls actions.

Agent systems require **resource-level restrictions**.

Examples:

Allow example:

light.turn_on:light.*

Block example:

switch.turn_on:switch.boiler

This allows precise control of automation systems.

---

## Policy First Design

Nemoclaw Guard evaluates policy **before any system action occurs**.

This ensures that:

- blocked actions never execute
- risky actions require approval
- policies remain transparent and auditable

Policy evaluation is local and deterministic.

No LLM interaction is required for policy decisions.
