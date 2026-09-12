The `knowledgenet autoins` rules are part of a rules-based system for processing auto insurance claims. The rules are organized into different phases or rulesets, each focusing on a specific aspect of the claims processing workflow.

These rules are designed to automate and streamline the processing of auto insurance claims by applying a series of logical checks and actions across distinct phases. The primary purpose of these rules is to ensure that each claim is thoroughly validated, checked for contractual compliance, screened for potential fraud, and finalized for payment in a transparent and explainable manner. The inputs to the rules engine are structured facts representing claims, policies, groups, drivers, automobiles, incidence reports, and estimates, loaded from EDI transactions and parsed into Request objects for each claim. As the rules are executed, they produce outputs in the form of actions, validation errors, eligibility determinations, fraud flags, and payment computations, which are collected and used to guide the final disposition of each claim. This rules-based approach enables consistent, auditable, and flexible decision-making for complex insurance workflows.

**Note:** While claim transaction data is processed using EDI format, reference data such as bluebook values for vehicle pricing are still maintained in CSV files.

## Rulesets Overview

The rules in this system are organized into distinct rulesets, each corresponding to a phase in the claims processing workflow. The ruleset names match the folder names under the `rules` directory, with numeric prefixes (e.g., `01_`, `02_`) used only for ordering and omitted here for clarity. Below is a list of the main rulesets and their functions:

- **02_validation**: Ensures all required information is present in the claim, checking for missing policies, drivers, automobiles, incidence reports, and sufficient estimates.
- **03_contract**: Verifies claim eligibility based on contract terms, such as policy activity, filing timeliness, and VIN matching.
- **04_fraud**: Detects potential fraud by checking for inconsistencies and mismatches between claim data and related entities, such as VIN mismatches.
- **05_finalization**: Computes final payments and completes the claims process, including calculations for collision and liability claims.
