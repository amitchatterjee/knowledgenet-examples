# mcp/ -- MCP tool configuration for autoins

MCP tool config for `autoins`'s live application data. Currently one service: OpenSearch, exposing
MSRP vehicle-pricing lookup as MCP tools. Migrated here from `knowledgexpert/infrastructure/conf/mcp/`
2026-09-18 -- see `knowledgexpert`'s
[`.plans/001-2026-09-05-deepagents-modernization-plan-INPROG.md`](../../../knowledgexpert/.plans/001-2026-09-05-deepagents-modernization-plan-INPROG.md)
("Repository layout").

## opensearch/

- **`mcp-tools.json`** -- registers two tools against the running OpenSearch instance:
  `ListIndexTool` (index metadata) and `SearchIndexTool` (supports both standard DSL and k-NN
  vector queries). The only index currently populated is `msrp` (MSRP vehicle pricing, queried via
  standard DSL, not k-NN) -- `SearchIndexTool`'s vector-search support isn't exercised by anything
  yet, consistent with `../infra/README.md`'s `vector_reader`/`vector_writer` roles being kept for
  anticipated future vector-DB use rather than a current need.
- **`agent.ndjson`** -- two OpenSearch "flow agents" wrapping those tools (`Agent_For_ListIndex_tool`,
  `Agent_For_Search_Index_Tool`).

Neither file is runnable on its own -- they're registered into a live OpenSearch instance via the
curl commands in `../infra/README.md` (steps 3-4), which also covers building/starting that instance
and setting up the security roles these tools' callers (`alice`/`bob`) authenticate as.

`mcp/` not existing at all under `RULEGEN_ROOT` is how "this application defines no MCP services" is
expressed to `knowledgexpert` -- see the plan doc's "Configuration approach" section.
