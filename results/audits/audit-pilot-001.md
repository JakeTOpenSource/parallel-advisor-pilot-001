# Independent audit: pilot-001 gold claim

Auditor: Claude Code, Track C machine (Windows 11, Python 3.14.6, Git Bash). Date: 2026-09-23.
Bundle: verify-pilot-001.zip (16,547 bytes), 14 files. A SHA-256 manifest of the extracted bundle was
recorded immediately after extraction and re-checked after every step: all 14 files unchanged throughout.
Every mutation and every run.sh invocation was done in a separate working copy.

Disclosure: the auditor was the Track C executor for runs 1 and 2. Both runs were delivered and hashed
before this bundle (which contains the sealed values) was opened. The auditor has now seen the sealed
values and must not be used as a blind executor for pilot-001 again.

## Step 0: extraction
Extracted cleanly. Contents match the zip listing: VERIFY.md, sealed/pilot-001.json, diff-tool/diff.py,
clauses/pilot-001/{README.md, result.json, run.sh, seeds.json, suite.py}, results/track-m/{run1, run2},
results/track-c/{run1, run2}, results/contradictions/pilot-001-2026-09-23.md, results/pilot-001-gold-evidence.md.
The bundle's run.sh, seeds.json and suite.py are byte-identical to the executor's original pilot-001 copies.
The bundle README.md adds one section (platform reproducibility note); nothing else differs.

## Step 1: recompute the answers from the public procedure alone
Command: `bash run.sh M` in a working copy of clauses/pilot-001 (the step as written overwrites result.json,
so it was not run inside the bundle). Exit 0, stdout `wrote result.json`, stderr empty.
Comparison of the fresh output against sealed/pilot-001.json:

| field | exact match | delta | tolerance | within tolerance |
|---|---|---|---|---|
| seeded_rng.values | yes | 0.0 | 1e-12 | yes |
| deterministic_sort.joined | yes | | | yes |
| numeric_tolerance.total | NO | 5.551115123125783e-16 | 1e-9 | yes |
| canary_reject.rejected | yes | | | yes |
| procedure_integrity.seeds_sha256 | yes | | | yes |

seed_registry_hash equals the sealed seeds_sha256. procedure_hash a5077f2f...e9e6.
Result: MATCHES within the clause's declared tolerances. On this platform the sealed T3 value is not
bit-reproducible; it is bit-identical to both Track M (Linux) outputs, consistent with the sealed file having
been derived from the public code on Linux. Bit-exact recomputation of the sealed file was only possible for
4 of 5 fields here.

## Step 2: verify the procedure was never changed
Exact command from VERIFY.md. Output: a5077f2f7373dc95d789e6dfd379ac41fcc3f7233e103e154bf8abd4cb34e9e6
Expected: a5077f2f7373dc95d789e6dfd379ac41fcc3f7233e103e154bf8abd4cb34e9e6. MATCHES.

## Step 3: re-run the advisor's full check (run-2 pair)
Exact command from VERIFY.md. Output: tracks_checked [M, C], contradictions [], verdict CLEAN,
"Clean: all hashes verified, all values within tolerance, tracks agree." Exit 0. MATCHES.

## Step 4: attack the detector
Each probe: copy of results/track-c/pilot-001-2026-09-23-run2.json, one change, re-run of step 3 with the mutant
in the Track C slot.

Prescribed by VERIFY.md (expect CONTRADICTION, exit 1):

| probe | exit | verdict | contradictions | matches expectation |
|---|---|---|---|---|
| a. total + 1e-6 | 1 | CONTRADICTION | VALUE_MISMATCH (delta 9.999999994e-07, tol 1e-9) + TRACK_DIVERGENCE | yes |
| b. procedure_hash = 64 zeroes | 1 | CONTRADICTION | PROCEDURE_TAMPER | yes |
| c. canary rejected = false | 1 | CONTRADICTION | VALUE_MISMATCH + TRACK_DIVERGENCE | yes |

Auditor-added probes (beyond VERIFY.md):

| probe | exit | verdict | assessment |
|---|---|---|---|
| x2. total + 1e-10 (inside tolerance) | 0 | CLEAN | correct: within declared tolerance |
| x3. canary status "fail" (value unchanged) | 1 | CONTRADICTION (TEST_NOT_PASS) | caught |
| x5. total = Infinity | 1 | CONTRADICTION | caught |
| x1. total = NaN | 0 | CLEAN | NOT CAUGHT |
| x6. seeded_rng.values[0] = NaN | 0 | CLEAN | NOT CAUGHT |
| x4. canary rejected = 1 (int) | 0 | CLEAN | NOT CAUGHT (minor) |

