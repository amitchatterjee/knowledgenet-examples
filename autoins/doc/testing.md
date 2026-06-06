
## Test Framework Overview

The test framework for the rules engine is designed to automate the verification of rule logic using realistic test data and expected results. Each test typically follows this workflow:

1. **Test Data Preparation:**
	- Test data is organized as EDI transactions, with each transaction containing segments representing different entities (claims, drivers, policies, etc.).
	- EDI transactions are delimited by STX (start) and ETX (end) markers.
	- A rule configuration file (JSON) specifies which rules are enabled and their expected actions.

2. **Test Execution:**
	- The test function (e.g., `test_validation_rules`) uses the EDI parser to parse transaction data into Request objects.
	- The rules engine processes the Request objects and produces a set of result facts (e.g., actions, validation errors).

3. **Result Verification:**
	- The test asserts that the engine produced results (not `None`).
	- The results are compared against expected outcomes to verify rule behavior.
	- If the actual and expected results match, the test passes, confirming the rules behave as intended.

This approach ensures that changes to rules or data are automatically checked for correctness, and that the rules engine remains robust and reliable as the system evolves.


## EDI Transaction Format

Test data is now provided as EDI transactions. Each EDI transaction represents a complete insurance claim request with all associated entities. The EDI format uses segment identifiers and CSV-formatted data lines.

### Transaction Structure

Each EDI transaction is delimited by:
- **STX**: Start of transaction marker
- **ETX**: End of transaction marker

Between STX and ETX, various segments define the entities involved in the claim. Each segment is a CSV-formatted line where:
- The first column is the **segment identifier** (3-letter code)
- Remaining columns contain the entity's field values in the order defined by the data model

Lines beginning with `#` are treated as comments and ignored.

### Segment Types

The following segment identifiers are supported:

#### CLA - Claim (Required)
The main claim being adjudicated.
- **id**: Unique claim identifier (e.g., `C1`)
- **type**: Claim type (`collision`, `liability`)
- **policy_id**: Associated policy (e.g., `P1`)
- **filing_date**: Date filed (`YYYY-MM-DD`)
- **claimed_amount**: Amount claimed (numeric)
- **paid_amount**: Amount paid (numeric, typically `0` for new claims)
- **vin**: Vehicle involved (e.g., `A1`)
- **driver_id**: Driver involved (e.g., `D1`)
- **status**: Claim status (`received`, `approved`, `rejected`)
- **description**: Description of incident
- **incidence_report_id**: Linked incident report (e.g., `R1`), may be empty

#### POL - Policy
The insurance policy associated with the claim.
- **id**: Policy identifier (e.g., `P1`)
- **group_id**: Associated group (e.g., `G1`)
- **policy_holder**: Name of policy holder
- **start_date**: Policy start date (`YYYY-MM-DD`)
- **end_date**: Policy end date (`YYYY-MM-DD`)
- **drivers**: List of driver IDs (semicolon-separated, e.g., `D1;D2`)
- **automobiles**: List of VINs (semicolon-separated, e.g., `A1;A2`)

#### GRP - Group
Policy group defining coverage limits and deductibles.
- **id**: Group identifier (e.g., `G1`)
- **collision_deductible**: Deductible for collision (numeric)
- **collision_coverage**: Collision coverage amount (numeric)
- **liability_coverage**: Liability coverage amount (numeric)

#### DRV - Driver
Driver associated with the claim.
- **id**: Driver identifier (e.g., `D1`)
- **name**: Driver's name
- **dob**: Date of birth (`YYYY-MM-DD`)
- **license_number**: License number
- **license_state**: State of license (e.g., `CA`)

#### AUT - Automobile
Vehicle involved in the claim.
- **vin**: Vehicle Identification Number (e.g., `A1`)
- **make**: Car manufacturer (e.g., `Toyota`, `Honda`)
- **model**: Car model (e.g., `Camry`, `Civic`)
- **year**: Year of manufacture (e.g., `2020`)

