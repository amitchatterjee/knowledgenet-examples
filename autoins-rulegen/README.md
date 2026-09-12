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
  specification-guidelines/    spec template + population instructions + validator sufficiency criteria
  configuration-guidelines/    rule-config.json conventions
  testing-guidelines/          test artifact formats and workflow
                                (hand-authored here; see tools/README.md for why these three
                                aren't generated)
target/knowledge/              generated, gitignored (**/target/ already in the repo .gitignore) --
                                a complete, ready-to-ship knowledge base assembled by tools/,
                                built as part of knowledgenet/autoins's release process:
                                knowledgenet-foundation/, application-domain/,
                                application-architecture/, exemplars/ pulled from those sibling
                                repos, plus specification-guidelines/, configuration-guidelines/,
                                testing-guidelines/ copied in from knowledge/ above. Not committed,
                                safe to delete/regenerate. Consumed by knowledgexpert either by
                                pushing to S3 (knowledge prefix) or by zipping with knowledge/ as
                                the zip's top-level dir, so a user unzips it and points
                                RULEGEN_ROOT at the parent -- no code change needed.
tools/                         bash/python scripts that assemble target/knowledge/ from source and
                                publish it (S3 push, or zip for filesystem/CLI distribution) --
                                see tools/README.md
prompts/                       supervisor + subagent prompts tuned for autoins
mcp/                           optional -- omitted entirely once autoins defines no MCP services
                                (not yet populated: OpenSearch MCP config still lives under
                                knowledgexpert/infrastructure/, pending migration)
infra/                         optional -- docker-compose/admin fixtures for whatever live-data
                                service the MCP config above points at (e.g. OpenSearch)
                                (not yet populated, same pending migration as mcp/ above)
```

## Status

`knowledge/` holds only the three hand-authored guideline directories now; each still has a
placeholder `README.md`, content not yet written. The other four knowledge-base directories
(`knowledgenet-foundation/`, `application-domain/`, `application-architecture/`, `exemplars/`)
moved out of `knowledge/` -- they'll be assembled into `target/knowledge/` by scripts under
`tools/` instead of hand-curated, since real source material for them already exists in the
sibling `knowledgenet` and `autoins` projects (see `tools/README.md` for the specific source
paths and the full `target/knowledge/` design). None of that assembly logic is written yet.

Content authoring happens interactively, starting with `specification-guidelines/` since it gates
everything downstream. `mcp/` and `infra/` don't exist yet either — the existing OpenSearch MCP
config/infra still lives under `knowledgexpert/infrastructure/` (`conf/mcp/opensearch/`,
`docker/opensearch-mcp/`, `admin/opensearch/`), not yet migrated here.
