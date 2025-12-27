from autoins.entities import Action
import csv
import hashlib
import json
import logging

from autoins.fact_io import load_facts, write_actions
from rule_runner import execute_service, init_knowledgebase, init_rules
import pytest

@pytest.fixture(autouse=True, scope="session")
def service():
    if not hasattr(service, "_instance"):
        logging.info("Initializing rules from the rules folder")
        service._instance = init_rules("rules")
    return service._instance

def execute(service, facts_paths, output_path):
    facts = load_facts(facts_paths)
    result_facts = execute_service(service, facts, None)
    write_actions(output_path, True, result_facts)
    return result_facts

def compute_checksum(data):
    checksum = hashlib.md5()
    for key, value in sorted(data.items()):
        if key != 'id':
            checksum.update(str(value).encode('utf-8'))
    return checksum.hexdigest()

def assert_result_matches(result_facts, expected):
    expected_checksums = []
    with open(expected, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            expected_checksums.append(compute_checksum(row))
    expected_checksums.sort()

    result_checksums = []
    for result_fact in result_facts:
        if type(result_fact) == Action:
            result_checksums.append(compute_checksum(result_fact.to_dict()))
    result_checksums.sort()

    assert len(expected_checksums) == len(result_checksums), "Mismatch in number of entries"
    for expected_checksum, result_checksum in zip(expected_checksums, result_checksums):
        assert expected_checksum == result_checksum, "Checksum mismatch"

def dump_result(result_facts):
    for result_fact in result_facts:
        if type(result_fact) == Action:
            logging.debug("Action: %s", json.dumps(result_fact.to_dict()))