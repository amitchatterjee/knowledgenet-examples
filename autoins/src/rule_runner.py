import argparse
import os
import sys
import pandas as pd
import json
from knowledgenet import scanner
from knowledgenet.service import Service
from knowledgenet.ftypes import Collector
from autoins.entities import Action, Adj, Claim, Driver, Policy
from autoins.fact_loader import load_from_csv

def argsparser():
    parser = argparse.ArgumentParser(description="Auto Insurance Payment Rules Service")
    parser.add_argument('--rulesPaths', required=True, nargs='+', help='Full paths from where the rules are loaded')
    parser.add_argument('--repository', required=True, help='Repository name')
    parser.add_argument('--factsPaths', required=True, nargs='+', help='Full paths from where the facts are loaded')
    parser.add_argument('--decision', required=True, help='Full path name where the decisions are written to')
    parser.add_argument('--trace', action='store_true', help='Enable tracing of rule execution')
    return parser.parse_args()

def subdirs(parent):
    return [os.path.join(parent, name) for name in os.listdir(parent) if os.path.isdir(os.path.join(parent, name))]

def subfiles(parent):
    return [name for name in os.listdir(parent) if os.path.isfile(os.path.join(parent, name))]

def init_repository(args):
    rules_paths = []
    for path in args.rulesPaths:
        repo = subdirs(path)
        for r in repo:
            rules_paths.append(r)
    return scanner.load_rules_from_filepaths(rules_paths)

def init_facts(subfiles, args):
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
                    'coverage': float,
                    'drivers': lambda d: d.split(';') if d else [],
                    'automobiles': lambda a: a.split(';') if a else []
                })
            elif f.startswith('claims'):
                load_from_csv(facts, Claim, os.path.join(path,f), converters={
                    'date': pd.to_datetime,
                    'amount': float,
                    'automobile': str,
                    'police_report': str
                })
            elif f.startswith('drivers'):
                load_from_csv(facts, Driver, os.path.join(path,f), converters={
                    'dob': pd.to_datetime
                })
    return facts

if __name__ == "__main__":
    args = argsparser()
    init_repository(args)
    repository = scanner.lookup(args.repository)
    service = Service(repository)
    facts = init_facts(subfiles, args)
    result_facts = service.execute(facts, tracer=sys.stdout if args.trace else None)
    print("\n\nResult:")
    for result_fact in result_facts:
        if type(result_fact) in [Adj, Action]:
            print(json.dumps(result_fact.to_dict()))
        elif type(result_fact) == Collector:
            print(f"Collector({result_fact.group}, collection:{result_fact.collection})")
        else:
            print(result_fact)