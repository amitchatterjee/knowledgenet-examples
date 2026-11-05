"""Phase 0 profiling harness (see knowledgenet/.plans/002-...-precompilation-options-exploratory-plan.md).

Profiles a single `Service.execute()` call over a synthetic, volume-sized
fact set (see `generate_data.py`) and attributes CPU time (`tottime`, i.e.
time spent in each function itself, not its callees - so buckets sum to the
profiled total without double-counting across nested calls) to three
buckets, by source file:

  - engine        knowledgenet's own internals (core/graph.py, factset.py,
                   node.py, service.py, ...)
  - rule_bodies   the `matches=`/`then=` callables under --rules-path
                   (autoins/rules/**/*.py)
  - other         everything else reached during execute() - autoins
                   platform code (entities.py, fact_io.py, ...), pydantic
                   validation triggered by rule actions, stdlib, etc.

This answers Phase 0's actual question: how much of engine runtime is
"bookkeeping" the engine controls vs. rule-author code it treats as opaque.

Two modes:
  --mode profile (default)  cProfile breakdown as above, plus a raw .prof
                             file (open with `snakeviz` or `pstats`).
  --mode time                cProfile-free wall-clock average over
                             --repeats runs, for later phases (PyPy/Nuitka)
                             to compare against on an apples-to-apples basis
                             - cProfile's own per-call overhead would
                             otherwise skew those comparisons.

Usage (from autoins/, with `uv run`):
    uv run python test/perf/profile_engine.py --count 5000
    uv run python test/perf/profile_engine.py --mode time --repeats 5
"""
from __future__ import annotations

import argparse
import cProfile
import os
import pstats
import sys
import time
from pathlib import Path

AUTOINS_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AUTOINS_ROOT / "src"))

from generate_data import write_edi  # noqa: E402  (path setup must run first)

from autoins.fact_io import load_facts  # noqa: E402
from autoins.entities import Action  # noqa: E402
from knowledgenet import scanner  # noqa: E402
from knowledgenet.ftypes import EventFact  # noqa: E402
from rule_runner import init_rules  # noqa: E402


def _build_service_and_facts(rules_path: Path, data_path: Path, perf_data_dir: Path, backend: str = "auto"):
    scanner.clear()
    service = init_rules(str(rules_path), backend=backend)
    facts = load_facts([str(data_path), str(perf_data_dir)])
    facts.add(EventFact(group="onAction", on_types=Action))
    return service, facts


def _bucket_for(filename: str, rules_abspath: str) -> str:
    if (os.sep + "knowledgenet" + os.sep) in filename or filename.endswith(os.sep + "knowledgenet"):
        return "engine"
    if filename.startswith(rules_abspath):
        return "rule_bodies"
    return "other"


def run_profile(service, facts, rules_abspath: str, out_dir: Path, top: int) -> None:
    profiler = cProfile.Profile()
    profiler.enable()
    result_facts = service.execute(facts, trc_level=0, trc_details=0)
    profiler.disable()

    out_dir.mkdir(parents=True, exist_ok=True)
    prof_path = out_dir / f"profile-{int(time.time())}.prof"
    stats = pstats.Stats(profiler)
    stats.dump_stats(str(prof_path))

    buckets: dict[str, float] = {"engine": 0.0, "rule_bodies": 0.0, "other": 0.0}
    per_function: dict[str, list] = {"engine": [], "rule_bodies": [], "other": []}
    for (filename, lineno, funcname), (cc, nc, tt, ct, callers) in stats.stats.items():
        bucket = _bucket_for(filename, rules_abspath)
        buckets[bucket] += tt
        per_function[bucket].append((tt, nc, filename, lineno, funcname))

    total = sum(buckets.values()) or 1e-9
    print(f"\nProfiled {len(result_facts)} result facts; raw profile: {prof_path}")
    print(f"\n{'bucket':<14}{'tottime (s)':>14}{'% of total':>14}")
    for bucket, secs in sorted(buckets.items(), key=lambda kv: -kv[1]):
        print(f"{bucket:<14}{secs:>14.4f}{100*secs/total:>13.1f}%")

    for bucket, entries in per_function.items():
        entries.sort(key=lambda e: -e[0])
        print(f"\nTop {top} in '{bucket}' by tottime:")
        for tt, nc, filename, lineno, funcname in entries[:top]:
            short = filename.rsplit(os.sep, 2)[-1] if os.sep in filename else filename
            print(f"  {tt:>9.4f}s  {nc:>8} calls  {short}:{lineno} {funcname}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--count", type=int, default=5000, help="Number of synthetic claims to generate")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--rules-path", type=Path, default=AUTOINS_ROOT / "rules")
    parser.add_argument("--data-path", type=Path, default=AUTOINS_ROOT / "data", help="Real data dir, for rule-config.json")
    parser.add_argument("--perf-data-dir", type=Path, default=Path(__file__).parent / "target" / "data")
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).parent / "target" / "results")
    parser.add_argument("--reuse-data", action="store_true", help="Skip regenerating the synthetic tx file if one already exists")
    parser.add_argument("--mode", choices=["profile", "time"], default="profile")
    parser.add_argument("--backend", choices=["auto", "native", "pure"], default="auto")
    parser.add_argument("--repeats", type=int, default=3, help="--mode time only")
    parser.add_argument("--top", type=int, default=20, help="--mode profile only")
    args = parser.parse_args()

    tx_path = args.perf_data_dir / "tx_vectors.edi"
    if not args.reuse_data or not tx_path.exists():
        write_edi(tx_path, args.count, args.seed)
        print(f"Generated {args.count} synthetic claims (seed={args.seed}) -> {tx_path}")

    if args.mode == "profile":
        service, facts = _build_service_and_facts(args.rules_path, args.data_path, args.perf_data_dir, args.backend)
        print(f"Loaded {len(facts)} facts; profiling a single Service.execute() call (backend={args.backend})...")
        run_profile(service, facts, str(args.rules_path.resolve()), args.out_dir, args.top)
    else:
        # Fresh service+facts per repeat so repeats don't observe each other's
        # inserted/updated facts (RETE execution mutates working memory).
        durations = []
        for i in range(args.repeats):
            service, facts = _build_service_and_facts(args.rules_path, args.data_path, args.perf_data_dir, args.backend)
            if i == 0:
                print(f"Loaded {len(facts)} facts; timing {args.repeats} independent Service.execute() calls (backend={args.backend})...")
            start = time.perf_counter()
            service.execute(facts, trc_level=0, trc_details=0)
            durations.append(time.perf_counter() - start)
            print(f"run {i + 1}/{args.repeats}: {durations[-1]*1000:.1f} ms")
        avg = sum(durations) / len(durations)
        print(f"\naverage over {args.repeats} runs: {avg*1000:.1f} ms (min {min(durations)*1000:.1f}, max {max(durations)*1000:.1f})")


if __name__ == "__main__":
    main()
