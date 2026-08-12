# FTO 防侵权检索计划：tfr1_patent_case

> 本文件用于公开专利候选初筛与后续 claim chart 准备，不构成侵权/不侵权法律意见。

## 1. 技术方案

围绕 Transferrin Receptor 1、TfR1 和 broad (cancer, iron metabolism, CNS delivery) 的拟实施技术方案，进行组成、用途、给药、检测或组合治疗的 FTO 初筛。

## 2. 技术特征

| ID | 类型 | 重要性 | 技术特征 | 分类号 |
|---|---|---|---|---|
| F01 | core | core | Transferrin Receptor 1 用于 broad (cancer, iron metabolism, CNS delivery)，作用于 TfR1。 | — |
| F02 | necessary | necessary | 治疗或检测步骤包含给药对象、方案或患者分层。 | — |

## 3. 扩展关键词

| 词簇 | 基础词 | 扩展词 | 关联特征 | 来源 |
|---|---|---|---|---|
| 研究对象 | Transferrin Receptor 1 | TfR1、CD71、TFRC、transferrin receptor protein 1、p90、T9 | F01 | scope/identity |
| 靶点/机制 | TfR1 | transferrin receptor 1、transferrin receptor protein 1、CD71、TFRC gene product、p90、T9 | F01 | scope/identity |
| 适应症 | broad (cancer, iron metabolism, CNS delivery) | iron-refractory iron deficiency anemia (IRIDA) TFRC context、cancer / proliferating-cell marker、receptor-mediated transcytosis across blood-brain barrier、erythroid iron delivery、hemochromatosis differential (TFR2)、tumor imaging / theranostics | F01 | scope/identity |
| 用途与治疗 | method of treatment、治疗方法 | combination、regimen、给药方案 | F02 | generic claim vocabulary |

## 4. IPC/CPC

未提供；需从高相关专利反向确认。

## 5. 来源目录

本 Skill 纳入 CNIPA/PatentDatabases 的来源目录：上游列出 143 条，去重后 140 个 URL。目录用于选择检索入口，不代表所有链接当前可访问或适合作为法律状态证据。

上游仓库：https://github.com/CNIPA/PatentDatabases

| 来源用途 | 数量 | 使用原则 |
|---|---:|---|
| classification_authority_or_navigator | 4 | This is a source directory, not an endorsement and not proof that every URL is current or accessible. |
| classification_navigator | 1 | This is a source directory, not an endorsement and not proof that every URL is current or accessible. |
| commercial_or_aggregator | 33 | Use for discovery, normalization, family/citation expansion and cross-checking; do not use alone for legal status. |
| literature_or_context | 5 | Use for technical, clinical or background context; it does not establish patent claim coverage. |
| official_or_authority | 33 | Use for primary publication, prosecution or legal-status verification when the target jurisdiction is covered. |
| public_or_national_database | 64 | Use for discovery and jurisdiction-specific cross-checking; verify scope and update date. |

## 6. 检索轮次

| 轮次 | 目标 | 字段 | 来源路线 | 检索式 | 状态 |
|---|---|---|---|---|---|
| R1 关键词组合检索 | 锁定研究对象、靶点、适应症和风险/监测场景同时出现的文献。 | title, abstract, claims | primary_or_status_check, discovery_and_cross_check | `("Transferrin Receptor 1") AND ("TfR1") AND ("broad (cancer, iron metabolism, CNS delivery)")` | planned |
| R2 机制与通路扩展 | 扩大到 PD-1/PD-L1 结合、阻断、免疫毒性和器官损伤表述。 | full_text, claims, CPC/IPC | primary_or_status_check, discovery_and_cross_check | `("Transferrin Receptor 1" OR "TfR1" OR "CD71" OR "TFRC" OR "transferrin receptor protein 1" OR "p90" OR "T9") AND ("TfR1" OR "transferrin receptor 1" OR "transferrin receptor protein 1" OR "CD71" OR "TFRC gene product" OR "p90" OR "T9")` | planned |
| R3 肺部不良事件专项 | 覆盖免疫相关性肺炎、间质性肺病、肺毒性和呼吸体征连续监测。 | claims, description | primary_or_status_check, discovery_and_cross_check, context_only | `("Transferrin Receptor 1" OR "TfR1" OR "CD71" OR "TFRC" OR "transferrin receptor protein 1" OR "p90" OR "T9" OR "broad (cancer, iron metabolism, CNS delivery)" OR "iron-refractory iron deficiency anemia (IRIDA) TFRC context" OR "cancer / proliferating-cell marker" OR "receptor-mediated transcytosis across blood-brain barrier" OR "erythroid iron delivery" OR "hemochromatosis differential (TFR2)" OR "tumor imaging / theranostics")` | planned |
| R4 生化指标与内分泌监测 | 覆盖 ALT/AST、肌酐、TSH、游离 T4、血糖等基线和治疗期监测。 | claims, abstract, full_text | primary_or_status_check, discovery_and_cross_check, context_only | `("Transferrin Receptor 1" OR "TfR1" OR "CD71" OR "TFRC" OR "transferrin receptor protein 1" OR "p90" OR "T9" OR "broad (cancer, iron metabolism, CNS delivery)" OR "iron-refractory iron deficiency anemia (IRIDA) TFRC context" OR "cancer / proliferating-cell marker" OR "receptor-mediated transcytosis across blood-brain barrier" OR "erythroid iron delivery" OR "hemochromatosis differential (TFR2)" OR "tumor imaging / theranostics")` | planned |
| R5 结肠炎与处置方案 | 覆盖腹泻分级、结肠炎、皮质类固醇和治疗决策。 | claims, description | primary_or_status_check, discovery_and_cross_check, context_only | `("Transferrin Receptor 1" OR "TfR1" OR "CD71" OR "TFRC" OR "transferrin receptor protein 1" OR "p90" OR "T9")` | planned |
| R6 IPC/CPC 组合检索 | 用分类号补足检测、抗体、免疫治疗和医疗数据分析类漏检。 | IPC, CPC, claims | classification_navigation, primary_or_status_check, discovery_and_cross_check | `("TfR1" OR "transferrin receptor 1" OR "transferrin receptor protein 1" OR "CD71" OR "TFRC gene product" OR "p90" OR "T9" OR "broad (cancer, iron metabolism, CNS delivery)" OR "iron-refractory iron deficiency anemia (IRIDA) TFRC context" OR "cancer / proliferating-cell marker" OR "receptor-mediated transcytosis across blood-brain barrier" OR "erythroid iron delivery" OR "hemochromatosis differential (TFR2)" OR "tumor imaging / theranostics")` | planned |
| R7 关系与边界扩展 | 从高相关文献扩展同族、申请人、引用、分案/继续申请和邻近技术。 | family, assignee, citations, legal_events | primary_or_status_check, discovery_and_cross_check | `已命中文献的 family / assignee / citation / continuity expansion; 不使用自由文本替代权利要求核验` | planned |

## 7. 初筛规则

- 核心特征命中 + 权利要求类别相关：进入高优先级人工复核。
- 必要特征命中但缺少核心对象或法域成员：标记为边界候选。
- 仅说明书/摘要或相邻分类号命中：作为线索，不升级为覆盖结论。
- 状态来自聚合镜像时标记待核验；以目标法域官方登记簿和审查档案为准。

## 8. 待补证据

- 这是由范围文件自动生成的保守模板，请在正式检索前人工补充技术特征、阈值和分类号。
- 每一轮的真实结果数量、纳排决定和官方法律状态需要在检索后回填。
- FTO 风险必须基于目标法域的完整独立权利要求和截至日期状态复核。
