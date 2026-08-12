# TfR1（Transferrin Receptor 1 / CD71 / TFRC）医药专利与技术路线报告

## 执行摘要

- **对象**：TfR1（转铁蛋白受体 1，基因 TFRC，蛋白 CD71；别名 transferrin receptor protein 1、p90、T9）。已与 TfR2（TFR2）和配体转铁蛋白（TF）做了消歧。
- **法域/时间**：重点 CN、US，关联观察 WO、EP、JP 等；检索与状态快照截至 2026-08-06。
- **核心结论**：TfR1 专利景观围绕一条主线展开——**把 TfR1 当作“分子卡车”的受体介导递送（RMT）**，分成三大技术阵营：(1) 血脑屏障（BBB）穿梭/中枢递送（Roche/Genentech、JCR Pharma、Ossianix、Denali、Regeneron 等）；(2) 肌肉靶向寡核苷酸偶联物（Dyne、Avidity、Sapreme，靶向 DMD/DM1/FSHD 等肌病）；(3) 肿瘤靶向的 CD71 偶联物/可活化抗体（AbbVie、CytomX、GenAhead、Inatherys）。铁代谢/铁死亡与诊断影像构成边界空间。
- **最大不确定性**：本报告的“状态”来自 Google Patents 聚合镜像的筛查快照（Google 明示其状态不是法律结论）；CN/US 官方登记簿（CNIPA、USPTO Patent Center）和 EPO Register 尚未逐族核验。任何 FTO/有效性结论都需要律师复核。

## 研究范围与方法

- **检索入口**：Google Patents 查询 XHR 接口（多路径、高精度→高召回）＋ Google Patents 详情页（经 Jina Reader 镜像抓取）；检索式、日期、命中数记录在 `source-log.jsonl`。
- **词表**：transferrin receptor 1 / TfR1 / CD71 / TFRC / transferrin receptor protein 1，叠加 antibody、blood-brain barrier、transcytosis、conjugate、ADC、lysosomal enzyme、bispecific、VNAR、peptide、muscle、cancer 等技术形态词。
- **纳排**：以“明确以 TfR1/CD71 为结合靶点的抗体/结合分子/偶联物/递送载体”为核心；排除仅把 TfR 当机制背景的文献（如铁代谢综述性专利），并把“ADC（模数转换器）”等电子工程噪音排除。结果分核心命中/边界命中/排除项。
- **族口径**：DOCDB simple family 主去重（比较优先权申请号），INPADOC extended family 做技术关联；分案/continuation/不同国家阶段单独保留为子分支。代表文献选择“权利要求最完整、与研究法域相关”的成员。
- **证据等级**：E1 官方登记簿（待核验）、E2 专利局公开文本（本次已抽取的代表族）、E3 WIPO/EPO/USPTO 聚合数据（Google 族/状态页面）、E4 聚合数据库、E5 推断。

## 专利族地图（25 族，含 3 个边界族）

