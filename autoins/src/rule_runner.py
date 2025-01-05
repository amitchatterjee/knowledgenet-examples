import argparse
import os
import sys
import time
import pandas as pd
import json
from knowledgenet import scanner
from knowledgenet.service import Service
from knowledgenet.collector import Collector
from autoins.entities import Action, Adj, Claim, Driver, PoliceReport, Policy
from autoins.fact_loader import load_from_csv
import logging

def argsparser():
    parser = argparse.ArgumentParser(description="Auto Insurance Payment Rules Service")
    parser.add_argument('--rulesPath', required=True, help='Full path of the location from where rules are loaded')
    parser.add_argument('--factsPaths', required=True, nargs='+', help='Full paths from where the facts are loaded')
    parser.add_argument('--outputPath', required=True, help='Full path name of the directory where the actions are written to')
    parser.add_argument('--cleanOutput', action='store_true', help='Clean the output directory before writing the actions')
    parser.add_argument('--trace', action='store_true', help='Enable tracing of rule execution')
    parser.add_argument('--log', help='Log severity level. The valid values are DEBUG, INFO, WARNING, ERROR, CRITICAL', default='INFO')
    return parser.parse_args()

def subdirs(parent):
    return [os.path.join(parent, name) for name in os.listdir(parent) if os.path.isdir(os.path.join(parent, name))]

def subfiles(parent):
    return [name for name in os.listdir(parent) if os.path.isfile(os.path.join(parent, name))]

def init_facts(args):
    facts = set()
    for path in args.factsPaths:
        files = subfiles(path)
        for f in files:
            converters = None
            if f.startswith('policies'):
                load_from_csv(facts, Policy, os.path.join(path,f), converters={
                    'start_date': pd.to_datetime,
                    'end_date': pd.to_datetime,
                    'deductible': float,
                    'max_coverage': float,
                    'drivers': lambda d: d.split(';') if d else [],
                    'automobiles': lambda a: a.split(';') if a else []
                })
            elif f.startswith('claims'):
                load_from_csv(facts, Claim, os.path.join(path,f), converters={
                    'accident_date': pd.to_datetime,
                    'claimed_amount': float,
                    'paid_amount': float,
                    'automobile': str,
                    'police_report': str
                })
            elif f.startswith('drivers'):
                load_from_csv(facts, Driver, os.path.join(path,f), converters={
                    'dob': pd.to_datetime
                })
            elif f.startswith('police_reports'):
                load_from_csv(facts, PoliceReport, os.path.join(path,f), converters={
                    'date': pd.to_datetime,
                    'responsible_parties': lambda d: d.split(';') if d else [],
                    'liability_percent': float
                })
    return facts

def init_knowledgebase(args):
    rules_paths = []
    repo = subdirs(args.rulesPath)
    for r in repo:
        rules_paths.append(r)
    scanner.load_rules_from_filepaths(rules_paths)

    rules_basename = os.path.basename(args.rulesPath)
    repository = scanner.lookup(rules_basename)
    service = Service(repository)
    logging.info(f"Loaded {len(repository.rulesets)} rulesets")
    facts = init_facts(args)
    logging.info(f"Loaded {len(facts)} facts")
    return service,facts

def init_logging(args):
    handlers = [logging.StreamHandler(sys.stdout)]
    logging.basicConfig(level=getattr(logging, args.log.upper(), None), handlers=handlers)

def write_result(args, result_facts):
    if not os.path.exists(args.outputPath):
        os.makedirs(args.outputPath)
    
    if args.cleanOutput:
        files = subfiles(args.outputPath)
        for f in files:
            os.remove(os.path.join(args.outputPath, f))

    df = pd.DataFrame(columns=Action.columns)
    for result_fact in result_facts:
            if type(result_fact) == Action:
                frame = pd.DataFrame(result_fact.to_dict(), index=[0])
                df = pd.concat([df if not df.empty else None, frame], ignore_index=True)
    df.to_csv(os.path.join(args.outputPath, f"{time.time()}.csv"), index=False)

if __name__ == "__main__":
    args = argsparser()

    init_logging(args)

    service, facts = init_knowledgebase(args)
    result_facts = service.execute(facts, tracer=sys.stdout if args.trace else None)

    write_result(args, result_facts)

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        logging.debug("\n\nResults:")
        for result_fact in result_facts:
            if type(result_fact) == Action:
                logging.debug("\t%s: %s", result_fact.__class__.__name__, json.dumps(result_fact.to_dict()))
            #elif type(result_fact) == Adj:
            #    logging.debug("\t%s: %s", result_fact.__class__.__name__, json.dumps(result_fact.to_dict()))
            #elif type(result_fact) == Collector:
            #    logging.debug("\t%s: %s(%d)", result_fact.__class__.__name__, result_fact.group, 
            #                  len(result_fact.collection))
            #else:
            #    logging.debug("\t%s: %s", result_fact.__class__.__name__, result_fact)