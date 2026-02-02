import csv
import json
import os
import time

from autoins.bluebook import BlueBook
from autoins.entities2 import Request
from autoins.edi_parser import parse_edi
from autoins.util import subfiles

from knowledgenet.ftypes import Wrapper


def load_facts(factsPaths):
    facts = set()
    for path in factsPaths:
        files = subfiles(path)
        for f in files:
            if f == 'rule-config.json':
                with open(os.path.join(path, f)) as file:
                    configs = json.load(file)
                    for rs, config in configs.items():
                        facts.add(
                            Wrapper(named=f"{rs}-ruleset", config=config))
            elif f.startswith('tx') and f.endswith('.edi'):
                # read entire EDI payload and parse into Request objects
                with open(os.path.join(path, f), 'r') as fh:
                    payload = fh.read()
                    reqs = parse_edi(payload)
                for req in reqs:
                    facts.add(req)
            elif f == 'blues.csv':
                facts.add(BlueBook(os.path.join(path, f)))
    return facts