x1 also passes in the single-track form (check_one alone, no cross-track diff): verdict CLEAN, exit 0.
Mechanism, demonstrated directly: `abs(nan - x) > 1e-9` is False for every tolerance, so compare_values
never appends a contradiction for a NaN observed value; `True == 1` in Python, so an int 1 satisfies the
boolean branch. NaN is not strict JSON but Python's json.load accepts it by default, which is what diff.py uses.
suite.py cannot produce NaN from this computation, so the pilot-001 evidence is unaffected; the hole matters
for the gold packet's "detector catches tampering" claim and for reuse of diff.py on real clauses.

## Step 5: the historical contradiction
Read results/contradictions/pilot-001-2026-09-23.md. Claims checked:
- Delta: |-0.012909906458835394 - (-0.012909906458835949)| = 5.551115123125783e-16. Confirmed.
- Run-1 pair under the bundled (amended) detector: verdict CLEAN, exit 0. Consistent with the amendment.
  The pre-amendment behaviour (exactly one TRACK_DIVERGENCE) cannot be reproduced from this bundle because
  only the amended diff.py ships; the amendment is documented in the diff_tracks docstring.
- Isolation to math.sin via libm: consistent with step 1 (Windows recompute reproduces the Track C value exactly,
  Linux archives carry the sealed value exactly).
- "suite.py line 60": inaccurate. The fsum expression is on line 63.
- "The saved Track M result file is a re-serialization ... environment before seed_registry_hash": does not
  match the bundled file. results/track-m/pilot-001-2026-09-23.json has suite.py's native key order, a trailing
  newline, and is identical to the M run-2 archive apart from timestamps. Its SHA-256 is
  ea421cc4a39084babb82a4618c386b949079ada07255ffa345ae0e0d7ef0ba48; the gold table lists no hash for it.
  Either the note is stale or the archive was replaced after the note was written. Values are correct either way.

## Step 6: timeline
| file | SHA-256 | gold table | match |
|---|---|---|---|
| track-m run2 | 8e95f7c19fee64c082e9e33090802e0ffa20e098e7058817d4709f35758e0c89 | same | yes |
| track-c run1 | be8a1848c1d4d487803db8be07fb2cc9fe20abe7ccd901a01bbe25906685256c | same | yes, and byte-identical to the executor's retained copy |
| track-c run2 | 9d22248e6917bfb0b5ab1668584f187a173f94b7fa34020c25589c618b8c89da | same | yes, and byte-identical to the executor's retained copy |
| clauses/pilot-001/result.json | 8e95f7c1... | | same bytes as the M run-2 archive |

Zip mtimes: sealed 14:27, procedure files 14:27, M run1 14:28 (in-file 18:28:02Z), C run1 14:54, M run2 14:59,
C run2 15:01. Sealed precedes the first run by about one minute on mtimes, which VERIFY.md correctly calls weak
evidence. The strong evidence is step 1.
Line endings: both Track C archives contain 63 CR bytes (Windows Python text-mode stdout emits CRLF), which is
why they are 1624 bytes against 1561 for Track M. JSON parsing is unaffected. Cross-platform "byte-exact"
comparison of result files is therefore never possible; per-platform hash relay checks remain valid.

## Environment notes (auditor's machine, not bundle defects)
Two false starts: the first extraction went to a temp folder whose path exceeded Windows' 260-character limit,
and the desktop app's packaged-process filesystem virtualisation made absolute paths invisible to the Python
launcher. Both were resolved by re-extracting to a shorter path and using cwd-relative paths. Neither touched
the bundle. One extra probe (x2) first failed for the same path-length reason and was rerun under a short name.

## Verdict
The gold claim HOLDS under independent verification as scoped by VERIFY.md. All six steps produced the
expected outcomes: the procedure hash reproduces; the sealed values are derivable from the public code (bit-exact
for four fields, within declared tolerance for the platform-dependent fifth); the run-2 pair is CLEAN; all three
prescribed tamper probes are caught; every archived hash matches; the Track C archives are byte-identical to the
executor's own retained outputs.

Single weakest point found: diff.py treats NaN as inside every tolerance. A result file with NaN in any numeric
observed field passes the sealed check and the cross-track check with verdict CLEAN, exit 0. This does not
affect pilot-001's evidence, whose values were reproduced here, but it falsifies the general statement that the
detector catches tampering, and it should be closed (reject non-finite observed values; load JSON with a
parse_constant that raises) before diff.py is reused on a real clause. Lesser items: bool/int conflation (x4),
and two stale statements in the contradiction log (line 60 citation; the Track M run-1 re-serialisation note).
