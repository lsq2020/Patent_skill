# 模块化报告规范

## 目录

1. [交付结构](#交付结构)
2. [抽取报告](#抽取报告)
3. [专利族地图报告](#专利族地图报告)
4. [技术路线图报告](#技术路线图报告)
5. [风险与 FTO 报告](#风险与-fto-报告)
6. [创新空间报告](#创新空间报告)
7. [证据链报告](#证据链报告)
8. [总报告与状态](#总报告与状态)

## 交付结构

每个案例默认生成以下独立 Markdown 报告、FTO 风格 HTML 页面和统计图，并用 `report-index.md` / `report-index.html` 统一索引：

```text
00-executive-summary.md       # 结论入口和证据边界
01-extraction-report.md       # 权利要求、结构、申请人、时间线、路线要素抽取
02-patent-family-map-report.md
03-technology-roadmap-report.md
04-risk-and-fto-report.md
05-innovation-space-report.md
06-evidence-chain-report.md
07-source-catalog-report.md   # 来源目录、访问限制和来源路由
report-index.md
report-index.html
report-visuals.html
case-output.json
graph-data.json
graph-quality.json
knowledge-graph.html
visuals/
  *.svg
  manifest.json
```

每份报告必须独立可读：开头写研究对象、法域、截至日期、数据版本和限制；表格中的每个关键结论绑定 `family_id`、`document_no` 或 `finding_id`；没有证据的内容写成“未建立/待补检/待官方核验”。

### 统一 FTO 风格和统计图规则

- 每个独立 HTML 页面使用统一的顶部案例信息、数据指标卡、左侧模块导航、正文卡片、黄色边界提示和底部证据入口；页面只能改变模块内容，不能改变证据口径。
- 每个 Markdown 报告至少有一个“统计可视化”小节，链接 `report-visuals.html`，并嵌入与本模块直接相关的 SVG 图。
- SVG 图由 `build_report_visuals.py` 生成；图表标题下方必须保留统计定义，`visuals/manifest.json` 必须记录输入字段、统计单位和数值。
- 族、claim、证据、FTO 候选和来源目录使用不同统计单位，图注必须写清楚；不把族数当作有效专利数，不把候选数当作侵权概率。
- 如果输入数据不足以支撑某图，保留“当前数据集暂无可绘制记录”或删除该图并在报告中说明，不用估算值补齐。
- HTML 页面是可读交付层，CSV/JSON 是事实层；任何图表结论都能回到源 CSV/JSON、`family_id`/`document_no`/`finding_id` 和 URL。

## 抽取报告

抽取报告是“事实层”输出，不等同于风险判断。至少包含：

- 实体消歧：分子、研发代号、商品名、靶点、适应症、申请人别名；
- 独立权利要求清单：文献号、claim 类别、claim 位置、要素、覆盖标记、置信度；
- 权利要求要素矩阵：对象、结构/组成、功能/机制、方法步骤、给药/剂量、患者人群、检测/阈值、结果限定；
- 结构抽取：核心骨架、序列、Markush、盐/晶型/前药、抗体链/变体、制剂组分；小分子任务没有结构数据时明确写“未采集结构/仅有文本描述”；
- 申请人/发明人：申请人、受让人、共同申请人、名称变更和来源；
- 时间线：优先权、PCT、公开、国家阶段、授权、分案/继续申请、关键法律事件；
- 主题路线：每一条抽取记录关联到化合物、用途、制剂、联合、诊断、耐药/标志物等主题；
- 抽取缺口：没有全文、只有摘要、claim 位置不明确、机器翻译、状态未核验、结构未解析等。

“摘要披露”与“独立权利要求明确限定”必须分栏，不能合并成“专利覆盖”。

## 专利族地图报告

专利族地图回答“谁在什么时间、什么法域、围绕什么保护主题进行布局”。至少包含：

- 族口径：DOCDB simple family 或 INPADOC extended family；同一报告不可混用统计；
- 族总览表：`family_id`、代表文献、最早优先权、申请人、法域、claim 类别、状态、置信度；
- 关系图：优先权、PCT、国家阶段、分案、continuation、CIP 和相关扩展族；
- 时间泳道：最早优先权、公开、授权和关键法律事件；
- 法域矩阵：CN/US/WO/EP 等成员是否存在、状态是否确认、证据来源；
- 主题矩阵：化合物、结构变体、制剂、用途、联合、给药、诊断、耐药/标志物；
- 申请人布局：申请人按族数、主题和时间阶段分组；
- 地图结论：只引用族表和证据链，不根据气泡大小推断市场或侵权风险。

可视化优先生成 HTML；至少提供一张可筛选的族表、一张优先权时间线、一张法域/主题矩阵，并让每个节点回到专利号和来源。

## 技术路线图报告

技术路线图回答“技术从需求、机制、结构到临床/实施方案如何演化”。建议分成两层：

1. **研发事实层**：疾病需求、靶点/机制、先导/候选物、制剂、给药、联合、患者分层、临床阶段；
2. **专利保护层**：每个节点对应的专利族、claim 类别、最早日期、法域和状态。

每条边都写明关系类型：`机制导致结构选择`、`结构扩展为用途`、`用途发展为联合/剂量`、`失败/耐药导致标志物` 等。没有证据支撑的“下一代路线”必须标为推断或机会假设。

报告至少包含：

- 技术路线 Mermaid 图或 HTML 图；
- 路线节点—专利族—证据映射表；
- 按时间阶段的路线演化；
- 保护路线与研发事实不一致处；
- 当前技术断点、耐药/安全性/诊断缺口和补检任务。

## 风险与 FTO 报告

风险报告必须把“检索优先级”与“法律风险”分开。至少包含：

- FTO 输入方案和特征分级：`core / necessary / support / context`；
- 每个候选族的完整命中、部分命中、未见披露和未核验特征；
- 独立权利要求要素对照表；
- CN/US 等目标法域成员、分案/继续申请和状态证据；
- 组合物、用途、给药/剂量、联合、诊断/监测等多层风险雷达；
- 高/中/低复核优先级及触发事实；
- 不能确认的项目：缺失 claim、状态来源、国家阶段或权利要求解释；
- 逐候选下一步：下载官方文本、核对审查档案、做 claim chart、查年费/异议/无效、请律师复核。

风险语言使用“重叠信号、重点复核、待官方核验、边界候选”，禁止写“必然侵权、绝对安全、没有风险”。FTO 排名分数不能写成侵权概率。

## 创新空间报告

创新空间只输出“可验证假设”，不把“没有搜到”写成“没有专利”。每个假设使用固定模板：

| 字段 | 要求 |
|---|---|
| 假设 | 具体到结构、盐/晶型、制剂、剂量、联合、患者分层、诊断或工艺 |
| 已有依据 | 关联 `family_id`、claim 要素、说明书/论文/临床来源 |
| 空白表现 | 未见同族覆盖、只见摘要、仅边界族、特定法域缺成员或证据不足 |
| 反例 | Markush 可能覆盖、同族分支未查、未公开申请、后续 continuation、检索词盲区 |
| 验证动作 | 结构/药效/制剂实验、补检、官方登记簿、律师 claim chart |
| 信心 | 证据等级和未解决问题 |

至少从以下维度逐项检查：核心化合物/序列、盐型/晶型/制剂、给药与暴露、联合治疗、患者分层、伴随诊断、耐药机制、制备工艺和安全窗。创新方向按“已有证据支持 / 需要实验 / 需要法律复核”分层。

## 证据链报告

证据链报告是所有模块的共同底座，至少包含：

`finding_id | 事实/结论 | evidence_type | source_url | document_no | claim_or_event_location | captured_at | direct_fact_or_inference | confidence | reviewer_action`

报告应把直接事实、模型推断、来源目录信息和待补检任务分开统计；列出来源角色、访问日期、上游快照、机器翻译/聚合镜像风险和官方核验状态。每个模块结论必须能反向定位到至少一个 `finding_id`，或明确标记为“待建立证据”。

## 总报告与状态

`00-executive-summary.md` 主要做入口，不替代模块报告：核心结论、最大风险信号、最大证据缺口、创新假设数量、下一步优先级和模块报告链接仍是必需内容。它可以额外包含一段可选的”专利布局解读”叙述——背景介绍、按技术主题分层的判断、对研发/决策的启示——但这段叙述仍要能回链具体模块报告（尤其是技术路线图报告）核对细节，不能替代模块报告本身的证据表格。该叙述来自案例目录下可选的 `<case>-interpretation.md` 文件（若存在则原样嵌入，若不存在则在执行摘要中显式标记缺口，不静默省略），由分析者/模型在有真实案例数据支撑时撰写，`build_modular_reports.py` 只负责嵌入，不负责生成判断性文字。

`<case>-interpretation.md` 只能用本项目 `build_report_pages.py` 里 `markdown_html()` 支持的极简 Markdown 子集：段落、`- ` 无序列表、`>` 引用、`[text](url)` 链接和 `**粗体**`；不支持 `1. 2. 3.` 有序列表（会被当成普通段落文字拼接，丢失分行和编号），需要分层编号时用 `- **第一层·…**：…` 这类无序列表 + 文字序号的写法。标题只用 `###` 或更低级别，不用 `#`/`##`，避免打乱报告本身的二级标题结构。

### 深度分级对产出的影响

`research_scope.json` 的 `depth` 字段现在真正控制产出规模，而不只是被回显：

- `quick_scan`（快速扫描）：只生成 `00-executive-summary.md/.html` 和 `report-index.md/.html`（含统计图，因为执行摘要仍嵌入 3 张核心图表），不生成 `01-07` 模块报告，也不生成知识图谱（`case-output.json`/`graph-data.json`/`graph-quality.json`/`knowledge-graph.html`）。这对应 SKILL.md 中“快速扫描：…输出简报和风险雷达”的定位。
- `standard_analysis` / `deep_review`：保持现有全量行为（8 份模块报告 + 图表 + 知识图谱）不变。

若某案例从 `standard_analysis`/`deep_review` 降级为 `quick_scan` 后重跑，脚本会清理此前生成的 `01-07-*.md/.html` 和知识图谱文件，避免遗留过期产物。

`state.json` 增加模块状态（`standard_analysis`/`deep_review` 时的取值；`quick_scan` 下除 `summary`/`index`/`visuals`/`html_pages` 外均为 `skipped_by_depth`）：

```json
{
  "reports": {
    "extraction": "complete",
    "family_map": "complete",
    "technology_roadmap": "complete",
    "risk_fto": "complete",
    "innovation_space": "complete",
    "evidence_chain": "complete",
    "source_catalog": "complete",
    "visuals": "complete",
    "html_pages": "complete",
    "knowledge_graph": "complete"
  }
}
```

如果某模块缺少输入，仍生成报告，但状态写为 `partial`，并在报告开头写明缺口；不得静默跳过模块。
