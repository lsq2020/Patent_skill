# 执行摘要

> 案例：`GLP1R_patent_case` · 生成时间：2026-08-07T06:40:29.657750+00:00 · 本报告为研究资料，不构成法律意见。

## 研究范围

- **研究对象**：GLP-1 receptor agonist (class landscape)；别名：semaglutide, 司美格鲁肽, liraglutide, tirzepatide, 替尔泊肽, orforglipron, oral GLP-1, 小分子GLP-1, GLP-1受体激动剂, GLP-1RA, glucagon-like peptide-1 receptor agonist, peptide GLP-1, GIP/GLP-1 dual
- **靶点/机制**：GLP1R (glucagon-like peptide 1 receptor)
- **适应症**：type 2 diabetes mellitus; obesity/overweight; cardiovascular risk
- **法域**：目标法域 CN, US, WO, EP；关联扩展法域 WO, EP
- **截至日期**：2026-08-07
- **深度**：standard_analysis；报告语言：zh
- **来源目录**：上游记录 — 条，去重 URL — 个；目录不是已访问结果集。
- **申请人消歧**：Novo Nordisk A/S (诺和诺德), Eli Lilly and Company (礼来), Gilead Sciences, Inc. (吉利德), Zealand Pharma A/S (西兰制药), Sanofi (赛诺菲), Qilu Regor Therapeutics Inc. (齐鲁锐格), Eccogene (Shanghai) Co., Ltd. (诚益生物), Hangzhou Zhongmeihuadong Pharmaceutical (华东医药/中美华东), Hangzhou Derui Zhizhi / Mindrank AI (杭州德睿智药), Shionogi & Co., Ltd. (盐野义), Jiangsu Hengrui Pharmaceuticals (恒瑞医药), Fujian Shengdi Pharmaceutical (福建盛迪), Beijing Hanmi Pharmaceutical (北京韩美/韩美药品), Chongqing Kangding Medical Technology (重庆康丁医药), Gasherbrum Bio, Inc., Twist Bioscience Corporation, Amgen Inc., CMPD Licensing, LLC, Pfizer Inc., Boehringer Ingelheim

## 模块化交付

本案例将事实抽取、族地图、技术路线、风险/FTO、创新空间和证据链拆成独立报告。每份报告可以单独阅读，也可以通过 `report-index.md` 回到同一组结构化数据。

## 数据规模

| 指标 | 数量/状态 | 说明 |
|---|---|---|
| 专利族 | 20 | 以案例族 CSV 的 family_id 为统计单位 |
| claim 要素记录 | 34 | 逐条保留文献号、claim 类别、位置和 coverage |
| 证据链条目 | 20 | 事实、推断、来源、定位和复核动作 |
| FTO 候选 | — | 排序是复核优先级，不是侵权概率 |
| 检索轮次 | — | 由 FTO/query plan 生成的可恢复策略 |
| 来源目录 | — | 可选来源 URL，不代表本案已全部访问 |

## 当前最重要的信号

1. **小分子口服 GLP-1R 赛道专利密集且多数已授权**：Gilead（F03，US/TW/AU 已授权，含超宽抗肥胖联合权利要求）、Qilu Regor（F04，AU/CN 已授权）、Eccogene（F05，US 已授权）、华东医药（F06，US/CN 已授权，且有晶型/口服制剂续案）、德睿智药（F07，CN 已授权）等构成 2020-2022 优先权高峰。新进入者的结构变体空间被快速压缩。
2. **双/三重激动剂（GIP/GLP-1、GCG/GLP-1/GIP）存在多条已授权肽类族**：Zealand（F02，US/CN 已授权）、Lilly（F09，CN/TW 已授权，tirzepatide 族）、Sanofi（F12，US/EP 已授权）、Hanmi（F14，EP/KR 已授权）。后续双靶点组合需逐条与这些序列限定族比对。
3. **口服给药技术是独立保护层**：Novo oral semaglutide + SNAC 固体组合物族（F01，ES 已授权/多国待核验）是口服 GLP-1 吸收技术的核心障碍；华东（F06）与 Hengrui/福建盛迪（F13/F20）正在用制剂+组合物续案围绕口服剂型布防。
4. **联合用药/组合物权利要求明显扩张**：Gilead F03 权利要求 4 和 Shionogi F08 都明确列出与 SGLT2i、ACC 抑制剂、PYY、其他 GLP-1 激动剂等联合用药，形成「化合物→组合→剂量」多层壁垒；Shionogi F08 甚至点名 danuglipron、PF07081532、LY-3502970、RGT-075 等候选。
5. **早期/试验性赛道仍开放**：Topical GLP-1（CMPD Licensing F19，2023 优先权）、抗体型 GLP1R 激动剂（Twist F17）、Gasherbrum 杂环骨架（F16）等仍以 pending 为主，是本轮检索中相对未饱和的区域。

## 最大证据缺口

1. **官方法律状态未核验（E1 缺口）**：所有状态均来自 Google Patents 聚合视图（E3），未在 USPTO Patent Center、EPO Register、CNIPA、JPO 等官方登记簿逐法域确认授权、年费、期限调整、异议/无效或分案/继续申请。
2. **族归并与成员清单未完整**：`family_id` 基于代表文献与人工归并，未按 DOCDB simple family 逐一重建优先权集合；CN/AU/HK 多件公开文本未提取到结构化 Claims 段（如 AU2020256647B2、CN112469731B、HK40113396A）。
3. **未做结构/序列级比对的 FTO 阅读**：对目标分子的 Markush 范围、盐型/晶型、前药、制剂专利是否存在独立保护，仅有 claim 要素初筛，没有完整独立权利要求 claim chart。
4. **检索覆盖有限**：只使用 Google Patents 单一检索入口；WIPO PATENTSCOPE、EPO Espacenet、CNIPA、USPTO Open Data 未直接执行；IPC/CPC 分类号反向扩展未完成。


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
