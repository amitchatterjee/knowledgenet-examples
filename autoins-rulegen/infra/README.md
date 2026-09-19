# infra/ -- OpenSearch setup for autoins

Docker infra and admin fixtures for the OpenSearch instance that backs `autoins`'s live-data MCP
tools (see `../mcp/README.md` for what those tools are). Migrated here from
`knowledgexpert/infrastructure/` 2026-09-18 -- see `knowledgexpert`'s
[`.plans/001-2026-09-05-deepagents-modernization-plan-INPROG.md`](../../../knowledgexpert/.plans/001-2026-09-05-deepagents-modernization-plan-INPROG.md)
("Repository layout") for why this lives here, alongside the application it serves.

This compose file is intended for a fully trusted developer environment. For production, the same
services need to be ported to a secure deployment model with proper secret handling, access
controls, and automation -- the credentials below are dev-only fixtures, already in git history in
plaintext (`roles.ndjson`/`users.ndjson`/`rolesmapping.ndjson`), not something to reuse anywhere real.

## One-time setup

Every command below is written to run from any directory -- nothing requires `cd`ing into this
folder first. Set these once per shell session:

```bash
export KNOWLEDGENET_EX_HOME=/path/to/knowledgenet-examples   # this repo's root
export KNOWLEDGEXPERT_HOME=/path/to/knowledgexpert           # sibling repo -- MSRP bulk data lives there
```

`jq` and `curl` are required for the OpenSearch admin API calls below.

## 1. Build the OpenSearch image

```bash
docker compose -p autoins-opensearch -f "$KNOWLEDGENET_EX_HOME/autoins-rulegen/infra/docker/docker-compose.yml" build opensearch
```

