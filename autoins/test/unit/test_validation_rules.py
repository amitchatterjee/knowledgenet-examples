from autoins.entities import Action
from util import execute, assert_result_matches, dump_result, service
import inspect

def test_sanity(service):
    result = execute(service, ['data'], f'../target/results')
    assert result is not None

def test_validation_rules(service):
    result_facts = execute(service, ['test/data/validation-rules'], '../target/test-results/validation-rules')
    assert result_facts is not None
    assert_result_matches(result_facts, 'test/expected/validation-rules/expected.csv')

