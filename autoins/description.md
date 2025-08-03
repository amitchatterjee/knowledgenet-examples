The `knowledgenet autoins` rules are part of a rules-based system for processing auto insurance claims. The rules are organized into different phases or rulesets, each focusing on a specific aspect of the claims processing workflow.

These rules are designed to automate and streamline the processing of auto insurance claims by applying a series of logical checks and actions across distinct phases. The primary purpose of these rules is to ensure that each claim is thoroughly validated, checked for contractual compliance, screened for potential fraud, and finalized for payment in a transparent and explainable manner. The inputs to the rules engine are structured facts representing claims, policies, groups, drivers, automobiles, incidence reports, and estimates, typically loaded from CSV files and assembled into an ExecutionContext for each claim. As the rules are executed, they produce outputs in the form of actions, validation errors, eligibility determinations, fraud flags, and payment computations, which are collected and used to guide the final disposition of each claim. This rules-based approach enables consistent, auditable, and flexible decision-making for complex insurance workflows.

**ExecutionContext Fact:**
The `ExecutionContext` fact serves as a central container for all the data and entities related to a single insurance claim during rules processing. It aggregates information such as the claim itself, the associated policy, group, driver, automobile, incidence report, and estimates. By joining these related entities into one context, the rules engine can efficiently access and reason about all relevant facts for a claim in one place. This enables rules to perform complex validations, eligibility checks, fraud detection, and payment calculations using a unified view of the claim and its relationships, ensuring consistency and simplifying rule logic throughout the workflow.

Although, strictly not necessary, all rules must operate on the ExecutionContext fact in order to incur less overhead and to ensure standardization.

**Rule Configuration:**
The behavior and execution of rules in the system can be controlled through configuration files, such as `rule-config.json` found in the `data` directory. This configuration allows administrators and developers to enable or disable specific rules, set actions and reasons for rule outcomes, provide explanations, and assign priorities (ranks) to rules. For example, validation rules like `no_policy` or `no_driver` can be toggled on or off, and their actions (such as marking a claim as incomplete) and explanations are defined in the configuration. Contract and fraud rules can similarly be customized, including group-specific overrides. This flexible configuration mechanism makes it easy to adapt the rules engine to changing business requirements without modifying the underlying code, supporting both global and context-specific rule behaviors.
  
Although, strictly not necessary, a rule configuration must be specified in every rule declaration so that the rule can be configured using `rule-config.json`.

## Rules
The rules in this system are implemented as Python functions, each encapsulating a specific business logic check or action. Rules are grouped into modules corresponding to different phases of claim processing, and each rule is annotated with metadata describing its purpose and dependencies. The rules engine executes these rules in a defined sequence, allowing for modularity and extensibility. This design makes it easy to add new rules, modify existing ones, or adjust the workflow to accommodate changes in business requirements.

> **Note:** Rules are typically defined declaratively using the `@ruledef` decorator. This approach allows rule authors to specify rule logic, metadata, and configuration in a clear and structured manner, making rules easy to manage, and extend the rules. 

The following section provides an overview of the rules and their organization within the `knowledgenet-example/autoins` system. The rules are among a growing number of rules being developed:

### Validation Rules (`02_validation`)
These rules validate the claims to ensure all necessary information is present.

- **no_policy**: Checks if the policy is missing.
- **no_incidence_report**: Checks if the incidence report is missing.
- **no_driver**: Checks if the driver is missing.
- **no_automobile**: Checks if the automobile is missing.
- **insufficient_estimates**: Checks if there are insufficient estimates.

### Contract Rules (`03_contract`)
These rules check the eligibility of the claims based on the contract terms.

- **inactive_policy**: Checks if the policy is inactive.
- **late_filing**: Checks if the claim was filed late.
- **vin_mismatch**: Checks if the VIN on the claim does not match the VINs in the policy's automobiles.

### Fraud Rules (`04_fraud`)
These rules detect potential fraud in the claims.

- **vin_mismatch_claim_incidence_report**: Checks if the VIN on the claim does not match the VIN on the incidence report.
- **vin_mismatch_claim_estimates**: Checks if the VIN on the claim does not match the VINs in the estimates.

### Finalization Rules (`05_finalization`)
These rules compute the final payments and finalize the claims.

- **compute_collision_payment**: Computes the payment for collision claims.
- **compute_liability_payment**: Computes the payment for liability claims.

### Selection Rules (`05_finalization/selection_rules.py`)
These rules select the appropriate actions based on the processed claims.

- **pay_on_no_action**: Pays the claim if no other action is taken.
- **select_action**: Selects the appropriate action for the claim.

These rules are defined using the `@ruledef` decorator and are executed by the Knowledgenet engine in the specified order. The rulesets are executed in ascending order of their subdirectory names, ensuring a structured and phased approach to claims processing.
  
## Tests

The rules in the `knowledgenet-example/autoins` system are verified using a suite of unit tests. These tests are designed to ensure that each rule and ruleset behaves as expected when processing various claim scenarios. The unit tests typically:

- Load test data from CSV files to create realistic claim, policy, driver, automobile, and related entity objects.
- Execute the rules engine on the constructed context, either for a single ruleset or the entire workflow.
- Asserts that execution of the above rule matched with the expected result by comparing the output with the stored expected result.

Some tests focus on individual rules (e.g., checking that a missing policy triggers the correct validation error), while others verify the integration of multiple rulesets and the overall claims processing flow. This approach ensures that the rules are robust, maintainable, and produce consistent results as the system evolves.