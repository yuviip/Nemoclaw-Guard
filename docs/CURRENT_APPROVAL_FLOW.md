# Nemoclaw Guard — Current Approval Flow

This document describes the current runtime approval flow implemented in Nemoclaw Guard.

The goal of the approval flow is to prevent dangerous system actions from executing without explicit human approval.

The system is designed to work across different agents and communication channels.


--------------------------------------------------

High Level Flow

1. Agent requests a tool action
2. Nemoclaw plugin intercepts the action
3. Runtime classifies the action
4. Policy engine evaluates the action
5. If approval is required, a pending approval is created
6. A human approval request is sent through a communication channel
7. Human replies with approval or denial
8. Approval resolver interprets the reply
9. Runtime executes the action if approved
10. Execution result is returned to the agent


--------------------------------------------------

Detailed Flow

Step 1 — Agent Action Request

An agent attempts to perform a system action such as:

- deleting a file
- stopping a service
- executing a command


Step 2 — Plugin Interception

The Nemoclaw plugin intercepts the action request before it reaches the system.


Step 3 — Policy Decision

The policy engine evaluates the request.

Possible outcomes:

- allow
- deny
- approval_required


Step 4 — Approval Request

If approval is required:

- an approval record is created
- the action is marked as pending


Step 5 — Human Approval

A human receives the approval request via a communication channel.

Examples:

- WhatsApp
- Slack
- Email
- CLI


Step 6 — Approval Resolution

The approval response is sent to the approval resolver which determines whether the reply means:

- approved
- denied
- needs clarification


Step 7 — Execution

If approved:

- the runtime dispatches the action to the appropriate execution handler


Step 8 — Execution Result

The execution result is recorded and returned to the agent.


--------------------------------------------------

Key Safety Properties

Nemoclaw Guard ensures:

- dangerous actions require explicit human approval
- approvals are interpreted using structured resolution
- actions are executed only once
- execution results are recorded


--------------------------------------------------

Future Improvements

Future versions of Nemoclaw Guard will introduce:

- action IDs
- execution receipts
- improved replay protection
- structured action schemas
- provider-based execution model
