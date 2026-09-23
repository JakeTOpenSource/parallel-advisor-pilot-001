# Detector versions (SHA-256)

Kept so every historical finding stays reproducible. A log entry names the
version it reproduces against; the live tool is always the newest.

- v1.0 `5c28b250888097a2bf4df1b790c2ade174a4717ccaba31009de835c974de8c67`
  Original. Cross-track comparison demands exact canonical-JSON equality.
  Reproduces the 2026-09-23 pilot-001 contradiction:
  `python3 diff-tool/versions/diff-v1.0.py clauses/pilot-001 sealed/pilot-001.json results/track-m/pilot-001-2026-09-23.json results/track-c/pilot-001-2026-09-23.json`
  -> 1 contradiction: numeric_tolerance TRACK_DIVERGENCE (5.55e-16).
- v1.1 `062c2c803c4d1869cce33d52c9d14d7263ee2b66c2660349427cec0ac0e7b8ee`
  Judge-approved amendment 2026-09-23: cross-track comparison honors the
  clause's declared numeric tolerances. Run-1 pair -> CLEAN. NaN hole present:
  a NaN in any numeric observed field returns CLEAN under v1.1.
- v1.2 `6d52f9653439a521e55b45286c83b711aaf36de7646c66ef16b68514d11aa1a6`
  Audit hardening 2026-09-23: non-finite numeric values raise
  NON_FINITE_VALUE; boolean fields must be JSON booleans on both sides
  (True == 1 no longer passes). Live as diff-tool/diff.py.

Rule (standing): never rebuild history in place. New detector versions are
added alongside the old; log entries cite the version they reproduce against.