#### INC - Incidence Report
Incident report linked to the claim.
- **id**: Incident report identifier (e.g., `R1`)
- **source**: Source of report (e.g., `police`, `self`)
- **policy**: Associated policy
- **accident_date**: Date of accident (`YYYY-MM-DD`)
- **description**: Description of incident
- **license_number**: License number involved
- **license_state**: State of license
- **vin**: Vehicle involved
- **liability_percent**: Percent liability (numeric, 0-100)

#### EST - Estimate
Repair or service estimate for the claim.
- **id**: Estimate identifier
- **estimator_id**: Estimator or vendor ID
- **certified**: Whether vendor is certified (`true`, `false`)
- **vin**: Vehicle involved
- **claim_id**: Associated claim
- **date**: Estimate date (`YYYY-MM-DD`)
- **amount**: Estimate amount (numeric)
- **description**: Description of estimate

#### CLH - Collision History
Historical collision claims. Uses the same fields as CLA segment.

#### LYH - Liability History
Historical liability claims. Uses the same fields as CLA segment.

### Example EDI Transaction

```
STX
CLA,C1,collision,P1,2024-01-15,5000.00,0,A1,D1,received,Rear-end collision,R1
POL,P1,G1,John Doe,2023-01-01,2024-01-01,D1,A1
GRP,G1,500.00,50000.00,100000.00
DRV,D1,John Doe,1980-05-15,DL12345,CA
AUT,A1,Toyota,Camry,2020
INC,R1,police,P1,2024-01-15,Rear-end collision on Highway 101,DL12345,CA,A1,30.0
EST,E1,EST001,true,A1,C1,2024-01-16,4500.00,Bumper and taillight repair
CLH,H1,collision,P1,2023-06-10,3000.00,3000.00,A1,D1,approved,Minor fender bender,
ETX
```

This EDI format provides a compact, structured way to represent complete claim requests for testing and processing.

## Current Claim vs Historical Claims

EDI transactions distinguish between the current claim being adjudicated and historical claims:

- **CLA segment**: Represents the current claim that has been newly submitted and is awaiting processing. The CLA segment typically has a status of `received` and a `paid_amount` of `0`, indicating that no payment has been made yet. This is the primary claim that the rules engine will adjudicate and validate.

- **CLH segment** (Collision History): Contains historical collision claims that have already been processed. These segments may include values like `approved` or `rejected` for the status field, and the `paid_amount` field reflects the actual amount paid out (if any). Multiple CLH segments can appear in a single transaction.

- **LYH segment** (Liability History): Contains historical liability claims that have already been processed, with the same structure as CLH but specifically for liability-type claims. Multiple LYH segments can appear in a single transaction.

Historical claim segments (CLH and LYH) are useful for testing rules that depend on past claim outcomes, such as:
- Detecting repeat or fraudulent claims
- Analyzing claim patterns and trends
- Applying frequency-based rules (e.g., multiple claims within a time period)
- Calculating risk scores based on claims history

In an EDI transaction, the CLA segment is required (one per transaction), while CLH and LYH segments are optional and can appear multiple times to represent the claimant's complete history.

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

## Creating a New Test

To create a test for a ruleset, you need to produce four artifacts organized into specific directories. The following sections describe each artifact and the directory conventions.

### Directory Structure

Tests follow a consistent directory layout:

```
autoins/
├── test/
│   ├── unit/
│   │   └── test_{ruleset}_rules.py      # Test module
│   ├── data/
│   │   └── {ruleset}-rules/
│   │       ├── tx_vectors.edi           # Test input data
│   │       └── rule-config.json         # Rule configuration
│   └── expected/
│       └── {ruleset}-rules/
│           └── expected.csv             # Expected results
└── target/
    └── test-results/
        └── {ruleset}-rules/             # Generated output (auto-created)
```

Replace `{ruleset}` with the name of the ruleset being tested (e.g., `validation`, `contract`, `fraud`).

### Artifact 1: Test Input Data (`tx_vectors.edi`)

**Location:** `test/data/{ruleset}-rules/tx_vectors.edi`

This file contains the EDI transactions that serve as test inputs. Each STX/ETX block represents a separate test case. Design each transaction to exercise a specific rule or scenario.

Use comments (lines starting with `#`) to document what each transaction is testing:

