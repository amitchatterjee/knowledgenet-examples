# Entity Relationships in Auto Insurance Claims Adjudication

This document describes the relationships between the Python classes (entities) used for adjudicating auto insurance claims in the `autoins` module.

## Overview
The entities represent real-world objects and concepts involved in the processing of auto insurance claims. Their relationships reflect how data flows and is connected during the adjudication process.

## Entity Descriptions and Relationships

### Policy
- Represents an insurance policy.
- Has a unique `id` and is associated with a `group_id` (see Group).
- Contains references to one or more `drivers` (Driver) and `automobiles` (Automobile).
- Linked to claims via `policy_id`.

### Group
- Represents a group or category of policies.
- Contains coverage and deductible information.
- Linked to policies via `group_id`.

### Automobile
- Represents a vehicle covered by a policy.
- Identified by a unique `vin`.
- Linked to policies and claims via `vin`.

### Driver
- Represents a person authorized to drive an insured automobile.
- Identified by a unique `id`.
- Linked to policies and claims via `driver_id`.

### Claim
- Represents an insurance claim filed under a policy.
- Contains references to `policy_id`, `driver_id`, `vin`, and `incidence_report_id`.
- Linked to Policy, Driver, Automobile, and IncidenceReport.

### IncidenceReport
- Represents a report of an incident (e.g., accident) related to a claim.
- Contains references to `policy`, `license_number`, `vin`, and `liability_percent`.
- Linked to claims via `incidence_report_id`.

### Estimate
- Represents a cost estimate for repairs or damages related to a claim.
- Contains references to `claim_id` and `vin`.
- Linked to claims and automobiles.

### ExecutionContext
- Central container that aggregates all related entities for a single claim.
- Contains references to Claim, Policy, Group, Driver, Automobile, IncidenceReport, and Estimate(s).
- Used by rules to access all relevant data for adjudication.

### Action
- Represents an action or decision taken during claim adjudication (e.g., approve, deny, pay).
- Linked to claims via `claim_id`.

## Relationship Diagram (Textual)

- **Policy** 1---* **Driver**
- **Policy** 1---* **Automobile**
- **Policy** 1---* **Claim**
- **Group** 1---* **Policy**
- **Claim** 1---1 **Driver**
- **Claim** 1---1 **Automobile**
- **Claim** 1---1 **IncidenceReport**
- **Claim** 1---* **Estimate**
- **ExecutionContext** aggregates: Claim, Policy, Group, Driver, Automobile, IncidenceReport, Estimate(s)
- **Action** 1---1 **Claim**

## Summary
The entities are tightly interconnected to reflect the real-world relationships in auto insurance claims processing. The `ExecutionContext` class serves as the central hub, joining all relevant entities for efficient rule evaluation and adjudication.
