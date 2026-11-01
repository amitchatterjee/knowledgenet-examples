## Python virtual environment setup

This example has its own `uv`-managed virtual environment, separate from `knowledgenet` and from
any other example in this repo. `knowledgenet` itself is not installed from PyPI — `pyproject.toml`
points `uv` at the sibling `knowledgenet` repo's source directory (`[tool.uv.sources]`), so `uv
sync` builds and installs it straight from there. There's nothing to configure to get the local
build; just run:

```bash
cd $KNOWLEDGENET_EX_HOME/autoins
uv venv --python 3.14
uv sync --group dev
```

To pick up new `knowledgenet` changes later, just re-run `uv sync` here (or `uv sync
--reinstall-package knowledgenet` to force a rebuild even if `knowledgenet`'s version string
hasn't changed).

### Running this example without the `knowledgenet` repo checked out

The sibling-repo source build above is a uv-only dev-time convenience
(`[tool.uv.sources]`) layered on top of a normal version-constrained dependency
(`knowledgenet>=1.0.1` in `pyproject.toml`). If you only have this repo (no sibling
`knowledgenet` checkout), tell uv to ignore that override and resolve `knowledgenet`
from PyPI instead:

```bash
cd $KNOWLEDGENET_EX_HOME/autoins
uv venv --python 3.14
uv sync --group dev --no-sources
```

This installs the published `knowledgenet` wheel and otherwise behaves identically.
Switch back to the local source build at any time with a plain `uv sync` (no flag).

## Execute Auto-insurance claim handling rules


### Execute the application:
```bash
uv run python $KNOWLEDGENET_EX_HOME/autoins/src/rule_runner.py --rulesPath $KNOWLEDGENET_EX_HOME/autoins/rules --factsPaths $KNOWLEDGENET_EX_HOME/autoins/data --log debug --outputPath $KNOWLEDGENET_EX_HOME/autoins/target/results --cleanOutput

```

### Run unit tests:
```bash
cd $KNOWLEDGENET_EX_HOME/autoins
uv run pytest -rPX

```

## Performance measurements and profiling

`data/tx_vectors.edi` and the `test/data/` fixtures are sized for correctness coverage (a handful
of hand-crafted claims, each exercising one edge case) — too small and too skewed toward
validation-failure paths to profile meaningfully. `test/perf/` holds a separate harness for that,
built to support the precompilation exploration in
`$KNOWLEDGENET_EX_HOME/knowledgenet/.plans/002-2026-10-10-precompilation-options-exploratory-plan.md`
(Phase 0: establishing how much of execution time is `knowledgenet` engine bookkeeping vs. time
spent inside rule-author `when`/`then` code, before evaluating any precompilation option against
that split).

- `test/perf/generate_data.py` — generates a synthetic, volume-sized `tx_vectors.edi` from the same
  claim patterns as `data/tx_vectors.edi` (valid claim, VIN mismatches, missing automobile,
  insufficient estimates), in a configurable mix weighted toward claims that flow through to
  `05_finalization`, so the profile reflects a realistic rule-path distribution rather than an even
  spread across edge cases. Deterministic given `--seed`.
- `test/perf/profile_engine.py` — loads the real `rule-config.json` (from `data/`) together with the
  generated transactions and profiles (or times) a single `Service.execute()` call over the whole
  batch, matching how `rule_runner.py` actually invokes the engine (one call across all requests,
  not one call per claim).

Generated data and profiling output land under `test/perf/target/` (gitignored, like
`target/results` above — regenerate anytime via `--seed`).

### Profile a run and see where time goes

```bash
cd $KNOWLEDGENET_EX_HOME/autoins
uv run python test/perf/profile_engine.py --count 5000
```

Prints a breakdown of `tottime` (time in each function itself, not its callees, so the buckets sum
to the profiled total without double-counting) into three buckets — `engine` (knowledgenet's own
internals), `rule_bodies` (the `matches=`/`then=` callables under `rules/`), and `other`
(everything else reached during execution: entity construction, pydantic validation, stdlib,
logging) — plus the hottest individual functions within each bucket, and writes a raw `.prof` file
you can open with `snakeviz` or `python -m pstats`.

### Time runs without profiler overhead

For comparing against other interpreters/compilers (PyPy, Nuitka, ...) later in the same
exploration, `cProfile`'s own per-call instrumentation cost would skew the comparison. Use:

```bash
uv run python test/perf/profile_engine.py --mode time --repeats 5
```

This rebuilds a fresh `Service` and fact set for each repeat (RETE execution mutates working
memory, so repeats must not observe each other's inserted/updated facts) and reports per-run and
average wall-clock time for `Service.execute()` alone, excluding rule scanning and fact loading.

### Use Opentelemetry for tracing:

### OpenTelemetry environment variables
The `autoins` example `rule_runner.py` supports configuring OpenTelemetry tracing via environment variables. The runner reads the following OTEL-related environment variables:

- `OTEL_SERVICE_NAME`
	- Description: Logical service name recorded with traces.
	- Possible values: any string (default used by the runner: `autoins`).
	- Example: `OTEL_SERVICE_NAME=autoins-payment`

- `OTEL_TRACES_EXPORTER`
	- Description: Selects which exporter the runner will use for traces.
	- Possible values (supported by the runner):
		- `console` — write spans to stdout using the ConsoleSpanExporter (default)
		- `otlp`, `otlp_grpc`, `otlp_proto_grpc` — use the OTLP gRPC exporter (requires `opentelemetry-exporter-otlp`)
		- `otlp_http`, `otlp_proto_http` — use the OTLP HTTP exporter
		- `file`, `file_json` — use the built-in file exporter that appends JSON-lines to a file
	- Example: `OTEL_TRACES_EXPORTER=otlp`

- `OTEL_EXPORTER_OTLP_ENDPOINT`
	- Description: Endpoint URL for the OTLP exporter (collector/ingest endpoint).
	- Possible values: full URL of the collector (for gRPC or HTTP), for example `http://localhost:4317` or `http://collector:4318`.
	- Example: `OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317`

