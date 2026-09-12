# Rule specification template

This is the template a rule-generation request against `autoins` gets interpreted through. The
supervisor reads a submitted spec against this template; the rule-spec-validator subagent checks it
for sufficiency before any code is generated (see "Sufficiency" under each section below). It's
free-form guidance, not a rigid machine-checkable schema — a spec that covers the same ground in a
different shape is fine.

A spec has three sections: **Requirements**, **Test Cases**, **Configuration**.

## Requirements

Describes **only the triggering condition** — what situation should cause this rule to fire. Not
the outcome (what happens when it fires) — that's the Configuration section's job entirely, see
below.

A Requirements entry should state:

- **Ruleset**: which of `02_validation`, `03_contract`, `04_fraud` this rule belongs to. (Rule
  generation is scoped to these three — see `knowledgexpert`'s plan doc, "Explicitly out of scope."
  A request for finalization/payment-computation behavior is out of scope and should be rejected by
  the validator, not routed anywhere.)
- **Rule name**: a short, descriptive identifier (existing convention is `snake_case`, stating the
  problem it detects — `no_policy`, `late_filing`, `vin_mismatch_claim_estimates`).
- **Trigger condition**: the business condition, in plain language, that should cause the rule to
  fire. Precise enough to be unambiguous — see "Sufficiency" below for what "precise enough" means.
- **Facts involved**: which fact type(s) and field(s) the condition depends on (e.g. "the claim's
  filing date and the incidence report's accident date"). Cross-reference
  `application-architecture/entities.py` for exact field names, or leave in business terms and let
  the code-generator subagent map them — either is fine at spec time.

**Sufficiency**: a trigger condition is insufficient if it leaves a **boundary ambiguous**. "Deny
claims filed late" is not sufficient — late relative to what, and is the boundary itself late or
on-time? "Deny claims filed more than 90 days after the accident date; exactly 90 days is on-time"
is sufficient. The validator's job is specifically to catch this kind of gap and ask for the missing
boundary rather than guess at it.

## Test Cases

Scenario-level, in business terms — **not** literal EDI/CSV syntax. Translating a scenario into an
actual `tx_vectors.edi` test vector and `expected.csv` row is the test-generator subagent's job,
guided by `testing-guidelines/` (not yet authored). A test case here just needs:

- A short scenario name.
- The relevant input facts, stated only for the fields that matter to this scenario (no need to
  specify an entire `Request` — "policy start date 2026-01-01, end date 2026-12-31, incident date
  2026-03-01" is enough if that's all this rule cares about).
- The expected outcome: does the rule fire? If so, which action/reason (matching the Configuration
  section below — they must agree).

**Sufficiency**: at minimum, one scenario where the rule fires (positive case) and one where it
doesn't (negative case). For any rule with a boundary condition (a threshold, a date comparison, an
inequality), a boundary-edge scenario is required too — exactly at the threshold, not just clearly
on either side. A spec missing a boundary case for a rule that has one is insufficient.

## Configuration

Every field `create_action()` populates from `rule-config.json` — this is the **entire** outcome of
the rule, since no rule in `02_validation`/`03_contract`/`04_fraud` hardcodes its action; all of them
call `create_action(ctx, ctx.ruleset_context, ctx.request)` verbatim and let configuration decide
what happens.

Standard fields, every rule needs all of them:

- **`enabled`** (bool) — usually `true` for a new rule.
- **`action`** (string) — the decision this rule signals. Existing convention: `"incomplete"` for
  validation-phase gaps, `"deny"` for contract/fraud rejections. Don't invent a new action string
  without checking `application-architecture/entities.py`'s `Action` class and existing usage first.
- **`reason`** (string) — a short, unique code. Existing convention is terse and uppercase
  (`NOPLY`, `LATFL`, `VINCI`) — not enforced mechanically, but new codes should match the style and
  must not collide with an existing one.
- **`explain`** (string) — a human-readable explanation, shown alongside the reason code.
- **`rank`** (int) — priority used when a request triggers multiple rules; the framework's
  (out-of-scope) selection logic uses this to pick among them.
- **`percent`** (float) — pay percentage. For `02_validation`/`03_contract`/`04_fraud`, this is
  `0.0` in every existing rule — these rulesets deny/flag, they don't compute payment (that's
  `05_finalization`, out of scope).

Beyond the standard fields, a rule may need **custom parameters** specific to its own condition
logic — read via `rule_config(ctx, ctx.ruleset_context, ctx.request)['<param>']` directly inside the
rule's `when`. Example: `late_filing` reads `['within']` for its day threshold. If the Requirements
section names a tunable threshold, name and define it here as a custom parameter rather than
hardcoding it in the rule's condition.

Optionally, a spec may call out a **group-specific override** — most new rules only need a
`default` entry, but if the requirement is known to vary by group from the start (e.g. "group G1
should have this rule disabled"), state that explicitly; otherwise the validator should assume
`default`-only and treat a later group override as a separate follow-up request.

This section states *what* the configuration should contain; the mechanical shape of
`rule-config.json` itself (nesting, how a config-generator subagent merges a new entry into the
existing file) belongs to `configuration-guidelines/` (not yet authored), not here.

**Sufficiency**: `action`, `reason`, and `explain` must all be present and mutually consistent with
the Requirements section (the reason/explanation should describe the same condition stated there).
A spec that only says "deny it" without a `reason`/`explain` is insufficient — the validator should
ask for them rather than invent placeholder text.

---

## Worked example

*(A spec that, if submitted today, would describe the already-existing `late_filing` rule under
`03_contract` — using an existing rule so the shape is verifiable against real code, not because
existing rules need re-specifying.)*

**Requirements**
- Ruleset: `03_contract`
- Rule name: `late_filing`
- Trigger condition: the claim was filed more than a configurable number of days after the
  incidence report's accident date. Exactly at the threshold counts as on-time, not late.
- Facts involved: `Claim.filing_date`, `IncidenceReport.accident_date` (both on the `Request` fact).

**Test Cases**
1. *Late filing*: accident date `2026-01-01`, filing date `2026-04-15` (104 days later, > 90) →
   rule fires; action `deny`, reason `LATFL`.
2. *Timely filing*: accident date `2026-01-01`, filing date `2026-02-01` (31 days later, ≤ 90) →
   rule does not fire.
3. *Boundary — exactly on the threshold*: accident date `2026-01-01`, filing date `2026-04-01`
   (exactly 90 days later) → rule does not fire (on-time, per "exactly at the threshold counts as
   on-time").

**Configuration**
```json
{
  "contract": {
    "default": {
      "rules": {
        "late_filing": {
          "enabled": true,
          "action": "deny",
          "reason": "LATFL",
          "explain": "late filing",
          "rank": 1000,
          "percent": 0.0,
          "within": 90
        }
      }
    }
  }
}
```
`within` is the custom parameter this rule needs beyond the five standard fields.
