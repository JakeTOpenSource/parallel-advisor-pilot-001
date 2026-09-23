# Verify pilot-001 yourself (no trust in the advisor required)

Bundle versions: v3 is v2 with documentary corrections only. The evidence
packet's four-runs table, the contradiction log's status line, PROBES.md's
historical note, and two precision sentences were corrected; every
executable file (detector versions, sealed expectations, clause files,
result archives) is byte-identical between v2 and v3. v1 is superseded as a
shareable bundle but remains the audited record of the first audit.

This bundle contains everything needed to redo every check behind the
pilot-001 gold claim, using only Python 3 standard library. It also contains
every detector version, so historical findings stay reproducible (the cracks
stay visible): see diff-tool/versions/MANIFEST.md.

## 1. Recompute the answers from the public procedure alone
The sealed expectations are not magic. Anyone can derive them:
  cd clauses/pilot-001
  bash run.sh M
Compare result.json against sealed/pilot-001.json. Bit-exact on the same
platform family; within the declared tolerances across platforms (the float
total is platform-dependent, see the clause README). "Recomputable" does not
mean bit-identical everywhere. If the advisor had tailored the sealed values
after seeing results, they would still have to match what the public code
computes, which you can check yourself. That recomputability, not file
timestamps, is the load-bearing evidence (mtimes are forgeable; the sealed
file's mtime does predate the first run, for what it is worth).

## 2. Verify the procedure was never changed
Recompute the procedure hash from the public files and compare it to the
hash every result file claims:
  python3 -c "
  import hashlib, os
  h = hashlib.sha256()
  for n in ['run.sh','seeds.json','suite.py']:
      h.update(n.encode()+b'\x00'+open(os.path.join('clauses/pilot-001',n),'rb').read()+b'\x00')
  print(h.hexdigest())"
Expected: a5077f2f7373dc95d789e6dfd379ac41fcc3f7233e103e154bf8abd4cb34e9e6

## 3. Re-run the advisor's full check (live detector, v1.2)
  python3 diff-tool/diff.py clauses/pilot-001 sealed/pilot-001.json \
      results/track-m/pilot-001-2026-09-23-run2.json \
      results/track-c/pilot-001-2026-09-23-run2.json
Expect: verdict CLEAN, exit code 0.

## 4. Attack the detector
Follow PROBES.md: nine specified mutations, each with its expected verdict.
All must behave as specified, including probe 9 (inside tolerance), which
must still pass CLEAN.

## 5. Reproduce the historical cracks
The original contradiction is reproducible against detector v1.0:
  python3 diff-tool/versions/diff-v1.0.py clauses/pilot-001 sealed/pilot-001.json \
      results/track-m/pilot-001-2026-09-23.json results/track-c/pilot-001-2026-09-23.json
Expect: exactly one contradiction, numeric_tolerance TRACK_DIVERGENCE.
The NaN hole is reproducible against v1.0 and v1.1 (see PROBES.md historical note).

## 6. Read the contradiction history
results/contradictions/pilot-001-2026-09-23.md records the flagged
cross-platform float delta, its isolation, classification, the
judge-approved amendment, the independent audit's findings (NaN hole,
bool/int conflation, both fixed; two stale log statements, corrected),
the v2 re-audit, and the auditor's disclosure.

## 7. Check the timeline
results/pilot-001-gold-evidence.md lists all four runs with SHA-256 hashes
and precision notes on what "recomputable" does and does not mean.

## Honest limits of this verification
- Executor blindness is attested by executor reports, not cryptographically
  proven. For a deterministic suite the executor cannot tailor output anyway.
- This pilot proves the machinery on easy ground. The real test is the first
  clause where the executor could actually drift: non-deterministic or
  judgment-based work.
