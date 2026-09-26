---
id: SPEC-epic-1
companions: []
sources: [../../../INTENT.md]
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Epic 1: triage data and schema

## Why

Epic 1 establishes the data foundation and decision contract for the support-ticket triage system. It gives later work a validated triage-decision shape and a deterministic local SQLite database populated from the workshop's seed data.

## Capabilities

- **CAP-1**
  - **intent:** A system can accept only triage decisions containing an allowed category, priority, route, and one-sentence rationale.
  - **success:** Valid decisions use category `billing`, `bug`, `access`, `performance`, or `how-to`; priority `P1` through `P4`; route `billing-team`, `bug-team`, `access-team`, `performance-team`, or `how-to-team`; and a one-sentence rationale. Any other decision is rejected with a clear error.

- **CAP-2**
  - **intent:** A person can load the workshop's ticket and customer seed data into a local SQLite database with one command and repeat the operation safely.
  - **success:** `uv run python load_seed.py` creates `app.db` with `tickets` and `customers` tables whose columns match the CSV files, and running the command twice produces the same database state.

## Constraints

- Use Python 3.12 or newer managed with uv.
- Files under `seed/` are read-only.
- This epic makes no network calls and requires no API keys.
- Preserve the table and column names expected by `mcp/triage_server.py` when creating `app.db`.

## Non-goals

- The agent.
- MCP tools.
- Evaluation harnesses.
- Any user interface.

## Success signal

The decision schema rejects malformed triage output clearly, while `uv run python load_seed.py` repeatably loads both seed CSVs into an MCP-compatible `app.db`. The foundation works without network access or API keys.
