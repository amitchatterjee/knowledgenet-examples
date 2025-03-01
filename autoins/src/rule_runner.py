import argparse
import os
import io
import sys
import time
import pandas as pd
import json
from knowledgenet import scanner
from knowledgenet.service import Service
from knowledgenet.ftypes import EventFact
from autoins.entities import Action
import logging

from autoins.loader import load_facts
from autoins.util import subfiles
from autoins.util import subdirs

def argsparser():
    parser = argparse.ArgumentParser(description="Auto Insurance Payment Rules Service")
    parser.add_argument('--rulesPath', required=True, help='Full path of the location from where rules are loaded')
    parser.add_argument('--factsPaths', required=True, nargs='+', help='Full paths from where the facts are loaded')
    parser.add_argument('--outputPath', required=True, help='Full path name of the directory where the actions are written to')
    parser.add_argument('--cleanOutput', action='store_true', help='Clean the output directory before writing the actions')
    parser.add_argument('--trace', help='location where the trace is stored. if "log" is specified, the trace is output as an INFO log')
    parser.add_argument('--log', help='Log severity level. The valid values are DEBUG, INFO, WARNING, ERROR, CRITICAL', default='INFO')
    return parser.parse_args()

def init_knowledgebase(rules_root, facts_path):
    rules_paths = []
    repo = subdirs(rules_root)
    for r in repo:
        rules_paths.append(r)
    scanner.load_rules_from_filepaths(rules_paths)

    rules_basename = os.path.basename(rules_root)
    repository = scanner.lookup(rules_basename)
    service = Service(repository)
    logging.info(f"Loaded {len(repository.rulesets)} rulesets")
    facts = load_facts(facts_path)
    logging.info(f"Loaded {len(facts)} facts")
    return service,facts

def init_logging(log):
    handlers = [logging.StreamHandler(sys.stdout)]
    logging.basicConfig(level=getattr(logging, log.upper(), None), handlers=handlers)

def write_result(output_path, clean_output, result_facts):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    if clean_output:
        files = subfiles(output_path)
        for f in files:
            os.remove(os.path.join(output_path, f))

    df = pd.DataFrame(columns=Action.columns)
    #df.set_index(Action.key, inplace=True)
    for result_fact in result_facts:
        if type(result_fact) == Action:
            df = pd.concat([df if not df.empty else None, pd.DataFrame(result_fact.to_dict(), index=[0])])
    df.to_csv(os.path.join(output_path, f"{time.time()}.csv"), index=False)

def execute_service(service, facts, trace, trace_stream):
    try:
        start_time = time.time()
        result_facts = service.execute(facts, tracer=None if not trace else trace_stream)
        if 'log' == trace:
            logging.info("Trace from the rules execution: \n%s", trace_stream.getvalue())
    finally:
        end_time = time.time()
        execution_time_ms = (end_time - start_time) * 1000
        logging.info("Execution time: %s ms", execution_time_ms)
    return result_facts

if __name__ == "__main__":
    args = argsparser()
    init_logging(args.log)

    service, facts = init_knowledgebase(args.rulesPath, args.factsPaths)
    facts.add(EventFact(group='onAction', on_types=Action))

    trace = args.trace
    trace_stream = io.StringIO() if not trace or trace == 'log' else open(trace, 'w')
    result_facts = execute_service(service, facts, trace, trace_stream)

    write_result(args.outputPath, args.cleanOutput, result_facts)

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