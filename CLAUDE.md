# Knowledgenet Examples

Companion project to [knowledgenet](../knowledgenet) (sibling repo). Demonstrates how to structure and author rules for a real Knowledgenet application. Each example lives in its own subdirectory; currently there is one: `autoins`.

Read `../knowledgenet/docs/concepts.md`, `docs/rule-service.md`, and `docs/rules-authoring.md` in the `knowledgenet` repo first — this repo assumes that vocabulary (Service, Fact, Ruleset, Repository, `@ruledef`, etc.).

## Environment

- Python 3.13+ (3.14 recommended).
- **Use the virtualenv at `../knowledgenet/.venv`** (`source ../knowledgenet/.venv/bin/activate`), not a separate venv per example — this repo does not maintain its own venv despite what individual example readmes may say.
- One-time env var: `export KNOWLEDGENET_EX_HOME=$HOME/git/knowledgenet-examples/` (adjust path as needed).
- To pick up local, unpublished changes to the `knowledgenet` library instead of the PyPI release:
  ```bash
  pip install --force-reinstall --no-deps $KNOWLEDGENET_HOME/dist/knowledgenet-*.whl
  ```
  (build the wheel in the `knowledgenet` repo first — see `docs/readme-development.md` there).

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
pip install -r requirements.txt   # only if deps changed

python src/rule_runner.py --rulesPath $KNOWLEDGENET_EX_HOME/autoins/rules \
    --factsPaths $KNOWLEDGENET_EX_HOME/autoins/data --log debug \
    --outputPath $KNOWLEDGENET_EX_HOME/autoins/target/results --cleanOutput
```

### Testing

```bash
cd $KNOWLEDGENET_EX_HOME/autoins
python -m pytest -rPX
```

When adding or changing a rule, add/update the corresponding EDI fixture under `test/data/` and expected output under `test/expected/`.

### Tracing

`rule_runner.py` supports OTEL tracing via env vars (`OTEL_TRACES_EXPORTER=console|otlp|otlp_http|file`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_FILE_EXPORT_PATH`, batch-processor tuning vars). See `autoins/readme.md` for the full list and for running a local Jaeger collector via Docker.

## Editing conventions

- Keep changes surgical; don't reformat unrelated files.
- New/changed rules need matching unit tests and, where behavior is configurable, a `rule-config.json` entry.
- Don't change license headers.
