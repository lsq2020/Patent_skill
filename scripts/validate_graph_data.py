#!/usr/bin/env python3
"""Validate graph-data.json without third-party packages."""

import argparse
import json
from pathlib import Path


def duplicates(values):
    seen = set()
    result = set()
    for value in values:
        if value in seen:
            result.add(value)
        seen.add(value)
    return sorted(result)


def validate(graph):
    errors = []
    for key in ("schema_version", "meta", "nodes", "edges", "facets", "presets", "legend"):
        if key not in graph:
            errors.append(f"missing top-level key: {key}")
    if graph.get("schema_version") != "1.1":
        errors.append("schema_version must be 1.1")
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if not isinstance(nodes, list):
        errors.append("nodes must be an array")
        nodes = []
    if not isinstance(edges, list):
        errors.append("edges must be an array")
        edges = []
    node_ids = [row.get("id") for row in nodes]
    for value in duplicates(node_ids):
        errors.append(f"duplicate node id: {value}")
    for row in nodes:
        for key in ("id", "type", "label", "properties", "facets"):
            if key not in row:
                errors.append(f"node {row.get('id', 'unknown')} missing {key}")
    node_id_set = set(node_ids)
    edge_ids = [row.get("id") for row in edges]
    for value in duplicates(edge_ids):
        errors.append(f"duplicate edge id: {value}")
    for row in edges:
        edge_id = row.get("id", "unknown")
        for key in (
            "id",
            "source",
            "target",
            "type",
            "assertion",
            "relation_kind",
            "causal_status",
            "polarity",
            "directness",
            "evidence_level",
            "confidence",
        ):
            if not row.get(key):
                errors.append(f"edge {edge_id} missing {key}")
        if row.get("source") not in node_id_set:
            errors.append(f"edge {edge_id} has dangling source: {row.get('source')}")
        if row.get("target") not in node_id_set:
            errors.append(f"edge {edge_id} has dangling target: {row.get('target')}")
        if row.get("assertion") not in {"direct_fact", "rule_derived", "model_inference"}:
            errors.append(f"edge {edge_id} has invalid assertion")
        if row.get("relation_kind") not in {
            "structural",
            "evidentiary",
            "causal",
            "mechanistic",
            "associative",
            "temporal",
        }:
            errors.append(f"edge {edge_id} has invalid relation_kind")
        if row.get("relation_kind") in {"causal", "mechanistic"}:
            if not row.get("evidence_ids"):
                errors.append(f"causal edge requires evidence_ids: {edge_id}")
            if not row.get("source_urls"):
                errors.append(f"causal edge requires source_urls: {edge_id}")
            if not str(row.get("rationale") or "").strip():
                errors.append(f"causal edge requires rationale: {edge_id}")
    meta = graph.get("meta", {})
    if meta.get("node_count") != len(nodes):
        errors.append("meta.node_count does not match nodes")
    if meta.get("edge_count") != len(edges):
        errors.append("meta.edge_count does not match edges")
    preset_ids = [row.get("id") for row in graph.get("presets", [])]
    for value in duplicates(preset_ids):
        errors.append(f"duplicate preset id: {value}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", required=True)
    args = parser.parse_args()
    path = Path(args.graph).expanduser().resolve()
    try:
        graph = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    errors = validate(graph)
    print(json.dumps({"valid": not errors, "graph": str(path), "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