| 阵营 | 代表族 | 申请人 | 最早优先权 | 代表文献 |
|---|---|---|---|---|
| BBB/CNS 递送 | TFR-FAM-001 | Roche/Genentech | 2013-05-20 | EP3594240B1 |
| BBB/CNS 递送 | TFR-FAM-002（安全分支） | Genentech/Roche | 2012-05-21 | JP6905966B2 |
| BBB/CNS 递送 | TFR-FAM-003（半抗原穿梭） | Roche | 2014-01-03 | US11273223B2 |
| BBB/CNS 递送 | TFR-FAM-004（单价穿梭） | Roche | 2014-01-06 | US20200071413A1 |
| BBB/CNS 递送 | TFR-FAM-005（定制亲和力） | Roche | 2015-06-24 | JP6975508B2 |
| BBB/CNS 递送 | TFR-FAM-006（scFv+酶融合） | JCR Pharma | 2013-12-25 | US9994641B2 |
| BBB/CNS 递送 | TFR-FAM-007/008（新抗体克隆） | JCR Pharma | 2015-06-24 / 2016-12-26 | EP3315606B1 / JP7588199B2 |
| BBB/CNS 递送 | TFR-FAM-009（冻干制剂） | JCR Pharma | 2016-12-28 | US12178858B2 |
| BBB/CNS 递送 | TFR-FAM-010/011/012（VNAR/肽） | Ossianix | 2014-11-14 / 2017-11-02 / 2016-08-06 | US11918647B2 / US12297286B2 |
| BBB/CNS 递送 | TFR-FAM-021（运输载体） | Denali | 2017-02-17 | EP3583120B1 / US11732023B2 |
| BBB/CNS 递送 | TFR-FAM-022 | Regeneron | 2015-12-08 | ES3045508T3 |
| 肌肉/寡核苷酸递送 | TFR-FAM-013 | Dyne | 2018-08-02（抗体支线 2021-07-09） | US11839660B2 / US11795234B2 |
| 肌肉/寡核苷酸递送 | TFR-FAM-014 | Avidity | 2018-12-21 / 2022-04-05 | JP7654757B2 / US12359202B2 |
| 肌肉/寡核苷酸递送 | TFR-FAM-018 | Sapreme | 2018-12-21 | EP4015003B1 |
| 肿瘤/偶联物 | TFR-FAM-015 | AbbVie | 2017-10-14 | US20240115724A1 |
| 肿瘤/偶联物 | TFR-FAM-016 | CytomX | 2015-05-04 | US20220306759A1 |
| 肿瘤/偶联物 | TFR-FAM-017 | GenAhead Bio | 2016-06-20 | JP7536328B2 |
| 肿瘤/偶联物 | TFR-FAM-019 | Inatherys | 2015-07-22 | CA2992509C |
| 肽/研究工具 | TFR-FAM-020 | Fred Hutchinson | 2018-12-14 | JP7664158B2 |
| 边界：纳米载体 | TFR-FAM-023 | UT Austin/SynerGene | 2006-09-12 | US8821943B2 |
| 边界：铁死亡/铁代谢 | TFR-FAM-024 | Columbia | 2012-04-02 | US10597381B2 |
| 边界：诊断/影像 | TFR-FAM-025 | Lumicell | 2009-05-27 | US11592396B2 |

## 核心族明细（抽取要点）

### 1. Roche/Genentech：anti-TfR1 BBB 穿梭平台（TFR-FAM-001/002/003/004/005）
- **TFR-FAM-001（EP3594240B1，优先权 2013-05-20，EP 2023-12-06 授权）**：独立权利要求覆盖“结合人 TfR 与灵长类 TfR、不抑制转铁蛋白结合”的抗体（VH SEQ ID NO:153 / VL SEQ ID NO:105）；核心工程思想是**降低亲和力 + 消除效应功能（ADCC）或 pH 敏感结合**，以减少对 TfR 高表达的网织红细胞（reticulocyte）的耗竭副作用，同时保持 BBB 转胞吞；双特异格式（anti-BACE1/anti-Abeta/anti-tau 等）用于阿尔茨海默等 CNS 病。这是罗氏“Brain Shuttle”的核心族。
- **TFR-FAM-002（Genentech，2012-05-21）**：专注于“提高 BBB 运输安全性”，即网织红细胞耗竭的给药/工程化缓解（EPO、铁剂联合或降低暴露）。
- **TFR-FAM-003（US11273223B2，2014-01-03）**：第二代平台——**抗半抗原/抗 BBBR 双特异性“通用穿梭”**，一个 anti-TfR（或 LRP8）双特异抗体结合半抗原化载荷（biotin/digoxigenin 等），从而无需为每种载荷重新设计抗体；效力沉默 Fc（LALA-PG）。
- **TFR-FAM-004（单价穿梭模块）与 TFR-FAM-005（定制亲和力）**：均为罗氏穿梭平台的格式/亲和力分支。

