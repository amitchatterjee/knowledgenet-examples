import json

from autoins.entities import Action
from framework import execute

def test_sanity():
    result = execute('rules', ['data'], '../target/results')
    assert result is not None


def test_validation_rules():
    result_facts = execute('rules', ['test/data/validation-rules'], '../target/test-results')
    assert result_facts is not None
    for result_fact in result_facts:
            if type(result_fact) == Action:
                print(f"\t{result_fact.__class__.__name__,}: {json.dumps(result_fact.to_dict())}")