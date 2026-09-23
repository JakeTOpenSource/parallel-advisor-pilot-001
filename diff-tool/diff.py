#!/usr/bin/env python3
"""Advisor diff tool for the parallel advisor system.

Verifies result JSON against a sealed clause:
  1. Recomputes procedure_hash from the public clause dir and compares.
  2. Compares each test's observed values against sealed expectations,
     applying declared tolerances to numbers (exact match otherwise).
  3. If two track results are given, diffs them field by field.

Emits a contradiction report (human text plus JSON). Exit 0 when clean,
exit 1 when any contradiction is found. A contradiction is never averaged
away; it is reported for the contradiction protocol.

Usage:
  python3 diff.py <clause_dir> <sealed.json> <result-track-m.json> [<result-track-c.json>]
"""
import hashlib
import json
import math
import os
import sys

PROCEDURE_FILES = ["run.sh", "seeds.json", "suite.py"]


def load(path):
    with open(path) as f:
        return json.load(f)


def recompute_procedure_hash(clause_dir):
    h = hashlib.sha256()
    for name in PROCEDURE_FILES:
        with open(os.path.join(clause_dir, name), "rb") as f:
            h.update(name.encode("utf-8") + b"\x00" + f.read() + b"\x00")
    return h.hexdigest()


def compare_values(expected, observed, tolerance, path, out):
    """Append contradiction dicts to out. Returns nothing."""
    if isinstance(expected, bool) or isinstance(observed, bool):
        # JSON true/false and 1/0 are distinct tokens; never conflate them.
        # Audit finding 2026-09-23: Python's True == 1 let an int 1 pass as
        # boolean true. A boolean field must be a JSON boolean on both sides.
        if not (isinstance(expected, bool) and isinstance(observed, bool)) \
                or expected != observed:
            out.append({"path": path, "kind": "VALUE_MISMATCH",
                        "expected": expected, "observed": observed,
                        "detail": "boolean field must be a JSON boolean"})
        return
    if isinstance(expected, (int, float)) and isinstance(observed, (int, float)):
        # Audit finding 2026-09-23: NaN passed every tolerance because
        # abs(nan - x) > tol is always False. A non-finite observed value is
        # always a contradiction; the suite cannot produce one.
        e, o = float(expected), float(observed)
        if not math.isfinite(e) or not math.isfinite(o):
            out.append({"path": path, "kind": "NON_FINITE_VALUE",
                        "expected": expected, "observed": observed})
            return
        tol = tolerance if tolerance is not None else 0.0
        if abs(e - o) > tol:
            out.append({"path": path, "kind": "VALUE_MISMATCH",
                        "expected": expected, "observed": observed,
                        "tolerance": tol,
                        "delta": abs(e - o)})
        return
    if isinstance(expected, list) and isinstance(observed, list):
        if len(expected) != len(observed):
            out.append({"path": path, "kind": "LENGTH_MISMATCH",
                        "expected_len": len(expected),
                        "observed_len": len(observed)})
            return
        for i, (e, o) in enumerate(zip(expected, observed)):
            compare_values(e, o, tolerance, "%s[%d]" % (path, i), out)
        return
    if isinstance(expected, dict) and isinstance(observed, dict):
        for key, e in expected.items():
            if key not in observed:
                out.append({"path": path + "." + key, "kind": "MISSING_FIELD"})
            else:
                compare_values(e, observed[key], tolerance,
                               path + "." + key, out)
        for key in observed:
            if key not in expected:
                out.append({"path": path + "." + key, "kind": "UNEXPECTED_FIELD"})
        return
    if expected != observed:
        out.append({"path": path, "kind": "VALUE_MISMATCH",
                    "expected": expected, "observed": observed})


