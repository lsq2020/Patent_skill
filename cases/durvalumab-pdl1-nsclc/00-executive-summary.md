# 执行摘要

> 案例：`durvalumab-pdl1-nsclc` · 生成时间：2026-08-07T09:49:32.719627+00:00 · 本报告为研究资料，不构成法律意见。

## 研究范围

- **研究对象**：Durvalumab
- **靶点**：PD-L1
- **适应症**：non-small cell lung cancer (NSCLC)
- **目标法域**：CN, US
- **关联法域**：WO, EP
- **截至**：2026-08-07
- **深度**：standard_analysis
- **主要申请人**：未提供（详情见[执行摘要](00-executive-summary.md)）

## 模块化交付

本案例将事实抽取、族地图、技术路线、风险/FTO、创新空间和证据链拆成独立报告。每份报告可以单独阅读，也可以通过 `report-index.md` 回到同一组结构化数据。

## 数据规模

| 指标 | 数量/状态 | 说明 |
|---|---|---|
| 专利族 | 7 | 以案例族 CSV 的 family_id 为统计单位 |
| claim 要素记录 | 9 | 逐条保留文献号、claim 类别、位置和 coverage |
| 证据链条目 | 7 | 事实、推断、来源、定位和复核动作 |
| FTO 候选 | 7 | 排序是复核优先级，不是侵权概率 |
| 检索轮次 | 7 | 由 FTO/query plan 生成的可恢复策略 |
| 来源目录 | 140 | 可选来源 URL，不代表本案已全部访问 |

## 当前最重要的信号

- **HIGH · DVL-FAM-004**：Durvalumab/PD-1-axis inhibition with concurrent platinum-based chemoradiation for unresectable stage III NSCLC；完整命中特征 F01, F02, F03, F04, F05；部分命中 无；[WO2022248478A1](https://patents.google.com/patent/WO2022248478A1/en)。
- **HIGH · DVL-FAM-002**：Durvalumab plus tremelimumab for selected NSCLC patients；完整命中特征 F01, F02, F04, F05；部分命中 F03；[US20190256603A1](https://patents.google.com/patent/US20190256603A1/en)。
- **HIGH · DVL-FAM-007**：Biomarker for immune checkpoint blockade therapy in NSCLC；完整命中特征 F01, F02, F04, F05；部分命中 F03；[WO2024234348A1](https://patents.google.com/patent/WO2024234348A1/en)。
- **MEDIUM · DVL-FAM-001**：Fc-optimized anti-PD-L1 antibody (durvalumab/MEDI4736) composition and sequence；完整命中特征 F02；部分命中 F01, F03, F04, F05；[US9493565B2](https://patents.google.com/patent/US9493565B2/en)。
- **MEDIUM · DVL-FAM-005**：Human anti-PD-L1 antibody formulation including durvalumab-relevant formulation disclosure；完整命中特征 F02；部分命中 F01, F03, F04, F05；[US20210054079A1](https://patents.google.com/patent/US20210054079A1/en)。

## 最大证据缺口

- 用户给出的 IPC/CPC 作为候选分类号导入；正式检索前应按目标法域分类版本和命中文献反向确认。
- “风险评估”与“发生机制”是技术特征候选，不代表所有相关专利都以风险评估为独立权利要求。
- irAE 监测与处置方案需要单独核对诊断/监测方法、治疗方法、给药方案和组合物权利要求。
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
