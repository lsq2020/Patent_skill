#!/usr/bin/env python3
"""Replay the local report pipeline and record deterministic reproducibility evidence."""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_output(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    value.pop("run", None)
    value.pop("reproducibility", None)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    scripts = Path(__file__).resolve().parent
    commands = [
        [sys.executable, str(scripts / "validate_case.py"), "--project-dir", str(project)],
        [sys.executable, str(scripts / "build_modular_reports.py"), "--project-dir", str(project)],
        [sys.executable, str(scripts / "build_case_output.py"), "--project-dir", str(project)],
        [sys.executable, str(scripts / "validate_output_schema.py"), "--output", str(project / "case-output.json")],
    ]
    snapshot_dir = project / "reproducibility-runs"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    runs = []
    for index in range(1, max(args.runs, 1) + 1):
        steps = []
        for command in commands:
            completed = subprocess.run(command, cwd=str(scripts.parent), capture_output=True, text=True)
            steps.append({
                "command": " ".join(command),
                "returncode": completed.returncode,
                "stdout_tail": completed.stdout[-1200:],
                "stderr_tail": completed.stderr[-1200:],
            })
        output_path = project / "case-output.json"
        snapshot_path = snapshot_dir / f"case-output-run-{index}.json"
        if output_path.exists():
            snapshot_path.write_text(output_path.read_text(encoding="utf-8"), encoding="utf-8")
        runs.append({
            "run": index,
            "success": all(step["returncode"] == 0 for step in steps) and output_path.exists(),
            "steps": steps,
            "canonical_case_output_sha256": hashlib.sha256(canonical_output(output_path).encode("utf-8")).hexdigest() if output_path.exists() else None,
            "snapshot": str(snapshot_path.relative_to(project)) if snapshot_path.exists() else None,
        })
    hashes = [row["canonical_case_output_sha256"] for row in runs if row["canonical_case_output_sha256"]]
    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_dir": str(project),
        "requested_runs": args.runs,
        "runs": runs,
        "stable_canonical_output": bool(hashes) and len(set(hashes)) == 1,
        "output_sha256": sha256(project / "case-output.json") if (project / "case-output.json").exists() else None,
        "note": "Network retrieval is not replayed here; source access and browser/manual failures remain in case-output.json.",
    }
    output = project / "reproducibility-report.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["stable_canonical_output"] and all(row["success"] for row in runs) else 1)


if __name__ == "__main__":
    main()
