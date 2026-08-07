---
name: medtech-patent-roadmap
description: 对小分子、靶点、适应症及其组合开展可复核的医药专利检索、专利族归并、权利要求/结构/申请人/时间线抽取、法律状态核验、技术路线、FTO 风险和创新空间分析，并分别生成抽取报告、专利族地图报告、技术路线图报告、风险与 FTO 报告、创新空间假设报告、证据链报告和来源目录报告，同时生成 WIPO 风格的专利景观图、Obsidian 式专利证据双链图、交互式/静态数据可视化、结构化数据和可组装的正式报告。用户要求“查某个分子/靶点/适应症的专利”“做专利地图”“看技术路线”“找空白点”“评估专利风险”或需要中美/全球医药专利分析时使用。不得将本 Skill 的结果表述为法律意见、侵权结论或可直接用于申报/诉讼的结论。
---

# 医药专利与技术路线分析

## 目标

将一个医药技术问题转化为可复核的研究结果：

`研究对象 → 检索集合 → 去重后的专利族 → 权利要求要素 → 法律状态 → 技术路线 → 风险与创新假设 → 证据链报告`

坚持“先证据、后判断；先族群、后单件；先权利要求、后标题摘要”。把同族公开文本与授权文本分开记录，把法律状态写成带日期的快照，把推断与原始事实明确区分。

默认将任务拆成五个层级：

`输入范围 → 检索与证据 → 专利族/权利要求 → 法律状态/技术路线 → 可视化与交付`

先确认研究对象、法域、截至日期和技术范围；再选择快速扫描、标准分析或深度复核级别。需要可视化时，优先产出“总览 + 时间线 + 专利族关系 + 技术路线 + 可追溯明细”，不要只画没有证据链接的装饰图。具体族判断规则见 [references/family-and-status.md](references/family-and-status.md)，景观字段和页面结构见 [references/landscape-visualization.md](references/landscape-visualization.md)，双链图的数据契约与交互规则见 [references/knowledge-graph.md](references/knowledge-graph.md)。

借鉴结构化药物情报 Skill 时，采用“实体消歧 → 核心检索 → 关系扩展 → 缺口补检 → 分段写作 → 统一组装”的编排方式。可迁移模式、可选富集源和边界见 [references/enrichment-and-orchestration.md](references/enrichment-and-orchestration.md)。

## 适用边界

适合：

- 小分子、盐型/晶型、前药、代谢物、药物组合物、制备工艺、制剂、给药方案、联合用药、伴随诊断和治疗用途；
- 以分子、靶点、机制、适应症、患者分层、剂量或制剂为入口的专利地图；
- 立项前检索、研发路线梳理、竞品/申请人布局分析、初步风险筛查和创新方向讨论。

不适合直接替代：

- 专利律师出具的 FTO/侵权、不侵权、有效性或无效分析；
- 对尚未公开申请的判断；
- 医疗诊断、治疗或临床决策；
- 仅凭聚合网站的“active/inactive”标签确认权利仍然有效。

若用户要求法律意见，先说明边界，再输出“需要律师复核的事实包”：权利要求原文位置、同族和审查文件、官方法律状态、未决不确定性。

## 输入合同

先从用户输入中抽取并回显以下字段；缺失时采用保守假设并标记：

| 字段 | 内容 |
|---|---|
| 研究对象 | 分子名称/代号、靶点、机制、适应症；注明是否为同一对象的同义词 |
| 研究目的 | 立项、竞品、技术路线、风险筛查、创新空间或其他 |
| 地域 | 至少写明 CN、US、EP/成员国、WO 或“全球主要法域” |
| 时间范围 | 优先权日、公开日、授权日和截至日期；默认截至当前日期 |
| 技术范围 | 化合物、组合物、用途、工艺、制剂、剂量、联合治疗、诊断等 |
| 深度 | 快速扫描、标准分析或律师预审资料包 |
| 交付格式 | Markdown、表格、CSV/JSON、PPT/报告；未指定时输出 Markdown 报告 |

如果研究对象只有商品名，先补齐通用名、研发代号、盐型/异构体和靶点别名；如果只有靶点或适应症，先建立候选分子与机制词，不要假设用户关注某一个具体药物。

### 实体消歧与研究范围确认

在正式检索前建立 `identity` 记录：

- 分子：通用名、研发代号、商品名、盐型/晶型、结构或 CAS 标识；
- 靶点：基因符号、蛋白名称、家族/亚型、通路和机制；
- 疾病：标准名称、别名、分型、治疗线次和生物标志物；
- 申请人：公司历史名称、子公司、大学/医院和共同申请人；
- 研究范围：法域、时间、技术主题、证据等级和输出格式。

若存在多个候选实体，先列出候选及选择理由，不要静默采用第一条自动补全结果。将消歧结果保存为可复核文件，并在报告中标记任何未解决的同名/异名问题。

## 检索与分析流程

### 1. 建立检索词矩阵

为每个概念建立中英文、缩写、旧名、代号和常见拼写变体：

