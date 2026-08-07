#!/usr/bin/env python3
"""Build independent, evidence-bounded reports for each patent-analysis module."""

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

try:
    from build_report_visuals import build_visuals
except ImportError:  # pragma: no cover - keeps the report script usable as a library
    build_visuals = None

try:
    from build_report_pages import build_pages
except ImportError:  # pragma: no cover
    build_pages = None

try:
    from build_case_output import build_case_output
    from build_graph_data import build_graph_data
    from build_knowledge_graph import build_knowledge_graph
except ImportError:  # pragma: no cover
    build_case_output = None
    build_graph_data = None
    build_knowledge_graph = None


REPORTS = [
    ("00-executive-summary.md", "执行摘要", "summary"),
    ("01-extraction-report.md", "权利要求与要素抽取报告", "extraction"),
    ("02-patent-family-map-report.md", "专利族地图报告", "family_map"),
    ("03-technology-roadmap-report.md", "技术路线图报告", "technology_roadmap"),
    ("04-risk-and-fto-report.md", "风险与 FTO 报告", "risk_fto"),
    ("05-innovation-space-report.md", "创新空间假设报告", "innovation_space"),
    ("06-evidence-chain-report.md", "证据链报告", "evidence_chain"),
    ("07-source-catalog-report.md", "来源目录报告", "source_catalog"),
]