def check_one(result, sealed, clause_dir, label):
    contradictions = []
    expectations = sealed["expectations"]

    if result.get("schema_version") != 1:
        contradictions.append({"path": "<envelope>", "kind": "SCHEMA_MISMATCH",
                               "detail": "schema_version != 1"})
    if result.get("suite_id") != sealed["suite_id"]:
        contradictions.append({"path": "<envelope>", "kind": "SUITE_MISMATCH"})
    if result.get("clause_version") != sealed["clause_version"]:
        contradictions.append({"path": "<envelope>", "kind": "CLAUSE_VERSION_MISMATCH",
                               "expected": sealed["clause_version"],
                               "observed": result.get("clause_version")})

    if result.get("procedure_hash") != recompute_procedure_hash(clause_dir):
        contradictions.append({"path": "procedure_hash",
                               "kind": "PROCEDURE_TAMPER",
                               "detail": "result's procedure hash does not match "
                                         "the advisor's public clause files"})
    if result.get("seed_registry_hash") != expectations["procedure_integrity"]["observed"]["seeds_sha256"]:
        contradictions.append({"path": "seed_registry_hash",
                               "kind": "SEED_TAMPER",
                               "detail": "seeds.json hash differs from sealed value"})

    by_id = {t["test_id"]: t for t in result.get("results", [])}
    for test_id, exp in expectations.items():
        if test_id not in by_id:
            contradictions.append({"path": test_id, "kind": "MISSING_TEST"})
            continue
        t = by_id[test_id]
        if t.get("status") != "pass":
            contradictions.append({"path": test_id, "kind": "TEST_NOT_PASS",
                                   "observed_status": t.get("status"),
                                   "notes": t.get("notes", "")})
            continue
        tols = exp.get("tolerances", {})
        obs = t.get("observed", {})
        for key, e_val in exp["observed"].items():
            if key not in obs:
                contradictions.append({"path": "%s.%s" % (test_id, key),
                                       "kind": "MISSING_FIELD"})
                continue
            compare_values(e_val, obs[key], tols.get(key),
                           "%s.%s" % (test_id, key), contradictions)
        for key in obs:
            if key not in exp["observed"]:
                contradictions.append({"path": "%s.%s" % (test_id, key),
                                       "kind": "UNEXPECTED_FIELD"})
    for c in contradictions:
        c["track"] = label
    return contradictions


def diff_tracks(ra, rb, sealed):
    """Diff two tracks' observed values, honoring the clause's declared tolerances.

    Amendment 2026-09-23 (judge-approved): numeric fields are compared with the
    clause's declared tolerances, mirroring check_one semantics, instead of
    demanding exact equality. Non-numeric fields still require exact match.
    Rationale: the 2026-09-23 pilot-001 contradiction (5.55e-16 libm sin delta
    across Linux/Windows) was flagged as TRACK_DIVERGENCE by exact comparison
    while sitting a million times inside the clause's own 1e-9 tolerance. The
    detector was stricter than the spec it serves. Logged under
    results/contradictions/pilot-001-2026-09-23.md, classified DETECTOR-SPEC.
    """
    contradictions = []
    expectations = sealed.get("expectations", {})
    ba = {t["test_id"]: t.get("observed", {}) for t in ra.get("results", [])}
    bb = {t["test_id"]: t.get("observed", {}) for t in rb.get("results", [])}
    for test_id in sorted(set(ba) | set(bb)):
        if test_id not in ba:
            contradictions.append({"path": test_id, "kind": "TRACK_DIVERGENCE",
                                   "detail": "present in track C, missing in track M"})
            continue
        if test_id not in bb:
            contradictions.append({"path": test_id, "kind": "TRACK_DIVERGENCE",
                                   "detail": "present in track M, missing in track C"})
            continue
        tols = expectations.get(test_id, {}).get("tolerances", {})
        oa, ob = ba[test_id], bb[test_id]
        for key in sorted(set(oa) | set(ob)):
            if key not in oa:
                contradictions.append({"path": "%s.%s" % (test_id, key),
                                       "kind": "TRACK_DIVERGENCE",
                                       "detail": "field present in track C, missing in track M"})
                continue
            if key not in ob:
                contradictions.append({"path": "%s.%s" % (test_id, key),
                                       "kind": "TRACK_DIVERGENCE",
                                       "detail": "field present in track M, missing in track C"})
                continue
            sub = []
            compare_values(oa[key], ob[key], tols.get(key),
                           "%s.%s" % (test_id, key), sub)
            for c in sub:
                c["kind"] = "TRACK_DIVERGENCE"
                c["track_m_value"] = oa[key]
                c["track_c_value"] = ob[key]
                contradictions.append(c)
    return contradictions


def main(argv):
    if len(argv) not in (4, 5):
        print(__doc__)
        return 2
    clause_dir, sealed_path = argv[1], argv[2]
    sealed = load(sealed_path)
    results = [(load(argv[3]), os.path.basename(argv[3]))]
    if len(argv) == 5:
        results.append((load(argv[4]), os.path.basename(argv[4])))

    all_contradictions = []
    for result, label in results:
        all_contradictions.extend(check_one(result, sealed, clause_dir, label))
    if len(results) == 2:
        all_contradictions.extend(diff_tracks(results[0][0], results[1][0], sealed))

    report = {
        "suite_id": sealed["suite_id"],
        "clause_version": sealed["clause_version"],
        "tracks_checked": [r[0].get("track", "?") for r in results],
        "contradictions": all_contradictions,
        "verdict": "CLEAN" if not all_contradictions else "CONTRADICTION",
    }
    print(json.dumps(report, indent=2))
    if all_contradictions:
        print("\nContradictions found: %d. Nothing is averaged away; "
              "each item enters the contradiction protocol." % len(all_contradictions))
        return 1
    print("\nClean: all hashes verified, all values within tolerance, tracks agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
