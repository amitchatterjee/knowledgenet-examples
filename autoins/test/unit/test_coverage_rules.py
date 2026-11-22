from util import execute, assert_result_matches, dump_result, service

def test_coverage_rules(service):
    result_facts = execute(service, ['test/data/coverage-rules'], 'target/test-results/coverage-rules')
    assert result_facts is not None
    dump_result(result_facts)
    assert_result_matches(result_facts, 'test/expected/coverage-rules/expected.csv')
