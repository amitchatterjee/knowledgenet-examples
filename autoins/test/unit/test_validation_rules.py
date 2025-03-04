from autoins.entities import Action
from util import execute, assert_result_matches, dump_result

def test_sanity():
    result = execute('rules', ['data'], '../target/results')
    assert result is not None

def test_validation_rules():
    result_facts = execute('rules', ['test/data/validation-rules'], '../target/test-results')
    assert result_facts is not None
    dump_result(result_facts)

def test_validation_rules():
    result_facts = execute('rules', ['test/data/validation-rules'], '../target/test-results')
    assert result_facts is not None
    assert_result_matches(result_facts, 'test/expected/validation-rules/expected.csv')