```
# Valid claim - should result in pay action
STX
CLA,C1,collision,P1,2024-02-20,5000,0,A1,D1,received,Valid claim,R1
POL,P1,G1,John Doe,2024-01-01,2024-12-31,D1;D2,A1;A2
GRP,G1,500,10000.00,100000.00
DRV,D1,John Doe,1985-02-15,D1234567,CA
AUT,A1,Toyota,Prius,2010
INC,R1,police,P1,2024-03-15,Accident description,D1234567,NY,A1,0.75
EST,E1,W1,yes,A1,C1,2024-02-15,3000.00,Valid estimate
ETX

# Missing policy - should trigger no_policy rule
STX
CLA,C2,collision,P2,2024-02-20,5000,0,A2,D2,received,Valid claim,R2
GRP,G2,500,10000.00,100000.00
DRV,D2,John Doe,1985-02-15,D1234567,CA
AUT,A2,Toyota,Prius,2010
INC,R2,police,P1,2024-03-15,Accident description,D1234567,NY,A2,0.75
EST,E2,W2,yes,A2,C2,2024-02-15,3000.00,Valid estimate
ETX
```

Use unique claim IDs (e.g., `C1`, `C2`) across transactions to avoid conflicts. Refer to the [EDI Transaction Format](#edi-transaction-format) and [Segment Types](#segment-types) sections above for the full list of available segments and their fields.

### Artifact 2: Rule Configuration (`rule-config.json`)

**Location:** `test/data/{ruleset}-rules/rule-config.json`

This file controls which rules are enabled and how they behave during the test. It must include configurations for all rulesets that the test transactions will pass through, not just the ruleset under test. Rules from other rulesets can be enabled or disabled as needed to isolate the behavior being tested.

Refer to the [rule-config.json](#rule-configjson) section above for the full configuration structure.

### Artifact 3: Expected Results (`expected.csv`)

**Location:** `test/expected/{ruleset}-rules/expected.csv`

This CSV file defines the expected Action outputs from the rules engine. There should be one row per Action produced - typically one per claim in the test data. The CSV columns are:

| Column | Description |
|---|---|
| `id` | A placeholder UUID (not verified by the test framework; any valid UUID will do) |
| `code` | Reason code matching the rule's `reason` field in the config |
| `claim_id` | The claim ID from the EDI transaction (e.g., `C1`) |
| `action` | Action type: `pay`, `incomplete`, or `deny` |
| `explain` | Explanation matching the rule's `explain` field in the config |
| `rank` | Priority rank matching the rule's `rank` field |
| `pay_percent` | Payment percentage (e.g., `0.75` for 75%) |
| `pay_amount` | Payment amount (typically `0.0` for non-pay actions) |
| `inactive` | Whether the action is inactive (`True` or `False`) |

Example:

```csv
id,code,claim_id,action,explain,rank,pay_percent,pay_amount,inactive
9f7db5e2-9884-46de-bc3b-f2e263518924,PAYCL,C1,pay,pay,0,0.75,0.0,False
01a8648b-7060-409b-8097-5aa234dd8ebb,NOPLY,C2,incomplete,no policy found,1000,0.0,0.0,False
```

**Note:** The `id` field is excluded from comparison. The test framework compares actual and expected results using MD5 checksums computed over all fields except `id`, so the UUID values in expected.csv do not need to match the actual output.

### Artifact 4: Test Module (`test_{ruleset}_rules.py`)

**Location:** `test/unit/test_{ruleset}_rules.py`

The test module is a pytest file that wires the test data to the rules engine and verifies the output. It follows a standard pattern:

```python
from util import execute, assert_result_matches, dump_result, service

def test_{ruleset}_rules(service):
    result_facts = execute(service, ['test/data/{ruleset}-rules'], 'target/test-results/{ruleset}-rules')
    assert result_facts is not None
    assert_result_matches(result_facts, 'test/expected/{ruleset}-rules/expected.csv')
```

The test module uses three functions from the shared `test/unit/util.py` module:

- **`service`** - A session-scoped pytest fixture that initializes the rules engine once by calling `init_rules("rules")`. It is shared across all test modules.
- **`execute(service, facts_paths, output_path)`** - Loads facts from the EDI data and rule configuration in the given paths, executes the rules engine, writes action results to CSV in `output_path`, and returns the result facts.
- **`assert_result_matches(result_facts, expected_csv_path)`** - Compares the actual Action results against the expected CSV by computing MD5 checksums over all fields except `id`. Asserts that the number of actions and their content match.
- **`dump_result(result_facts)`** - Logs the result facts at DEBUG level. Useful during test development to inspect actual output before creating the expected CSV.

### Generating the Expected Results

When developing a new test, you may not know the exact expected output in advance. A practical approach is:

1. Create the test data (`tx_vectors.edi`) and rule configuration (`rule-config.json`).
2. Write the test module but temporarily omit the `assert_result_matches` call.
3. Call `dump_result(result_facts)` and run the test with `log_cli_level = DEBUG` in `pytest.ini` to inspect the actual output.
4. Review the generated CSV in `target/test-results/{ruleset}-rules/` to verify the results are correct.
5. Copy the verified CSV to `test/expected/{ruleset}-rules/expected.csv`.
6. Add the `assert_result_matches` assertion back to the test module.

## Expected results — creating `expected.csv`

This short guide explains the `expected.csv` format and a reproducible workflow to generate it from real engine output.

- **Location:** `test/expected/{ruleset}-rules/expected.csv`
- **Columns (order matters):** `id,code,claim_id,action,explain,rank,pay_percent,pay_amount,inactive`
- **Important:** The `id` column is ignored by the test comparison. The test framework computes an MD5 checksum over all fields except `id` when comparing actual vs expected, so UUIDs in `id` may be arbitrary.

Steps to create expected results:

1. Add your test input in `test/data/{ruleset}-rules/tx_vectors.edi` and the corresponding `rule-config.json`.
2. In the test module (`test/unit/test_{ruleset}_rules.py`) temporarily omit or comment out the `assert_result_matches` call so the test doesn't fail while you inspect output.
3. Enable result dumping in the test by calling `dump_result(result_facts)` (the helper logs the actions at DEBUG level).
4. Run the test and produce output files:

```bash
python -m pytest test/unit/test_{ruleset}_rules.py -q
```

If you need to see `dump_result` output on the console, set `log_cli_level = DEBUG` in `pytest.ini` or run pytest with `-o log_cli=true -o log_cli_level=DEBUG`.

5. Inspect the generated CSV in `target/test-results/{ruleset}-rules/` and verify each row matches your expected action semantics.
6. When satisfied, copy the generated CSV to `test/expected/{ruleset}-rules/expected.csv` (replace any UUIDs in the `id` column if you prefer a deterministic value).
7. Restore the `assert_result_matches` assertion in the test module to lock the expectation.

Example expected CSV (IDs can be any UUID):

```csv
id,code,claim_id,action,explain,rank,pay_percent,pay_amount,inactive
9f7db5e2-9884-46de-bc3b-f2e263518924,PAYCL,C1,pay,pay,0,0.75,0.0,False
01a8648b-7060-409b-8097-5aa234dd8ebb,NOPLY,C2,incomplete,no policy found,1000,0.0,0.0,False
```

Quick notes:
- Use unique claim IDs in `tx_vectors.edi` to avoid collisions in output rows.
- The test helpers (`execute`, `dump_result`, `assert_result_matches`) live in `test/unit/util.py` — review them if you need to customize the CSV layout or comparison logic.
- Keep the `rule-config.json` in sync with the scenario you're testing; rule `reason`/`explain`/`rank` values drive the expected `code`, `explain`, and `rank` columns.

### Running Tests

Tests are run using pytest from the `autoins` directory:

```bash
python -m pytest -rPX
```

The `pytest.ini` file configures the Python path to include `src` and `test/unit`, and enables console logging at the INFO level. To see DEBUG-level output (including `dump_result` output), change `log_cli_level` to `DEBUG` in `pytest.ini`.

To run a specific test:

```bash
python -m pytest test/unit/test_validation_rules.py -rPX
```