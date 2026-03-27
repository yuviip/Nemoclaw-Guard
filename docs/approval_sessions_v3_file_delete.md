# Approval Sessions V3 - file.delete Adapter

## Goal
Define how file.delete actions integrate with the generic approval resolver.

This stage still does NOT change runtime logic.

## Resource model

For file.delete, each action should expose:

{
  "resource": {
    "kind": "file",
    "primary": "/tmp/test123",
    "display": "test123",
    "aliases": [
      "/tmp/test123",
      "test123"
    ]
  }
}

## Matching rules

### 1. Exact path match
If user mentions the full path, match directly.

Example:
- "/tmp/test123"

### 2. Basename match
If user mentions only the filename, match against display.

Example:
- "test123"

### 3. Alias match
Aliases allow flexible matching without requiring full path.

## Ambiguity rule

If multiple pending actions share the same basename:
- do NOT auto-approve
- resolver must return no_match or ambiguous

## Approval examples (generic, not language-bound)

User replies that should match a file action:

- positive + resource match → approve
- negative + resource match → deny

Examples:
- "<positive> + test123"
- "<negative> + test123"

The actual words for positive/negative must NOT be hard-coded here.

## Session behavior

If multiple file.delete actions exist in one session:

- "approve all" style intent → whole_session_approve
- otherwise → require resource match

## Safety constraints

- never delete multiple files from a vague reply
- always prefer specific match over global approval
- require clarity when ambiguity exists

## Next stage

V4: connect resolver + file.delete into guarded_file_delete.sh flow