def load_json(path, default=None):
    if not path.exists():
        return default if default is not None else {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path):
    if not path or not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [{str(k).strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(handle)]


def load_jsonl(path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({"raw": line, "parse_error": True})
    return rows


def first_match(project, pattern):
    matches = sorted(project.glob(pattern))
    return matches[0] if matches else None


def compact(value, limit=420):
    value = " ".join(str(value or "").split())
    return value if len(value) <= limit else value[: limit - 1] + "…"


def md(value):
    return str(value or "—").replace("|", "\\|").replace("\n", "<br>")


def table(headers, rows):
    lines = ["| " + " | ".join(md(x) for x in headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(md(x) for x in row) + " |" for row in rows)
    return "\n".join(lines)


def link(label, url):
    return f"[{label}]({url})" if url else str(label or "—")


def source_link(row, label=None):
    return link(label or row.get("document_no") or "来源", row.get("source_url", ""))


def pct(value):
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return "—"


def priority_sort(row):
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    try:
        score = -float(row.get("screen_score") or 0)
    except ValueError:
        score = 0
    return order.get(row.get("review_priority", "LOW"), 9), score


def heading(title, level=2):
    return f"{'#' * level} {title}\n"


def scope_block(scope, identity, catalog):
    obj = scope.get("research_object", {})
    jurisdictions = ", ".join(scope.get("jurisdictions", [])) or "未指定"
    related = ", ".join(scope.get("related_jurisdictions", [])) or "无"
    counts = catalog.get("counts", {})
    return "\n".join([
        f"- **研究对象**：{obj.get('molecule', '未指定')}；别名：{', '.join(obj.get('synonyms', [])) or '未记录'}",
        f"- **靶点/机制**：{obj.get('target', '未指定')}",
        f"- **适应症**：{obj.get('indication', '未指定')}",
        f"- **法域**：目标法域 {jurisdictions}；关联扩展法域 {related}",
        f"- **截至日期**：{scope.get('as_of', '未指定')}",
        f"- **深度**：{scope.get('depth', '未指定')}；报告语言：{scope.get('report_language', 'zh')}",
        f"- **来源目录**：上游记录 {counts.get('upstream_listings', '—')} 条，去重 URL {counts.get('unique_urls', '—')} 个；目录不是已访问结果集。",
        f"- **申请人消歧**：{', '.join(identity.get('applicants', [])) or '未提供；需从族记录反向归一化'}",
    ])


def family_stage(family):
    text = " ".join([
        family.get("claim_theme", ""), family.get("claim_categories", ""),
        family.get("key_claim_elements", ""), family.get("mutation_or_biomarker", ""),
    ]).lower()
    has_combo = any(token in text for token in ("combination", "regimen", "method of treatment", "联合", "给药"))
    has_patient_selection = any(token in text for token in ("patient selection", "biomarker", "diagnostic", "标志物", "诊断"))
    if any(token in text for token in ("composition", "antibody", "sequence", "compound", "化合物", "抗体")):
        return "结构/组成与核心实体"
    if any(token in text for token in ("formulation", "制剂", "excipient", "晶型", "salt")):
        return "制剂/盐型/工艺"
    if has_combo and has_patient_selection:
        return "联合治疗/患者分层"
    if has_patient_selection:
        return "生物标志物/诊断/患者分层"
    if any(token in text for token in ("regimen", "combination", "method", "治疗", "联合", "给药")):
        return "治疗用途/联合/给药方案"
    return "邻近技术/待归类"


def claim_status(coverage):
    if coverage in ("明确披露", "explicit", "explicitly_disclosed"):
        return "独立权利要求/claim 记录明确披露"
    if coverage in ("可能覆盖", "possible", "potential"):
        return "可能相关，但需完整 claim chart"
    if coverage in ("未见披露", "not_seen"):
        return "当前记录未见披露"
    return coverage or "待核验"


def common_header(title, case, scope, identity, catalog, generated):
    return "\n".join([
        f"# {title}",
        "",
        f"> 案例：`{case}` · 生成时间：{generated} · 本报告为研究资料，不构成法律意见。",
        "",
        "## 研究范围",
        "",
        scope_block(scope, identity, catalog),
        "",
    ])


def visual_block(files, chart_ids):
    """Embed generated SVGs in Markdown while keeping an interactive hub link."""
    manifest = files.get("visual_manifest") or {}
    chart_map = {item.get("id"): item for item in manifest.get("charts", [])}
    selected = [chart_map[chart_id] for chart_id in chart_ids if chart_id in chart_map]
    if not selected:
        return ""
    lines = ["## 统计可视化", "", "[打开 FTO 风格统计总览](report-visuals.html) · 图表由当前案例 CSV/JSON 自动生成。", ""]
    for chart in selected:
        lines.extend([
            f"### {chart.get('title', chart.get('id', '图表'))}",
            "",
            f"![{chart.get('title', chart.get('id', '图表'))}](visuals/{chart.get('filename')})",
            "",
            f"> 统计口径：{chart.get('metric_definition', '—')}",
            "",
        ])
    return "\n".join(lines).rstrip()


def render_summary(case, scope, identity, families, claims, evidence, ranking, plan, catalog, files):
    top = sorted(ranking, key=priority_sort)[:5]
    gaps = plan.get("gaps", [])
    lines = [common_header("执行摘要", case, scope, identity, catalog, files["generated"]), "## 模块化交付", ""]
    lines.append("本案例将事实抽取、族地图、技术路线、风险/FTO、创新空间和证据链拆成独立报告。每份报告可以单独阅读，也可以通过 `report-index.md` 回到同一组结构化数据。")
    lines += ["", "## 数据规模", "", table(["指标", "数量/状态", "说明"], [
        ["专利族", len(families), "以案例族 CSV 的 family_id 为统计单位"],
        ["claim 要素记录", len(claims), "逐条保留文献号、claim 类别、位置和 coverage"],
        ["证据链条目", len(evidence), "事实、推断、来源、定位和复核动作"],
        ["FTO 候选", len(ranking), "排序是复核优先级，不是侵权概率"],
        ["检索轮次", len(plan.get("search_rounds", [])), "由 FTO/query plan 生成的可恢复策略"],
        ["来源目录", catalog.get("counts", {}).get("unique_urls", "—"), "可选来源 URL，不代表本案已全部访问"],
    ]), "", "## 当前最重要的信号", ""]
    for row in top:
        family = next((f for f in families if f.get("family_id") == row.get("family_id")), {})
        lines.append(f"- **{row.get('review_priority', '—')} · {row.get('family_id')}**：{family.get('claim_theme', row.get('relevance', '—'))}；完整命中特征 {row.get('matched_features') or '无'}；部分命中 {row.get('partial_features') or '无'}；{source_link(row, row.get('representative_document', '代表文献'))}。")
    lines += ["", "## 最大证据缺口", ""]
    for gap in gaps[:12]:
        lines.append(f"- {gap}")
    lines += ["", visual_block(files, ["family-theme", "priority-year", "risk-priority"])]
    lines += ["", "## 独立报告索引", ""]
    for filename, title, _ in REPORTS[1:]:
        lines.append(f"- [{title}]({filename})")
    lines += ["", "## 结论边界", "", "本摘要不把摘要命中、聚合网站状态或模型推断升级为权利要求覆盖、有效性或 FTO 结论。正式实施前，优先核验目标法域的完整独立权利要求、国家阶段、分案/继续申请、审查档案和法律事件。"]
    return "\n".join(lines) + "\n"


def render_extraction(case, scope, identity, families, claims, evidence, plan, catalog, files):
    lines = [common_header("权利要求与要素抽取报告", case, scope, identity, catalog, files["generated"]), "## 1. 抽取方法与口径", "", "本报告只描述从当前结构化数据中抽取到的事实。`明确披露`、`可能覆盖`、`未见披露`和`待核验`分别保留；摘要/说明书内容不会自动等同于独立权利要求。", "", "## 2. 权利要求要素清单", ""]
    claim_rows = []
    for row in claims:
        claim_rows.append([
            row.get("family_id"), source_link(row, row.get("document")), row.get("claim_category"), compact(row.get("element"), 340),
            claim_status(row.get("coverage")), row.get("claim_location"), row.get("confidence"),
        ])
    lines.append(table(["专利族", "文献", "类别", "抽取要素", "覆盖标记", "定位", "置信度"], claim_rows or [["—"] * 7]))
    lines += ["", visual_block(files, ["claim-category", "applicant", "priority-year"])]
    lines += ["", "## 3. 结构、组成和保护对象", "", "结构字段按现有族/claim 数据可见内容整理；如果只有功能性或文本描述，不补写未采集的化学结构。", ""]
    structure_rows = []
    for family in families:
        structure_rows.append([family.get("family_id"), family.get("representative_document"), family_stage(family), compact(family.get("key_claim_elements"), 440), family.get("mutation_or_biomarker") or "未记录", family.get("claim_categories")])
    lines.append(table(["族", "代表文献", "抽取主题", "结构/组成/功能要素", "突变/标志物", "claim 类别"], structure_rows or [["—"] * 6]))
    lines += ["", "## 4. 申请人、受让人和发明人", ""]
    applicant_rows = []
    for family in families:
        applicant_rows.append([family.get("family_id"), family.get("applicant_or_assignee"), family.get("inventors"), family.get("jurisdictions"), family.get("source_url") and link("来源", family.get("source_url"))])
    lines.append(table(["族", "申请人/受让人", "发明人", "法域", "来源"], applicant_rows or [["—"] * 5]))
    lines += ["", "## 5. 时间线抽取", "", "以下时间是族级记录中的日期快照；它不是对当前有效性的判断。分案、继续申请和国家阶段若未在输入 CSV 单独建模，标记为需要补检。", ""]
    timeline_rows = []
    for family in sorted(families, key=lambda r: r.get("earliest_priority", "9999")):
        timeline_rows.append([family.get("family_id"), family.get("earliest_priority"), family.get("publication_date"), family.get("status_as_of"), family.get("official_status"), family.get("status_source")])
    lines.append(table(["族", "最早优先权", "公开日", "状态截至", "状态快照", "状态来源"], timeline_rows or [["—"] * 6]))
    lines += ["", "## 6. 抽取质量与缺口", ""]
    missing = []
    for family in families:
        if not family.get("mutation_or_biomarker"):
            missing.append(f"{family.get('family_id')}：未建立突变/标志物字段记录")
        if not family.get("grants"):
            missing.append(f"{family.get('family_id')}：未记录授权号，需查目标法域官方登记簿")
        if "public mirror" in family.get("status_source", "").lower():
            missing.append(f"{family.get('family_id')}：状态主要来自公开镜像，需官方核验")
    for item in missing + plan.get("gaps", []):
        lines.append(f"- {item}")
    lines += ["", "## 7. 抽取字段字典", "", table(["字段层", "字段", "解释"], [
        ["权利要求", "claim_category / element / coverage", "保护对象和要素的初步结构化记录"],
        ["族", "family_id / family_definition", "族口径及族内关系说明"],
        ["主体", "applicant_or_assignee / inventors", "申请人、受让人和发明人快照"],
        ["时间", "earliest_priority / publication_date / status_as_of", "时间线和状态快照"],
        ["证据", "claim_location / evidence_url / confidence", "可回溯定位和可信度"],
    ])]
    return "\n".join(lines) + "\n"


def render_family_map(case, scope, identity, families, plan, catalog, files):
    lines = [common_header("专利族地图报告", case, scope, identity, catalog, files["generated"]), "## 1. 族口径", "", "本报告按输入数据中的 `family_id` 统计，并保留 `family_definition`。若同时需要 DOCDB simple family 与 INPADOC extended family，应分别建字段和分别统计，不能混合去重。", "", "## 2. 专利族总览", ""]
    rows = []
    for family in sorted(families, key=lambda r: r.get("earliest_priority", "9999")):
        rows.append([family.get("family_id"), family.get("family_definition"), link(family.get("representative_document"), family.get("source_url")), family.get("earliest_priority"), family.get("applicant_or_assignee"), family.get("jurisdictions"), family.get("claim_categories"), family.get("official_status"), family.get("status_confidence")])
    lines.append(table(["族", "族定义", "代表文献", "最早优先权", "申请人", "法域", "claim 类别", "状态快照", "置信度"], rows or [["—"] * 9]))
    lines += ["", visual_block(files, ["family-theme", "priority-year", "jurisdiction", "applicant"])]
    lines += ["", "## 3. 主题关联图", "", "下图是“研究对象—筛选到的专利族—技术主题”关联图，不把不同 `family_id` 之间强行画成继承或同族关系。正式族关系应进一步补录 priority/continuity/member 边。", "", "```mermaid", "flowchart LR", "  Q[研究对象/技术方案]"]
    for idx, family in enumerate(families, start=1):
        node = f"F{idx}"
        label = compact(f"{family.get('family_id')} · {family_stage(family)}", 70).replace('"', "'")
        lines.append(f"  Q --> {node}[\"{label}\"]")
    lines += ["```", "", "## 4. 优先权时间泳道数据", "", table(["族", "最早优先权", "公开日", "代表文献", "后续关系/待补检"], [[f.get("family_id"), f.get("earliest_priority"), f.get("publication_date"), link(f.get("representative_document"), f.get("source_url")), "分案/继续申请/国家阶段需逐项核验"] for f in families] or [["—"] * 5]), "", "## 5. 法域矩阵", ""]
    jurisdictions = sorted({x.strip() for f in families for x in f.get("jurisdictions", "").split(";") if x.strip()})
    matrix = []
    for family in families:
        present = {x.strip() for x in family.get("jurisdictions", "").split(";") if x.strip()}
        matrix.append([family.get("family_id")] + ["有记录" if j in present else "未见成员记录" for j in jurisdictions])
    lines.append(table(["族"] + jurisdictions, matrix or [["—"]]))
    lines += ["", "## 6. 地图解读与限制", "", "- 族数反映当前数据集中的去重结果，不反映商业价值、市场份额或有效专利数量。", "- `official_status` 是输入快照；没有目标法域官方来源时，必须进入状态复核队列。", "- 代表文献不能替代族内成员清单；国家阶段、分案和继续申请可能有不同 claim 范围。"]
    return "\n".join(lines) + "\n"


def render_roadmap(case, scope, identity, families, claims, plan, catalog, files, roadmap_path):
    lines = [common_header("技术路线图报告", case, scope, identity, catalog, files["generated"]), "## 1. 路线分层", "", "本报告把研发/技术事实与专利保护层分开：专利记录说明“文本和 claim 保护了什么”，论文、临床或产品资料才能说明“技术走到了哪里”。当前没有外部研发资料时，不补写临床阶段。", "", "## 2. 技术路线图", "", "```mermaid", "flowchart LR", "  Need[疾病/未满足需求] --> Mechanism[靶点与作用机制]"]
    lines.extend([
        "  Mechanism --> Structure[结构/组成与核心实体]",
        "  Structure --> Use[治疗用途/联合/给药方案]",
        "  Structure --> Formulation[制剂/盐型/工艺]",
        "  Use --> Selection[患者分层/诊断/耐药]",
    ])
    stages = []
    for idx, family in enumerate(families, start=1):
        stage = family_stage(family)
        stages.append((family, stage))
        node = f"R{idx}"
        label = compact(f"{family.get('family_id')}\\n{stage}", 70).replace('"', "'")
        stage_node = {"结构/组成与核心实体": "Structure", "制剂/盐型/工艺": "Formulation", "治疗用途/联合/给药方案": "Use", "联合治疗/患者分层": "Selection", "生物标志物/诊断/患者分层": "Selection"}.get(stage, "Use")
        lines.append(f"  {stage_node} --> {node}[\"{label}\"]")
    lines += ["```", "", "> 图中顺序是由主题字段生成的分析路线，不是申请人明确披露的研发先后；需要用日期、实施例、临床注册或公司披露进一步验证。", "", "## 3. 路线节点—专利族—证据", ""]
    route_rows = []
    for family, stage in stages:
        route_rows.append([family.get("family_id"), stage, family.get("claim_theme"), family.get("claim_categories"), compact(family.get("key_claim_elements"), 320), family.get("earliest_priority"), family.get("status_confidence")])
    lines.append(table(["族", "路线阶段", "技术主题", "claim 类别", "关键要素", "最早优先权", "状态置信度"], route_rows or [["—"] * 7]))
    lines += ["", visual_block(files, ["family-theme", "claim-category", "priority-year"])]
    lines += ["", "## 4. 路线演化观察", ""]
    stage_counts = {}
    for _, stage in stages:
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    for stage, count in stage_counts.items():
        lines.append(f"- **{stage}**：{count} 个族/分支进入当前样本；需要继续区分核心保护与邻近技术。")
    if roadmap_path and roadmap_path.exists():
        lines += ["", "## 5. 案例已有路线材料", "", f"已有路线草稿：[{roadmap_path.name}]({roadmap_path.name})。它可作为人工补充材料，但本报告的族—路线映射仍以结构化 CSV/证据链为准。"]
    lines += ["", "## 6. 技术断点与补检", "", "- 核心结构/抗体或化合物与用途之间是否存在独立保护层，需按 claim 类别逐族核对。", "- 联合/剂量/患者分层是否形成独立权利要求，不能只由说明书或临床事实推断。", "- 耐药、标志物和诊断节点若没有直接 family/claim 证据，应保留为补检缺口。", "- 制剂、盐型/晶型、工艺或安全窗节点需要结构/组成字段和实施例支持。"]
    return "\n".join(lines) + "\n"


def render_risk(case, scope, identity, families, claims, ranking, plan, catalog, files):
    family_map = {f.get("family_id"): f for f in families}
    claim_map = {}
    for claim in claims:
        claim_map.setdefault(claim.get("family_id"), []).append(claim)
    lines = [common_header("风险与 FTO 报告", case, scope, identity, catalog, files["generated"]), "## 1. 风险边界", "", "本报告识别的是值得继续核验的重叠信号和 FTO 工作队列，不是侵权、不侵权、有效性或自由实施法律意见。排序分数只代表复核优先级。", "", "## 2. 拟实施方案与特征分级", "", plan.get("technical_solution", "未记录"), ""]
    feature_rows = []
    for feature in plan.get("features", []):
        feature_rows.append([feature.get("id"), feature.get("feature_type"), feature.get("importance"), feature.get("text"), ", ".join(feature.get("keyword_clusters", [])), ", ".join(feature.get("classifications", [])) or "—"])
    lines.append(table(["ID", "类型", "重要性", "技术特征", "词簇", "IPC/CPC"], feature_rows or [["—"] * 6]))
    lines += ["", "## 3. FTO 候选族排序", ""]
    risk_rows = []
    for row in sorted(ranking, key=priority_sort):
        family = family_map.get(row.get("family_id"), {})
        risk_rows.append([
            row.get("review_priority"), row.get("family_id"), source_link(row, row.get("representative_document")), family.get("claim_theme", row.get("relevance")),
            pct(row.get("screen_score")), row.get("matched_features") or "无", row.get("partial_features") or "无", row.get("claim_categories"),
            row.get("official_status_signal") or family.get("official_status"), row.get("status_source") or family.get("status_source"),
        ])
    lines.append(table(["优先级", "族", "代表文献", "主题", "排序分数", "完整命中", "部分命中", "claim 类别", "状态信号", "状态来源"], risk_rows or [["—"] * 10]))
    lines += ["", visual_block(files, ["risk-priority", "status", "claim-category"])]
    lines += ["", "## 4. 逐族 claim 要素风险", ""]
    for row in sorted(ranking, key=priority_sort):
        family_id = row.get("family_id")
        family = family_map.get(family_id, {})
        lines.append(f"### {family_id} · {row.get('review_priority', '—')} · {family.get('representative_document', row.get('representative_document', '—'))}")
        lines.append("")
        lines.append(f"- **触发事实**：{compact(family.get('claim_theme', row.get('relevance')), 360)}；完整命中 `{row.get('matched_features') or '无'}`；部分命中 `{row.get('partial_features') or '无'}`。")
        lines.append(f"- **状态限制**：{compact(row.get('official_status_signal') or family.get('official_status'), 360)}；来源：{row.get('status_source') or family.get('status_source') or '未记录'}。")
        claim_summary = "; ".join(compact(f"{c.get('claim_category')}: {c.get('element')}", 220) for c in claim_map.get(family_id, [])) or "未建立逐条 claim 记录"
        lines.append(f"- **claim 记录**：{claim_summary}。")
        lines.append("- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。")
        lines.append("")
    lines += ["## 5. 风险雷达", "", table(["风险层", "触发条件", "当前判断", "必须补证据"], [
        ["高复核优先", "核心对象、机制/用途和独立 claim 要素同时命中", "进入 claim chart 队列，不等同于侵权", "完整独立 claim + 官方状态 + 实施方案映射"],
        ["中复核优先", "主题或必要特征部分命中，法域/状态不完整", "保留为重叠信号", "国家阶段、分支、审查档案"],
        ["边界候选", "相邻通路、诊断或竞争方案，缺少对象级 claim linkage", "用于召回和创新空间，不计入核心 FTO", "对象特异性 claim、更多检索入口"],
    ]), "", "## 6. FTO 结论边界", "", "当前数据不足以确认自由实施或侵权。若要进入商业决策，应先对高优先族逐项制作 claim chart，并由目标法域专利律师复核法律状态和解释问题。"]
    return "\n".join(lines) + "\n"


def render_innovation(case, scope, identity, families, claims, ranking, evidence, plan, catalog, files):
    family_map = {f.get("family_id"): f for f in families}
    claim_by_family = {}
    for claim in claims:
        claim_by_family.setdefault(claim.get("family_id"), []).append(claim)
    lines = [common_header("创新空间假设报告", case, scope, identity, catalog, files["generated"]), "## 1. 使用原则", "", "本报告只提出可验证的创新空间假设。空白表示当前检索集合、字段或法域没有建立充分证据，不表示不存在专利，也不表示可直接实施。", "", "## 2. 假设总表", ""]
    hypotheses = []
    for family in families:
        text = " ".join([family.get("claim_theme", ""), family.get("claim_categories", ""), family.get("key_claim_elements", "")]).lower()
        if "formulation" in text or "制剂" in text:
            direction = "制剂参数、赋形剂、浓度/pH、输注条件或稳定性窗口"
            evidence_text = "制剂/组合物族已进入样本"
        elif any(token in text for token in ("composition", "antibody", "sequence", "compound", "化合物", "抗体")):
            direction = "核心实体的结构、序列、变体、盐型/晶型或选择性/安全窗"
            evidence_text = "核心组成/功能性 claim 记录提供边界"
        elif "biomarker" in text or "diagnostic" in text or "标志物" in text:
            direction = "患者分层、伴随诊断、反应预测和耐药/微环境标志物"
            evidence_text = "标志物/诊断族或邻近族提供入口"
        elif "combination" in text or "regimen" in text or "method" in text:
            direction = "联合治疗、给药顺序、周期、剂量和治疗线次"
            evidence_text = "用途/联合/方案族存在保护布局"
        else:
            direction = "核心实体的结构、序列、变体、盐型/晶型或选择性/安全窗"
            evidence_text = "核心组成/功能性 claim 记录提供边界"
        related_claims = claim_by_family.get(family.get("family_id"), [])
        counter = family.get("notes") or "Markush、分案/继续申请、未公开申请和目标法域状态仍可能改变空白判断。"
        hypotheses.append([
            direction, family.get("family_id"), evidence_text, compact(family.get("key_claim_elements"), 260),
            compact(counter, 240), "补检同族/官方 claim；必要时做结构、制剂、药效或生物标志物实验", "中/待验证",
        ])
    hypotheses.extend([
        ["耐药机制与下一代联合策略", "GAP-RESISTANCE", "当前样本未建立对象特异性耐药核心族", "需要把 B2M、JAK/IFN、抗原呈递、TIL、髓系和替代检查点分层检索", "不能把未搜到写成没有专利；文献机制不等于专利保护", "专利+文献+临床注册三线补检，再做 claim chart", "低/需补检"],
        ["安全窗、免疫相关不良反应监测和处置", "GAP-SAFETY", "当前技术方案包含监测和处置特征，但样本中直接 claim linkage 不足", "监测指标、影像、分级阈值和激素处置可能形成方法/诊断方向", "医疗指南或说明书内容不自动产生专利保护", "逐项检索监测/阈值/处置组合并核对法域 claim", "中/需法律复核"],
    ])
    lines.append(table(["候选方向", "关联族/缺口", "已有依据", "当前技术缺口", "反例", "验证动作", "信心"], hypotheses))
    lines += ["", visual_block(files, ["family-theme", "claim-category", "status"])]
    lines += ["", "## 3. 分维度空白检查", ""]
    lines.append(table(["维度", "当前样本信号", "空白判定", "建议"], [
        ["核心结构/序列/化合物", "见核心组成或抗体/序列方向", "需查 Markush、序列变体和子族", "结构检索+独立 claim 对比"],
        ["盐型/晶型/制剂/工艺", "若有制剂族则存在分层布局", "配方和状态需单独核验", "做组成、工艺、稳定性和制剂 claim chart"],
        ["给药/剂量/联合", "用途、组合和 regimen 族较易出现", "时间、剂量、患者人群可能有边界", "按治疗线次、周期、顺序和联合对象补检"],
        ["患者分层/诊断", "标志物或邻近 ICB 族提供入口", "对象特异性 linkage 可能不足", "检索 biomarker + molecule + indication + claim"],
        ["耐药突变/机制", "需要单独补检，不能用相邻标志物代替", "当前证据不足", "建立机制词表、文献证据和专利族三联表"],
    ]))
    lines += ["", "## 4. 不得越过的结论", "", "- “没有检索到”只能说明当前检索范围没有建立证据。", "- 空白机会必须经结构、药效/制剂/诊断实验和法律复核后才能进入研发决策。", "- 任何方向都要重新检查未公开申请、国家阶段、分案/继续申请、Markush 和官方法律状态。"]
    return "\n".join(lines) + "\n"


def render_evidence(case, scope, identity, families, evidence, plan, catalog, source_log, files):
    lines = [common_header("证据链报告", case, scope, identity, catalog, files["generated"]), "## 1. 证据等级与字段", "", "E1/E2 用于官方登记簿、审查档案和专利文本；E3/E4 用于 WIPO/EPO/USPTO 全球数据、聚合数据库、论文、临床和公司资料；E5 是模型推断或待验证假设。来源角色和证据等级不能混用。", "", "## 2. 证据条目", ""]
    evidence_rows = []
    for row in evidence:
        evidence_rows.append([
            row.get("finding_id"), compact(row.get("conclusion_or_fact"), 360), row.get("evidence_type"), source_link(row, row.get("document_no") or "来源"),
            row.get("claim_or_event_location"), row.get("captured_at"), row.get("direct_fact_or_inference"), row.get("confidence"), row.get("reviewer_action"),
        ])
    lines.append(table(["Finding", "事实/结论", "证据类型", "来源", "定位", "抓取时间", "事实/推断", "置信度", "复核动作"], evidence_rows or [["—"] * 9]))
    lines += ["", visual_block(files, ["evidence-confidence", "evidence-type", "source-kind"])]
    lines += ["", "## 3. 来源日志", ""]
    log_rows = []
    for row in source_log:
        log_rows.append([row.get("captured_at"), row.get("source_id"), row.get("source_type"), link("打开", row.get("source_url", "")), compact(row.get("query"), 280), row.get("document_no"), row.get("result_count"), row.get("decision"), row.get("note")])
    lines.append(table(["时间", "source_id", "类型", "URL", "检索式", "文献号", "结果数", "决定", "备注"], log_rows or [["—"] * 9]))
    lines += ["", "## 4. 模块—证据回溯要求", "", table(["模块", "最低回溯键", "当前责任"], [
        ["抽取", "family_id + document + claim_location", "每条 claim 要素必须有定位和置信度"],
        ["族地图", "family_id + priority_set + member/source", "族口径和国家成员不得只靠标题推断"],
        ["技术路线", "family_id 或 finding_id", "路线节点和边要有来源或标记为推断"],
        ["风险/FTO", "family_id + claim element + jurisdiction status", "排名不能替代完整 claim chart"],
        ["创新空间", "finding_id + gap + counterexample", "每个空白假设必须写反例和验证动作"],
    ]), "", "## 5. 当前证据缺口", ""]
    for gap in plan.get("gaps", []):
        lines.append(f"- {gap}")
    lines += ["", "## 6. 证据使用声明", "", "本报告以可复核为目标，保留公开镜像、机器翻译、国家阶段未核验、文本位置不完整和来源不可访问等不确定性。需要用于商业实施、许可、诉讼或监管的结论，应重新采集目标法域官方证据。"]
    return "\n".join(lines) + "\n"


def render_source_catalog(case, scope, identity, catalog, files):
    lines = [common_header("来源目录报告", case, scope, identity, catalog, files["generated"]), "## 1. 目录说明", "", "该目录来自 CNIPA/PatentDatabases 上游 README 的快照。它是检索入口目录，不是质量背书，也不代表所有网站当前可用。来源必须按角色路由，并在 source-log 中记录实际访问。", "", "## 2. 统计", "", table(["指标", "数值"], [
        ["上游仓库", link("CNIPA/PatentDatabases", catalog.get("upstream_repo"))],
        ["上游 README 哈希", catalog.get("upstream_readme_sha256")],
        ["上游记录数", catalog.get("counts", {}).get("upstream_listings")],
        ["去重 URL 数", catalog.get("counts", {}).get("unique_urls")],
        ["分组", json.dumps(catalog.get("counts", {}).get("by_section", {}), ensure_ascii=False)],
        ["来源角色", json.dumps(catalog.get("counts", {}).get("by_source_kind", {}), ensure_ascii=False)],
    ]), "", "## 3. 使用原则", ""]
    for key, value in (catalog.get("source_policy") or {}).items():
        lines.append(f"- **{key}**：{value}")
    lines += ["", visual_block(files, ["source-kind", "search-round"])]
    lines += ["", "## 4. 完整来源清单", ""]
    rows = []
    for source in catalog.get("sources", []):
        listed = "; ".join(sorted({x.get("section", "") for x in source.get("listed_in", [])}))
        rows.append([source.get("source_id"), source.get("name"), link(source.get("url"), source.get("url")), source.get("source_kind"), source.get("default_use"), listed, ", ".join(map(str, source.get("upstream_indices", [])))])
    lines.append(table(["ID", "名称", "URL", "来源角色", "默认用途", "上游分组", "上游序号"], rows or [["—"] * 7]))
    lines += ["", "## 5. 访问限制", "", "对需登录/验证码/订阅、无法检全库、仅显示著录项、没有全文或链接失效的来源，写入 `pending/manual`，不要填充虚假的结果数量；法律状态仍以目标法域官方登记簿为准。"]
    return "\n".join(lines) + "\n"


def build_reports(project):
    scope = load_json(project / "research_scope.json")
    identity = load_json(project / "identity.json")
    plan = load_json(project / "fto-search-plan.json")
    catalog = plan.get("source_catalog") or load_json(project / "patent-database-sources.json")
    families_path = first_match(project, "*-patent-families.csv")
    claims_path = first_match(project, "*-claim-elements.csv")
    evidence_path = first_match(project, "*-evidence.csv")
    ranking_path = project / "fto-candidate-ranking.csv"
    source_log_path = project / "source-log.jsonl"
    families = load_csv(families_path)
    claims = load_csv(claims_path)
    evidence = load_csv(evidence_path)
    ranking = load_csv(ranking_path)
    source_log = load_jsonl(source_log_path)
    roadmap_path = first_match(project, "*-roadmap.md")
    generated = datetime.now(timezone.utc).isoformat()
    if build_visuals and not (project / "visuals" / "manifest.json").exists():
        build_visuals(project)
    files = {
        "generated": generated,
        "visual_manifest": load_json(project / "visuals" / "manifest.json", {}),
    }
    outputs = {}
    outputs["00-executive-summary.md"] = render_summary(project.name, scope, identity, families, claims, evidence, ranking, plan, catalog, files)
    outputs["01-extraction-report.md"] = render_extraction(project.name, scope, identity, families, claims, evidence, plan, catalog, files)
    outputs["02-patent-family-map-report.md"] = render_family_map(project.name, scope, identity, families, plan, catalog, files)
    outputs["03-technology-roadmap-report.md"] = render_roadmap(project.name, scope, identity, families, claims, plan, catalog, files, roadmap_path)
    outputs["04-risk-and-fto-report.md"] = render_risk(project.name, scope, identity, families, claims, ranking, plan, catalog, files)
    outputs["05-innovation-space-report.md"] = render_innovation(project.name, scope, identity, families, claims, ranking, evidence, plan, catalog, files)
    outputs["06-evidence-chain-report.md"] = render_evidence(project.name, scope, identity, families, evidence, plan, catalog, source_log, files)
    outputs["07-source-catalog-report.md"] = render_source_catalog(project.name, scope, identity, catalog, files)
    index_lines = [f"# {project.name} 模块化报告索引", "", f"> 生成时间：{generated} · 结构化数据目录：`{project}`", "", "## 交互式入口", "", "- [打开专利证据双链图](knowledge-graph.html)", "- [打开交互式统计总览](report-visuals.html)", "- [查看图表数据清单](visuals/manifest.json)", "- [查看图谱质量报告](graph-quality.json)", "", "## 报告清单", ""]
    for filename, title, _ in REPORTS:
        index_lines.append(f"- [{title}]({filename})")
    index_lines += ["", "## 输入与过程数据", "", "- `research_scope.json` / `identity.json`：研究范围和实体消歧", "- `*-patent-families.csv`：族级数据", "- `*-claim-elements.csv`：权利要求要素", "- `*-evidence.csv`：证据链", "- `case-output.json`：稳定 ID 和一等关系边", "- `graph-data.json` / `graph-quality.json`：图谱数据和质量缺口", "- `fto-search-plan.json`：FTO 特征、检索轮次和来源目录", "- `fto-candidate-ranking.csv`：候选排序", "- `source-log.jsonl`：实际访问日志", "- `visuals/`：依赖无外部图库的 SVG 统计图和 manifest", "", "## 总体限制", "", "报告将未核验的国家阶段、聚合状态、缺失 claim 和未采集结构明确标出；不把模块报告升级为法律意见。"]
    outputs["report-index.md"] = "\n".join(index_lines) + "\n"
    for filename, content in outputs.items():
        (project / filename).write_text(content, encoding="utf-8")
    if build_pages:
        build_pages(project)
    graph_quality = {}
    if build_case_output and build_graph_data and build_knowledge_graph:
        build_case_output(project)
        _, graph_quality = build_graph_data(project)
        build_knowledge_graph(project)
        build_case_output(project)
    state_path = project / "state.json"
    state = load_json(state_path, {})
    state.setdefault("reports", {})
    for _, _, key in REPORTS:
        state["reports"][key] = "complete"
    state["reports"]["index"] = "complete"
    state["reports"]["visuals"] = "complete"
    state["reports"]["html_pages"] = "complete"
    state["reports"]["knowledge_graph"] = "complete" if (project / "knowledge-graph.html").exists() else "partial"
    state["graph_quality"] = graph_quality.get("status", "not_generated")
    state["reports_generated_at"] = generated
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    outputs = build_reports(project)
    for filename in outputs:
        print(f"Generated {project / filename}")
    print(json.dumps({"report_count": len(outputs), "case": project.name}, ensure_ascii=False))


if __name__ == "__main__":
    main()
