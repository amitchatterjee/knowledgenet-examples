from autoins.entities import Action
from util import execute, assert_result_matches, dump_result

def test_contract_rules():
    result_facts = execute('rules', ['test/data/contract-rules'], '../target/test-results')
    assert result_facts is not None
    dump_result(result_facts)
    #assert_result_matches(result_facts, 'test/expected/validation-rules/expected.csv')

