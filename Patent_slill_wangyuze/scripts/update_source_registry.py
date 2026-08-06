#!/usr/bin/env python3
"""Refresh the patent-database source registry from CNIPA/PatentDatabases."""

import argparse
import hashlib
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


UPSTREAM_REPO = "https://github.com/CNIPA/PatentDatabases"
UPSTREAM_README = "https://raw.githubusercontent.com/CNIPA/PatentDatabases/master/README.md"


def fetch_readme(url=UPSTREAM_README):
    request = urllib.request.Request(url, headers={"User-Agent": "medtech-patent-roadmap/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def classify_source(name, url, section):
    lowered = f"{name} {url}".lower()
    if section == "classification":
        if any(token in lowered for token in ("cnipa", "jpo", "espacenet", "epo", "incopat")):
            return "classification_authority_or_navigator", "classification_navigation"
        return "classification_navigator", "classification_navigation"
    if any(token in lowered for token in ("pubmed", "cnki", "wanfang", "nstl", "duxiu")):
        return "literature_or_context", "context_only"
    official_tokens = (
        "cnipa", "cponline", "ipd.gov.hk", "tipo.gov.tw", "economia.gov.mo",
        "epo", "espacenet", "eapo", "aripo", "patentscope", "wipo", "kipris",
        "j-platpat", "uspto", "ipindia", "inpi.gov", "cipo.ic.gc.ca", "ipo.gov",
        "ipos.gov.sg", "patentstyret", "prv.se", "ige.ch", "oepm.es", "inpi.fr",
        "patentamt", "patent.gov", "iponz", "ipthailand", "gov.uk",
    )
    if any(token in lowered for token in official_tokens):
        return "official_or_authority", "primary_or_status_check"
    commercial_tokens = (
        "incopat", "patentics", "zhihuiya", "himmpat", "innojoy", "patenthub",
        "uyanip", "rainpat", "baiten", "patyee", "soopat", "patentstar",
        "thomson", "derwent", "questel", "totalpatent", "patbase", "patentcloud",
        "wips", "delphion", "dialog", "freepatentsonline", "ip.com", "rpxcorp",
        "jpds", "stn.org", "cas.org", "micropat", "patseer", "patanalyse",
        "lens.org", "sumobrain", "surechem",
    )
    if any(token in lowered for token in commercial_tokens):
        return "commercial_or_aggregator", "discovery_and_cross_check"
    return "public_or_national_database", "discovery_and_cross_check"


def parse_sources(markdown):
    section = None
    records = []
    pattern = re.compile(r"^\d+\.\s*(.+?)：<([^>]+)>")
    for line in markdown.splitlines():
        title = line.strip()
        if title == "## 国内篇":
            section = "domestic"
            continue
        if title == "## 国外篇":
            section = "international"
            continue
        if title == "# 分类号检索":
            section = "classification"
            continue
        match = pattern.match(line)
        if not match or section is None:
            continue
        name, url = match.groups()
        name = " ".join(name.split())
        url = url.strip()
        records.append({"upstream_index": len(records) + 1, "name": name, "url": url, "section": section})
    return records


def deduplicate(records):
    by_url = {}
    for record in records:
        url = record["url"]
        if url not in by_url:
            source_kind, default_use = classify_source(record["name"], url, record["section"])
            by_url[url] = {
                "source_id": f"src-{len(by_url) + 1:03d}",
                "name": record["name"],
                "url": url,
                "source_kind": source_kind,
                "default_use": default_use,
                "listed_in": [],
                "upstream_indices": [],
            }
        item = by_url[url]
        item["listed_in"].append({"section": record["section"], "name": record["name"]})
        item["upstream_indices"].append(record["upstream_index"])
    return list(by_url.values())


def build_registry(markdown):
    records = parse_sources(markdown)
    sources = deduplicate(records)
    section_counts = {section: sum(1 for item in records if item["section"] == section) for section in ("domestic", "international", "classification")}
    kind_counts = {}
    for source in sources:
        kind_counts[source["source_kind"]] = kind_counts.get(source["source_kind"], 0) + 1
    return {
        "schema_version": "1.0",
        "upstream_repo": UPSTREAM_REPO,
        "upstream_readme": UPSTREAM_README,
        "upstream_readme_sha256": hashlib.sha256(markdown.encode("utf-8")).hexdigest(),
        "snapshot_at": datetime.now(timezone.utc).isoformat(),
        "source_policy": {
            "description": "This is a source directory, not an endorsement and not proof that every URL is current or accessible.",
            "official_or_authority": "Use for primary publication, prosecution or legal-status verification when the target jurisdiction is covered.",
            "commercial_or_aggregator": "Use for discovery, normalization, family/citation expansion and cross-checking; do not use alone for legal status.",
            "public_or_national_database": "Use for discovery and jurisdiction-specific cross-checking; verify scope and update date.",
            "literature_or_context": "Use for technical, clinical or background context; it does not establish patent claim coverage.",
            "classification_navigation": "Use to interpret or expand IPC/CPC/FI/ECLA/ICO classifications; confirm the classification definition and version.",
        },
        "counts": {
            "upstream_listings": len(records),
            "unique_urls": len(sources),
            "by_section": section_counts,
            "by_source_kind": kind_counts,
        },
        "sources": sources,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="references/patent-database-sources.json")
    parser.add_argument("--upstream", default=UPSTREAM_README)
    args = parser.parse_args()
    output = Path(args.output).expanduser().resolve()
    registry = build_registry(fetch_readme(args.upstream))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {output}")
    print(json.dumps(registry["counts"], ensure_ascii=False))


if __name__ == "__main__":
    main()
