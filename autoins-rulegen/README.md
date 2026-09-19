# autoins-rulegen

Per-application content for [`knowledgexpert`](../../knowledgexpert) targeting the `autoins` example in
this repo — the knowledge base, prompts, and (optionally) MCP tool config and live-data infra that
`knowledgexpert`'s DeepAgents graph reads at runtime via the `RULEGEN_ROOT` env var. See
`knowledgexpert`'s
[`.plans/001-2026-09-05-deepagents-modernization-plan-INPROG.md`](../../knowledgexpert/.plans/001-2026-09-05-deepagents-modernization-plan-INPROG.md)
("Repository layout" section) for why this lives here, physically alongside the application it
describes, rather than inside `knowledgexpert` itself.

Not a Python package — this directory holds curated data (markdown, JSON, docker-compose), not code.

## Layout

```
knowledge/
  specification-guidelines/    spec template + population instructions + validator sufficiency
                                criteria -- hand-authored (the only remaining hand-authored
                                directory; see tools/README.md for why the other six are generated)
target/knowledge/              generated, gitignored (**/target/ already in the repo .gitignore) --
                                a complete, ready-to-ship knowledge base assembled by tools/:
                                knowledgenet-foundation/, application-domain/,
                                application-architecture/, exemplars/, testing-guidelines/,
                                configuration-guidelines/ (generated from knowledgenet/autoins) plus
                                specification-guidelines/ (copied in from knowledge/ above). Not
                                committed, safe to delete/regenerate. Consumed by knowledgexpert
                                either by pushing to S3 (knowledge prefix) or by zipping with
                                knowledge/ as the zip's top-level dir, so a user unzips it and
                                points RULEGEN_ROOT at the parent -- no code change needed.
tools/                         bash scripts that assemble target/knowledge/ from source and publish
                                it (S3 push; zip-for-filesystem-distribution not written yet) --
                                assemble-all.sh orchestrates all seven per-directory scripts in one
                                command; see tools/README.md
prompts/                       supervisor + subagent prompts tuned for autoins (not yet authored --
                                blocked on knowledgexpert's phase 2 supervisor/validator design)
mcp/                           optional -- omitted entirely once autoins defines no MCP services.
                                Currently one service, OpenSearch (MSRP vehicle pricing lookup) --
                                see mcp/README.md.
infra/                         optional -- docker-compose/admin fixtures for whatever live-data
                                service the MCP config above points at -- see infra/README.md for
                                full build/up/down/setup instructions.
```

## Status

Knowledge-base content work is essentially done: all seven directories assemble via
`tools/assemble-all.sh` (six generated, verified against real `knowledgenet`/`autoins` source;
`specification-guidelines/spec-template.md` hand-authored, drafted and approved). See
`tools/README.md` for exact source mappings and the whole-file-copy design principle.

`mcp/` and `infra/` are populated -- the OpenSearch MCP config/infra migrated here 2026-09-18 from
`knowledgexpert/infrastructure/` (which now holds only the generic, tool-level `conf/log-config.yaml`),
with full setup instructions in their own READMEs (dropped the migrated `compose.sh` wrapper as dead
code -- see `infra/README.md`). Two things deliberately not migrated/resolved: `data/opensearch/msrp/`
(the bulk pricing data itself, still under `knowledgexpert/`) and whether `knowledgexpert` should
orchestrate starting the OpenSearch container itself, versus a manual step.

Remaining phase-1 work: `prompts/` (blocked on phase 2) and the golden fixture set that phases 2-5
reuse for CLI verification.
