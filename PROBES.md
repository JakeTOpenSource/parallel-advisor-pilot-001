# Tamper probes for diff.py v1.2 (nine probes)

Each probe: copy `results/track-c/pilot-001-2026-09-23-run2.json` to a temp
file, apply exactly one mutation, then run the advisor's check. Python's
`json.dump(..., allow_nan=True)` writes NaN/Infinity tokens; the diff tool's
`json.load` accepts them, which is what makes probes 4, 5, and 7 meaningful.

Single-track form (probes 1-7, 9):
  python3 diff-tool/diff.py clauses/pilot-001 sealed/pilot-001.json <mutant>

Two-track form (probe 8):
  python3 diff-tool/diff.py clauses/pilot-001 sealed/pilot-001.json \
      results/track-m/pilot-001-2026-09-23-run2.json <mutant>

| # | Mutation | Expected |
|---|---|---|
| 1 | `numeric_tolerance.total += 1e-6` (1000x the 1e-9 tolerance) | CONTRADICTION, exit 1, VALUE_MISMATCH |
| 2 | `procedure_hash = "0"*64` | CONTRADICTION, exit 1, PROCEDURE_TAMPER |
| 3 | `canary_reject.rejected = false` | CONTRADICTION, exit 1, VALUE_MISMATCH |
| 4 | `numeric_tolerance.total = NaN` | CONTRADICTION, exit 1, NON_FINITE_VALUE |
| 5 | `seeded_rng.values[0] = NaN` | CONTRADICTION, exit 1, NON_FINITE_VALUE |
| 6 | `canary_reject.rejected = 1` (int, not boolean) | CONTRADICTION, exit 1, VALUE_MISMATCH |
| 7 | `numeric_tolerance.total = Infinity` | CONTRADICTION, exit 1, NON_FINITE_VALUE |
| 8 | probe 4 mutation, two-track form | CONTRADICTION, exit 1, NON_FINITE_VALUE + TRACK_DIVERGENCE |
| 9 | `numeric_tolerance.total += 1e-10` (inside tolerance) | CLEAN, exit 0 (must still pass) |

Historical note: probes 4 and 5 return CLEAN under detector v1.0 and v1.1
(the NaN hole predates the tolerance amendment) and probe 6 returns CLEAN
under v1.0/v1.1 (bool/int conflation).
Verify with:
  python3 diff-tool/versions/diff-v1.1.py clauses/pilot-001 sealed/pilot-001.json <probe-4-mutant>
  -> CLEAN, exit 0. The crack stays visible.
