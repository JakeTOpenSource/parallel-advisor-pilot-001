# Pilot clause 001 (public spec)

Version 1.0.0. Status: active pilot.

## Purpose

Prove the parallel-advisor loop end to end on a tiny deterministic suite
before any real baseline is attempted. This directory is the entire public
spec. Executors must not look anywhere else.

## Procedure

From a cold shell, in this directory:

```sh
bash run.sh M
```

For Track C, replace `M` with `C`. The runner writes `result.json` next to
this file. That file is the executor's entire deliverable: send it to the
advisor unchanged.

## Rules for executors

- Run the procedure exactly. Do not edit seeds, code, or thresholds.
- A failure is a result, not a bug in the test. Report it unchanged.
- You do not need expected values and you must not go looking for them.
- Requirements: POSIX shell, Python 3 (standard library only), no network.

## The five tests

1. `seeded_rng`: five floats from a seeded generator. Must reproduce exactly.
2. `deterministic_sort`: fixed word list sorted and joined. Must match exactly.
3. `numeric_tolerance`: float accumulation. Asserted with a declared tolerance.
4. `canary_reject`: negative control. A forged input must be rejected.
5. `procedure_integrity`: tripwire. Hash of seeds.json; detects tampering.

## Platform reproducibility note (added 2026-09-23)

Test 3 sums `math.sin(i)` over 1000 terms. `math.sin` dispatches to the
platform C math library, which is not bit-identical across operating systems.
On 2026-09-23, Track M (Linux/glibc) and Track C (Windows CRT) differed by
5.55e-16, roughly a million times inside the declared 1e-9 tolerance. This is
expected and acceptable: the clause promises agreement *within tolerance*,
not bit-identical floats, across platforms. The advisor's cross-track
comparator honors declared tolerances for exactly this reason. Same machine,
same platform: observed values must reproduce exactly run to run.
