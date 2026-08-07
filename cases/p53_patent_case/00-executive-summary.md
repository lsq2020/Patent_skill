# 执行摘要

> 案例：`p53_patent_case` · 生成时间：2026-08-07T17:04:47.961508+00:00 · 本报告为研究资料，不构成法律意见。

## 研究范围

- **研究对象**：p53-targeted therapies (MDM2-p53 antagonists, mutant p53 reactivators, p53 gene therapy, p53 vaccines)
- **靶点**：TP53 (p53 tumor suppressor protein, cellular tumor antigen p53)
- **适应症**：cancer (solid tumors, hematologic malignancies, and therapy-resistant states)
- **目标法域**：US, CN, WO, EP
- **关联法域**：WO, EP, JP, KR, AU
- **截至**：2026-08-07
- **深度**：standard_analysis
- **主要申请人**：F. Hoffmann-La Roche AG, Novartis AG, Ascentage Pharma, Kartos Therapeutics / MD Anderson, Daiichi Sankyo, Amgen Inc., Aprea Therapeutics AB / Inc., PMV Pharmaceuticals, Inc., Jacobio Pharmaceuticals Co., Ltd. / 北京加科思新药研发有限公司, Canji, Inc., Shenzhen SiBiono GeneTech Co., Ltd., Introgen Therapeutics, Multivir Inc., The Regents of the University of Michigan, Arvinas Operations, Inc., C4 Therapeutics, Inc., Critical Outcome Technologies Inc., Aileron Therapeutics, The Regents of the University of Texas System, Hangzhou Converd/Convero Co., Ltd.（详情见[执行摘要](00-executive-summary.md)）

## 申请人与角色

（本表是全案唯一列出完整角色说明的位置；其余模块报告只显示申请人名称。）

- F. Hoffmann-La Roche AG (idasanutlin/RG7388, RG7112; MDM2 领域先驱)
- Novartis AG (siremadlin/HDM201, MDM2-p53 抑制剂与剂量方案)
- Ascentage Pharma (Suzhou) Co., Ltd. (APG-115/alrizomadlin, BCL-2+MDM2 联用)
- Kartos Therapeutics / MD Anderson (navtemadlin/KRT-232, 肿瘤治疗与眼科)
- Daiichi Sankyo (milademetan/DS-3032b)
- Amgen Inc. (AMG-232, MDM2 联用疗法)
- Aprea Therapeutics AB / Inc. (APR-246/eprenetapopt/PRIMA-1MET)
- PMV Pharmaceuticals, Inc. (rezatapopt/PC14586, p53-Y220C 再激活)
- Jacobio Pharmaceuticals Co., Ltd. / 北京加科思新药研发有限公司 (突变 p53 靶向化合物)
- Canji, Inc. (Schering) (腺病毒介导 p53 基因治疗, Ad-p53/SCH-58500)
- Shenzhen SiBiono GeneTech Co., Ltd. (深圳赛百诺, Gendicine/今又生 Ad5CMV-p53)
- Introgen Therapeutics (Advexin/INGN-201)
- Multivir Inc. (p53 生物标志物、肿瘤抑制基因治疗)
- The Regents of the University of Michigan (MDM2 蛋白降解剂)
- Arvinas Operations, Inc. (MDM2 靶向 PROTAC)
- C4 Therapeutics, Inc. (靶向蛋白降解, MDM2)
- Critical Outcome Technologies Inc. (COTI-2)
- Aileron Therapeutics (稳定 p53 肽)
- The Regents of the University of Texas System (溶瘤腺病毒, E1A/E1B 突变体)
- Hangzhou Converd/Convero Co., Ltd. (杭州康万达, 溶瘤腺病毒 p53)

## 模块化交付

本案例将事实抽取、族地图、技术路线、风险/FTO、创新空间和证据链拆成独立报告。每份报告可以单独阅读，也可以通过 `report-index.md` 回到同一组结构化数据。

