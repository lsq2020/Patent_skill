# 执行摘要

> 案例：`trem2-atherosclerosis` · 生成时间：2026-08-07T02:40:54.233544+00:00 · 本报告为研究资料，不构成法律意见。

## 研究范围

- **研究对象**：TREM2-targeted therapeutics (agonist antibodies, small molecules; no single lead molecule specified)
- **靶点**：TREM2
- **适应症**：atherosclerosis
- **目标法域**：CN, US
- **关联法域**：WO, EP
- **截至**：2026-08-06
- **深度**：standard_analysis
- **主要申请人**：Alector LLC / Alector, Inc., Amgen Inc., Denali Therapeutics Inc., Vigil Neuroscience, Inc., iTeos Therapeutics（详情见[执行摘要](00-executive-summary.md)）

## 申请人与角色

（本表是全案唯一列出完整角色说明的位置；其余模块报告只显示申请人名称。）

- Alector LLC / Alector, Inc.（激动性抗体原研方；AL002与AbbVie合作）
- Amgen Inc.（激动性抗体原研方，US11186636B2、hT2AB/WO2022120373A1；小分子项目后分拆予Vigil）
- Denali Therapeutics Inc.（激动性抗体+ATV血脑屏障递送平台，DNL919/TAK-920，与Takeda合作）
- Vigil Neuroscience, Inc.（口服小分子激动剂VG-3927，2025年5月被Sanofi收购）
- iTeos Therapeutics（拮抗性抗体EOS006215，肿瘤方向；公司披露收到Concentra Biosciences收购要约）

## 模块化交付

本案例将事实抽取、族地图、技术路线、风险/FTO、创新空间和证据链拆成独立报告。每份报告可以单独阅读，也可以通过 `report-index.md` 回到同一组结构化数据。

## 数据规模

| 指标 | 数量/状态 | 说明 |
|---|---|---|
| 专利族 | 9 | 以案例族 CSV 的 family_id 为统计单位 |
| claim 要素记录 | 12 | 逐条保留文献号、claim 类别、位置和 coverage |
| 证据链条目 | 10 | 事实、推断、来源、定位和复核动作 |
| FTO 候选 | — | 排序是复核优先级，不是侵权概率 |
| 检索轮次 | — | 由 FTO/query plan 生成的可恢复策略 |
| 来源目录 | — | 可选来源 URL，不代表本案已全部访问 |

## 当前最重要的信号


## 最大证据缺口


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
