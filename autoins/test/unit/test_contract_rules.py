from util import execute, assert_result_matches, dump_result, service

def test_contract_rules(service):
    result_facts = execute(service, ['test/data/contract-rules'], 'target/test-results/contract-rules')
    assert result_facts is not None
    dump_result(result_facts)
    assert_result_matches(result_facts, 'test/expected/contract-rules/expected.csv')
