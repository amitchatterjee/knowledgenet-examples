# prompts

Supervisor + subagent prompts tuned for `autoins`, loaded by `knowledgexpert` via
`RULEGEN_ROOT/prompts/<filename>.md` (see `knowledgexpert`'s `_load_prompt_from_file()`). The legacy
`infrastructure/conf/wolfpack/{analyst,developer,tester}/agentic_prompt.txt` files (now retired) assumed
a RAG-injected-context paradigm and need full rewriting for the filesystem-browsing paradigm, plus new
prompts for the rule-spec-validator and config-generator, which don't have legacy equivalents.

Status: scaffold only, content not yet curated.
