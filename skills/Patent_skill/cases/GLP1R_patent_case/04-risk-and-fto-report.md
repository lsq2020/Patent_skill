# 风险与 FTO 报告

> 案例：`GLP1R_patent_case` · 生成时间：2026-08-07T11:20:26.718863+00:00 · 本报告为研究资料，不构成法律意见。

## 研究范围

- **研究对象**：GLP-1 receptor agonist (class landscape)
- **靶点**：GLP1R (glucagon-like peptide 1 receptor)
- **适应症**：type 2 diabetes mellitus; obesity/overweight; cardiovascular risk
- **目标法域**：CN, US, WO, EP
- **关联法域**：WO, EP
- **截至**：2026-08-07
- **深度**：standard_analysis
- **主要申请人**：Novo Nordisk A/S, Eli Lilly and Company, Gilead Sciences, Inc., Zealand Pharma A/S, Sanofi, Qilu Regor Therapeutics Inc., Eccogene, Hangzhou Zhongmeihuadong Pharmaceutical, Hangzhou Derui Zhizhi / Mindrank AI, Shionogi & Co., Ltd., Jiangsu Hengrui Pharmaceuticals, Fujian Shengdi Pharmaceutical, Beijing Hanmi Pharmaceutical, Chongqing Kangding Medical Technology, Gasherbrum Bio, Inc., Twist Bioscience Corporation, Amgen Inc., CMPD Licensing, LLC, Pfizer Inc., Boehringer Ingelheim（详情见[执行摘要](00-executive-summary.md)）

## 1. 风险边界

本报告识别的是值得继续核验的重叠信号和 FTO 工作队列，不是侵权、不侵权、有效性或自由实施法律意见。排序分数只代表复核优先级。

## 2. 拟实施方案与特征分级

围绕 GLP-1 receptor agonist (class landscape)、GLP1R (glucagon-like peptide 1 receptor) 和 type 2 diabetes mellitus; obesity/overweight; cardiovascular risk 的拟实施技术方案，进行组成、用途、给药、检测或组合治疗的 FTO 初筛。

| ID | 类型 | 重要性 | 技术特征 | 词簇 | IPC/CPC |
|---|---|---|---|---|---|
| F01 | core | core | GLP-1 receptor agonist (class landscape) 用于 type 2 diabetes mellitus; obesity/overweight; cardiovascular risk，作用于 GLP1R (glucagon-like peptide 1 receptor)。 | drug, target, indication | — |
| F02 | necessary | necessary | 治疗或检测步骤包含给药对象、方案或患者分层。 | use | — |

## 3. FTO 候选族排序