- `OTEL_FILE_EXPORT_PATH`
	- Description: When using the `file` exporter, this controls the output file path where spans are written (JSON lines).
	- Possible values: file path string. Default: `trace.json` in the current working directory.
	- Example: `OTEL_FILE_EXPORT_PATH=/tmp/kn-trace.json`

#### Batch span processor tuning (runner-specific env vars)

The runner reads environment variables to tune the `BatchSpanProcessor` used when exporting spans. Defaults match the prior behavior.

- `OTEL_SPAN_PROCESSOR_MAX_QUEUE_SIZE`
	- Description: Maximum number of spans the processor will queue before dropping.
	- Example: `OTEL_SPAN_PROCESSOR_MAX_QUEUE_SIZE=4096`

- `OTEL_SPAN_PROCESSOR_SCHEDULE_DELAY_MILLIS`
	- Description: Time in milliseconds between export attempts (batch schedule delay).
	- Example: `OTEL_SPAN_PROCESSOR_SCHEDULE_DELAY_MILLIS=10000`

- `OTEL_SPAN_PROCESSOR_MAX_EXPORT_BATCH_SIZE`
	- Description: Maximum number of spans to include in a single export batch.
	- Example: `OTEL_SPAN_PROCESSOR_MAX_EXPORT_BATCH_SIZE=250`

Notes:
- The example runner performs a simple, env-driven exporter selection. For full OpenTelemetry configuration and automatic exporter setup, you can install and use the OpenTelemetry distro (`opentelemetry-distro`) or the auto-instrumentation tool and control behavior solely via standard OTEL_* environment variables.
- If you choose OTLP exporters, make sure the corresponding exporter package is installed in your Python environment (for example, `opentelemetry-exporter-otlp`).

### Run a OTEL metrics collector and viewer
A metrics/traces collector receives telemetry data from instrumented applications and forwards or stores it for analysis and viewing. In a typical setup the OpenTelemetry Collector accepts OTLP (gRPC or HTTP) on well-known ports (commonly `4317` for gRPC and `4318` for HTTP), can perform batching and processing, and then exports spans and metrics to backends such as Jaeger, Zipkin, an OTLP-compatible collector, or a local viewer.

The `Jaegar UI` used in the example runs a collector plus a browser-based UI so you can view traces locally without a full observability stack. The container exposes:

- port `4317` (OTLP/gRPC) and `4318` (OTLP/HTTP) — endpoints that instrumented applications can send data to;
- port `16686` — the viewer UI where you can inspect traces.

Run the Jaegar UI locally (container will listen on the ports above):

```bash

#docker run --rm -d  --name jaeger   -p 16686:16686   -p 4317:4317   -p 4318:4318 -v $KNOWLEDGENET_EX_HOME/autoins/config/jaeger/config.json:/etc/jaeger/config.json  cr.jaegertracing.io/jaegertracing/jaeger:latest --query.ui-config=/etc/jaeger/config.json

docker run --rm -d  --name jaeger   -p 16686:16686   -p 4317:4317   -p 4318:4318  cr.jaegertracing.io/jaegertracing/jaeger:latest

```

Point the example runner at the local collector and enable the OTLP exporter:

```bash
export OTEL_ENABLED=true
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_TRACES_EXPORTER=otlp
uv run python src/rule_runner.py --rulesPath $KNOWLEDGENET_EX_HOME/autoins/rules \
	--factsPaths $KNOWLEDGENET_EX_HOME/autoins/data --log info \
	--outputPath $KNOWLEDGENET_EX_HOME/autoins/target/results --cleanOutput --traceLevel 5 --traceDetails 10
```

View the traces by pointing a web browser to [http://localhost:16686](http://localhost:16686).

Notes:
- Use `OTEL_TRACES_EXPORTER=file` and `OTEL_FILE_EXPORT_PATH` if you prefer writing spans to a local JSON-lines file instead of sending them to a collector.
- Ensure required OTEL Python exporter packages are installed when using OTLP exporters (for example `opentelemetry-exporter-otlp`).
