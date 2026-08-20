#!/usr/bin/env python3
"""Time each pipeline script for a case and report per-module latency.

Runs the standard case-build sequence via subprocess (same mechanism as
run_reproducibility.py / run_source_pipeline.py - see those for the pattern)
and records wall-clock duration per step to <project>/benchmark-report.json,
plus a summary printed to stdout. Steps that don't apply to a case (no
fto-input.json, no *-patent-families.csv yet) are skipped, not failed, so the
FTO and landscape modules stay optional exactly like they are everywhere else
in this Skill.

Usage:
    python3 benchmark_pipeline.py --project-dir <case-dir>
    python3 benchmark_pipeline.py --project-dir <case-dir> \
        --dataset-input <case-dir>/dataset-input.json --prefix mycase
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def timed_run(label, command, cwd):
    start = time.perf_counter()
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    duration = time.perf_counter() - start
    return {
        "module": label,
        "command": " ".join(command),
        "duration_seconds": round(duration, 3),
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-800:],
        "stderr_tail": completed.stderr[-800:],
    }


def iter_steps(project, scripts, args):
    """Yield (label, command) lazily so file-existence checks (fto-input.json,
    *-patent-families.csv) run right before that step - not all upfront, which
    would miss files that earlier steps in this same sequence just created
    (e.g. build_datasets.py writing *-patent-families.csv for build_landscape_v2)."""
    py = sys.executable
    if args.dataset_input:
        yield ("build_datasets", [py, str(scripts / "build_datasets.py"), "--project-dir", str(project), "--input", args.dataset_input, "--prefix", args.prefix])
    yield ("validate_case", [py, str(scripts / "validate_case.py"), "--project-dir", str(project)])
    yield ("build_query_matrix", [py, str(scripts / "build_query_matrix.py"), "--project-dir", str(project)])
    if not args.skip_fto and (project / "fto-input.json").exists():
        yield ("build_fto_plan", [py, str(scripts / "build_fto_plan.py"), "--project-dir", str(project)])
        yield ("score_fto_candidates", [py, str(scripts / "score_fto_candidates.py"), "--project-dir", str(project)])
        yield ("build_fto_dashboard", [py, str(scripts / "build_fto_dashboard.py"), "--project-dir", str(project)])
    families_csv = sorted(project.glob("*-patent-families.csv"))
    if not args.skip_landscape and families_csv:
        yield ("build_landscape_v2", [py, str(scripts / "build_landscape_v2.py"), "--families", str(families_csv[0]), "--output", str(project / f"{project.name}-landscape-v2.html"), "--title", project.name, "--as-of", datetime.now().strftime("%Y-%m-%d")])
    yield ("build_modular_reports", [py, str(scripts / "build_modular_reports.py"), "--project-dir", str(project)])
    yield ("validate_all", [py, str(scripts / "validate_all.py"), "--project-dir", str(project)])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--dataset-input", help="Optional dataset-input.json for build_datasets.py.")
    parser.add_argument("--prefix", default="case", help="CSV filename prefix passed to build_datasets.py.")
    parser.add_argument("--skip-fto", action="store_true", help="Skip build_fto_plan/score_fto_candidates/build_fto_dashboard even if fto-input.json exists.")
    parser.add_argument("--skip-landscape", action="store_true", help="Skip build_landscape_v2.py.")
    args = parser.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    scripts = Path(__file__).resolve().parent

    results = []
    total_start = time.perf_counter()
    for label, command in iter_steps(project, scripts, args):
        print(f"[benchmark] running {label} ...", file=sys.stderr)
        result = timed_run(label, command, cwd=str(scripts.parent))
        results.append(result)
        status = "ok" if result["returncode"] == 0 else f"FAILED (exit {result['returncode']})"
        print(f"[benchmark] {label}: {result['duration_seconds']}s - {status}", file=sys.stderr)
    total_duration = round(time.perf_counter() - total_start, 3)

    report = {
        "project_dir": str(project),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "steps": results,
        "total_duration_seconds": total_duration,
        "success": all(r["returncode"] == 0 for r in results),
    }
    (project / "benchmark-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "summary_seconds": {r["module"]: r["duration_seconds"] for r in results},
        "total_duration_seconds": total_duration,
        "success": report["success"],
        "report_file": str(project / "benchmark-report.json"),
    }, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["success"] else 1)


if __name__ == "__main__":
    main()
