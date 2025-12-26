import argparse
import os
import io
import sys
import time
import json
from knowledgenet import scanner
from knowledgenet.service import Service
from knowledgenet.ftypes import EventFact
from autoins.entities import Action
import logging

from autoins.fact_io import load_facts, write_actions
from autoins.util import subdirs
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPHTTPExporter

from file_exporter import FileSpanExporter

def argsparser():
    parser = argparse.ArgumentParser(description="Auto Insurance Payment Rules Service")
    parser.add_argument('--rulesPath', required=True, help='Full path of the location from where rules are loaded')
    parser.add_argument('--factsPaths', required=True, nargs='+', help='Full paths from where the facts are loaded')
    parser.add_argument('--outputPath', required=True, help='Full path name of the directory where the actions are written to')
    parser.add_argument('--cleanOutput', action='store_true', help='Clean the output directory before writing the actions')
    parser.add_argument('--traceMethod', choices=['otel', 'stream'], default=None,
                        help='Trace method to use. Valid values: otel, stream. Defaults to None')
    parser.add_argument('--traceFile', help='If traceMethod is "stream", location where the trace is stored. if "log" is specified, the trace is output as an INFO log')
    parser.add_argument('--log', help='Log severity level. The valid values are DEBUG, INFO, WARNING, ERROR, CRITICAL', default='INFO')
    return parser.parse_args()

def init_knowledgebase(rules_root, facts_path):
    service = init_rules(rules_root)

    facts = load_facts(facts_path)
    logging.info(f"Loaded {len(facts)} facts")
    return service,facts

def init_rules(rules_root):
    rules_paths = []
    repo = subdirs(rules_root)
    for r in repo:
        rules_paths.append(r)
    scanner.load_rules_from_filepaths(rules_paths)

    rules_basename = os.path.basename(rules_root)
    repository = scanner.lookup(rules_basename)
    service = Service(repository)
    logging.info(f"Loaded {len(repository.rulesets)} rulesets")
    return service

def init_logging(log):
    handlers = [logging.StreamHandler(sys.stdout)]
    logging.basicConfig(level=getattr(logging, log.upper(), None), handlers=handlers)

def execute_service(service, facts, trace_method, trace_file):
    try:
        trace_stream = None
        if trace_method and trace_method == 'stream':
            trace_stream = sys.stdout if not trace_file else (io.StringIO() if trace_file == 'log' else open(trace_file, 'w'))
        start_time = time.time()
        result_facts = service.execute(facts, trc_method=trace_method, trc_stream=trace_stream)
        if 'log' == trace_file:
            logging.info("Trace from the rules execution: \n%s", trace_stream.getvalue())
    finally:
        end_time = time.time()
        execution_time_ms = (end_time - start_time) * 1000
        logging.info("Execution time: %s ms", execution_time_ms)
    return result_facts

def init_otel():
    provider = TracerProvider(resource=Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "autoins")}))
    exporter_name = os.getenv('OTEL_TRACES_EXPORTER', 'console').lower()
    if exporter_name in ('otlp', 'otlp_grpc', 'otlp_proto_grpc'):
        endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
        exporter = OTLPSpanExporter(endpoint=endpoint) if endpoint else OTLPSpanExporter()
    elif exporter_name in ('otlp_http', 'otlp_proto_http'):
        endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
        exporter = OTLPHTTPExporter(endpoint=endpoint) if endpoint else OTLPHTTPExporter()
    elif exporter_name in ('file', 'file_json'):
        file_path = os.getenv('OTEL_FILE_EXPORT_PATH', 'trace.json')
        exporter = FileSpanExporter(file_path)
    else:
            # default to console exporter
        exporter = ConsoleSpanExporter()

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    logging.info("OpenTelemetry initialized using exporter '%s'", exporter_name)

if __name__ == "__main__":
    args = argsparser()
    init_logging(args.log)

    service, facts = init_knowledgebase(args.rulesPath, args.factsPaths)
    facts.add(EventFact(group='onAction', on_types=Action))

    if args.traceMethod == 'otel':
        init_otel()

    result_facts = execute_service(service, facts, args.traceMethod, args.traceFile)

    write_actions(args.outputPath, args.cleanOutput, result_facts)

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        logging.debug("\n\nResults:")
        for result_fact in result_facts:
            if type(result_fact) == Action:
                logging.debug("\t%s: %s", result_fact.__class__.__name__, json.dumps(result_fact.to_dict()))
            #elif type(result_fact) == ExecutionContext:
            #    logging.debug("\t%s: %s", result_fact.__class__.__name__, json.dumps(result_fact.to_dict()))
            #elif type(result_fact) == Collector:
            #    logging.debug("\t%s: %s(%d)", result_fact.__class__.__name__, result_fact.group, 
            #                  len(result_fact.collection))
            #else:
            #    logging.debug("\t%s: %s", result_fact.__class__.__name__, result_fact)