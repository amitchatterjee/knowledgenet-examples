"""Synthetic EDI transaction generator for performance profiling.

`data/tx_vectors.edi` (6 hand-crafted claims) and the unit-test fixtures under
`test/data/` are sized and shaped for correctness coverage, not profiling: too
few transactions to get a stable profile, and skewed toward validation-failure
edge cases rather than a realistic claim mix. This module generates a much
larger synthetic `tx*.edi` file, built from the same patterns as
`data/tx_vectors.edi`, in a configurable mix, so Phase 0 (and later phases that
reuse the same dataset for end-to-end timing) see a representative spread
across all four rule phases (validation, contract, fraud, finalization).

Each generated claim gets a unique id suffix (`_{i}`) so `Request`/`Claim`
identity (hash/eq are id-based, see `autoins.entities`) never collides across
the generated set.
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

# Each template is a function (i: int) -> str producing one STX/ETX block.
# Field order/positions mirror data/tx_vectors.edi exactly (autoins.edi_parser
# zips CSV columns positionally against autoins.entities' model field order).


def _valid_claim(i: int) -> str:
    return f"""# valid_claim_{i}
STX
CLA,C{i},collision,P{i},2024-02-20,5000,0,A{i},D{i},received,Valid claim,R{i}
POL,P{i},G{i},John Doe,2024-01-01,2024-12-31,D{i},A{i}
GRP,G{i},500,10000.00,100000.00
DRV,D{i},John Doe,1985-02-15,D1234567,CA
AUT,A{i},Toyota,Prius,2010
INC,R{i},police,P{i},2024-03-15,Accident description,D1234567,NY,A{i},0.75
EST,E{i},W1,yes,A{i},C{i},2024-02-15,3000.00,Valid estimate
ETX"""


def _vin_mismatch_estimate(i: int) -> str:
    return f"""# vin_mismatch_estimate_{i}
STX
CLA,C{i},collision,P{i},2024-02-20,4000,0,A{i},D{i},received,Claim with mismatched VIN,R{i}
POL,P{i},G{i},Jane Roe,2024-01-01,2024-12-31,D{i},A{i}
GRP,G{i},500,10000.00,100000.00
DRV,D{i},Jane Roe,1990-05-01,D7654321,CA
AUT,A{i},Toyota,Prius,2010
INC,R{i},police,P{i},2024-03-15,Accident description,D7654321,CA,A{i},0.50
EST,E{i},W2,yes,XX{i},C{i},2024-02-16,1500.00,Estimate
ETX"""


def _vin_mismatch_incidence(i: int) -> str:
    return f"""# vin_mismatch_incidence_{i}
STX
CLA,C{i},collision,P{i},2024-02-20,4000,0,A{i},D{i},received,Claim with mismatched VIN,R{i}
POL,P{i},G{i},Jane Roe,2024-01-01,2024-12-31,D{i},A{i}
GRP,G{i},500,10000.00,100000.00
DRV,D{i},Jane Roe,1990-05-01,D7654321,CA
AUT,A{i},Toyota,Prius,2010
INC,R{i},police,P{i},2024-03-15,Accident description,D7654321,CA,XX{i},0.50
EST,E{i},W3,yes,A{i},C{i},2024-02-16,1500.00,Estimate
ETX"""


def _vin_mismatch_claim(i: int) -> str:
    return f"""# vin_mismatch_claim_{i}
STX
CLA,C{i},collision,P{i},2024-06-15,2000,0,XX{i},D{i},received,Vehicle not on policy,R{i}
POL,P{i},G{i},Sam Smith,2024-01-01,2024-12-31,D{i},A{i}
GRP,G{i},500,10000.00,100000.00
DRV,D{i},Sam Smith,1992-07-07,D4444444,CA
AUT,A{i},Ford,Focus,2012
INC,R{i},police,P{i},2024-06-15,Accident for VIN mismatch,D4444444,CA,XX{i},0.5
EST,E{i},W4,yes,XX{i},C{i},2024-06-16,750.00,Estimate
ETX"""


def _missing_automobile(i: int) -> str:
    return f"""# missing_automobile_{i}
STX
CLA,C{i},collision,P{i},2024-02-20,5000,0,XX{i},D{i},received,Valid claim,R{i}
POL,P{i},G{i},John Doe,2024-01-01,2024-12-31,D{i},A{i}
GRP,G{i},500,10000.00,100000.00
DRV,D{i},John Doe,1985-02-15,D1234567,CA
INC,R{i},police,P{i},2024-03-15,Accident description,D1234567,NY,A{i},0.75
EST,E{i},W5,yes,A{i},C{i},2024-02-15,3000.00,Valid estimate
ETX"""


def _insufficient_estimates(i: int) -> str:
    return f"""# insufficient_estimates_{i}
STX
CLA,C{i},collision,P{i},2024-02-20,5000,0,A{i},D{i},received,Valid claim,R{i}
POL,P{i},G{i},John Doe,2024-01-01,2024-12-31,D{i},A{i}
GRP,G{i},500,10000.00,100000.00
DRV,D{i},John Doe,1985-02-15,D1234567,CA
AUT,A{i},Toyota,Prius,2010
INC,R{i},police,P{i},2024-03-15,Accident description,D1234567,NY,A{i},0.75
EST,E{i}-1,W1,no,A{i},C{i},2024-02-15,3000.00,Valid estimate
EST,E{i}-2,W1,no,A{i},C{i},2024-02-15,2000.00,Valid estimate
ETX"""


# (template, weight) - weights need not sum to 1; default mix favors claims
# that flow all the way through to 05_finalization, matching a plausible
# real-world distribution rather than an even spread across edge cases.
DEFAULT_MIX = [
    (_valid_claim, 0.60),
    (_vin_mismatch_estimate, 0.08),
    (_vin_mismatch_incidence, 0.08),
    (_vin_mismatch_claim, 0.08),
    (_missing_automobile, 0.08),
    (_insufficient_estimates, 0.08),
]


def generate_edi(count: int, seed: int = 42, mix: list | None = None) -> str:
    """Return a tx*.edi payload with `count` synthetic claims."""
    mix = mix or DEFAULT_MIX
    templates, weights = zip(*mix)
    rng = random.Random(seed)
    chosen = rng.choices(templates, weights=weights, k=count)
    return "\n\n".join(template(i) for i, template in enumerate(chosen, start=1))


def write_edi(output_path: Path, count: int, seed: int = 42) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generate_edi(count, seed) + "\n")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=5000, help="Number of synthetic claims to generate")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed, for reproducible datasets")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "target" / "data" / "tx_vectors.edi",
        help="Output file path (must be named tx*.edi for autoins.fact_io.load_facts to pick it up)",
    )
    args = parser.parse_args()
    path = write_edi(args.output, args.count, args.seed)
    print(f"Wrote {args.count} synthetic claims (seed={args.seed}) to {path}")


if __name__ == "__main__":
    main()
