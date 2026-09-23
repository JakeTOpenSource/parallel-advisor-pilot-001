# Independent re-audit: pilot-001 gold claim, bundle v2

Auditor: Claude Code, Track C machine (Windows 11, Python 3.14.6, Git Bash). Date: 2026-09-23.
Bundle: verify-pilot-001-v2.zip (29,448 bytes), 19 files. A SHA-256 manifest was recorded at extraction and
re-checked at the end: all 19 files unchanged. All mutations and the run.sh invocation were done in separate
working copies. Disclosure unchanged: the auditor has seen the sealed values and is not a blind executor for pilot-001.

## Detector version hashes vs diff-tool/versions/MANIFEST.md
| file | SHA-256 | manifest | match |
|---|---|---|---|
| versions/diff-v1.0.py | 5c28b250888097a2bf4df1b790c2ade174a4717ccaba31009de835c974de8c67 | same | yes |
| versions/diff-v1.1.py | 062c2c803c4d1869cce33d52c9d14d7263ee2b66c2660349427cec0ac0e7b8ee | same | yes, and identical to the v1 bundle's live diff.py |
| versions/diff-v1.2.py | 6d52f9653439a521e55b45286c83b711aaf36de7646c66ef16b68514d11aa1a6 | same | yes |
| diff.py (live) | 6d52f9653439a521e55b45286c83b711aaf36de7646c66ef16b68514d11aa1a6 | = v1.2 | yes |

Continuity: sealed/pilot-001.json, the five clause files, and all four result archives are byte-identical to the
v1 bundle (checked against the v1 manifest recorded in the first audit).

Code review of the version diffs: v1.0 to v1.1 replaces canonical-JSON equality in diff_tracks with
tolerance-aware compare_values. v1.1 to v1.2 adds math.isfinite gating (NON_FINITE_VALUE) before the numeric
tolerance test and requires both sides of a boolean field to be JSON booleans. Both changes do what the
manifest says and nothing else.

## VERIFY.md steps
| step | result | as specified |
|---|---|---|
| 1. recompute from public code | exit 0; 4 of 5 fields bit-exact; float total delta 5.551115123125783e-16 vs tol 1e-9 | yes (VERIFY.md now states within-tolerance across platforms) |
| 2. procedure hash | a5077f2f7373dc95d789e6dfd379ac41fcc3f7233e103e154bf8abd4cb34e9e6 | yes |
| 3. live v1.2 on run-2 pair | CLEAN, exit 0 | yes |
| 4. nine probes | see below | yes, all nine |
| 5. historical cracks | see below | yes |
| 6. contradiction log | read; correction and struck note present; line 63 fixed | see stale items |
| 7. gold evidence timeline | hashes M2 8e95f7c1..., C1 be8a1848..., C2 9d22248e... all match files | see stale items |

## PROBES.md, nine probes against v1.2
| # | mutation | exit | verdict | kinds | as specified |
|---|---|---|---|---|---|
| 1 | total += 1e-6 | 1 | CONTRADICTION | VALUE_MISMATCH | yes |
| 2 | procedure_hash = 64 zeroes | 1 | CONTRADICTION | PROCEDURE_TAMPER | yes |
| 3 | rejected = false | 1 | CONTRADICTION | VALUE_MISMATCH | yes |
| 4 | total = NaN | 1 | CONTRADICTION | NON_FINITE_VALUE | yes |
| 5 | values[0] = NaN | 1 | CONTRADICTION | NON_FINITE_VALUE | yes |
| 6 | rejected = 1 | 1 | CONTRADICTION | VALUE_MISMATCH | yes |
| 7 | total = Infinity | 1 | CONTRADICTION | NON_FINITE_VALUE | yes |
| 8 | probe 4, two-track | 1 | CONTRADICTION | NON_FINITE_VALUE + TRACK_DIVERGENCE | yes |
| 9 | total += 1e-10 | 0 | CLEAN | none | yes |

Auditor-added bite tests on v1.2, all caught: rejected = "true" (string) VALUE_MISMATCH; rejected = null
VALUE_MISMATCH; total = -Infinity NON_FINITE_VALUE; extra element in values LENGTH_MISMATCH; extra observed
key UNEXPECTED_FIELD.

## Historical cracks
| detector | input | exit | verdict | as specified |
|---|---|---|---|---|
| v1.0 | run-1 pair | 1 | CONTRADICTION, exactly one: numeric_tolerance TRACK_DIVERGENCE | yes |
| v1.1 | probe-4 mutant (NaN total) | 0 | CLEAN | yes, the crack stays visible |
| v1.1 | probe-5 mutant (NaN in list) | 0 | CLEAN | matches historical note |
| v1.0 and v1.1 | probe-6 mutant (int for bool) | 0 | CLEAN | matches historical note |
| v1.1 and v1.2 | run-1 pair | 0 | CLEAN | consistent with amendment |
| v1.0 | run-2 pair | 1 | TRACK_DIVERGENCE | expected, same values as run 1 |
| v1.0 | probe-4 mutant (NaN total) | 0 | CLEAN | not stated in PROBES.md; the NaN hole predates v1.1 |

## Items that do not match the record (none affect the verdict)
1. gold-evidence.md, four-runs table: the Track M run-1 row still reads "(re-serialized archive; values faithful)".
   The contradiction log's own correction says that claim was false and gives the hash
   ea421cc4a39084babb82a4618c386b949079ada07255ffa345ae0e0d7ef0ba48. The table was not updated to match
   the correction. This is the exact class of error the recorded lesson is about, carried into the rebuilt packet.
2. contradictions log, Status section: still ends "Awaiting run-2 results; then final diff and gold evidence".
   Run-2 results, the audit, and v1.2 all postdate that sentence. Stale.
3. gold-evidence.md, Independent audit section: says the bundle "was rebuilt ... so it always reflects the
   current detector and log: bundles/verify-pilot-001.zip". That describes the v1 rebuild and conflicts with the
   MANIFEST.md standing rule "never rebuild history in place". The v2 bundle itself complies with the rule; the
   sentence should say so or be dated. The referenced bundles/ path does not exist in this bundle.
4. PROBES.md historical note attributes the NaN hole to v1.1 only. Verified: v1.0 has it too. Incomplete, not wrong.
5. gold-evidence.md precision note claims Linux/glibc reproduces all five sealed fields exactly. Consistent with
   the Linux archives matching the sealed value bit-for-bit, but not independently verifiable on this Windows machine.

## Verdict
Bundle v2 behaves as specified on every executable check: three version hashes match the manifest, the live tool
is v1.2, seven VERIFY.md steps pass, all nine PROBES.md probes give their specified verdict and kind, and both
historical cracks reproduce against their named detector versions. The gold claim holds. The only defects are
documentary: one uncorrected table cell and one stale status line in the evidence packet, plus two wording items.
