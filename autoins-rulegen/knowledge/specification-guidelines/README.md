# specification-guidelines

`autoins`'s **specification template** the supervisor interprets requests against, instructions on how
to populate it, and the **sufficiency criteria the rule-spec-validator subagent checks a submitted spec
against** — what counts as clear enough to proceed (possibly with stated assumptions) versus
insufficient (must be rejected with specific gaps). Written as free-form guidance, consistent with
every other directory here, not a rigid machine-checkable schema.

This directory gates everything downstream (phases 2-5) — it was the first content authored.

See `spec-template.md` for the actual template: three sections (Requirements, Test Cases,
Configuration), sufficiency criteria under each, and a worked example grounded in the real
`late_filing` rule under `03_contract`.

Status: drafted and reviewed 2026-09-12, grounded in the real `02_validation`/`03_contract`/
`04_fraud` rules and `rule-config.json`. First hand-authored content in this repo to be approved.