### 2. JCR Pharma：anti-hTfR scFv + 溶酶体酶融合（TFR-FAM-006/007/008/009）
- **TFR-FAM-006（US9994641B2，2013-12-25）**：单链 anti-human TfR 抗体（识别 hTfR 肽段 SEQ ID NOs:1-3）C 端融合 CNS 蛋白，例如艾杜糖醛酸-2-硫酸酯酶（I2S，Hunter 综合征）——即用 anti-TfR 把酶替换疗法（ERT）带过 BBB 治疗 CNS 型溶酶体贮积症。这是 JCR 血脑屏障 ERT 平台的基石。
- TFR-FAM-007/008 为新克隆迭代，TFR-FAM-009 为冻干制剂保护层。

### 3. Ossianix：鲨鱼 VNAR 单域抗体（TFR-FAM-010/011/012）
- **TFR-FAM-010（US11918647B2，2014-11-14）**：护士鲨 VNAR（~12 kDa 单域抗体）选择性结合人 TfR-1 顶端结构域（aa 215-380），不阻断转铁蛋白结合、不结合 TfR-2、pH 依赖可逆结合、诱导内吞、人鼠交叉反应；VNAR-Fc 融合与 TfR1/BACE1 双特异用于 BBB 或肠道递送。区别于常规 IgG 穿梭的小分子抗体片段路线。

### 4. Dyne / Avidity / Sapreme：TfR1 肌肉靶向寡核苷酸偶联物（TFR-FAM-013/014/018）
- **TFR-FAM-013（Dyne，US11839660B2/US11795234B2，基础优先权 2018-08-02）**：anti-TfR1 抗体（Fab/IgG，识别 TfR1 表位 258-291 与/或 358-381，KD 1e-11~1e-6 M，不抑制转铁蛋白结合、人+猴交叉反应）通过可裂解连接子（valine-citrulline 等）共价连接寡核苷酸载荷（DUX4/DMD/DMPK 靶向的 ASO/gapmer/RNAi/PMO/gRNA），实现肌肉靶向递送，治疗 FSHD、DMD、DM1 等肌病。多个 US 授权成员与 CN 国家阶段（CN115349013B、CN116194470B、CN114025805B）。
- **TFR-FAM-014（Avidity，JP7654757B2，2018-12-21）**：anti-TfR 抗体-寡核苷酸偶联物（AOC），DMD 外显子跳跃（US12359202B2 覆盖 anti-TfR1-PMO 外显子 44 偶联物）。
- **TFR-FAM-018（Sapreme，EP4015003B1，2018-12-21）**：anti-CD71/TfR AOC 加皂素类内体逃逸增强剂，解决寡核苷酸胞内释放瓶颈。

### 5. 肿瘤 CD71 偶联物/可活化抗体（TFR-FAM-015/016/017/019）
- **AbbVie（2017-10-14）anti-CD71 可活化 ADC**、**CytomX（2015-05-04）anti-CD71 可活化抗体**：用“前体/遮蔽”降低 anti-CD71 对正常 TfR 高表达组织（红细胞前体、增殖细胞）的脱靶毒性，肿瘤微环境蛋白酶激活。**GenAhead Bio（2016-06-20）anti-CD71 ADC**。**Inatherys（2015-07-22）anti-TfR** 用于增殖性/炎症疾病。

### 6. Denali / Regeneron（TFR-FAM-021/022）
- **Denali（2017-02-17）**：工程化 TfR1 结合“运输载体”（engineered Fc/antibody），分支覆盖亲和力方法、ERT 酶融合、progranulin 融合与双特异蛋白——其 TV 平台用于中枢神经系统大分子递送。
- **Regeneron（2015-12-08）**：TfR 介导的治疗性酶内化递送组合物。

## 权利要求要素矩阵（节选）

