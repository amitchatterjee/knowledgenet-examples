import argparse
import os
import pandas as pd
from knowledgenet import scanner
from knowledgenet.service import Service
from autoins.fact_loader import load_from_csv

def argsparser():
    parser = argparse.ArgumentParser(description="Auto Insurance Payment Rules Service")
    parser.add_argument('--rulesPaths', required=True, nargs='+', help='Full paths from where the rules are loaded')
    parser.add_argument('--repository', required=True, help='Repository name')
    parser.add_argument('--factsPaths', required=True, nargs='+', help='Full paths from where the facts are loaded')
    parser.add_argument('--decision', required=True, help='Full path name where the decisions are written to')
    return parser.parse_args()

def subdirs(parent):
    return [os.path.join(parent, name) for name in os.listdir(parent) if os.path.isdir(os.path.join(parent, name))]

def subfiles(parent):
    return [os.path.join(parent, name) for name in os.listdir(parent) if os.path.isfile(os.path.join(parent, name))]

def init_repository(subdirs, args):
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
            if f.startswith('policy'):
                converters = {
                    'start_date': pd.to_datetime,
                    'end_date': pd.to_datetime,
                    'deductible': float,
                    'coverage': float,
                    'drivers': lambda d: d.split(':') if d else [],
                    'automobiles': lambda a: a.split(':') if a else []
                }
            load_from_csv(facts, os.path.join(path,f), converters=converters)
    return facts

if __name__ == "__main__":
    args = argsparser()
    init_repository(subdirs, args)
    repository = scanner.lookup(args.repository)
    service = Service(repository)
    facts = init_facts(subfiles, args)
    service.execute(facts)
    print(facts)