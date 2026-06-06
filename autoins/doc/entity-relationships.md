# Entity Relationships in Auto Insurance Claims Adjudication

This document describes the relationships between the Python classes (entities) used for adjudicating auto insurance claims in the `autoins` module.

## Overview
The entities represent real-world objects and concepts involved in the processing of auto insurance claims. The system processes EDI (Electronic Data Interchange) transactions where the **Request** entity represents the incoming transaction containing all claim-related data. Other entities are extracted and structured from this incoming Request transaction during the adjudication process.

## Entity Descriptions and Relationships

### Request
- **Represents the incoming EDI transaction** containing all claim-related data.
- Serves as the primary entry point for claim adjudication processing.
- Contains and aggregates all related entities: Claim, Policy, Group, Driver, Automobile, IncidenceReport, and Estimate(s).
- All other entities are parsed and extracted from the Request transaction data.
- Used by rules to access all relevant data for adjudication.

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

### Action
- Represents an action or decision taken during claim adjudication (e.g., approve, deny, pay).
- Linked to claims via `claim_id`.
The response to the transaction is written to a CSV file containing one or more action records.

## Relationship Diagram (Textual)

### Primary Transaction Flow
- **Request** (incoming EDI transaction) contains/aggregates: Claim, Policy, Group, Driver, Automobile, IncidenceReport, Estimate(s)

### Entity Relationships
- **Policy** 1---* **Driver**
- **Policy** 1---* **Automobile**
- **Policy** 1---* **Claim**
- **Group** 1---* **Policy**
- **Claim** 1---1 **Driver**
- **Claim** 1---1 **Automobile**
- **Claim** 1---* **IncidenceReport**
- **Claim** 1---* **Estimate**

## Summary
The system processes EDI transactions where the `Request` entity represents the incoming transaction containing all claim-related data. The entities within Request are tightly interconnected to reflect the real-world relationships in auto insurance claims processing. Request serves as the primary entry point and central hub, providing all relevant entities for efficient rule evaluation and adjudication.
