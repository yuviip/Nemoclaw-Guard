# Quickstart

This guide shows how to integrate Nemoclaw Guard with an agent system such as NVIDIA NemoClaw.

---

## Initial Setup

A typical setup includes:

1. installing NemoClaw
2. configuring an LLM provider
3. adding Nemoclaw Guard wrappers
4. defining policy rules

Nemoclaw Guard does not require any specific infrastructure or LLM provider.

It works anywhere the agent can execute shell commands.

---

## Example NemoClaw Setup

NemoClaw can be configured with an OpenAI provider.

Example environment variables:

OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o-mini

Nemoclaw Guard operates independently of the LLM provider.

---

## Provider Flexibility

Nemoclaw Guard is **LLM-provider agnostic**.

It works with:

OpenAI  
Anthropic  
Gemini  
local LLM models  
self-hosted inference servers  

The policy engine itself does **not depend on any LLM**.

---

## Minimal Token Usage

Nemoclaw Guard minimizes token usage by design.

Policy evaluation happens locally.

This means:

- blocked operations consume zero tokens
- allowed operations do not require LLM reasoning
- only minimal context may be sent when needed

This significantly reduces cost and latency.

---

## Example Workflow

Agent request:

guarded_git_push.sh user role repo origin main

Wrapper flow:

1. build resource
2. evaluate policy
3. execute only if allowed

---

## Extending the System

New wrappers can be added for:

docker  
kubernetes  
systemctl  
file management  
external APIs  

Nemoclaw Guard acts as the **policy gate** for these operations.
