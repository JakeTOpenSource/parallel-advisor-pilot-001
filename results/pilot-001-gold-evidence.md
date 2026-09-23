# Gold evidence packet: pilot-001

Clause: pilot-001, version 1.0.0.
Procedure hash (run.sh + seeds.json + suite.py): `a5077f2f7373dc95d789e6dfd379ac41fcc3f7233e103e154bf8abd4cb34e9e6`
Seed registry hash: `78226a72d8a997ac7edd5f3040d3318dd6481fb386239f7df202626a902b2981`
Both hashes verified independently on every run below against the advisor's
sealed expectations and recomputed procedure files.

## The four runs

| Track | Run | Executor | Exit | Tests | result.json SHA-256 | Archive |
|---|---|---|---|---|---|---|
| M | 1 | blind subagent (Ed side) | 0 | 5/5 pass | ea421cc4a39084babb82a4618c386b949079ada07255ffa345ae0e0d7ef0ba48 | results/track-m/pilot-001-2026-09-23.json |
| M | 2 | blind subagent (Ed side) | 0 | 5/5 pass | 8e95f7c19fee64c082e9e33090802e0ffa20e098e7058817d4709f35758e0c89 | results/track-m/pilot-001-2026-09-23-run2.json |
| C | 1 | Claude Code (Jacob side, win32/py3.14.6) | 0 | 5/5 pass | be8a1848c1d4d487803db8be07fb2cc9fe20abe7ccd901a01bbe25906685256c | results/track-c/pilot-001-2026-09-23.json |
| C | 2 | Claude Code (Jacob side, win32/py3.14.6) | 0 | 5/5 pass | 9d22248e6917bfb0b5ab1668584f187a173f94b7fa34020c25589c618b8c89da | results/track-c/pilot-001-2026-09-23-run2.json |

Track C run files are byte-exact: each archived SHA-256 matches the hash the
executor reported for its own output file, confirming lossless relay.
Track C run 2 was preceded by a byte-for-byte integrity check of all five
public files against a fresh extraction of the original bundle: no differences.

## Sealed verification

Both tracks, both runs: all five tests pass, all observed values within the
clause's declared tolerances, procedure and seed hashes match sealed values.
No sealed expectation was visible to either executor during its run.

## Self-repeat (same machine, same platform)

- M run 1 vs M run 2: observed values bit-identical. Diff CLEAN.
- C run 1 vs C run 2: observed values bit-identical; the two files differ only
  in the informational timestamps. Diff CLEAN.
- The cross-platform float delta in T3 (-0.012909906458835394 on Linux vs
  -0.012909906458835949 on Windows) is stable across runs on each machine:
  a fixed platform property, not drift.

## Cross-track agreement

Amended detector (judge-approved 2026-09-23, honors declared numeric
tolerances): CLEAN on run-1 pair and on run-2 pair.

## Contradiction history

One item, fully processed under the contradiction protocol:
results/contradictions/pilot-001-2026-09-23.md. The pre-amendment detector
flagged the 5.55e-16 T3 delta as TRACK_DIVERGENCE. Isolated to libm `sin`
differences (glibc vs Windows CRT) across 1000 summed terms. Classified
DETECTOR-SPEC (primary: detector stricter than the clause's own 1e-9
tolerance) and PREMISE (secondary: bit-identical cross-platform floats was
never a safe premise). Procedure, model, and executor error ruled out.
After the judge-approved amendment, the detector was re-challenged with four
tamper probes (beyond-tolerance value, forged procedure hash, flipped canary,
cross-track beyond-tolerance): all four caught. Nothing was averaged away;
the false positive was fixed at the detector, not hidden.

## Clause hardening

The platform reproducibility note is now part of the public clause
(clauses/pilot-001/README.md): cross-platform agreement is within tolerance
by design; same-machine runs must reproduce exactly.

## Standing by for the judge

Evidence is complete: two green tracks, each self-reproducing, agreeing
within declared tolerances, with one contradiction found, classified, logged,
and resolved by judge-approved amendment. Gold status is the judge's alone
to mint.

## Independent audit, 2026-09-23 (Claude Code, Track C machine)

The judge ordered an independent audit via verify-pilot-001.zip. Verdict:
the gold claim HOLDS as scoped. All six verification steps produced their
expected outcomes; every archived hash matched; both Track C archives were
byte-identical to the executor's retained outputs.

Findings (all verified by the advisor against its own files before acting):