Builds from `opensearch-mcp/Dockerfile` -- the stock `opensearchproject/opensearch` image plus the
`transport-reactor-netty4` plugin (required for the MCP server/connector features enabled in
`docker-compose.yml`'s `environment:` block). Pass `OPENSEARCH_VERSION=<version>` to pin a version
instead of `latest`.

## 2. Bring the infrastructure up / down

```bash
docker compose -p autoins-opensearch -f "$KNOWLEDGENET_EX_HOME/autoins-rulegen/infra/docker/docker-compose.yml" up -d    # start
docker compose -p autoins-opensearch -f "$KNOWLEDGENET_EX_HOME/autoins-rulegen/infra/docker/docker-compose.yml" down     # stop (add -v to also drop the opensearch-data volume)
```

**Always pass `-p autoins-opensearch`** (an explicit Compose project name). Without it, Compose
derives the project name from the compose file's *containing directory's basename* --
`docker-compose.yml` here lives under `infra/docker/`, so the default name is just `docker`. Any
other project on the machine that also happens to keep its compose file under a directory literally
named `docker/` (e.g. `carqna-agent/infrastructure/docker/`) collides on that same default name, and
`docker compose ps`/`down` then operate across *both* projects' containers together -- confirmed via
`docker inspect <container> --format '{{index .Config.Labels "com.docker.compose.project"}}'`, which
showed our `opensearch` and `carqna-agent`'s `postgres` sharing project `docker` despite different
`working_dir` labels. An explicit `-p` makes this impossible regardless of directory-name coincidences
elsewhere. Worth preserving verbatim, not rediscovering the hard way.

No wrapper script needed -- an earlier `compose.sh` (translating a `KNOWLEDGEXPERT_ENV` var into
`COMPOSE_PROFILES` to conditionally start dev/build-only services) was dropped during the migration:
the services it gated (`chromadb`, `knowledgexpert-base`) were already retired in phase 0, leaving
only the profile-less `opensearch` service, which always starts regardless of `COMPOSE_PROFILES`.
The plain `docker compose -p ... -f ... up -d` above is equivalent to what `compose.sh up -d` used to do.

REST API is exposed on `https://localhost:9200` (self-signed cert -- `curl` calls below use `-k`/
`--insecure`). Admin credentials: `admin` / `openSearch$2025` (dev fixture, see disclaimer above).

## 3. Configure OpenSearch security (roles, users, role mappings)

Loads the ndjson fixtures under `admin/opensearch/` to create users and bind them to index-scoped
roles.

```bash
# Create or update roles
while IFS= read -r payload || [ -n "$payload" ]; do
  role_name=$(printf '%s' "$payload" | jq -r '.name')
  role_body=$(printf '%s' "$payload" | jq 'del(.name)')
  curl -k -u 'admin:openSearch$2025' \
    -H 'Content-Type: application/json' \
    -X PUT "https://localhost:9200/_plugins/_security/api/roles/$role_name" \
    --data-binary "$role_body"
done < "$KNOWLEDGENET_EX_HOME/autoins-rulegen/infra/admin/opensearch/roles.ndjson"

# Create or update internal users
while IFS= read -r payload || [ -n "$payload" ]; do
  user_name=$(printf '%s' "$payload" | jq -r '.name')
  user_body=$(printf '%s' "$payload" | jq 'del(.name)')
  curl -k -u 'admin:openSearch$2025' \
    -H 'Content-Type: application/json' \
    -X PUT "https://localhost:9200/_plugins/_security/api/internalusers/$user_name" \
    --data-binary "$user_body"
done < "$KNOWLEDGENET_EX_HOME/autoins-rulegen/infra/admin/opensearch/users.ndjson"

# Map users to roles
while IFS= read -r payload || [ -n "$payload" ]; do
  role_name=$(printf '%s' "$payload" | jq -r '.name')
  mapping_body=$(printf '%s' "$payload" | jq 'del(.name)')
  curl -k -u 'admin:openSearch$2025' \
    -H 'Content-Type: application/json' \
    -X PUT "https://localhost:9200/_plugins/_security/api/rolesmapping/$role_name" \
    --data-binary "$mapping_body"
done < "$KNOWLEDGENET_EX_HOME/autoins-rulegen/infra/admin/opensearch/rolesmapping.ndjson"
```

The fixtures define two users and four roles (see `admin/opensearch/roles.ndjson`):
- `alice` -- `msrp_reader` (read `msrp`/`msrp-*`) + `vector_reader` (read the vector-collection
  indices, kept for anticipated future vector-DB capability -- not currently populated by anything).
- `bob` -- `msrp_writer` (write `msrp`/`msrp-*`) + `vector_writer` (same caveat as above).

**No step here builds `all_collection`/`app_platform_collection`/`rules_collection`/
`app_docs_collection`/`framework_docs_collection`, by design.** The original (pre-migration)
instructions built those five via `vector_store.py` -- deleted in phase 0's legacy retirement, and
not resurrected here even in principle: they *are* the old vector-store knowledge base
(`app_platform_collection` -> `entities.py`/`util.py`, `rules_collection` -> `autoins/rules`,
`app_docs_collection` -> `autoins/docs`, `framework_docs_collection` -> `knowledgenet/docs`,
`all_collection` -> everything combined), which `autoins-rulegen/target/knowledge/`'s generated
directories now serve instead, filesystem-backed. Rebuilding them would duplicate that content
through the exact mechanism this whole modernization retires. `vector_reader`/`vector_writer`
staying in the role fixtures is a placeholder for some future, not-yet-designed vector-DB
capability -- not a reason to bring this pipeline back.

## 4. Register MCP agents and tools

Config source files live in `../mcp/opensearch/` (see `../mcp/README.md`).

```bash
# sanity checks
curl -X GET 'https://localhost:9200/_cat/plugins?v' --insecure -u 'admin:openSearch$2025'
curl -X GET "https://localhost:9200/_cluster/settings" -u 'admin:openSearch$2025' --insecure

# create agents
curl --insecure \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @"$KNOWLEDGENET_EX_HOME/autoins-rulegen/mcp/opensearch/agent.ndjson" \
  "https://localhost:9200/_plugins/_ml/agents/_register" \
  -u 'admin:openSearch$2025'

# register tools
curl -X POST 'https://localhost:9200/_plugins/_ml/mcp/tools/_register' \
  --insecure \
  -u 'admin:openSearch$2025' \
  -H 'Content-Type: application/json' \
  --data-binary @"$KNOWLEDGENET_EX_HOME/autoins-rulegen/mcp/opensearch/mcp-tools.json"
```

Whichever MCP client consumes these tools (a `knowledgexpert` subagent, VS Code's MCP client, etc.)
authenticates with `alice`'s credentials for read-only use, `bob`'s for write. (Verifying `alice` can
actually read data belongs in step 5, below, since `msrp` has no data until that step loads it.)

## 5. Load MSRP index data

The bulk-load data itself (`toyota-2025-msrp-bulk.ndjson`, `msrp-mappings.json`) has **not** been
migrated out of `knowledgexpert` -- it stays under `$KNOWLEDGEXPERT_HOME/data/opensearch/msrp/` for
now (open question, not yet decided, whether it should move here too; see the plan doc's phase-1
notes).

```bash
# Clear existing msrp index data. Only run this when you want to clear the data -- the commands
# below this one will upsert content if the index already exists.
curl -k -u 'admin:openSearch$2025' -X DELETE "https://localhost:9200/msrp?ignore_unavailable=true"

# Load msrp index
curl -sS -H "Content-Type: application/x-ndjson" \
  -u 'bob:X5@mD8!zH3#uC1%w' \
  --data-binary @"$KNOWLEDGEXPERT_HOME/data/opensearch/msrp/toyota-2025-msrp-bulk.ndjson" \
  --insecure \
  "https://localhost:9200/_bulk"

curl -k -X PUT "https://localhost:9200/msrp/_mapping" \
  -H "Content-Type: application/json" \
  -u 'admin:openSearch$2025' \
  --data-binary @"$KNOWLEDGEXPERT_HOME/data/opensearch/msrp/msrp-mappings.json"

# verify
curl -sSk -u 'alice:N7!qL2#vP9@tR4$k' "https://localhost:9200/msrp/_search?size=2"
```

**Gotcha, worth preserving verbatim: `_bulk` requires `indices:data/write/bulk` granted as a
*cluster* permission, not just covered by an index-level `crud`/`write` action group.** Despite
`write`'s `allowed_actions` textually including `indices:data/write*`, OpenSearch's security plugin
checks the top-level bulk action at the cluster-permission layer before per-item index-level checks
-- an index-scoped `crud` role alone gets a 403 `security_exception` on `_bulk`. `msrp_writer` in
`roles.ndjson` already includes `"cluster_permissions":["indices:data/write/bulk"]` for this reason.
`vector_writer` has the same `crud`-only shape and likely needs the same fix whenever the vector-DB
work actually lands and starts exercising it.

Use the admin account for the mapping update (a security-sensitive operation); use `bob` only for
the bulk ingest step.

## Periodic maintenance

Re-run step 5 whenever `msrp-mappings.json` or the bulk-load ndjson changes. Re-run steps 3-4 after
running step 2's `down -v` (security config and registered agents/tools live inside the container's
data volume, so a fresh volume needs them reloaded).
