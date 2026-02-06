import csv
import json
import os
import time

from autoins.bluebook import BlueBook
from autoins.edi_parser import parse_edi
from autoins.entities import Action
from autoins.util import subfiles

from knowledgenet.ftypes import Wrapper
from knowledgenet.container import Collector

def load_facts(factsPaths):
    facts = set()
    for path in factsPaths:
        files = subfiles(path)
        for f in files:
            if f == 'rule-config.json':
                with open(os.path.join(path,f)) as file:
                    configs = json.load(file)
                    for rs,config in configs.items():
                        facts.add(Wrapper(named=f"{rs}-ruleset", config=config))
            elif f.startswith('tx') and f.endswith('.edi'):
                with open(os.path.join(path, f), 'r') as fh:
                    payload = fh.read()
                    reqs = parse_edi(payload)
                    for req in reqs:
                        facts.add(req)
                        facts.add(Collector(of_type=Action, group='action-collector', 
                                    request=req, 
                                    filter=lambda this,action: this.request.claim.id == action.claim_id))
            elif f == 'blues.csv':
                facts.add(BlueBook(os.path.join(path,f)))
    
    return facts

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
