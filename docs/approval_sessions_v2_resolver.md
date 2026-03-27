# Approval Sessions V2 - Generic Resolver

## Goal
Add a generic approval resolver layer that can interpret a user reply
against a pending approval session, without hard-coded language rules.

## Principles
- keep token usage low
- prefer deterministic matching first
- allow later family-specific adapters
- do not hard-code one exact approval sentence
- do not depend on full absolute path repetition only

## Inputs
- pending approval session object
- user reply text
- optional chat/session metadata

## Output
Resolver returns one of:

{
  "result": "single_action_approve" | "whole_session_approve" | "deny" | "no_match",
  "matched_action_ids": [],
  "reason": "<short_reason>"
}

## Matching model

### 1. Exact structural commands
High-confidence explicit commands should match first.

Examples:
- /approve
- /approve all
- /deny
- /deny all

Exact command words should remain configurable, not hard-coded inside logic.

### 2. Resource-aware free text matching
If user reply contains a resource display name, alias, or primary identifier
from a pending action, treat that as a candidate match.

Examples:
- "מאשר למחוק test123"
- "תמחק את test123"
- "אל תמחק test123"
- "approve test123"
- "delete test123"

### 3. Session-wide intent
If the reply clearly refers to all pending actions in the request session,
resolver may return whole_session_approve.

Examples:
- "מאשר הכל"
- "תאשר הכל"
- "approve all"
- "כולן"

This must remain configurable and extensible.

### 4. Deny intent
If reply clearly indicates cancellation / deny, return deny.

Examples:
- "אל תמחק"
- "עזוב"
- "cancel"
- "deny"

This must remain configurable and extensible.

## Generic matching stages

1. Normalize text
   - trim
   - lowercase where relevant
   - collapse spaces
   - preserve original text too

2. Structural command match
   - check configured explicit commands

3. Resource alias match
   - compare against:
     - resource.primary
     - resource.display
     - resource.aliases[]

4. Scope inference
   - one action matched -> single_action_approve
   - multiple actions + all-session wording -> whole_session_approve
   - deny wording -> deny
   - otherwise -> no_match

## Non-goals in V2
- no family-specific destructive policy logic here
- no direct execution here
- no final approval persistence format yet
- no LLM dependence required for baseline resolver

## Extension point
Later each family may contribute:
- aliases builder
- display formatter
- additional match hints
- family-specific confirmation rules

Examples:
- file.delete
- ha.service_call
- docker.restart
- systemctl
- git.push

## Next stage
V3 should implement the first family adapter for file.delete.
