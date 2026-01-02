## Auto-insurance claim handling rules

# Install required dependencies
cd $KNOWLEDGENET_EX_HOME/autoins
pip install -r requirements.txt

```

### Execute the application:
```bash
python $KNOWLEDGENET_EX_HOME/autoins/src/rule_runner.py --rulesPath $KNOWLEDGENET_EX_HOME/autoins/rules --factsPaths $KNOWLEDGENET_EX_HOME/autoins/data --log debug --outputPath $KNOWLEDGENET_EX_HOME/autoins/target/results --cleanOutput

```

### Run unit tests:
```bash
cd $KNOWLEDGENET_EX_HOME/autoins
python -m pytest -rPX

```

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

invalid parent span IDs=851628afc07999a9; skipping clock skew adjustment

```

Point the example runner at the local collector and enable the OTLP exporter:

```bash
export OTEL_ENABLED=true
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_TRACES_EXPORTER=otlp
python src/rule_runner.py --rulesPath $KNOWLEDGENET_EX_HOME/autoins/rules \
	--factsPaths $KNOWLEDGENET_EX_HOME/autoins/data --log info \
	--outputPath $KNOWLEDGENET_EX_HOME/autoins/target/results --cleanOutput --traceLevel 10
```

View the traces by pointing a web browser to [http://localhost:8000](http://localhost:8000).

Notes:
- Use `OTEL_TRACES_EXPORTER=file` and `OTEL_FILE_EXPORT_PATH` if you prefer writing spans to a local JSON-lines file instead of sending them to a collector.
- Ensure required OTEL Python exporter packages are installed when using OTLP exporters (for example `opentelemetry-exporter-otlp`).