| 族 | 对象 | 结构/组成 | 功能/机制 | 方法/用途 | 状态 |
|---|---|---|---|---|---|
| TFR-FAM-001 | 抗体 | 序列定义（VH:153/VL:105） | 结合人+灵长 TfR、不抑制转铁蛋白；低亲和/pH敏感；效应沉默 | 跨 BBB 递送 CNS 药物；双特异(BACE1/Aβ/tau) | EP 授权（镜像显示 Active） |
| TFR-FAM-003 | 双特异抗体 | 半抗原臂(生物素/DIG)+BBBR臂 | 通用半抗原穿梭；效力沉默 Fc | CNS 递送半抗原化载荷 | US 授权（Active） |
| TFR-FAM-006 | scFv 融合蛋白 | scFv(表位 SEQ1-3)+CNS蛋白(I2S等) | 跨 BBB ERT | Hunter/Hurler 脑病、神经退行 | US 授权（Active） |
| TFR-FAM-010 | VNAR 单域抗体 | 序列库 SEQ1-184 | 结合 TfR1 顶端域、不抑制转铁蛋白、不结合 TfR2、pH依赖 | BBB/GI 递送载荷；TfR1/BACE1 双特异 | US 授权（Active） |
| TFR-FAM-013 | 偶联物 | anti-TfR1 抗体+寡核苷酸(vc 连接子) | 肌肉内吞、不抑制转铁蛋白 | DMD/DM1/FSHD 治疗 | US 多件授权（Active） |
| TFR-FAM-021 | 工程化多肽 | 工程化 TfR1 结合 Fc/载体 | 脑递送 | ERT/蛋白递送 | EP/US 授权（镜像） |

完整矩阵见 `tfr1-claim-elements.csv`；“明确披露/可能覆盖”区分摘要披露与独立权利要求限定。

## 技术路线图（两条可对照的线）

**研发事实线（文献/临床共识，E4 背景）**：
`铁需求/增殖细胞高表达 TfR1 → 配体转铁蛋白摄取 → 受体介导转胞吞(RMT) → 被改造为跨 BBB 的“特洛伊木马” → 抗体/片段/载体携带 CNS 药物或酶 → 肌肉/肿瘤组织选择性递送 → 临床应用（阿尔茨海默、溶酶体贮积症、DMD/DM1/FSHD、肿瘤）`

**专利保护线（本次族证据）**：
`anti-TfR1 抗体组成（TFR-FAM-001/006/007/010/013）→ 亲和力/效应功能/表位工程（001/005/013）→ 穿梭格式（单价/双特异/半抗原，003/004/010）→ 载荷偶联（酶融合 006/021，寡核苷酸 013/014/018，ADC 015/017，可活化 015/016）→ 制剂与安全（009/002）→ 适应症（肌病 013/014，CNS 001/006/021，肿瘤 015/016/019）`

两条线在“RMT 递送”机制上一致；不一致处在于：专利保护多集中在抗体/格式/连接子层面，而“哪种适应症先用”由临床决定，专利文本通常不限定单一适应症。

## 风险提示（信号分级，非法律结论）

- **高复核优先**：若拟实施“以 anti-TfR1 抗体携带载荷跨 BBB/入肌肉”的技术方案，TFR-FAM-001/003/006/010/013/021 的独立权利要求存在高重叠信号，需逐一制作 claim chart 并核验 CN/US 授权状态与分案/继续申请。
- **中复核优先**：Roche 2012 安全族（002）、JCR 新克隆（007/008/009）、Avidity/Sapreme AOC（014/018）、肿瘤 CD71 偶联物（015/016/017/019）、Denali（021）——主题或必要特征部分命中。
- **状态待核验**：全部 25 族的 CN/US 官方状态均为“待核验”；本次仅采集了 Google 镜像的聚合状态。
- **边界信号**：转移铁蛋白-配体纳米载体（023）、铁死亡机制（024）、TfR/CD71 诊断影像（025）属于相邻空间，不直接构成 TfR1 核心 FTO，但纳入创新空间讨论。

