# prompts

Supervisor + subagent prompts tuned for `autoins`, loaded by `knowledgexpert` via
`RULEGEN_ROOT/prompts/<filename>.md` (see `knowledgexpert`'s `_load_prompt_from_file()`). The legacy
`infrastructure/conf/wolfpack/{analyst,developer,tester}/agentic_prompt.txt` files (now retired) assumed
a RAG-injected-context paradigm and need full rewriting for the filesystem-browsing paradigm, plus new
prompts for the rule-spec-validator and config-generator, which don't have legacy equivalents.

All five prompts are drafted. None have been exercised against a real graph yet — phase 2 (supervisor
+ rule-spec-validator) hasn't started, and phases 3-5 (the three generator subagents) come after
that. Testing happens once each phase's actual graph code exists; until then these are written
against the plan's design, not a running implementation, same as `specification-guidelines/` was.

- **`rule-spec-validator.md`** — grounded in `specification-guidelines/spec-template.md`'s three
  sections/sufficiency criteria and the plan's "Rule spec validation" output contract
  (`sufficient`/`assumptions`/`gaps`). Reviewed and looks right.
- **`supervisor.md`** — grounded in the plan's "Graph" and "Conversational memory" sections:
  classifies every message into fresh-request / clarification-reply / post-generation-feedback /
  out-of-scope, routes accordingly, forwards the validator's `assumptions`, enforces the
  code-generator-implies-config-generator convention for new rules.
- **`code-generator.md`** — grounded in `rules-authoring.md`, `application-architecture/`'s
  `entities.py`/`util.py`, and the real exemplar rule shape (`@ruledef`, the
  `execute()`/`create_action()` pattern). States the real `autoins.entities`/`autoins.util` import
  paths explicitly, since the knowledge base's flattened file layout doesn't reveal them.
- **`config-generator.md`** — grounded in `configuration-guidelines/configuration.md`; merge-only
  `rule-config.json` edits, standard fields, reason-code collision checking, group overrides only
  when the spec names one.
- **`test-generator.md`** — grounded in `testing-guidelines/testing.md`, including its "tests always
  run the full pipeline, including finalization" gotcha: a claim that doesn't trigger the rule under
  test still needs a `pay`/`PAYCL` row in `expected.csv`, not an absent one. Explicit about deriving
  expected results by reasoning, never by running anything, and stating that as a caveat.

All five include generate-fresh-vs-revise-existing guidance (per the plan's phase-6 note) and the
assumption-stating discipline (per "Rule spec validation") from the start, rather than being written
narrowly to only what their own first phase exercises.

Status: all five drafted, awaiting review.