| 优先级 | 族 | 代表文献 | 主题 | 排序分数 | 完整命中 | 部分命中 | claim 类别 | 状态信号 | 状态来源 |
|---|---|---|---|---|---|---|---|---|---|
| HIGH | F02 | [US11008375B2](https://patents.google.com/patent/US11008375B2/en) | dual GIP/GLP-1 peptide agonist | 100.0% | F01, F02 | 无 | composition; compound; method_of_treatment | granted(US/CN) | Google Patents (E3) |
| HIGH | F03 | [US12091404B2](https://patents.google.com/patent/US12091404B2/en) | small-molecule GLP-1R agonist | 100.0% | F01, F02 | 无 | combination; composition; compound; method_of_treatment | granted(US/TW/AU) | Google Patents (E3) |
| HIGH | F05 | [US11584751B1](https://patents.google.com/patent/US11584751B1/en) | small-molecule GLP-1R agonist | 100.0% | F01, F02 | 无 | compound; method_of_treatment | granted(US) | Google Patents (E3) |
| HIGH | F06 | [US11981666B2](https://patents.google.com/patent/US11981666B2/en) | small-molecule GLP-1R agonist | 100.0% | F01, F02 | 无 | composition; compound; method_of_treatment | granted(US/CN); pending elsewhere | Google Patents (E3) |
| HIGH | F08 | [US20240374587A1](https://patents.google.com/patent/US20240374587A1/en) | combination; composition | 100.0% | F01, F02 | 无 | combination | pending | Google Patents (E3) |
| HIGH | F09 | [CN112469731B](https://patents.google.com/patent/CN112469731B/en) | dual GIP/GLP-1 peptide agonist | 100.0% | F01, F02 | 无 | compound | granted(CN/TW) | Google Patents (E3) |
| HIGH | F15 | [CN113773310B](https://patents.google.com/patent/CN113773310B/en) | small-molecule GLP-1R agonist | 100.0% | F01, F02 | 无 | compound | granted(CN) | Google Patents (E3) |
| HIGH | F17 | [US12391762B2](https://patents.google.com/patent/US12391762B2/en) | antibody; GLP1R modulator | 100.0% | F01, F02 | 无 | antibody | granted(US/JP) | Google Patents (E3) |
| HIGH | F18 | [JP7574253B2](https://patents.google.com/patent/JP7574253B2/en) | peptide GLP-1R agonist; method_of_treatment | 100.0% | F01, F02 | 无 | method_of_treatment | granted(JP/ES) | Google Patents (E3) |
| HIGH | F19 | [WO2025042974A1](https://patents.google.com/patent/WO2025042974A1/en) | topical administration; delivery | 100.0% | F01, F02 | 无 | delivery | pending | Google Patents (E3) |
| MEDIUM | F01 | [US20240277817A1](https://patents.google.com/patent/US20240277817A1/en) | oral formulation; solid composition | 72.9% | F02 | F01 | composition; formulation | granted(ES)/pending(US) - 待核验 | Google Patents (E3); EPO register pending |
| MEDIUM | F12 | [US9789165B2](https://patents.google.com/patent/US9789165B2/en) | dual GLP-1/GIP peptide agonist | 72.9% | F02 | F01 | compound | granted(US/EP) | Google Patents (E3) |
| MEDIUM | F20 | [HK40111760A](https://patents.google.com/patent/HK40111760A/en) | combination; formulation | 72.9% | F02 | F01 | composition | pending | Google Patents (E3) |
| MEDIUM | F04 | [US20260035362A1](https://patents.google.com/patent/US20260035362A1/en) | small-molecule GLP-1R agonist | 56.1% | F01 | 无 | compound; process | granted(AU/CN)/pending(US) | Google Patents (E3) |
| MEDIUM | F07 | [CN117242067B](https://patents.google.com/patent/CN117242067B/en) | small-molecule GLP-1R agonist | 56.1% | F01 | 无 | compound | granted(CN) | Google Patents (E3) |
| MEDIUM | F16 | [EP4229050A1](https://patents.google.com/patent/EP4229050A1/en) | small-molecule GLP-1R agonist | 56.1% | F01 | 无 | compound | pending | Google Patents (E3) |
| MEDIUM | F13 | [HK40113396A](https://patents.google.com/patent/HK40113396A/en) | dual GLP-1/GIP peptide agonist; formulation | 53.9% | F02 | 无 | composition | pending | Google Patents (E3) |
| LOW | F10 | [US11518795B2](https://patents.google.com/patent/US11518795B2/en) | peptide GLP-1 derivative | 22.1% | 无 | F01 | compound | granted(US) | Google Patents (E3) |
| LOW | F11 | [EP2190872B1](https://patents.google.com/patent/EP2190872B1/en) | peptide GLP-1 derivative | 22.1% | 无 | F01 | compound | granted(EP) | Google Patents (E3) |
| LOW | F14 | [EP2718317B1](https://patents.google.com/patent/EP2718317B1/en) | GIP analog; long-acting conjugate | 3.0% | 无 | 无 | compound; conjugate | granted(EP/KR) | Google Patents (E3) |

## 统计可视化

[打开 FTO 风格统计总览](report-visuals.html) · 图表由当前案例 CSV/JSON 自动生成。

### FTO 复核优先级

![FTO 复核优先级](visuals/risk-priority-distribution.svg)

> 统计口径：按 fto-candidate-ranking.csv 的 review_priority 统计（状态色板）；是复核队列，不是侵权概率。

### 状态信号分布

![状态信号分布](visuals/status-distribution.svg)

> 统计口径：把官方状态和状态来源文字归入研究阶段信号（状态色板），不替代官方法律状态。

### 权利要求类别分布

![权利要求类别分布](visuals/claim-category-distribution.svg)

> 统计口径：按 claim-elements.csv 的 claim_category 记录数统计。

## 4. 逐族 claim 要素风险

### F02 · HIGH · US11008375B2

- **触发事实**：dual GIP/GLP-1 peptide agonist；完整命中 `F01, F02`；部分命中 `无`。
- **状态限制**：granted(US/CN)；来源：Google Patents (E3)。
- **claim 记录**：compound: GIP analogue Formula I with X2=Aib, X16=Lys, C-ext Y1, acylated Lys; composition: Pharmaceutical composition (injection/infusion or slow release); method_of_treatment: Treating diabetes/diabetes-related or obesity/obesity-related disorder。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F03 · HIGH · US12091404B2

- **触发事实**：small-molecule GLP-1R agonist；完整命中 `F01, F02`；部分命中 `无`。
- **状态限制**：granted(US/TW/AU)；来源：Google Patents (E3)。
- **claim 记录**：compound: Compound of defined structure; composition: Pharmaceutical composition + carrier/excipient; combination: Combination with anti-obesity agent (PYY, NPYR2 agonist, SGLT2i, ACCi, etc.); method_of_treatment: Method of treating GLP-1R mediated disease。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F05 · HIGH · US11584751B1

- **触发事实**：small-molecule GLP-1R agonist；完整命中 `F01, F02`；部分命中 `无`。
- **状态限制**：granted(US)；来源：Google Patents (E3)。
- **claim 记录**：compound: Substituted imidazole Formula (I): R1=phenyl, R2=heteroaryl/indazolyl, T=oxadiazolyl; method_of_treatment: Modulating GLP-1R activity; indications incl. obesity, diabetes, Alzheimer's, CVD, liver disease。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F06 · HIGH · US11981666B2

- **触发事实**：small-molecule GLP-1R agonist；完整命中 `F01, F02`；部分命中 `无`。
- **状态限制**：granted(US/CN); pending elsewhere；来源：Google Patents (E3)。
- **claim 记录**：compound: Compound Formula II-4 (aryl-alkyl-acid; R1=F/Cl); composition: Pharmaceutical composition + carrier; method_of_treatment: Treating GLP-1R mediated disease (diabetes, obesity, dyslipidemia, etc.)。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F08 · HIGH · US20240374587A1

- **触发事实**：combination; composition；完整命中 `F01, F02`；部分命中 `无`。
- **状态限制**：pending；来源：Google Patents (E3)。
- **claim 记录**：combination: Combo of (A) GLP-1R agonist fused-ring compound + (B) anti-obesity/blood glucose/cholesterol/BP drug; combination: (B) selected from GLP-1 agonists incl. semaglutide, tirzepatide, danuglipron, PF07081532, LY-3502970, RGT-075。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F09 · HIGH · CN112469731B

- **触发事实**：dual GIP/GLP-1 peptide agonist；完整命中 `F01, F02`；部分命中 `无`。
- **状态限制**：granted(CN/TW)；来源：Google Patents (E3)。
- **claim 记录**：compound: GIP/GLP1 co-agonist compounds (tirzepatide-class)。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F15 · HIGH · CN113773310B

- **触发事实**：small-molecule GLP-1R agonist；完整命中 `F01, F02`；部分命中 `无`。
- **状态限制**：granted(CN)；来源：Google Patents (E3)。
- **claim 记录**：compound: GLP-1 small molecule with cardiovascular benefit。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F17 · HIGH · US12391762B2

- **触发事实**：antibody; GLP1R modulator；完整命中 `F01, F02`；部分命中 `无`。
- **状态限制**：granted(US/JP)；来源：Google Patents (E3)。
- **claim 记录**：antibody: Antibody/antibody fragment binding GLP1R with defined VH/VL; antibody: Antibody as GLP1R agonist or antagonist (methods)。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F18 · HIGH · JP7574253B2

- **触发事实**：peptide GLP-1R agonist; method_of_treatment；完整命中 `F01, F02`；部分命中 `无`。
- **状态限制**：granted(JP/ES)；来源：Google Patents (E3)。
- **claim 记录**：method_of_treatment: Method of treating metabolic disorder with GLP-1R agonist。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F19 · HIGH · WO2025042974A1

- **触发事实**：topical administration; delivery；完整命中 `F01, F02`；部分命中 `无`。
- **状态限制**：pending；来源：Google Patents (E3)。
- **claim 记录**：delivery: Topical administration of GLP-1R agonist (oral cavity/skin)。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F01 · MEDIUM · US20240277817A1

- **触发事实**：oral formulation; solid composition；完整命中 `F02`；部分命中 `F01`。
- **状态限制**：granted(ES)/pending(US) - 待核验；来源：Google Patents (E3); EPO register pending。
- **claim 记录**：composition: Solid oral composition of GLP-1 agonist + SNAC salt; formulation: Solid composition comprising GLP-1 agonist and SNAC。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F12 · MEDIUM · US9789165B2

- **触发事实**：dual GLP-1/GIP peptide agonist；完整命中 `F02`；部分命中 `F01`。
- **状态限制**：granted(US/EP)；来源：Google Patents (E3)。
- **claim 记录**：compound: Dual GLP-1/GIP receptor agonist peptides (exendin-4 based)。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F20 · MEDIUM · HK40111760A

- **触发事实**：combination; formulation；完整命中 `F02`；部分命中 `F01`。
- **状态限制**：pending；来源：Google Patents (E3)。
- **claim 记录**：composition: Pharma composition of GLP-1R + GIPR agonist。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F04 · MEDIUM · US20260035362A1

- **触发事实**：small-molecule GLP-1R agonist；完整命中 `F01`；部分命中 `无`。
- **状态限制**：granted(AU/CN)/pending(US)；来源：Google Patents (E3)。
- **claim 记录**：compound: Compound of specific structure (post-cancellation claims 41-44); process: Process for preparing compound by reacting intermediate with acid; compound: GLP-1R agonist compounds (AU grant)。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F07 · MEDIUM · CN117242067B

- **触发事实**：small-molecule GLP-1R agonist；完整命中 `F01`；部分命中 `无`。
- **状态限制**：granted(CN)；来源：Google Patents (E3)。
- **claim 记录**：compound: Aromatic ether-substituted heterocyclic compound as GLP1R agonist。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F16 · MEDIUM · EP4229050A1

- **触发事实**：small-molecule GLP-1R agonist；完整命中 `F01`；部分命中 `无`。
- **状态限制**：pending；来源：Google Patents (E3)。
- **claim 记录**：compound: Heterocyclic GLP-1 agonists。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F13 · MEDIUM · HK40113396A

- **触发事实**：dual GLP-1/GIP peptide agonist; formulation；完整命中 `F02`；部分命中 `无`。
- **状态限制**：pending；来源：Google Patents (E3)。
- **claim 记录**：composition: Pharma composition of GLP-1 + GIP receptor dual agonist。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F10 · LOW · US11518795B2

- **触发事实**：peptide GLP-1 derivative；完整命中 `无`；部分命中 `F01`。
- **状态限制**：granted(US)；来源：Google Patents (E3)。
- **claim 记录**：compound: Double-acylated GLP-1 derivatives with SEQ ID NOs 3,5,7,9,10。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F11 · LOW · EP2190872B1

- **触发事实**：peptide GLP-1 derivative；完整命中 `无`；部分命中 `F01`。
- **状态限制**：granted(EP)；来源：Google Patents (E3)。
- **claim 记录**：compound: GLP-1 derivatives (acylated) + pharmaceutical compositions。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

### F14 · LOW · EP2718317B1

- **触发事实**：GIP analog; long-acting conjugate；完整命中 `无`；部分命中 `无`。
- **状态限制**：granted(EP/KR)；来源：Google Patents (E3)。
- **claim 记录**：compound: GIP analogs; conjugate: Long-acting conjugate of trigonal glucagon/GLP-1/GIP receptor agonist。
- **下一步**：下载目标法域官方文本；核对完整独立权利要求、分案/继续申请、审查档案、年费/异议/无效和实施方案逐项要素。

## 5. 风险雷达

| 风险层 | 触发条件 | 当前判断 | 必须补证据 |
|---|---|---|---|
| 高复核优先 | 核心对象、机制/用途和独立 claim 要素同时命中 | 进入 claim chart 队列，不等同于侵权 | 完整独立 claim + 官方状态 + 实施方案映射 |
| 中复核优先 | 主题或必要特征部分命中，法域/状态不完整 | 保留为重叠信号 | 国家阶段、分支、审查档案 |
| 边界候选 | 相邻通路、诊断或竞争方案，缺少对象级 claim linkage | 用于召回和创新空间，不计入核心 FTO | 对象特异性 claim、更多检索入口 |

## 6. FTO 结论边界

当前数据不足以确认自由实施或侵权。若要进入商业决策，应先对高优先族逐项制作 claim chart，并由目标法域专利律师复核法律状态和解释问题。
