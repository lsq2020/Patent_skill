# 专利证据双链图规范

## 目的

双链图用于回答“这个族/claim 由什么 finding 支持”和“这个 finding 反向支持哪些族/claim”。它是复核导航，不是用节点距离、大小或颜色表达法律风险。

## 构建顺序

```bash
python scripts/build_case_output.py --project-dir <case-dir>
python scripts/validate_output_schema.py --output <case-dir>/case-output.json
python scripts/build_graph_data.py --project-dir <case-dir>
python scripts/validate_graph_data.py --graph <case-dir>/graph-data.json
python scripts/build_knowledge_graph.py --project-dir <case-dir>
```

`build_modular_reports.py` 会按相同顺序联动执行。

## 节点与关系

核心节点：`research_object`、`target`、`indication`、`patent_family`、`patent_document`、`claim`、`evidence`、`source`、`applicant`、`jurisdiction`、`technology_theme`。

核心边：

```text
IN_SCOPE
HAS_MEMBER
HAS_CLAIM
CLAIMS_DOCUMENT
SUPPORTED_BY
HAS_SOURCE
FILED_BY
FILED_IN
PROTECTS
PRIORITY_TO
NATIONAL_PHASE_OF
DIVISIONAL_OF
CONTINUATION_OF
CONTINUATION_IN_PART_OF
RELATED_TO
```

边只存一次，右侧“反向链接”通过入边动态生成。关系 ID 由 source/type/target 稳定生成。

## 证据口径

- `direct_fact`：关系来自显式结构化字段，使用实线；
- `rule_derived`：关系来自完全匹配的 document_no 或 source_url，使用虚线；
- `model_inference`：模型推断，使用点线，默认构建器不自动产生。

不得从 `notes`、标题相似、申请人相同或日期接近推断族间连续关系。

## 交互

- 专利族视图：族、成员文献、claim、finding、source 和族间关系；
- 技术保护视图：研究对象、靶点、适应症、技术主题、族和 claim；
- 证据链视图：family/claim → finding → source；
- 申请人布局：申请人、族、法域和主题。
- 因果全景视图：以有出处的因果/机制关系为核心，同时展示研究对象、靶点、适应症、专利族、claim、技术主题、finding 与 source。研究对象到因果概念使用 `IN_SCOPE` 结构边，`causal_status=not_applicable`，只表示本 case 的上下文收录，不表示因果。

页面默认使用 URL 状态：`?focus=<node-id>&view=<preset>&depth=1&q=<query>`。默认展开一跳，最多显示 80 个节点；超过限制时必须提示并要求缩小范围。节点检查器包含摘要、Claims、证据、出链和反向链接。

## 质量规则

`graph-quality.json` 至少检查：

- node/edge ID 唯一；
- 无悬空 source/target；
- 所有 claim 有稳定 ID；
- evidence 的 family/claim 关联率；
- 显式专利族连续关系边数量和覆盖情况。
- 因果概念的研究上下文接入率（`causal_context_coverage_rate`）；有因果概念时应为 `1.0`。

质量为 `warning` 时仍可生成视图，但页面必须显示缺口。`error` 表示关系结构不可安全使用，应先修复数据。

## 离线交付

`knowledge-graph.html` 内嵌图数据、样式、交互代码和 Cytoscape.js，不依赖 CDN、Node.js 或后端服务。第三方 Cytoscape.js 版本和许可证保存在 `assets/graph-viewer/`。
