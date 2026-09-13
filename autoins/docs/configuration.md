# rule-config.json

The `rule-config.json` file defines the configuration for all rulesets used in the rules engine. It allows fine-grained control over which rules are enabled, their actions, reasons, explanations, and priorities. The configuration is organized by ruleset (e.g., `validation`, `contract`, `fraud`), and can specify default settings as well as group-specific overrides.

## Structure
- **Top-level keys**: Each ruleset (e.g., `validation`, `contract`, `fraud`).
- **default**: The default configuration for the ruleset, including:
	- `enabled`: Whether the ruleset is active.
	- `rules`: A dictionary of rule IDs, each with:
		- `enabled`: Whether the rule is active.
		- `action`: The action to take if the rule fires (e.g., `incomplete`, `deny`).
		- `reason`: A short code for the rule's outcome (e.g., `NOPLY`, `NOACT`).
		- `explain`: Human-readable explanation for the rule.
		- `rank`: Priority for the rule (higher means higher priority).
		- `percent`: Percentage value for payment or penalty (if applicable).
		- Additional fields as needed (e.g., `within` for time windows).
- **Group-specific overrides**: (e.g., `G1` under `fraud`) allow rules to be enabled/disabled or reconfigured for specific groups. A group that overrides only some rules falls back to the `default` group's entries for any rule it doesn't explicitly list.

## Example
For the `validation` ruleset, the rule `no_policy` is enabled, marks the claim as `incomplete`, and provides a reason and explanation. In the `fraud` ruleset, the rule `vin_mismatch_claim_estimates` can be disabled for group `G1`.

This configuration mechanism makes it easy to adapt the rules engine to different business requirements and test scenarios without changing the code, simply by editing the JSON file.

Note: this document describes the general format. `test/data/{ruleset}-rules/rule-config.json` files
(one per test) use the exact same structure, scoped to what a given test needs — see
`docs/testing.md`'s "rule-config.json for tests" section for that specific case.
