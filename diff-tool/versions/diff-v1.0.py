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
        if expected is not observed and expected != observed:
            out.append({"path": path, "kind": "VALUE_MISMATCH",
                        "expected": expected, "observed": observed})
        return
    if isinstance(expected, (int, float)) and isinstance(observed, (int, float)):
        tol = tolerance if tolerance is not None else 0.0
        if abs(float(expected) - float(observed)) > tol:
            out.append({"path": path, "kind": "VALUE_MISMATCH",
                        "expected": expected, "observed": observed,
                        "tolerance": tol,
                        "delta": abs(float(expected) - float(observed))})
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


def diff_tracks(ra, rb):
    contradictions = []
    ba = {t["test_id"]: t.get("observed", {}) for t in ra.get("results", [])}
    bb = {t["test_id"]: t.get("observed", {}) for t in rb.get("results", [])}
    for test_id in sorted(set(ba) | set(bb)):
        if test_id not in ba:
            contradictions.append({"path": test_id, "kind": "TRACK_DIVERGENCE",
                                   "detail": "present in track C, missing in track M"})
        elif test_id not in bb:
            contradictions.append({"path": test_id, "kind": "TRACK_DIVERGENCE",
                                   "detail": "present in track M, missing in track C"})
        elif json.dumps(ba[test_id], sort_keys=True) != json.dumps(bb[test_id], sort_keys=True):
            contradictions.append({"path": test_id, "kind": "TRACK_DIVERGENCE",
                                   "detail": "observed values differ between tracks",
                                   "track_m": ba[test_id], "track_c": bb[test_id]})
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
        all_contradictions.extend(diff_tracks(results[0][0], results[1][0]))

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