1. 分子：通用名、研发代号、CAS/结构标识、核心骨架、Markush 片段、盐/溶剂化物/晶型/立体异构体/前药/代谢物；
2. 靶点：基因符号、蛋白全称、旧符号、家族名、通路名、机制词、结合位点和功能结果；
3. 适应症：疾病标准名、旧称、分型、器官/肿瘤部位、生物标志物、患者人群、治疗线次和复发/难治表达；
4. 技术形态：composition of matter、salt、polymorph、prodrug、formulation、crystal、process、combination、regimen、method of treatment、biomarker/diagnostic 等；
5. 申请人/发明人：公司历史名称、子公司、大学/医院、共同申请人和已知竞争方；
6. 分类号：从命中专利确认 IPC/CPC 后反向扩展，不要只凭关键词猜分类号。

记录每个词的来源、语言、命中类型和是否纳入主检索。结构检索不可用时，用“骨架/取代基/功能性描述 + claims/full text”替代，并降低结论置信度。

### 2. 采用多路径检索

按“高精度 → 高召回 → 关系扩展”执行，并保存每条检索式、日期、数据库和结果数量：

- 路径 A：精确分子/靶点/适应症的标题、摘要和权利要求检索；
- 路径 B：分子同义词 + 机制/适应症 + 技术形态检索；
- 路径 C：已知命中文献的 IPC/CPC、申请人、发明人、引用/被引用扩展；
- 路径 D：按最早优先权、WO/PCT、国家阶段和授权文本扩展同族；
- 路径 E：从竞争方或临床项目反向检索，不把新闻稿、论文或临床注册号当成专利证据。

