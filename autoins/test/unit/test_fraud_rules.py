from util import execute, assert_result_matches, dump_result, service

def test_validation_rules(service):
    result_facts = execute(service, ['test/data/fraud-rules'], 'target/test-results/fraud-rules')
    assert result_facts is not None
    assert_result_matches(result_facts, 'test/expected/fraud-rules/expected.csv')
