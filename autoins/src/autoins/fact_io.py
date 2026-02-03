import csv
import json
import os
import time

from autoins.bluebook import BlueBook
from autoins.csv_parser import read_csv_and_convert
from autoins.edi_parser import parse_edi
from autoins.entities import Action, Automobile, Claim, Driver, Estimate, Group, IncidenceReport, Policy
from autoins.util import subfiles, to_bool, to_datetime

from knowledgenet.ftypes import Wrapper

def load_facts(factsPaths):
    facts = set()
    for path in factsPaths:
        files = subfiles(path)
        for f in files:
            converters = None
            if f == 'rule-config.json':
                with open(os.path.join(path,f)) as file:
                    configs = json.load(file)
                    for rs,config in configs.items():
                        facts.add(Wrapper(named=f"{rs}-ruleset", config=config))
            elif f.startswith('policies'):
                load_facts_from_csv(facts, Policy, os.path.join(path,f), converters={
                    'start_date': to_datetime,
                    'end_date': to_datetime,
                    'collision_deductible': float,
                    'collision_coverage': float,
                    'liability_coverage': float,
                    'drivers': lambda d: d.split(';') if d else [],
                    'automobiles': lambda a: a.split(';') if a else []
                })
            elif f.startswith('groups') and f.endswith('.csv'):
                load_facts_from_csv(facts, Group, os.path.join(path,f), converters={
                    'collision_deductible': float,
                    'collision_coverage': float,
                    'liability_coverage': float
                })
            elif f.startswith('claims') and f.endswith('.csv'):
                load_facts_from_csv(facts, Claim, os.path.join(path,f), converters={
                    'filing_date': to_datetime,
                    'claimed_amount': float,
                    'paid_amount': float
                })
            elif f.startswith('drivers') and f.endswith('.csv'):
                load_facts_from_csv(facts, Driver, os.path.join(path,f), converters={
                    'dob': to_datetime
                })
            elif f.startswith('incidence_reports') and f.endswith('.csv'):
                load_facts_from_csv(facts, IncidenceReport, os.path.join(path,f), converters={
                    'accident_date': to_datetime,
                    'liability_percent': float
                })
            elif f.startswith('estimates') and f.endswith('.csv'):
                load_facts_from_csv(facts, Estimate, os.path.join(path,f), converters={
                    'approved_vendor': to_bool,
                    'date': to_datetime,
                    'amount': float
                })
            elif f.startswith('tx') and f.endswith('.edi'):
                # read entire EDI payload and parse into Request objects
                with open(os.path.join(path, f), 'r') as fh:
                    payload = fh.read()
                    reqs = parse_edi(payload)
                    for req in reqs:
                        facts.add(req)
            elif f.startswith('automobiles') and f.endswith('.csv'):
                load_facts_from_csv(facts, Automobile, os.path.join(path,f))
            elif f == 'blues.csv':
                facts.add(BlueBook(os.path.join(path,f)))
    return facts

def load_facts_from_csv(facts, of_type, file_path, converters=None):
    df = read_csv_and_convert(file_path, converters)
    for row in df:
        fact = of_type(**row)
        facts.add(fact)

def write_actions(output_path, clean_output, result_facts):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if clean_output:
        files = subfiles(output_path)
        for f in files:
            os.remove(os.path.join(output_path, f))

    timestamp = str(time.time())
    output_file = os.path.join(output_path, f"{timestamp}.csv")

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=Action.columns)
        writer.writeheader()
        for result_fact in result_facts:
            if type(result_fact) == Action:
                writer.writerow(result_fact.to_dict())
