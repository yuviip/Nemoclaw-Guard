# Nemoclaw Guard

Nemoclaw Guard is a lightweight **policy-gated execution layer** for AI agents, automation systems, and operator-driven tooling.

It was originally built around **OpenClaw** and designed to integrate naturally with the NVIDIA NemoClaw ecosystem, but its architecture is intentionally **agent-agnostic** and can be used with any system capable of executing shell wrappers or guarded commands.

NVIDIA NemoClaw:
https://build.nvidia.com/nemoclaw

NVIDIA NemoClaw repository:
https://github.com/NVIDIA/NemoClaw

---

## What Nemoclaw Guard is

Nemoclaw Guard implements a **lightweight RBAC + resource policy model** adapted for agent-driven environments.

Instead of allowing an agent to execute sensitive actions directly, Nemoclaw Guard places a **policy enforcement layer** between the agent and the real system action.

Core idea:

Agent → Guarded Wrapper → Policy Engine → Decision → Action

This allows a system to enforce permissions before executing operations such as:

- Home Assistant service calls
- Git pushes
- filesystem operations
- infrastructure commands
- external integrations

Capabilities are implemented as **wrappers** and **skills**.  
Permissions are defined by **policy**.
Policies are human-readable and configuration-driven.

This makes the system:

- safer
- auditable
- configurable
- easy to extend

---

## What this project is for

Nemoclaw Guard was originally built for the OpenClaw ecosystem and validated with NVIDIA NemoClaw-style agent execution flows, but the design itself is generic.

It can be used with:

- OpenClaw
- NVIDIA NemoClaw
- other AI agents
- automation systems
- CLI tools
- DevOps workflows
- self-hosted orchestration systems

If a system can call a wrapper or shell command, it can use Nemoclaw Guard.

---

## Architecture

Nemoclaw Guard is composed of three layers.

### 1. Policy Layer

Defines **who can do what**.

Typical files:

users.yml  
permissions.yml  

These define:

- users
- aliases
- roles
- rules
- default risk handling

### 2. SDK Layer

Reusable helper library used by wrappers.

Location:

sdk/lib/policy_sdk.sh

Current helper functions include:

- policy_decide
- policy_extract_decision
- policy_is_allowed
- policy_require_allow
- policy_echo_and_require_allow
- policy_build_git_push_resource
- policy_build_ha_resource

Wrappers use this SDK to enforce policy before executing actions.

### 3. Skills Layer

Skills describe the capabilities available in the system.

Examples currently included:

- ha_control
- git_push
- delete_files

Each skill defines:

- action
- resource type
- expected inputs
- default risk level

Skills are declared in:

skills/registry.yml

---

## Example flow

1. A wrapper receives a request.

Example:

guarded_git_push.sh requester_id requester_role /repo/path origin main

2. The wrapper builds a policy request.

Example:

action = git_push  
resource = repo_name:origin:main  
risk = high  

3. The policy engine evaluates the request.

Possible decisions:

ALLOW  
DENY  
REQUIRE_OWNER_CONFIRMATION  
REQUIRE_OWNER_APPROVAL  

4. Only ALLOW executes the action.

---

## LLM provider setup

Nemoclaw Guard itself does **not require an LLM**.

The policy engine evaluates requests locally using configuration rules.

However, the surrounding agent environment may rely on an LLM. In the initial setup, NVIDIA NemoClaw was configured with an OpenAI provider.

Example environment variables:

OPENAI_API_KEY=your_api_key  
OPENAI_MODEL=gpt-4o-mini  

Nemoclaw Guard sits **between the agent and the system actions**, meaning that the LLM never executes sensitive system operations directly.

This architecture works with **any LLM provider**, including:

- OpenAI
- Anthropic
- Google Gemini
- local LLM models
- self-hosted inference servers

Nemoclaw Guard is therefore **LLM-provider agnostic**.

---

## Token efficiency

Nemoclaw Guard is designed to minimize token usage.

Key principles:

- policy decisions are evaluated locally
- blocked actions consume zero tokens
- allowed actions do not require LLM reasoning
- only minimal context is ever sent when LLM interaction is needed

This makes the system:

- faster
- cheaper
- deterministic
- suitable for high-frequency automation

Many operations are **blocked immediately by policy** without any LLM involvement.

---

## Relation to NemoClaw

Nemoclaw Guard integrates naturally with **NVIDIA NemoClaw**.

NemoClaw allows agents to execute system actions such as:

- filesystem operations
- infrastructure commands
- automation tasks
- service control

Without guardrails these capabilities can be dangerous.

Nemoclaw Guard acts as a **policy enforcement layer** between the agent and the system.

Agent  
↓  
Guarded Wrapper  
↓  
Policy Engine  
↓  
Decision  
↓  
System Action  

Official NemoClaw resources:

https://build.nvidia.com/nemoclaw  
https://github.com/NVIDIA/NemoClaw  

Nemoclaw Guard complements NemoClaw by providing a lightweight safety layer for agent-driven operations.

---

## What can be changed

Nemoclaw Guard is designed to be highly customizable.

You can add or change:

Users  
Update users.yml to define your own identities, aliases, and roles.

Roles examples:

owner  
family  
guest  
operator  
admin  
devops  

Policy rules can restrict:

- Home Assistant entities
- Git repositories and branches
- file paths
- infrastructure actions
- custom resources

You can also add new guarded wrappers such as:

guarded_read_path.sh  
guarded_write_file.sh  
guarded_docker_restart.sh  
guarded_systemctl_restart.sh  
guarded_kubernetes_apply.sh  

Skills can be extended by adding manifests under skills/.

---

## Current included examples

SDK

- shell-based policy enforcement helpers
- example wrapper using the SDK

Skills

- Home Assistant control
- Git push protection
- file deletion protection
- Docker restart protection
- Systemctl control skeleton

Policy examples

users.example.yml  
permissions.example.yml  

---

## Why this exists

Automation agents are powerful, but without guardrails they can easily perform:

- destructive infrastructure actions
- unsafe git pushes
- accidental service calls
- dangerous file operations
- risky system changes

Nemoclaw Guard provides a simple and transparent enforcement layer to keep agent-driven systems safer and more controllable.

---

## Design principles

- wrappers define capabilities
- policy defines permissions
- identities are configuration-driven
- roles are configuration-driven
- resources are explicit
- risky actions should be gated
- the system should be easy to extend

---

## Project layout

nemoclaw-guard/

README.md

docs/

policy/
users.example.yml
permissions.example.yml

sdk/
lib/policy_sdk.sh
examples/example_wrapper.sh

skills/
registry.yml
delete_files/skill.yml
git_push/skill.yml
ha_control/skill.yml

---

## Intended next steps

Typical next extensions:

- read-path wrapper
- write-file wrapper
- named-action wrapper
- permissions-admin wrapper
- richer SDK helpers
- additional documentation
- GitHub packaging

---

## License

MIT is recommended for open-source distribution.



Testing

- Refactored wrapper test harness documentation: docs/TESTING.md


## Investigation Notes

- OpenClaw exec hook investigation findings: 