1. Detector hole, real: NaN in any numeric observed field passed as CLEAN,
   because abs(nan - x) > tol is always False. Also, Python's True == 1 let
   an integer 1 pass as boolean true. Neither affects pilot-001's evidence
   (all values were independently reproduced), but both falsified the general
   "detector catches tampering" claim. Fixed in diff.py the same day:
   non-finite numeric values now raise NON_FINITE_VALUE, and boolean fields
   must be JSON booleans on both sides. Re-validated: both real pairs still
   CLEAN; NaN, Infinity, int-for-bool, and all four original tamper probes
   caught; inside-tolerance values still pass.
2. Stale log statements, real: the contradiction log cited suite.py line 60
   (correct: line 63), and its "re-serialization" note about the Track M
   run-1 archive was false. The auditor verified the archive is byte-faithful
   (SHA-256 ea421cc4a39084babb82a4618c386b949079ada07255ffa345ae0e0d7ef0ba48,
   native key order). The advisor wrote the false note from a misremembered
   read; it is struck and corrected in the log, with the lesson recorded:
   verify file claims with hashes before writing them into the record.
3. Auditor disclosure: Claude has now seen the sealed values and must not
   serve as a blind executor for pilot-001 again. Future Track C reruns need
   a fresh blind executor or an explicit non-blind re-run designation.

After these fixes the v1 verify bundle (bundles/verify-pilot-001.zip) was
rebuilt in place so it reflected the current detector and log. That practice
was superseded the same day: the standing rule is now never rebuild history
in place (see diff-tool/versions/MANIFEST.md). verify-pilot-001-v2.zip
complies with the rule, shipping all three detector versions side by side
with their hashes.

## Precision notes (auditor feedback, 2026-09-23)

On "recomputable": the sealed values are derivable by anyone from the public
procedure, bit-exact on the same platform family (the archived Track M
result files in this bundle match the sealed values field-for-field; a
Windows machine cannot independently re-derive the Linux libm float total,
it can only confirm the archived Linux value sits 5.55e-16 inside the 1e-9
tolerance), within the declared tolerances across platforms (the
Windows float total differs by 5.55e-16 against a 1e-9 tolerance).
"Recomputable" does not mean bit-identical everywhere, and the gold claim
does not require it. The clause promises agreement within tolerance across
platforms and exact repeat on the same machine; both hold.

On "timestamped": the sealed file's mtime predates the first run, which is
consistent with sealed-before-execution but weak evidence on its own
(mtimes are forgeable). The load-bearing evidence is recomputability: any
post-hoc tailoring of the sealed values would still have to equal what the
public code computes, which anyone can check.

## Independent re-audit (bundle v2), 2026-09-23

Claude re-verified verify-pilot-001-v2.zip end to end on the Track C machine
(Windows 11, Python 3.14.6): all three detector hashes match MANIFEST.md,
live diff.py is byte-identical to v1.2, v1.1 is byte-identical to the v1
bundle's live tool, sealed/clause/result files unchanged from v1, all seven
VERIFY.md steps pass, all nine PROBES.md probes return their specified
verdicts and kinds, both historical cracks reproduce against their named
versions, and five extra auditor-added bite tests (string "true", null,
-Infinity, extra list element, extra field) were all caught. Verdict: the
gold claim holds; the only defects were documentary, and they are corrected
in this packet, in the contradiction log's status line, and in PROBES.md's
historical note. verify-pilot-001-v3.zip = v2 with those documentary
corrections only; every executable file is byte-identical between the two
bundles.

## Mint

Minted as gold by the judge (Jacob Tiller) on 2026-09-23.

Accepted state:
- Clause pilot-001 v1.0.0, procedure hash a5077f2f7373dc95d789e6dfd379ac41fcc3f7233e103e154bf8abd4cb34e9e6
- Four green runs: M1 ea421cc4a39084babb82a4618c386b949079ada07255ffa345ae0e0d7ef0ba48, M2 8e95f7c19fee64c082e9e33090802e0ffa20e098e7058817d4709f35758e0c89, C1 be8a1848c1d4d487803db8be07fb2cc9fe20abe7ccd901a01bbe25906685256c, C2 9d22248e6917bfb0b5ab1668584f187a173f94b7fa34020c25589c618b8c89da
- Detector v1.2 (6d52f9653439a521e55b45286c83b711aaf36de7646c66ef16b68514d11aa1a6), CLEAN on both run pairs
- Contradiction log: one cross-platform float delta (5.55e-16), classified DETECTOR-SPEC (primary) / PREMISE (secondary), resolved by judge-approved amendment
- Independent audits: results/audits/audit-pilot-001.md and results/audits/audit-pilot-001-v2.md, gold claim holds on every executable check
- Public receipts: https://github.com/JakeTOpenSource/parallel-advisor-pilot-001
