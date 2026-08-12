# FTO 防侵权检索计划：p53_patent_case

> 本文件用于公开专利候选初筛与后续 claim chart 准备，不构成侵权/不侵权法律意见。

## 1. 技术方案

围绕 p53 靶点肿瘤治疗领域进行研发立项调研：评估进入 MDM2-p53 拮抗剂、突变 p53 再激活、p53 基因治疗/溶瘤病毒、p53 疫苗与 p53 蛋白降解等方向的专利壁垒、技术路线与创新空间。

## 2. 技术特征

| ID | 类型 | 重要性 | 技术特征 | 分类号 |
|---|---|---|---|---|
| F01 | core | core | 小分子恢复 p53 肿瘤抑制功能（MDM2-p53 界面拮抗或突变 p53 再激活）用于肿瘤治疗 | A61K31/00, C07D, A61P35/00 |
| F02 | necessary | necessary | 靶点特异性：TP53 野生型恢复 vs 突变 p53（尤其 Y220C）的选择性 | C07D, A61K31/40 |
| F03 | support | support | p53 基因递送：腺病毒/溶瘤病毒载体表达野生型 p53 | C12N15/861, A61K48/00 |
| F04 | support | support | 联合治疗与伴随诊断：MDM2 拮抗剂联用、p53 生物标志物患者分层 | A61K45/06, C12Q1/6886, G01N33/574 |
| F05 | context | context | p53 蛋白降解（PROTAC/degronimer）新机制方向 | C07D, A61K47/55 |

## 3. 扩展关键词

| 词簇 | 基础词 | 扩展词 | 关联特征 | 来源 |
|---|---|---|---|---|
| 靶点/机制 | p53、TP53 | tumor protein p53、p53 tumor suppressor、p53 reactivation、mutant p53、p53-Y220C、MDM2、MDMX、MDM4、p53-MDM2 interaction、p53、TP53、tumor suppressor p53、p53靶点、抑癌基因p53、p53突变、p53再激活 | F01, F02 | scope/identity + mechanism |
| 机制词 | MDM2 antagonist、p53 reactivator | MDM2-p53 inhibitor、nutlin、mutant p53 reactivation、PRIMA-1、quinuclidinone、Y220C、MDM2 inhibitor、p53 activator、MDM2拮抗剂、p53激活、p53再激活剂 | F01 | scope/identity |
| 适应症 | cancer | tumor、solid tumor、hematologic malignancy、AML、MDS、lymphoma、TP53-mutant cancer、cancer、malignancy、neoplasm、肿瘤、癌症、实体瘤、血液肿瘤 | F01 | scope/identity |
| 突变/标志物 | TP53-mutant | p53 Y220C、p53 mutation、TP53 mutation、p53 biomarker、TP53 status、mutant p53、Y220C、p53突变、Y220C突变、p53生物标志物 | F02 | scope/identity + claims |
| 基因治疗 | p53 gene therapy | adenoviral p53、Ad5CMV-p53、oncolytic adenovirus p53、tumor suppressor gene therapy、Ad-p53、Gendicine、Advexin、SCH-58500、ONYX-015、p53基因治疗、腺病毒p53、溶瘤腺病毒 | F03 | scope/identity |
| 联合治疗 | combination therapy | MDM2 inhibitor combination、p53 reactivator combination、BCL-2 inhibitor combination、immune checkpoint combination、rituximab combination、co-administration、combination、联合用药、联合治疗 | F04 | claims + literature |
| 伴随诊断/分层 | p53 biomarker | biomarker profile、patient selection、companion diagnostic、response prediction、TP53 status biomarker、biomarker、生物标志物、伴随诊断、患者分层 | F04 | claims + clinical context |
| 蛋白降解 | PROTAC | MDM2 degrader、targeted protein degradation、degronimer、MDM2-based PROTAC、PROTAC、degrader、protein degradation、蛋白降解、降解剂 | F05 | claims + literature |

## 4. IPC/CPC

