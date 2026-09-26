---
title: 'Implement Epic 1 Story 1: triage decision schema'
type: 'feature'
created: '2026-09-26'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: ['{project-root}/AGENTS.md', '{project-root}/_bmad-output/specs/spec-epic-1/SPEC.md', '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Epic 1 needs a reusable, strict contract for triage decisions so malformed model or application output cannot pass downstream as a valid decision.

**Approach:** Add a Pydantic-backed `triage.schema` module exposing typed category, priority, and route values, a `TriageDecision` model, and a `validate_decision` entry point that accepts JSON text or dictionaries and raises a clear validation error for malformed input.

**Always:** Allow only categories `billing`, `bug`, `access`, `performance`, and `how-to`; priorities `P1` through `P4`; and routes `billing-team`, `bug-team`, `access-team`, `performance-team`, and `how-to-team`. Require a non-empty one-sentence rationale, reject extra or missing fields, and keep validated decisions immutable. Use the existing Python 3.12+/uv and Pydantic dependencies; make no network calls and require no API keys.

**Never:** Do not implement the agent, seed loader, MCP tools, evals, or UI. Do not modify `INTENT.md`, the Epic 1 spec, `seed/`, `mcp/triage_server.py`, or unrelated existing worktree changes.

**Validation behavior:** Parse JSON strings and bytes, accept dictionaries, and reject invalid JSON, non-object payloads, unsupported enum values, missing fields, blank or multi-sentence rationales, and unknown fields with `TriageValidationError` messages that identify the problem field when applicable.

</frozen-after-approval>

## Implementation Notes

- Added `triage.schema` with Pydantic literal fields, frozen extra-forbid validation, one-sentence rationale checking, and clear `TriageValidationError` wrapping.
- Added focused schema tests covering valid dict/JSON input, invalid and missing fields, non-object payloads, and immutability.
- Reused the repository's existing Pydantic dependency and did not modify the loader, MCP server, agent, or unrelated worktree changes.
- Verification passed: the full available test suite reports 21 passing tests; the default pytest environment requires disabling its native debugging plugin because it segfaults before test collection.
