# FTO 防侵权检索计划：GLP1R_patent_case

> 本文件用于公开专利候选初筛与后续 claim chart 准备，不构成侵权/不侵权法律意见。

## 1. 技术方案

围绕 GLP-1 receptor agonist (class landscape)、GLP1R (glucagon-like peptide 1 receptor) 和 type 2 diabetes mellitus; obesity/overweight; cardiovascular risk 的拟实施技术方案，进行组成、用途、给药、检测或组合治疗的 FTO 初筛。

## 2. 技术特征

| ID | 类型 | 重要性 | 技术特征 | 分类号 |
|---|---|---|---|---|
| F01 | core | core | GLP-1 receptor agonist (class landscape) 用于 type 2 diabetes mellitus; obesity/overweight; cardiovascular risk，作用于 GLP1R (glucagon-like peptide 1 receptor)。 | — |
| F02 | necessary | necessary | 治疗或检测步骤包含给药对象、方案或患者分层。 | — |

## 3. 扩展关键词

| 词簇 | 基础词 | 扩展词 | 关联特征 | 来源 |
|---|---|---|---|---|
| 研究对象 | GLP-1 receptor agonist (class landscape) | semaglutide、司美格鲁肽、liraglutide、tirzepatide、替尔泊肽、orforglipron、oral GLP-1、小分子GLP-1、GLP-1受体激动剂、GLP-1RA、glucagon-like peptide-1 receptor agonist、peptide GLP-1、GIP/GLP-1 dual、索马鲁肽、利拉鲁肽、奥福格利普隆、GLP1R agonist、GIP/GLP1 co-agonist、exenatide、dulaglutide、lixisenatide | F01 | scope/identity |
| 靶点/机制 | GLP1R (glucagon-like peptide 1 receptor) | GLP-1R、GLP-1 receptor、glucagon-like peptide 1 receptor、胰高血糖素样肽-1受体、GLP1R | F01 | scope/identity |
| 适应症 | type 2 diabetes mellitus; obesity/overweight; cardiovascular risk | 2型糖尿病、T2DM、肥胖、超重、体重管理、MACE/心血管结局、NASH/MASH、diabetes、obesity | F01 | scope/identity |
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
| R1 核心对象与用途组合检索 | 锁定核心技术特征在标题、摘要和权利要求中的共同披露。 当前词簇：研究对象、靶点/机制、适应症。 | title, abstract, claims | primary_or_status_check, discovery_and_cross_check | `("GLP-1 receptor agonist (class landscape)") AND ("GLP1R (glucagon-like peptide 1 receptor)") AND ("type 2 diabetes mellitus; obesity/overweight; cardiovascular risk")` | planned |
| R2 同义词与机制扩展 | 用案例声明的别名、同义词、译名和机制词扩大召回，并回到权利要求核验。 当前词簇：研究对象、靶点/机制、适应症、用途与治疗。 | full_text, claims, CPC/IPC | primary_or_status_check, discovery_and_cross_check | `("GLP-1 receptor agonist (class landscape)" OR "semaglutide" OR "司美格鲁肽" OR "liraglutide" OR "tirzepatide" OR "替尔泊肽" OR "orforglipron" OR "oral GLP-1" OR "小分子GLP-1" OR "GLP-1受体激动剂" OR "GLP-1RA" OR "glucagon-like peptide-1 receptor agonist" OR "peptide GLP-1" OR "GIP/GLP-1 dual" OR "索马鲁肽" OR "利拉鲁肽") AND ("GLP1R (glucagon-like peptide 1 receptor)" OR "GLP-1R" OR "GLP-1 receptor" OR "glucagon-like peptide 1 receptor" OR "胰高血糖素样肽-1受体" OR "GLP1R") AND ("type 2 diabetes mellitus; obesity/overweight; cardiovascular risk" OR "2型糖尿病" OR "T2DM" OR "肥胖" OR "超重" OR "体重管理" OR "MACE/心血管结局" OR "NASH/MASH" OR "diabetes" OR "obesity") AND ("method of treatment" OR "治疗方法" OR "combination" OR "regimen" OR "给药方案")` | planned |
| R3 技术特征分层检索 | 围绕尚未覆盖的技术特征分别检索，避免由单一对象词主导结果。 当前词簇：用途与治疗。 | claims, description, abstract | primary_or_status_check, discovery_and_cross_check, context_only | `("method of treatment" OR "治疗方法" OR "combination" OR "regimen" OR "给药方案")` | planned |
| R4 实施方式与边界检索 | 补检组成、制剂、给药、检测、工艺或用途等案例实际声明的边界特征。 当前词簇：研究对象、靶点/机制、适应症。 | claims, abstract, full_text | primary_or_status_check, discovery_and_cross_check, context_only | `("GLP-1 receptor agonist (class landscape)" OR "semaglutide" OR "司美格鲁肽" OR "liraglutide" OR "tirzepatide" OR "替尔泊肽" OR "orforglipron" OR "oral GLP-1" OR "小分子GLP-1" OR "GLP-1受体激动剂" OR "GLP-1RA" OR "glucagon-like peptide-1 receptor agonist" OR "peptide GLP-1" OR "GIP/GLP-1 dual" OR "索马鲁肽" OR "利拉鲁肽") AND ("GLP1R (glucagon-like peptide 1 receptor)" OR "GLP-1R" OR "GLP-1 receptor" OR "glucagon-like peptide 1 receptor" OR "胰高血糖素样肽-1受体" OR "GLP1R") AND ("type 2 diabetes mellitus; obesity/overweight; cardiovascular risk" OR "2型糖尿病" OR "T2DM" OR "肥胖" OR "超重" OR "体重管理" OR "MACE/心血管结局" OR "NASH/MASH" OR "diabetes" OR "obesity")` | planned |
| R5 未充分命中特征补检 | 根据初筛中未命中或仅部分命中的技术特征，补充术语、别名、译名、分类号和相邻实施方式。 | claims, description, CPC/IPC | primary_or_status_check, discovery_and_cross_check, context_only | `("GLP-1 receptor agonist (class landscape)" OR "semaglutide" OR "司美格鲁肽" OR "liraglutide" OR "tirzepatide" OR "替尔泊肽" OR "orforglipron" OR "oral GLP-1" OR "小分子GLP-1" OR "GLP-1受体激动剂" OR "GLP-1RA" OR "glucagon-like peptide-1 receptor agonist" OR "peptide GLP-1" OR "GIP/GLP-1 dual" OR "索马鲁肽" OR "利拉鲁肽") AND ("GLP1R (glucagon-like peptide 1 receptor)" OR "GLP-1R" OR "GLP-1 receptor" OR "glucagon-like peptide 1 receptor" OR "胰高血糖素样肽-1受体" OR "GLP1R") AND ("type 2 diabetes mellitus; obesity/overweight; cardiovascular risk" OR "2型糖尿病" OR "T2DM" OR "肥胖" OR "超重" OR "体重管理" OR "MACE/心血管结局" OR "NASH/MASH" OR "diabetes" OR "obesity") AND ("method of treatment" OR "治疗方法" OR "combination" OR "regimen" OR "给药方案")` | planned |
| R6 IPC/CPC 组合检索 | 用当前案例声明或从高相关文献反向确认的分类号补足漏检。 | IPC, CPC, claims | classification_navigation, primary_or_status_check, discovery_and_cross_check | `("GLP-1 receptor agonist (class landscape)" OR "semaglutide" OR "司美格鲁肽" OR "liraglutide" OR "tirzepatide" OR "替尔泊肽" OR "orforglipron" OR "oral GLP-1" OR "小分子GLP-1" OR "GLP-1受体激动剂" OR "GLP-1RA" OR "glucagon-like peptide-1 receptor agonist" OR "peptide GLP-1" OR "GIP/GLP-1 dual" OR "索马鲁肽" OR "利拉鲁肽") AND ("GLP1R (glucagon-like peptide 1 receptor)" OR "GLP-1R" OR "GLP-1 receptor" OR "glucagon-like peptide 1 receptor" OR "胰高血糖素样肽-1受体" OR "GLP1R") AND ("type 2 diabetes mellitus; obesity/overweight; cardiovascular risk" OR "2型糖尿病" OR "T2DM" OR "肥胖" OR "超重" OR "体重管理" OR "MACE/心血管结局" OR "NASH/MASH" OR "diabetes" OR "obesity")` | planned |
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
