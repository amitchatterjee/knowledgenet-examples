
## Test Framework Overview

The test framework for the rules engine is designed to automate the verification of rule logic using realistic test data and expected results. Each test typically follows this workflow:

1. **Test Data Preparation:**
	- Test data is organized in CSV files, each representing a different entity (claims, drivers, policies, etc.).
	- A rule configuration file (JSON) specifies which rules are enabled and their expected actions.

2. **Test Execution:**
	- The test function (e.g., `test_validation_rules`) uses a helper function like `execute` to run the rules engine on the test data.
	- The engine processes the data and produces a set of result facts (e.g., actions, validation errors).

3. **Result Verification:**
	- The test asserts that the engine produced results (not `None`).
	- The results are compared against an expected output file (CSV) using a function like `assert_result_matches`.
	- If the actual and expected results match, the test passes, confirming the rules behave as intended.

This approach ensures that changes to rules or data are automatically checked for correctness, and that the rules engine remains robust and reliable as the system evolves.


## Rules Test Data

Each test has a dedicated folder containing CSV files representing all the entities and facts needed to test contract-related rules in the claims adjudication process. Below is a description of each file and its fields, including possible values:

### automobiles.csv
- **vin**: Vehicle Identification Number (e.g., `A1`, `A2`)
- **make**: Car manufacturer (e.g., `Toyota`, `Honda`)
- **model**: Car model (e.g., `Camry`, `Civic`)
- **year**: Year of manufacture (e.g., `2020`)

### claims-history.csv / claims-received.csv
- **id**: Unique claim identifier (e.g., `H1`, `C1`)
- **type**: Claim type (`collision`, `liability`)
- **policy_id**: Associated policy (e.g., `P1`)
- **filing_date**: Date filed (`YYYY-MM-DD`)
- **claimed_amount**: Amount claimed (numeric)
- **paid_amount**: Amount paid (numeric, may be `0` if not paid)
- **vin**: Vehicle involved (e.g., `A1`)
- **driver_id**: Driver involved (e.g., `D1`)
- **status**: Claim status (`approved`, `rejected`, `received`)
- **description**: Description of incident
- **incidence_report_id**: Linked incident report (e.g., `R1`), may be empty

### drivers.csv
- **id**: Driver identifier (e.g., `D1`)
- **name**: Driver's name
- **dob**: Date of birth (`YYYY-MM-DD`)
- **license_number**: License number
- **license_state**: State of license (e.g., `CA`)

### estimates.csv
- **id**: Estimate identifier
- **estimator_id**: Estimator or vendor
- **approved_vendor**: Approved vendor name
- **vin**: Vehicle involved
- **claim_id**: Associated claim
- **date**: Estimate date (`YYYY-MM-DD`)
- **amount**: Estimate amount (numeric)
- **description**: Description of estimate

### groups.csv
- **id**: Group identifier (e.g., `G1`)
- **collision_deductible**: Deductible for collision (numeric)
- **collision_coverage**: Collision coverage amount (numeric)
- **liability_coverage**: Liability coverage amount (numeric)

### incidence_reports.csv
- **id**: Incident report identifier (e.g., `R1`)
- **source**: Source of report (e.g., `police`, `self`)
- **policy**: Associated policy
- **accident_date**: Date of accident (`YYYY-MM-DD`)
- **description**: Description of incident
- **license_number**: License number involved
- **license_state**: State of license
- **vin**: Vehicle involved
- **liability_percent**: Percent liability (numeric)

### policies.csv
- **id**: Policy identifier (e.g., `P1`)
- **group_id**: Associated group (e.g., `G1`)
- **policy_holder**: Name of policy holder
- **start_date**: Policy start date (`YYYY-MM-DD`)
- **end_date**: Policy end date (`YYYY-MM-DD`)
- **drivers**: List of driver IDs (comma-separated)
- **automobiles**: List of VINs (comma-separated)

These files collectively provide a comprehensive dataset for simulating and testing contract rule scenarios in the rules engine.

## claims-received vs claims-history

Both `claims-received.csv` and `claims-history.csv` contain records of insurance claims, but they serve different purposes in the testing and adjudication process:

- **claims-received.csv**: This file contains claims that have been newly submitted and are awaiting processing. The claims in this file typically have a status such as `received` and a `paid_amount` of `0`, indicating that no payment has been made yet. These records represent the input to the rules engine for adjudication and validation.

- **claims-history.csv**: This file contains claims that have already been processed, including those that have been approved, rejected, or paid. The status field may include values like `approved` or `rejected`, and the `paid_amount` field reflects the actual amount paid out (if any). This file is useful for testing rules that depend on historical claim outcomes, such as detecting repeat claims or analyzing claim trends.

In summary, `claims-received.csv` is used to simulate new, unprocessed claims, while `claims-history.csv` provides a record of past claims and their outcomes for more advanced rule scenarios.

## rule-config.json

The `rule-config.json` file defines the configuration for all rulesets used in the test framework. It allows fine-grained control over which rules are enabled, their actions, reasons, explanations, and priorities. The configuration is organized by ruleset (e.g., `validation`, `contract`, `fraud`), and can specify default settings as well as group-specific overrides.

### Structure
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
- **Group-specific overrides**: (e.g., `G1` under `fraud`) allow rules to be enabled/disabled or reconfigured for specific groups.

### Example
For the `validation` ruleset, the rule `no_policy` is enabled, marks the claim as `incomplete`, and provides a reason and explanation. In the `fraud` ruleset, the rule `vin_mismatch_claim_estimates` can be disabled for group `G1`.

This configuration mechanism makes it easy to adapt the rules engine to different business requirements and test scenarios without changing the code, simply by editing the JSON file.