## 创新空间假设（逐项“假设—证据—反例—验证”）

1. **组织选择性/低脱靶 anti-TfR1 抗体**：现有 anti-CD71 的瓶颈是红细胞前体/增殖组织毒性。可活化（probody）或 pH 敏感设计已有 TFR-FAM-015/016/001/010 证据；空白点在于“肿瘤微环境特异激活 + 保留 BBB 递送”的组合尚少见直接族证据。反例：多族覆盖亲和力/遮蔽概念，需律师 claim chart 确认自由度。
2. **寡核苷酸胞内释放增强**：Sapreme（018）覆盖皂素内体逃逸；其他内体逃逸肽/脂质体系与 anti-TfR1 偶联的组合空间存在空白表现。反例：存在未检索的 continuation。
3. **TfR1 靶向的 mRNA/siRNA/基因编辑载体**：现有证据集中在 ASO/PMO（013/014）与酶融合（006/021）；mRNA 脂质体与 anti-TfR1 或转铁蛋白配体偶联在核心族中未见直接族证据（仅边界 023 纳米载体）。反例：可能以其他靶向词检索到；需补检。
4. **新表位/结构域选择性**：FAM-001（转铁蛋白结合位点外）、FAM-010（顶端域 215-380）、FAM-013（258-291/358-381）已占位；针对 TfR1 二聚化界面或其他表位、且不与现有表位竞争的结合分子可能是空白。反例：Markush/表位权利要求可能覆盖。
5. **联合/给药方案**：FAM-002 已覆盖“联合 EPO/铁剂以保护网织红细胞”的给药策略；空白点在于“anti-TfR1 递送 + 免疫检查点或其他疗法”的联合方案族证据有限。反例：需确认未检索盲区。

## 证据链（节选）

- 事实：EP3594240B1 权利要求的核心要素（人+灵长 TfR、不抑制转铁蛋白、效应沉默/低亲和）来自该专利公开文本（E2）——TFR-E-001。
- 事实：US9994641B2 覆盖 anti-hTfR scFv + I2S 融合治疗 Hunter 脑病（E2）——TFR-E-004。
- 事实：US11918647B2 覆盖 VNAR 对 TfR-1 的选择性、TfR-2 排除与 BBB/GI 递送（E2）——TFR-E-005。
- 推断/待核验：全部族的状态来自 Google 聚合镜像（E3），官方登记簿（E1）未核验——TFR-E-011。
- 检索盲区：Google Patents 接口本次限流，详情页经 Jina 镜像获取；未覆盖 Espacenet/CNIPA 原生检索与 WIPO 中文检索；JP/EP 机器翻译文本存在误差风险。

完整证据链见 `tfr1-evidence.csv`。

## 附录

- 检索式与命中数：`source-log.jsonl`、`web_research/_search_summary.json`（含 15 组查询，命中数 1.7k~145k 不等，ADC 词有电子噪音需剔除）。
- 族数据：`tfr1-patent-families.csv`；权利要求要素：`tfr1-claim-elements.csv`；证据链：`tfr1-evidence.csv`。
- 可视化：`tfr1-landscape.html`、`tfr1-landscape-v2.html`、`report-visuals.html`、`visuals/*.svg`。
- 模块化报告：`00-executive-summary.md`~`07-source-catalog-report.md`、`report-index.md`。
- 未解决问题：CN/US 官方状态核验（25 族）；anti-CD71 肿瘤偶联物族的完整 claim 文本；WIPO PATENTSCOPE 中文检索；anti-TfR1 直接肿瘤治疗（非递送）的经典抗体族补检。

> 免责声明：本报告是研究资料，不是法律意见、FTO 结论、侵权/无效结论或医疗建议。任何商业或申报决策前，请由目标法域专利律师基于官方登记簿与完整权利要求复核。