## 数据规模

| 指标 | 数量/状态 | 说明 |
|---|---|---|
| 专利族 | 25 | 以案例族 CSV 的 family_id 为统计单位 |
| claim 要素记录 | 36 | 逐条保留文献号、claim 类别、位置和 coverage |
| 证据链条目 | 26 | 事实、推断、来源、定位和复核动作 |
| FTO 候选 | 25 | 排序是复核优先级，不是侵权概率 |
| 检索轮次 | 7 | 由 FTO/query plan 生成的可恢复策略 |
| 来源目录 | 140 | 可选来源 URL，不代表本案已全部访问 |

## 当前最重要的信号

- **HIGH · P53-FAM-010**：突变 p53 再激活（rezatapopt/PC14586, p53-Y220C）；完整命中特征 F01, F02, F04；部分命中 无；[EP4034104B1](https://patents.google.com/patent/EP4034104B1/en)。
- **HIGH · P53-FAM-008**：突变 p53 再激活（APR-246/eprenetapopt）及联用；完整命中特征 F01, F02, F04；部分命中 无；[WO2021053155A1](https://patents.google.com/patent/WO2021053155A1/en)。
- **HIGH · P53-FAM-023**：MDM2 拮抗剂伴随诊断生物标志物（大冢制药）；完整命中特征 F01, F02, F04；部分命中 无；[US20230338337A1](https://patents.google.com/patent/WO2021133772A1/en)。
- **HIGH · P53-FAM-025**：p53 疗法联合免疫治疗（Multivir）；完整命中特征 F01, F02, F04；部分命中 无；[WO2021113644A1](https://patents.google.com/patent/WO2021113644A1/en)。
- **HIGH · P53-FAM-022**：突变 p53 再激活中国跟进（p53-Y220C, 长春金赛）；完整命中特征 F01, F02；部分命中 无；[CN117986235A](https://patents.google.com/patent/CN117986235A/en)。

## 最大证据缺口

- P53 靶点领域专利总量极大，本案例按全靶点概览收录各方向代表族，FTO 初筛为立项前的方向级信号，不构成侵权结论。
- 所有状态均需回目标法域官方登记簿复核。
- 若后续进入具体分子立项，应建立分子级 fto-input 并按 R1-R7 逐轮检索。
- 每一轮的真实结果数量、纳排决定和官方法律状态需要在检索后回填。
- FTO 风险必须基于目标法域的完整独立权利要求和截至日期状态复核。

## 统计可视化

[打开 FTO 风格统计总览](report-visuals.html) · 图表由当前案例 CSV/JSON 自动生成。

### 专利族技术主题分布

![专利族技术主题分布](visuals/family-theme-distribution.svg)

> 统计口径：按 family_id 统计，每族归入一个主技术阶段。

### 最早优先权年度分布

![最早优先权年度分布](visuals/priority-year-distribution.svg)

> 统计口径：按族级 earliest_priority 的年份统计（趋势折线）。

### FTO 复核优先级

![FTO 复核优先级](visuals/risk-priority-distribution.svg)

> 统计口径：按 fto-candidate-ranking.csv 的 review_priority 统计（状态色板）；是复核队列，不是侵权概率。

## 独立报告索引

- [权利要求与要素抽取报告](01-extraction-report.md)
- [专利族地图报告](02-patent-family-map-report.md)
- [技术路线图报告](03-technology-roadmap-report.md)
- [风险与 FTO 报告](04-risk-and-fto-report.md)
- [创新空间假设报告](05-innovation-space-report.md)
- [证据链报告](06-evidence-chain-report.md)
- [来源目录报告](07-source-catalog-report.md)

## 结论边界

本摘要不把摘要命中、聚合网站状态或模型推断升级为权利要求覆盖、有效性或 FTO 结论。正式实施前，优先核验目标法域的完整独立权利要求、国家阶段、分案/继续申请、审查档案和法律事件。
