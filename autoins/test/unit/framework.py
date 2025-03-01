
from rule_runner import execute_service, init_knowledgebase, write_result

def execute(rules_path, facts_paths, output_path):
    service, facts = init_knowledgebase(rules_path, facts_paths)
    result_facts = execute_service(service, facts, False, None)
    write_result(output_path, True, result_facts)
    return result_facts