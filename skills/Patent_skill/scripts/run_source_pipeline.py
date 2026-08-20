#!/usr/bin/env python3
"""Sequence the per-case public-source scripts (audit -> search) into one command.

update_source_registry.py refreshes the repo-wide CNIPA/PatentDatabases catalog
(network call, not scoped to a case) - it stays opt-in via --refresh-registry
instead of running on every case. append_source_log.py logs one manual entry at
a time and needs per-entry args (--source-url, --query, ...), so it is not part
of this automated sequence; call it directly when you have a specific record to add.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--refresh-registry", action="store_true", help="Also refresh references/patent-database-sources.json from the upstream CNIPA/PatentDatabases README before auditing.")
    parser.add_argument("--query", default="", help="Optional query override passed through to audit_public_sources.py")
    args = parser.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    scripts = Path(__file__).resolve().parent

    commands = []
    if args.refresh_registry:
        commands.append([sys.executable, str(scripts / "update_source_registry.py")])
    audit_cmd = [sys.executable, str(scripts / "audit_public_sources.py"), "--project-dir", str(project)]
    if args.query:
        audit_cmd += ["--query", args.query]
    commands.append(audit_cmd)
    commands.append([sys.executable, str(scripts / "search_public_sources.py"), "--project-dir", str(project)])

    steps = []
    for command in commands:
        completed = subprocess.run(command, cwd=str(scripts.parent), capture_output=True, text=True)
        steps.append({
            "command": " ".join(command),
            "returncode": completed.returncode,
            "stdout_tail": completed.stdout[-1200:],
            "stderr_tail": completed.stderr[-1200:],
        })
        print(f"[run_source_pipeline] {command[1].rsplit(chr(92), 1)[-1].rsplit('/', 1)[-1]} -> exit {completed.returncode}", file=sys.stderr)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_dir": str(project),
        "steps": steps,
        "success": all(step["returncode"] == 0 for step in steps),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["success"] else 1)


if __name__ == "__main__":
    main()
