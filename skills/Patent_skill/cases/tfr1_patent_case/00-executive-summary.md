# 执行摘要

> 案例：`tfr1_patent_case` · 生成时间：2026-08-06T05:47:44.783064+00:00 · 本报告为研究资料，不构成法律意见。

## 研究范围

- **研究对象**：Transferrin Receptor 1；别名：transferrin receptor 1, TfR1, CD71, TFRC, transferrin receptor protein 1
- **靶点/机制**：TfR1
- **适应症**：broad (cancer, iron metabolism, CNS delivery)
- **法域**：目标法域 CN, US；关联扩展法域 WO, EP
- **截至日期**：2026-08-06
- **深度**：standard_analysis；报告语言：zh
- **来源目录**：上游记录 143 条，去重 URL 140 个；目录不是已访问结果集。
- **申请人消歧**：未提供；需从族记录反向归一化

## 模块化交付

本案例将事实抽取、族地图、技术路线、风险/FTO、创新空间和证据链拆成独立报告。每份报告可以单独阅读，也可以通过 `report-index.md` 回到同一组结构化数据。

## 数据规模

| 指标 | 数量/状态 | 说明 |
|---|---|---|
| 专利族 | 25 | 以案例族 CSV 的 family_id 为统计单位 |
| claim 要素记录 | 32 | 逐条保留文献号、claim 类别、位置和 coverage |
| 证据链条目 | 15 | 事实、推断、来源、定位和复核动作 |
| FTO 候选 | 12 | 排序是复核优先级，不是侵权概率 |
| 检索轮次 | 7 | 由 FTO/query plan 生成的可恢复策略 |
| 来源目录 | 140 | 可选来源 URL，不代表本案已全部访问 |

## 当前最重要的信号

- **LOW · TFR-FAM-013**：Muscle-targeting complexes comprising anti-transferrin receptor antibody linked to an oligonucleotide; uses for muscle diseases (DMD, DM1, FSHD, muscle atrophy, Pompe, Friedreich's ataxia)；完整命中特征 F02；部分命中 F01；[US11795234B2](https://patents.google.com/patent/US11839660B2/en)。
- **LOW · TFR-FAM-015**：Anti-CD71 activatable antibody drug conjugates and methods of use；完整命中特征 F02；部分命中 F01；[US20240115724A1](https://patents.google.com/patent/US20240115724A1/en)。
- **LOW · TFR-FAM-021**：Engineered transferrin receptor binding polypeptides / transport vehicles and uses；完整命中特征 F02；部分命中 F01；[EP3583120B1](https://patents.google.com/patent/EP3583120B1/en)。
- **LOW · TFR-FAM-016**：Anti-CD71 antibodies, activatable anti-CD71 antibodies, and methods of use；完整命中特征 F02；部分命中 F01；[US20220306759A1](https://patents.google.com/patent/US20220306759A1/en)。
- **LOW · TFR-FAM-024**：Compounds, compositions, and methods for modulating ferroptosis；完整命中特征 F02；部分命中 F01；[US10597381B2](https://patents.google.com/patent/US10597381B2/en)。

## 最大证据缺口

- 这是由范围文件自动生成的保守模板，请在正式检索前人工补充技术特征、阈值和分类号。
- 每一轮的真实结果数量、纳排决定和官方法律状态需要在检索后回填。
- FTO 风险必须基于目标法域的完整独立权利要求和截至日期状态复核。

## 统计可视化

[打开 FTO 风格统计总览](report-visuals.html) · 图表由当前案例 CSV/JSON 自动生成。

### 专利族技术主题分布

![专利族技术主题分布](visuals/family-theme-distribution.svg)

> 统计口径：按 family_id 统计，每族归入一个主技术阶段。

### 最早优先权年度分布

![最早优先权年度分布](visuals/priority-year-distribution.svg)

> 统计口径：按族级 earliest_priority 的年份统计。

### FTO 复核优先级

![FTO 复核优先级](visuals/risk-priority-distribution.svg)

> 统计口径：按 fto-candidate-ranking.csv 的 review_priority 统计；是复核队列，不是侵权概率。

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
