### More information to come:

This is an example project for developing a Knowledgenet rules network. This project is in a very early phase.  

**Before you start:**  
The knowledgenet package has not been published to PyPI yet. So, you will have to manually build the package and install it using pip. Please see the instructions in the [knowledgenet project's development documentation](https://github.com/amitchatterjee/knowledgenet/blob/develop/doc/readme-development.md){:target="_blank"}. Once you are done with that, follow the instructions below from a shell.

```bash
# Change as needed
export KNOWLEDGENET_EX_HOME=$HOME/git/knowledgenet-examples/

# One-time setup
cd $KNOWLEDGENET_EX_HOME
pip install -r requirements.txt

# Set the PYTHONPATH environment variable
export PYTHONPATH=$KNOWLEDGENET_EX_HOME/autoins/src

# Change to the root of the auto insurance example directory 
cd $KNOWLEDGENET_EX_HOME/autoins

# Run the rule_runner.py script with specified arguments
python src/rule_runner.py --rulesPath $KNOWLEDGENET_EX_HOME/autoins/rules --factsPaths $KNOWLEDGENET_EX_HOME/autoins/data --log debug --outputPath $KNOWLEDGENET_EX_HOME/target/results --cleanOutput

# Run the rule_runner.py script with legacy tracing
python src/rule_runner.py --rulesPath $KNOWLEDGENET_EX_HOME/autoins/rules --factsPaths $KNOWLEDGENET_EX_HOME/autoins/data --log info --outputPath $KNOWLEDGENET_EX_HOME/target/results --cleanOutput --traceMethod stream --traceFile $KNOWLEDGENET_EX_HOME/target/trace.json

# Run the rule_runner.py script with otel tracing
python src/rule_runner.py --rulesPath $KNOWLEDGENET_EX_HOME/autoins/rules --factsPaths $KNOWLEDGENET_EX_HOME/autoins/data --log info --outputPath $KNOWLEDGENET_EX_HOME/target/results --cleanOutput --traceMethod otel

# Run pytest
python -m pytest -rPX
```

**OpenTelemetry environment variables (used by the example runner)**

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