A61K31/00, C07D, A61P35/00, A61K31/40, C12N15/861, A61K48/00, A61K45/06, C12Q1/6886, G01N33/574, A61K47/55

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
| R1 核心对象与用途组合检索 | 锁定核心技术特征在标题、摘要和权利要求中的共同披露。 当前词簇：靶点/机制、机制词、适应症。 | title, abstract, claims | primary_or_status_check, discovery_and_cross_check | `("p53" OR "TP53") AND ("MDM2 antagonist" OR "p53 reactivator") AND ("cancer")` | planned |
| R2 同义词与机制扩展 | 用案例声明的别名、同义词、译名和机制词扩大召回，并回到权利要求核验。 当前词簇：靶点/机制、机制词、适应症、突变/标志物、基因治疗。 | full_text, claims, CPC/IPC | primary_or_status_check, discovery_and_cross_check | `("p53" OR "TP53" OR "tumor protein p53" OR "p53 tumor suppressor" OR "p53 reactivation" OR "mutant p53" OR "p53-Y220C" OR "MDM2" OR "MDMX" OR "MDM4" OR "p53-MDM2 interaction" OR "tumor suppressor p53" OR "p53靶点" OR "抑癌基因p53" OR "p53突变" OR "p53再激活") AND ("MDM2 antagonist" OR "p53 reactivator" OR "MDM2-p53 inhibitor" OR "nutlin" OR "mutant p53 reactivation" OR "PRIMA-1" OR "quinuclidinone" OR "Y220C" OR "MDM2 inhibitor" OR "p53 activator" OR "MDM2拮抗剂" OR "p53激活" OR "p53再激活剂") AND ("cancer" OR "tumor" OR "solid tumor" OR "hematologic malignancy" OR "AML" OR "MDS" OR "lymphoma" OR "TP53-mutant cancer" OR "malignancy" OR "neoplasm" OR "肿瘤" OR "癌症" OR "实体瘤" OR "血液肿瘤") AND ("TP53-mutant" OR "p53 Y220C" OR "p53 mutation" OR "TP53 mutation" OR "p53 biomarker" OR "TP53 status" OR "mutant p53" OR "Y220C" OR "p53突变" OR "Y220C突变" OR "p53生物标志物") AND ("p53 gene therapy" OR "adenoviral p53" OR "Ad5CMV-p53" OR "oncolytic adenovirus p53" OR "tumor suppressor gene therapy" OR "Ad-p53" OR "Gendicine" OR "Advexin" OR "SCH-58500" OR "ONYX-015" OR "p53基因治疗" OR "腺病毒p53" OR "溶瘤腺病毒")` | planned |
| R3 技术特征分层检索 | 围绕尚未覆盖的技术特征分别检索，避免由单一对象词主导结果。 当前词簇：联合治疗、伴随诊断/分层、蛋白降解。 | claims, description, abstract | primary_or_status_check, discovery_and_cross_check, context_only | `("combination therapy" OR "MDM2 inhibitor combination" OR "p53 reactivator combination" OR "BCL-2 inhibitor combination" OR "immune checkpoint combination" OR "rituximab combination" OR "co-administration" OR "combination" OR "联合用药" OR "联合治疗") AND ("p53 biomarker" OR "biomarker profile" OR "patient selection" OR "companion diagnostic" OR "response prediction" OR "TP53 status biomarker" OR "biomarker" OR "生物标志物" OR "伴随诊断" OR "患者分层") AND ("PROTAC" OR "MDM2 degrader" OR "targeted protein degradation" OR "degronimer" OR "MDM2-based PROTAC" OR "degrader" OR "protein degradation" OR "蛋白降解" OR "降解剂")` | planned |
| R4 实施方式与边界检索 | 补检组成、制剂、给药、检测、工艺或用途等案例实际声明的边界特征。 当前词簇：伴随诊断/分层、蛋白降解。 | claims, abstract, full_text | primary_or_status_check, discovery_and_cross_check, context_only | `("p53 biomarker" OR "biomarker profile" OR "patient selection" OR "companion diagnostic" OR "response prediction" OR "TP53 status biomarker" OR "biomarker" OR "生物标志物" OR "伴随诊断" OR "患者分层") AND ("PROTAC" OR "MDM2 degrader" OR "targeted protein degradation" OR "degronimer" OR "MDM2-based PROTAC" OR "degrader" OR "protein degradation" OR "蛋白降解" OR "降解剂")` | planned |
| R5 未充分命中特征补检 | 根据初筛中未命中或仅部分命中的技术特征，补充术语、别名、译名、分类号和相邻实施方式。 | claims, description, CPC/IPC | primary_or_status_check, discovery_and_cross_check, context_only | `("p53" OR "TP53" OR "tumor protein p53" OR "p53 tumor suppressor" OR "p53 reactivation" OR "mutant p53" OR "p53-Y220C" OR "MDM2" OR "MDMX" OR "MDM4" OR "p53-MDM2 interaction" OR "tumor suppressor p53" OR "p53靶点" OR "抑癌基因p53" OR "p53突变" OR "p53再激活") AND ("MDM2 antagonist" OR "p53 reactivator" OR "MDM2-p53 inhibitor" OR "nutlin" OR "mutant p53 reactivation" OR "PRIMA-1" OR "quinuclidinone" OR "Y220C" OR "MDM2 inhibitor" OR "p53 activator" OR "MDM2拮抗剂" OR "p53激活" OR "p53再激活剂") AND ("cancer" OR "tumor" OR "solid tumor" OR "hematologic malignancy" OR "AML" OR "MDS" OR "lymphoma" OR "TP53-mutant cancer" OR "malignancy" OR "neoplasm" OR "肿瘤" OR "癌症" OR "实体瘤" OR "血液肿瘤") AND ("TP53-mutant" OR "p53 Y220C" OR "p53 mutation" OR "TP53 mutation" OR "p53 biomarker" OR "TP53 status" OR "mutant p53" OR "Y220C" OR "p53突变" OR "Y220C突变" OR "p53生物标志物") AND ("p53 gene therapy" OR "adenoviral p53" OR "Ad5CMV-p53" OR "oncolytic adenovirus p53" OR "tumor suppressor gene therapy" OR "Ad-p53" OR "Gendicine" OR "Advexin" OR "SCH-58500" OR "ONYX-015" OR "p53基因治疗" OR "腺病毒p53" OR "溶瘤腺病毒") AND ("combination therapy" OR "MDM2 inhibitor combination" OR "p53 reactivator combination" OR "BCL-2 inhibitor combination" OR "immune checkpoint combination" OR "rituximab combination" OR "co-administration" OR "combination" OR "联合用药" OR "联合治疗") AND ("p53 biomarker" OR "biomarker profile" OR "patient selection" OR "companion diagnostic" OR "response prediction" OR "TP53 status biomarker" OR "biomarker" OR "生物标志物" OR "伴随诊断" OR "患者分层") AND ("PROTAC" OR "MDM2 degrader" OR "targeted protein degradation" OR "degronimer" OR "MDM2-based PROTAC" OR "degrader" OR "protein degradation" OR "蛋白降解" OR "降解剂")` | planned |
| R6 IPC/CPC 组合检索 | 用当前案例声明或从高相关文献反向确认的分类号补足漏检。 | IPC, CPC, claims | classification_navigation, primary_or_status_check, discovery_and_cross_check | `("p53" OR "TP53" OR "tumor protein p53" OR "p53 tumor suppressor" OR "p53 reactivation" OR "mutant p53" OR "p53-Y220C" OR "MDM2" OR "MDMX" OR "MDM4" OR "p53-MDM2 interaction" OR "tumor suppressor p53" OR "p53靶点" OR "抑癌基因p53" OR "p53突变" OR "p53再激活") AND ("MDM2 antagonist" OR "p53 reactivator" OR "MDM2-p53 inhibitor" OR "nutlin" OR "mutant p53 reactivation" OR "PRIMA-1" OR "quinuclidinone" OR "Y220C" OR "MDM2 inhibitor" OR "p53 activator" OR "MDM2拮抗剂" OR "p53激活" OR "p53再激活剂") AND ("cancer" OR "tumor" OR "solid tumor" OR "hematologic malignancy" OR "AML" OR "MDS" OR "lymphoma" OR "TP53-mutant cancer" OR "malignancy" OR "neoplasm" OR "肿瘤" OR "癌症" OR "实体瘤" OR "血液肿瘤") AND ("A61K31/00" OR "C07D" OR "A61P35/00" OR "A61K31/40" OR "C12N15/861" OR "A61K48/00" OR "A61K45/06" OR "C12Q1/6886" OR "G01N33/574" OR "A61K47/55")` | planned |
| R7 关系与边界扩展 | 从高相关文献扩展同族、申请人、引用、分案/继续申请和邻近技术。 | family, assignee, citations, legal_events | primary_or_status_check, discovery_and_cross_check | `已命中文献的 family / assignee / citation / continuity expansion; 不使用自由文本替代权利要求核验` | planned |

## 7. 初筛规则

- 核心特征命中 + 权利要求类别相关：进入高优先级人工复核。
- 必要特征命中但缺少核心对象或法域成员：标记为边界候选。
- 仅说明书/摘要或相邻分类号命中：作为线索，不升级为覆盖结论。
- 状态来自聚合镜像时标记待核验；以目标法域官方登记簿和审查档案为准。

## 8. 待补证据

- P53 靶点领域专利总量极大，本案例按全靶点概览收录各方向代表族，FTO 初筛为立项前的方向级信号，不构成侵权结论。
- 所有状态均需回目标法域官方登记簿复核。
- 若后续进入具体分子立项，应建立分子级 fto-input 并按 R1-R7 逐轮检索。
- 每一轮的真实结果数量、纳排决定和官方法律状态需要在检索后回填。
- FTO 风险必须基于目标法域的完整独立权利要求和截至日期状态复核。
