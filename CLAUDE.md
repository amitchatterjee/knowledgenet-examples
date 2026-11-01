# Knowledgenet Examples

Companion project to [knowledgenet](../knowledgenet) (sibling repo). Demonstrates how to structure and author rules for a real Knowledgenet application. Each example lives in its own subdirectory; currently there is one: `autoins`.

Read `../knowledgenet/docs/concepts.md`, `docs/rule-service.md`, and `docs/rules-authoring.md` in the `knowledgenet` repo first — this repo assumes that vocabulary (Service, Fact, Ruleset, Repository, `@ruledef`, etc.).

## Environment

- Python 3.13+ (3.14 recommended).
- **Each example subdirectory owns its own `uv`-managed `.venv`, `pyproject.toml`, and `uv.lock`** —
  not shared with `knowledgenet` or with other examples. See the example's own README for its
  one-time setup (e.g. `autoins/README.md`).
- One-time env var: `export KNOWLEDGENET_EX_HOME=$HOME/git/knowledgenet-examples/` (adjust path as needed).
- Examples depend on `knowledgenet` via a `[tool.uv.sources]` path entry pointing at the sibling
  `knowledgenet` repo (e.g. `{ path = "../../knowledgenet" }` from an example subdirectory), **plus**
  a normal version-floor requirement in `project.dependencies` (e.g. `"knowledgenet>=1.0.1"`) for
  when that source isn't used — see below. By default (sibling repo checked out, the common dev
  case), `uv sync` builds `knowledgenet` straight from that source tree, so there is no separate
  "install the local wheel" step — just re-run `uv sync` (or `uv sync --reinstall-package
  knowledgenet` to force a rebuild) after changing `knowledgenet` source.
- **Running an example standalone, without cloning `knowledgenet`:** `tool.uv.sources` is a uv-only
  dev-time override and isn't respected by non-uv consumers or by uv itself when told to ignore it.
  Pass `--no-sources` (or the narrower `--no-sources-package knowledgenet`) to `uv sync`/`uv lock` to
  resolve `knowledgenet` from PyPI per the version floor instead of the local path — e.g. `uv sync
  --no-sources` in `autoins/`. This installs the published `knowledgenet` wheel; no sibling checkout,
  no extra files, same `pyproject.toml`. Re-run a plain `uv sync` (no flag) to switch back to the
  local path source.

## `autoins` example

Auto-insurance claim adjudication: rules decide whether a claim should be paid or denied. See `autoins/docs/description.md` for the domain model (`Request` fact aggregating claim/policy/group/driver/automobile/incidence-report/estimates) and `autoins/docs/entity-relationships.md` / `autoins/docs/testing.md` for entity and test-framework details.

Layout:
- `autoins/src/` — platform code: EDI/CSV parsers, fact entities, the `rule_runner.py` CLI entrypoint.
- `autoins/rules/` — the rulesets, one directory per phase, ordered by numeric prefix:
  - `02_validation` — required-field/entity checks (missing policy, driver, automobile, incidence report, insufficient estimates).
  - `03_contract` — eligibility (inactive policy, late filing, VIN mismatch).
  - `04_fraud` — fraud detection (VIN mismatches across claim/incidence-report/estimates).
  - `05_finalization` — payment computation (collision, liability).
- `autoins/data/` — `rule-config.json` (enables/disables rules, sets actions/reasons/explanations/ranks per rule — most rules should reference a config entry) and sample EDI test-vector data.
- `autoins/test/` — unit tests (`test/unit/`), test fixtures (`test/data/`), expected outputs (`test/expected/`).
- `autoins/config/jaeger/` — local Jaeger config for OTEL trace viewing.

Rules are authored declaratively with `@ruledef` and, by convention here, always operate on the `Request` fact and reference a `rule-config.json` entry so behavior can be tuned without code changes.

### Running

```bash
cd $KNOWLEDGENET_EX_HOME/autoins
uv sync --group dev   # only if deps changed

uv run python src/rule_runner.py --rulesPath $KNOWLEDGENET_EX_HOME/autoins/rules \
    --factsPaths $KNOWLEDGENET_EX_HOME/autoins/data --log debug \
    --outputPath $KNOWLEDGENET_EX_HOME/autoins/target/results --cleanOutput
```

### Testing

```bash
cd $KNOWLEDGENET_EX_HOME/autoins
uv run pytest -rPX
```

When adding or changing a rule, add/update the corresponding EDI fixture under `test/data/` and expected output under `test/expected/`.

### Tracing

`rule_runner.py` supports OTEL tracing via env vars (`OTEL_TRACES_EXPORTER=console|otlp|otlp_http|file`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_FILE_EXPORT_PATH`, batch-processor tuning vars). See `autoins/README.md` for the full list and for running a local Jaeger collector via Docker.

## Editing conventions

- Keep changes surgical; don't reformat unrelated files.
- New/changed rules need matching unit tests and, where behavior is configurable, a `rule-config.json` entry.
- Don't change license headers.