来源选择采用 [references/patent-database-sources.json](references/patent-database-sources.json) 的目录快照。该目录同步 [CNIPA/PatentDatabases](https://github.com/CNIPA/PatentDatabases) README 中的全部来源记录：当前为国内 25 条、国外 113 条、分类号工具 5 条，去重后 140 个 URL。它覆盖 CNIPA 公告/审查系统、各国官方或地区数据库、WIPO/EPO/USPTO/KIPRIS/J-PlatPat 等国际入口、商业聚合数据库、文献/临床上下文来源和 IPC/CPC/FI/ECLA/ICO 分类导航。

目录只解决“有哪些来源、分别适合做什么”的问题，不代表所有链接仍然可用，也不代表来源之间证据等级相同。执行时按 `primary_or_status_check`、`discovery_and_cross_check`、`context_only`、`classification_navigation` 路由；对需要登录、验证码、订阅、人工操作、无法检全库或仅显示著录项的来源标为 `pending/manual`。正式法律状态优先回到目标法域官方登记簿，论文/临床/新闻只作为研发上下文。

### 网络访问与 Google Patents 备用路径

开始检索前，确认环境已配置可用的 VPN 或网络代理。Google Patents、WIPO、EPO、USPTO 等外部来源在受限网络中可能无法访问全文、下载页面或返回完整结果；无法连通时必须在报告中标记为检索盲区，不能把“未检到”写成“不存在”。

当 Google Patents 无法直接访问时，可使用 Jina Reader 的只读文本镜像作为**发现与文本提取备用路径**：将原始公开页 URL 包装为 `https://r.jina.ai/http://patents.google.com/patent/<document>/en`（HTTPS 原始 URL 同理包装）。记录原始 URL、Jina Reader URL、访问日期、文献号和获取结果；镜像文本可用于定位公开页面的摘要、权利要求和书目信息，但不得单独作为法律状态、授权有效性、完整档案或权利要求最终范围的证据。对关键结论仍须回到官方登记簿、原始公开文本或其他独立来源复核，并遵守相关服务条款与访问限制。

优先使用官方源：

- 中国：国家知识产权局专利检索及分析系统，支持检索、浏览、分析和下载；
- 国际/PCT：WIPO PATENTSCOPE；注意 WIPO 的 PCT 数据产品说明并不等于所有国家/地区专利的程序化接口；
- 欧洲/全球覆盖：EPO Espacenet 做人工检索；需要程序化取数时使用 EPO OPS，遵守其认证、配额和 fair-use 规则；
- 美国：USPTO Patent Center 核验申请状态和 file history，USPTO Open Data Portal 取结构化数据；
- 分类：使用 WIPO 官方 IPC；若使用 CPC，保存所采用版本与分类定义链接。

不得为了“补齐数量”把相邻但不属于研究对象的专利纳入主集合。将结果分成 `核心命中`、`边界命中`、`排除项`，并为排除项写一行原因。

### 2A. 可选的结构化情报富集

当用户提供了有权限的药物情报数据库连接器时，可以在专利主线之外追加：

- 临床阶段、试验设计、注册号和公开结果；
- 同靶点/同适应症竞品及直接竞争、同类/亚型、通路邻近、标准治疗四层分类；
- 授权交易、合作、转让和许可事件；
- 新闻、论文、转化医学和监管公开资料；
- 基于已采集数据自动生成的“信息缺口清单”。

这些资料用于解释研发路线、竞品位置和技术效果，不能替代专利文本或官方法律状态，也不能把结构化数据库的“无结果”写成事实不存在。优先使用实体 ID 而不是自由文本，并保存查询参数、返回数量、时间戳和来源 URL。

若没有连接器，使用官方数据库、公开网页和论文实现同一逻辑；不要复制受限 API 地址、密钥、数据库内容或商业排序算法。

### 2B. FTO 防侵权检索模块

当用户提供拟实施技术方案、截图式技术特征或要求“类似智慧芽的防侵权检索”时，读取 [references/fto-search.md](references/fto-search.md)，并在案例目录建立 `fto-input.json`。该模块将工作拆成：

`技术方案 → 技术特征分级 → 扩展关键词 → IPC/CPC → R1-R7 多轮检索式 → 候选专利族初筛 → claim 要素比对准备`

运行顺序：

```text
scripts/build_fto_plan.py --project-dir <case-dir>
scripts/score_fto_candidates.py --project-dir <case-dir>
scripts/build_fto_dashboard.py --project-dir <case-dir>
```

输出 `fto-search-plan.json/md`、`fto-candidate-ranking.csv/md` 和 `fto-search.html`。候选排序必须显示命中的特征、关键词、权利要求类别、状态信号和缺口；禁止把排序分数写成侵权概率。扩词来自用户词表、实体消歧和可解释的同义/旧名/机制/临床表达；IPC/CPC 只作为召回和邻近技术入口，需用命中文献或官方分类定义反向确认。

当用户要求“类似样例的 FTO 报告”或需要正式文档交付时，运行 `scripts/build_fto_docx.py --project-dir <case-dir>`，从 FTO 输入、检索计划、专利族、claim 要素、证据链和候选排序数据生成模板化 A4 DOCX。报告采用“封面—概览—检索范围—技术方案—技术特征—专利族初筛—权利要求比对—证据链—附录—免责声明”的结构；含表格、横向宽表、可点击来源链接和页眉页脚。该脚本是样例结构的可复用实现，不复制样例数据，也不把候选排序升级为法律结论。

### 3. 规范化、去重和专利族归并

建立一条“文献记录”和一条“专利族记录”，不要把每个国家公开文本直接计为一个独立创新：

- 规范公开号、申请号、授权号、国家/地区代码、kind code、日期格式、申请人名称和发明人名称；
- 记录优先权链、最早优先权日、公开日、授权日、国家阶段和分案/继续申请关系；
- 明确族口径：默认以 DOCDB simple family 做同一发明的主去重，以 INPADOC extended family 做技术关联扩展；不得混用后再比较数量；
- 对分案、继续申请、部分继续申请和同一族中的不同权利要求方向单独保留“子族/分支”；
- 为每一族选择一个代表文献：优先选择权利要求最完整、文本可读、与研究地域最相关且有官方状态记录的成员；
- 同时保存“族内成员清单”，避免代表文献掩盖某一国家阶段的不同保护范围。

族归并采用以下硬规则：

1. 先比较**优先权申请号**，不要只比较优先权日期；
2. 优先权集合完全相同，通常归入同一 DOCDB simple family；
3. 只共享部分优先权的，作为 INPADOC extended family 或相关族，不能直接当作同一简单族；
4. PCT 与其中国/美国国家阶段通常属于同一主族；
5. 分案、continuation、continuation-in-part 保留为同一大族下的子族/分支，并分别解析权利要求和状态；
6. 新增技术内容获得新的优先权时，不因申请人、标题或分子相同而强行合并；
7. 同一族中出现“核心化合物、盐型/晶型、制剂、用途、联合治疗、诊断”等不同保护方向时，保留主题标签和分支层级。

判断记录至少包含：`family_id | family_definition | priority_set | earliest_priority | continuity_relation | branch_type | representative_document | members`。

### 4. 抽取权利要求和保护要素

对每个核心族至少分析独立权利要求；只有在解释从属限定、有效性或路线分支时才扩展到关键从属权利要求。

按以下模板把权利要求拆成要素，并回填原始 claim 编号/段落位置：

| 维度 | 要素示例 |
|---|---|
| 对象 | 化合物、盐、晶型、组合物、试剂盒、用途、工艺、装置 |
| 结构/组成 | 核心骨架、取代基、立体化学、纯度、比例、粒径、赋形剂 |
| 功能/机制 | 靶点、结合/抑制方式、选择性、功能结果、生物标志物 |
| 方法步骤 | 给药对象、剂量、频次、疗程、联合药物、治疗线次 |
| 结果限定 | 响应、复发、耐药、毒性、暴露量、诊断阈值 |
| 地域/状态 | 目标国家的公开、授权、审查或失效信息 |

输出“权利要求要素矩阵”，用 `明确披露 / 可能覆盖 / 未见披露 / 不确定` 标注，不要把摘要中的技术效果直接升级成权利要求保护范围。对 Markush 权利要求要说明：是宽泛结构概念、明确实施例，还是仅由从属项/说明书支持。

### 5. 核验法律状态

把状态写成“截至 YYYY-MM-DD，在法域 X 的公开记录显示为……”，至少区分：

`已公开未授权 / 审查中 / 已授权且未发现失效记录 / 已放弃或视为撤回 / 已驳回 / 已到期 / 状态不明`。

按以下优先级核验：

1. 目标国家/地区官方登记簿或审查档案；
2. EPO Register 的 EP/UP 及其 federated register；
3. WIPO、EPO 或 USPTO 等官方数据中的法律事件；
4. 聚合数据库仅作线索，不作为最终状态证据。

特别注意：INPADOC/聚合状态是补充信息；涉及授权后国家阶段、年费、异议、无效、限制或撤销时，回到相关国家官方登记簿。对没有可靠官方记录的国家标为“待核验”，不要猜测“有效”。

### 6. 构建技术路线图

将专利文本、论文/临床资料和申请人披露分层使用：专利负责“保护了什么”，论文/临床资料负责“技术走到了哪里”，不能用后者证明前者的法律范围。

按下列链路组织技术路线：

`疾病/未满足需求 → 靶点与机制 → 结构系列/化学空间 → 先导与候选物 → 选择性/药代/安全性 → 制剂/给药方案 → 联合策略/生物标志物 → 适应症与临床阶段`

为每个节点绑定：代表专利族、最早日期、关键权利要求、公开实施例、证据来源和置信度。将“专利保护路线”和“研发事实路线”画成两条可对照的线；二者不一致时，解释是范围宽、实施例窄、路线已转向，还是证据不足。

若加入临床/竞品/交易/文献富集，将路线图分为两层：

1. **专利保护层**：化合物、制剂、用途、剂量、联合、诊断和法律状态；
2. **研发情报层**：临床阶段、试验结果、竞争者、交易、新闻和论文。

两层之间用 `family_id`、`entity_id`、临床注册号或 DOI 连接；没有连接证据时保持并列，不强行合并。

### 7. 识别风险和创新空间

风险只做信号分级，不下法律结论。至少检查：

- 目标分子/盐型/晶型是否落入核心化合物或 Markush 要素；
- 目标适应症、患者分层、联合用药、剂量/疗程是否存在独立用途或给药方案族；
- 关键国家是否有授权、审查中、分案/继续申请或近期法律事件；
- 同一申请人是否沿“化合物 → 制剂 → 用途 → 联合/剂量”形成多层壁垒；
- 研发路线是否依赖一个高重叠且尚未确认状态的专利族。

创新空间只输出“假设”，按 `有证据支持的候选方向 / 需要实验验证 / 需要律师复核` 分层。可从以下维度提出候选：未见同族覆盖的结构变体、盐/晶型/制剂、选择性或安全窗、给药方案、联合治疗、患者分层、伴随诊断和新的制备工艺。每个候选都要说明检索范围、缺口证据和可能的反例；不要把“没搜到”写成“没有专利”。

## 输出合同

默认生成以下章节，除非用户指定其他格式：

1. **执行摘要**：对象、覆盖法域/时间、核心结论、最大不确定性；
2. **研究范围与方法**：输入假设、检索式、数据库、日期、纳排标准、族口径；
3. **专利族地图**：按技术主题/申请人/优先权时间/法域/状态分组；
4. **核心族明细**：公开号/申请号/授权号、优先权链、申请人、代表文献、成员、状态证据、核心 claim 要素；
5. **权利要求要素矩阵**：独立权利要求逐族对照，标注明确/可能/未见/不确定；
6. **技术路线图**：靶点—结构—候选物—制剂—方案—适应症—临床阶段，节点绑定专利和证据；
7. **风险提示**：按高/中/低或红/黄/绿排序，写明触发事实、缺口和下一步核验；
8. **创新空间假设**：逐项写“假设—证据—反例—建议实验/检索/法律复核”；
9. **证据链报告**：事实、来源、定位、抓取日期、证据级别、置信度和推断说明；
10. **附录**：完整检索式、排除项、原始链接、族内成员、字段字典和未解决问题。

### 模块化报告交付

除总报告外，必须为每个任务模块生成独立、可单独阅读的 Markdown 报告和 FTO 风格 HTML 页面。读取 [references/modular-reporting.md](references/modular-reporting.md) 获取详细章节和字段要求，并运行 `scripts/build_modular_reports.py --project-dir <case-dir>`；该脚本会联动生成统计图和独立页面。

固定输出：

1. `00-executive-summary.md`：执行摘要、关键风险、最大缺口和模块索引；
2. `01-extraction-report.md`：权利要求、结构/组成、申请人/发明人、时间线、技术要素和抽取缺口；
3. `02-patent-family-map-report.md`：族口径、专利族地图数据、优先权时间、法域矩阵、申请人布局和族关系缺口；
4. `03-technology-roadmap-report.md`：研发事实层与专利保护层分离的技术路线图、节点映射、演化、断点和补检任务；
5. `04-risk-and-fto-report.md`：FTO 输入、特征分级、claim 要素比对、候选族排序、法域状态、风险雷达和下一步核验；
6. `05-innovation-space-report.md`：结构、制剂、用途、联合、给药、诊断、耐药和安全窗等逐项创新空间假设，每项包含依据、反例、验证动作和信心；
7. `06-evidence-chain-report.md`：事实、推断、来源、claim/事件定位、抓取时间、置信度、复核动作和证据缺口；
8. `07-source-catalog-report.md`：来源目录、来源角色、访问限制、上游快照和完整 URL 清单；
9. `report-index.md`：所有模块报告和过程数据入口；同时生成 `report-index.html` 作为 FTO 风格工作台。
10. `knowledge-graph.html`：离线 Cytoscape.js 双链图，可从 family/claim 回溯 finding/source，并查看出链、反向链接和数据质量缺口。

每个模块页面统一采用 FTO 式信息架构：案例范围与免责声明 → 顶部数据指标 → 左侧模块导航 → 分段正文/表格 → 统计图 → 证据和限制。图表必须由当前案例 CSV/JSON 自动生成，并在页面或报告中给出统计口径；不得用估算数填充。

如果输入不足，仍生成对应报告并将模块状态标为 `partial`，在报告开头列出缺口，不得静默跳过。抽取报告是事实层；风险、FTO 和创新空间报告必须引用抽取报告/证据链中的 `family_id`、`document_no` 或 `finding_id`。

### WIPO 风格可视化交付

当用户要求“专利地图”“仪表盘”或参考 WIPO/商业数据库展示时，按数据驱动的可追溯结构输出：

1. **总览面板**：族数、申请人、国家、年份、技术主题和状态分布；
2. **时间线**：最早优先权、公开、授权、分案/继续申请和关键法律事件；
3. **族关系图**：PCT、国家阶段、分案、continuation 与相关扩展族；
4. **主题矩阵**：化合物、制剂、用途、联合治疗、耐药突变、诊断等；
5. **技术路线图**：疾病需求 → 靶点/机制 → 化合物 → 适应症 → 耐药 → 下一代方案；
6. **详情抽屉/附录**：点击或检索到族时展示成员、权利要求要素、状态来源和证据链。

推荐默认使用“技术景观图 + 保护层级矩阵 + 优先权时间泳道 + CN/US 法域矩阵 + 选中族详情”组合视图：它比单一时间线或国家数量柱状图更适合回答“谁保护了什么、何时布局、目标法域是否出现成员、证据在哪里”。可参考 WIPO 的 [COVID-19 vaccines and therapeutics patent landscape](https://www.wipo.int/en/web/patent-analytics/patent-landscape-on-covid-19-vaccines-and-therapeutics)，但只借鉴信息架构，不复制其数据或实现。

静态结构使用 Mermaid 或 Markdown 图表；需要筛选、点击、钻取时生成独立 HTML；需要比赛答辩时同时生成 PPT/PNG 或 PDF 版本。图中每个关键节点必须绑定 `family_id` 或 `finding_id`，并能够回到专利号、claim/事件位置和来源链接。可视化字段参见 [references/landscape-visualization.md](references/landscape-visualization.md)。

### 专利证据双链图

构建双链图前必须先运行 `build_case_output.py`，使 claim 获得稳定 `claim_id`，evidence 获得 `family_ids` / `claim_ids`，并把族成员、优先权和连续关系转换为一等关系边。随后运行 `build_graph_data.py` 和 `build_knowledge_graph.py`。边只存一次，反向链接由视图按入边计算；显式事实、规则匹配和模型推断分别使用实线、虚线和点线。

默认提供专利族、技术保护、证据链和申请人四个预设；默认只展开焦点节点一跳，并限制可见节点数量。族间 `priority`、`national phase`、`divisional`、`continuation` 只能来自结构化字段或证据，不从 notes 猜测。完整字段见 [references/output-schema.md](references/output-schema.md)，图谱规则见 [references/knowledge-graph.md](references/knowledge-graph.md)。

### FTO 风格统计可视化

统一使用 `scripts/build_report_visuals.py --project-dir <case-dir>` 生成依赖外部图库的 SVG/HTML 资产。默认图表包括：专利族技术主题、最早优先权年度、申请人/受让人、法域覆盖、权利要求类别、状态信号、FTO 复核优先级、证据置信度、证据类型、来源角色和检索轮次。每张图都写入 `visuals/manifest.json`，记录数据来源字段、统计定义和数值。

模块报告只嵌入与主题相关的图：族地图偏重主题/时间/法域，路线图偏重主题/claim 类别/时间，风险与 FTO 偏重优先级/状态/claim 类别，证据链偏重置信度/证据类型/来源角色。状态图是研究阶段信号，不得写成官方法律状态；FTO 优先级是复核排序，不得写成侵权概率。

可借鉴结构化药物情报报告的“分段写作 + 统一组装”方式：分别生成执行摘要、核心专利/竞争景观、临床/研发上下文、交易/组织背景和新闻/战略洞察，再统一组装 HTML/PDF。每个分段都必须带来源和免责声明；若某一模块无可靠数据，保留“未覆盖/待补检”而不是生成空泛段落。

核心族表至少包含：

`family_id | family_definition | representative_publication | applications | grants | earliest_priority | publication_date | applicant | inventors | jurisdictions | claim_categories | key_claim_elements | official_status | status_as_of | status_source | confidence | notes`

证据链表至少包含：

`finding_id | conclusion_or_fact | evidence_type | source_url | document_no | claim_or_event_location | captured_at | direct_fact_or_inference | confidence | reviewer_action`

允许使用 Mermaid 绘制路线图，但图中每个关键节点都必须能回溯到表格中的 `family_id` 或 `finding_id`。表格无法支持的结论不得进入摘要。

## 证据等级与表达规则

采用下列证据等级：

- **E1**：目标法域官方登记簿、官方审查档案、官方法律事件；
- **E2**：专利局公开文本中的权利要求、说明书、摘要、图式；
- **E3**：WIPO/EPO/USPTO 等官方全球/族/事件数据；
- **E4**：可靠的聚合数据库、公司公告、论文、临床注册或监管材料；
- **E5**：模型根据多个来源作出的推断或待验证假设。

表达时使用：

- E1/E2 事实： “官方记录显示……”“权利要求 X 明确包含……”；
- E3/E4 交叉证据： “可由……佐证，但应以目标法域登记簿为准”；
- E5 推断： “基于现有检索范围的假设……”“尚不足以证明……”；
- 状态：永远附带法域、日期和来源；
- 风险：使用“重叠信号/需复核/存在不确定性”，避免“必然侵权/绝对安全/一定无效”。

## 运行模式与通用输出

根据用户目的选择模式：

- **快速扫描**：20—50 个高相关文献线索，5—10 个核心族，输出简报和风险雷达；
- **标准分析**：完成词表、多路径检索、族归并、独立权利要求矩阵、状态快照、技术路线和地图；
- **深度复核资料包**：增加国家阶段、分案/continuation、事件记录、claim chart、原始文本定位和人工复核清单。

默认生成以下文件（用户未指定时使用 Markdown/CSV/HTML）：

```text
outputs/<skill-name>/
├── SKILL.md                         # 可复用工作规范（仅创建/更新 Skill 时）
├── <case>-report.md                 # 可读研究报告
├── <case>-patent-families.csv       # 专利族和成员数据
├── <case>-claim-elements.csv        # 权利要求要素矩阵
├── <case>-evidence.csv              # 证据链
├── <case>-landscape.html            # 可筛选的地图/仪表盘（需要时）
├── <case>-landscape-v2.html         # 推荐：保护层级/时间/法域/详情组合视图（需要时）
├── <case>-roadmap.md                # 技术路线和创新假设（需要时）
├── <case>-context/                  # 可选：临床/竞品/交易/新闻/文献上下文
├── query-matrix.json                # 可恢复的多路径检索计划（需要时）
├── patent-database-sources.json     # CNIPA/PatentDatabases 来源目录快照（需要时）
├── gap_brief.json                   # 基于缺口的补检任务（需要时）
├── fto-input.json                   # FTO 技术方案、特征、扩词和分类号输入（需要时）
├── fto-search-plan.json/md          # FTO 特征工程与 R1-R7 检索计划（需要时）
├── fto-candidate-ranking.csv/md     # 基于 claim-elements 的透明候选排序（需要时）
├── fto-search.html                  # 阶段式 FTO 检索与特征比对页面（需要时）
├── <case>-fto-report.docx            # 类样例的正式 FTO 报告（需要时）
├── 00-executive-summary.md          # 模块化交付入口（需要时）
├── 01-extraction-report.md          # 抽取报告（需要时）
├── 02-patent-family-map-report.md   # 专利族地图报告（需要时）
├── 03-technology-roadmap-report.md  # 技术路线图报告（需要时）
├── 04-risk-and-fto-report.md        # 风险与 FTO 报告（需要时）
├── 05-innovation-space-report.md    # 创新空间假设报告（需要时）
├── 06-evidence-chain-report.md      # 证据链报告（需要时）
├── 07-source-catalog-report.md      # 来源目录报告（需要时）
├── report-index.md                  # 模块化报告索引（需要时）
├── report-index.html                # FTO 风格模块报告工作台（需要时）
├── report-visuals.html              # FTO 风格统计总览（需要时）
├── case-output.json                 # 稳定 ID、记录与一等关系边（需要时）
├── graph-data.json                  # Cytoscape.js 图数据（需要时）
├── graph-quality.json               # 缺失关系、孤立证据和悬空边检查（需要时）
├── knowledge-graph.html             # 离线专利证据双链图（需要时）
├── 00-executive-summary.html        # 独立模块页面（需要时）
├── 01-extraction-report.html        # 独立模块页面（需要时）
├── 02-patent-family-map-report.html # 独立模块页面（需要时）
├── 03-technology-roadmap-report.html
├── 04-risk-and-fto-report.html
├── 05-innovation-space-report.html
├── 06-evidence-chain-report.html
├── 07-source-catalog-report.html
├── visuals/                         # SVG 图、manifest.json（需要时）
└── <case>-source-log.jsonl          # 可选：结构化数据或网页检索调用日志
```

若数据无法支持某一图表，删掉该图表并说明原因，不以估算值填充。若法律状态无法由官方记录确认，标为“待核验”，不写成“有效”。

推荐使用可恢复的状态编排：每个阶段只在输入文件存在且通过最小校验后标记完成；暂停点要求人工补写规定文件；失败时回退到最近一个已验证阶段。大型项目可采用 `state.json`、阶段清单、项目级 step override 和 JSONL 调用日志，但不要让编排器掩盖证据缺失。

### 已提供的可运行组件

在重复运行或需要标准化交付时，优先使用 `scripts/`：

- `init_case.py`：创建研究范围、实体和可恢复状态文件；
- `validate_case.py`：校验输入合同、CSV 字段和证据产物；
- `generate_gap_brief.py`：根据缺失的状态、claim、临床、竞品和文献资料生成补检任务；
- `build_query_matrix.py`：根据实体与范围生成精确检索、同义词/技术形态、分类/引证、族关系、竞争景观和耐药/标志物补检路径；
- `update_source_registry.py`：从 CNIPA/PatentDatabases README 刷新全部来源目录，记录上游哈希、分组、来源角色和默认用途；
- `append_source_log.py`：以 JSONL 追加查询、专利、官方登记簿、论文、临床、新闻和交易来源记录；
- `build_landscape_html.py`：从标准化专利族 CSV 生成可筛选的 WIPO 风格 HTML 地图。
- `build_landscape_v2.py`：生成保护层级矩阵、优先权时间泳道、CN/US 法域矩阵和可点击证据详情的组合视图。
- `build_fto_plan.py`：从 `fto-input.json` 生成技术特征、扩展关键词、IPC/CPC 和 R1-R7 检索轮次；
- `score_fto_candidates.py`：用声明的关键词簇和已有 claim-elements 做可解释的候选族排序；
- `build_fto_dashboard.py`：生成类似产品工作流的 FTO 检索、初筛和特征比对 HTML 页面。
- `build_fto_docx.py`：将上述 FTO 结构化数据组装为可复用的 A4 正式报告 DOCX，支持纵向叙述页、横向权利要求比对表、证据链和附录。
- `build_modular_reports.py`：从族、claim、证据、FTO 排名、检索计划和来源目录生成独立抽取/族地图/路线/风险/FTO/创新/证据链/来源报告，并更新 `state.json` 的模块状态。
- `build_report_visuals.py`：从案例 CSV/JSON 生成可嵌入 Markdown 的 SVG 统计图、`visuals/manifest.json` 和 FTO 风格 `report-visuals.html`。
- `build_report_pages.py`：把独立 Markdown 报告渲染成带 FTO 式导航、指标卡、免责声明和图表的 HTML 页面；通常由 `build_modular_reports.py` 自动调用。
- `build_case_output.py`：统一案例记录，生成稳定 `claim_id`、文献记录、family/claim→finding 双链和显式专利族关系边。
- `validate_output_schema.py`：检查 `case-output.json` 的字段、ID 唯一性、关系口径和悬空边。
- `build_graph_data.py`：从 `case-output.json` 生成 Cytoscape-ready `graph-data.json` 与 `graph-quality.json`。
- `validate_graph_data.py`：检查图节点/边 ID、悬空边、计数和预设。
- `build_knowledge_graph.py`：内嵌 Cytoscape.js、图数据和交互组件，生成无需服务器或 CDN 的 `knowledge-graph.html`。

这些脚本不连接智慧芽或任何私有数据库；可选结构化数据库应通过外部连接器提供标准化 JSON，再由上述校验、缺口分析和可视化组件消费。

## 质量门槛

交付前逐项检查：

- 是否至少使用两个独立检索入口，并保留检索式、日期和数据库；
- 是否对关键词、分类、申请人/发明人、引证和同族扩展做了覆盖说明；
- 是否以专利族而非公开文本数量做主统计，并注明 DOCDB/INPADOC 口径；
- 每个核心族是否有至少一个权利要求定位和一个状态来源；
- 是否区分公开申请、授权专利、审查中、放弃/撤回、到期和未知；
- 是否将分案/继续申请和不同国家阶段的不同保护范围保留下来；
- 是否把“标题/摘要命中”与“独立权利要求明确覆盖”分开；
- 是否每个关键判断都能回溯到 `family_id`、文献号、claim/事件位置和抓取日期；
- 是否显式写出未检索到的范围、数据库盲区、机器翻译风险和需要专家复核的地方；
- 是否避免将研究报告写成法律意见、FTO 结论、无效结论或医疗建议。
- 若使用 FTO 模块，是否区分 `core/necessary/support/context` 特征，并把扩展词与专利事实分开记录；
- FTO 候选排序是否可回溯至命中特征、命中词、权利要求类别、族记录和状态来源；
- 是否明确说明候选排序是检索优先级，不是侵权概率，且完整独立权利要求和官方登记簿尚需复核。
- 是否从来源目录中选择了与目标法域匹配的官方入口，并区分官方核验、聚合扩展、文献/临床上下文和分类导航来源；
- 是否记录了来源目录快照日期/哈希、访问日期、结果数量和访问限制，未把不可访问或过时链接写成已检索事实。
- 是否生成了独立抽取报告和每个 Skill 输出模块报告；抽取、族图、路线、风险/FTO、创新空间和证据链是否分别可读、互相可回溯；
- 技术路线图是否区分研发事实与专利保护，风险/FTO 是否列出完整命中特征、部分命中特征、法域状态和下一步 claim chart，创新空间是否逐项写出反例与验证动作。
- 是否生成稳定且唯一的 `claim_id`；finding 是否通过显式 ID 或可复核规则回链到 family/claim；图谱是否无悬空边。
- 专利族连续关系是否来自 `members`、`priority_set`、`family_relations` 或相应证据；缺失时是否在 `graph-quality.json` 报告，而不是从 notes 猜造。

若无法满足上述门槛，降低报告级别为“快速扫描”，并在执行摘要中直说限制，不要用更强的措辞掩盖证据不足。

## 最小实现方案

### 快速可用版

使用官方数据库人工检索 + 结构化 Markdown/表格：保存检索式、公开文本链接、代表族、权利要求要素和状态截图/链接。适合一次性立项调研，重点是可审计而非自动化。

### 可复用研究版

建立以下数据层：

1. `query_set`：对象、词表、检索式、来源和日期；
2. `document`：公开号、标题、摘要、claims、申请人、日期、分类号和源链接；
3. `family`：族口径、优先权链、成员、分案/继续关系；
4. `legal_event`：法域、事件日期、事件代码、来源和状态快照；
5. `claim_element`：稳定 `claim_id`、族/文献、claim 编号、要素、原文定位、标准化标签；
6. `finding`：稳定 `finding_id`、结论、证据、推断、置信度、复核状态及关联的 `family_ids` / `claim_ids`；
7. `relation`：稳定 `relation_id`、源/目标节点、关系类型、事实/规则/推断口径和关联证据。

自动化时优先接入 EPO OPS、USPTO Open Data 等允许程序化访问的官方接口；中国专利和各国后授权状态按官方系统可用方式取数。让规则/代码负责规范化、去重、日期和族关系，让模型负责同义词扩展、claim 要素初步抽取、技术主题聚类和自然语言报告；模型不得单独决定法律状态或侵权结论。

### 生产化增强版

增加：原始数据快照、请求日志、重试和速率限制、版本化词表、人工复核队列、claim diff、国家阶段状态同步、检索召回/精度抽样评估和报告版本号。将“源数据、标准化字段、模型推断、人工确认”分层保存，保证后续能重跑和解释结果变化。

## 官方起始来源

- CNIPA 专利检索及分析系统介绍：<https://www.cnipa.gov.cn/art/2023/2/13/art_3166_182074.html>
- CNIPA 检索入口：<https://pss-system.cponline.cnipa.gov.cn/conventionalSearch>
- WIPO PATENTSCOPE：<https://patentscope.wipo.int/search/en/search.jsf>
- WIPO PCT 数据产品与程序化访问说明：<https://www.wipo.int/en/web/patentscope/data/index>
- WIPO IPC：<https://www.wipo.int/en/web/classification-ipc>
- EPO Espacenet：<https://www.epo.org/en/searching-for-patents/technical/espacenet>
- EPO OPS：<https://www.epo.org/en/searching-for-patents/data/web-services/ops>
- EPO 专利族定义：<https://register.epo.org/help?lng=en&topic=patentfamily>
- EPO 法律状态说明：<https://register.epo.org/help?lng=en&topic=eplegalstatus>
- USPTO Patent Center：<https://www.uspto.gov/patents/apply/patent-center>
- USPTO Open Data Portal：<https://developer.uspto.gov/>

## 推荐调用方式

执行任务时先问清或补齐：

> 请对【分子/靶点/适应症】进行【目的】导向的医药专利与技术路线分析，覆盖【法域】、截至【日期】，重点看【化合物/用途/制剂/给药方案/联合治疗/诊断】。请采用专利族去重，逐族解析独立权利要求，核验官方法律状态，输出专利族地图、技术路线图、风险提示、创新空间假设和逐条证据链；所有状态和风险均标明法域、日期、来源与置信度，不给出未经律师复核的侵权或 FTO 结论。
