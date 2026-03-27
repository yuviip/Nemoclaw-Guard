# Contributing to Nemoclaw Guard

Thank you for your interest in improving Nemoclaw Guard.

This project aims to remain lightweight, deterministic, and easy to audit.

---

## Contribution Guidelines

Good contributions include:

- new guarded wrappers
- additional skills
- improvements to policy helpers
- documentation improvements
- architecture clarifications
- integration examples

---

## Design Principles

When contributing, please follow these principles:

- keep the system simple
- avoid unnecessary dependencies
- prioritize deterministic behavior
- keep policies human-readable
- minimize LLM coupling

Nemoclaw Guard should remain usable in environments where:

- no LLM is available
- minimal resources exist
- automation must remain predictable

---

## Suggested Extensions

Examples of useful contributions:

- docker control wrappers
- kubernetes wrappers
- terraform wrappers
- CI/CD guardrails
- additional policy helpers
- richer skill definitions

---

## Development Philosophy

Nemoclaw Guard favors:

- transparency
- explicit policy rules
- minimal complexity
- agent-agnostic design

