import json
import os
import pandas as pd

from autoins.bluebook import BlueBook
from autoins.entities import Automobile, Claim, Driver, Estimate, Group, IncidenceReport, Policy
from autoins.util import load_from_csv, subfiles, to_bool

from knowledgenet.ftypes import Wrapper

def load_facts(args):
    facts = set()
    for path in args.factsPaths:
        files = subfiles(path)
        for f in files:
            converters = None
            if f == 'rule-config.json':
                with open(os.path.join(path,f)) as file:
                    configs = json.load(file)
                    for rs,config in configs.items():
                        facts.add(Wrapper(of_type=f"{rs}-ruleset", config=config))
            elif f.startswith('policies'):
                load_from_csv(facts, Policy, os.path.join(path,f), converters={
                    'start_date': pd.to_datetime,
                    'end_date': pd.to_datetime,
                    'collision_deductible': float,
                    'collision_coverage': float,
                    'liability_coverage': float,
                    'drivers': lambda d: d.split(';') if d else [],
                    'automobiles': lambda a: a.split(';') if a else []
                })
            elif f.startswith('groups') and f.endswith('.csv'):
                load_from_csv(facts, Group, os.path.join(path,f), converters={
                    'collision_deductible': float,
                    'collision_coverage': float,
                    'liability_coverage': float
                })
            elif f.startswith('claims') and f.endswith('.csv'):
                load_from_csv(facts, Claim, os.path.join(path,f), converters={
                    'filing_date': pd.to_datetime,
                    'claimed_amount': float,
                    'paid_amount': float
                })
            elif f.startswith('drivers') and f.endswith('.csv'):
                load_from_csv(facts, Driver, os.path.join(path,f), converters={
                    'dob': pd.to_datetime
                })
            elif f.startswith('incidence_reports') and f.endswith('.csv'):
                load_from_csv(facts, IncidenceReport, os.path.join(path,f), converters={
                    'accident_date': pd.to_datetime,
                    'liability_percent': float
                })
            elif f.startswith('estimates') and f.endswith('.csv'):
                load_from_csv(facts, Estimate, os.path.join(path,f), converters={
                    'approved_vendor': to_bool,
                    'date': pd.to_datetime,
                    'amount': float
                })
            elif f.startswith('automobiles') and f.endswith('.csv'):
                load_from_csv(facts, Automobile, os.path.join(path,f))
            elif f == 'blues.csv':
                facts.add(BlueBook(os.path.join(path,f)))
    return facts
