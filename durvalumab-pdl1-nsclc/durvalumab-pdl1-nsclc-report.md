# 度伐利尤单抗（Durvalumab/MEDI4736）—PD-L1—NSCLC 专利与技术路线快速示例

## 执行摘要

本示例验证通用 `medtech-patent-roadmap` Skill 能否从“实体消歧—多路径检索—专利族归并—权利要求要素—缺口分析—可视化”跑通第二个药物，而不依赖奥希替尼专属逻辑。

范围：度伐利尤单抗（Durvalumab、MEDI4736、MEDI-4736、Imfinzi、度伐利尤单抗），靶点 PD-L1/B7-H1/CD274，适应症 NSCLC，重点法域 CN/US，并观察 WO/EP；截至 2026-08-06；标准分析示例。

初步结果：公开证据支持一条从抗 PD-L1 抗体/序列与 Fc 工程，到 NSCLC 联合治疗、同步放化疗、围手术期方案和制剂的分层路线。耐药突变并未在本次少量专利样本中建立为度伐利尤单抗特异性核心族，因此被保留为补检缺口，而不是被模型填补。

> 重要限制：状态来自公开镜像的筛查快照，Google Patents 明确提示其法律状态可能不是法律结论；CN/US 官方登记簿和审查档案仍需复核。本报告不是法律意见、FTO 或侵权结论。

## 核心族与边界族

| 族 | 主题 | 初步定位 |
|---|---|---|
| DVL-FAM-001 | 抗 PD-L1/B7-H1 抗体、序列与 Fc 工程 | 核心组成族；优先级最高 |
| DVL-FAM-002 | Durvalumab + tremelimumab；PD-L1−/高 CD8+ TIL NSCLC | 核心联合/患者分层族 |
| DVL-FAM-003 | 可切除 NSCLC 的铂类 + durvalumab 围手术期方案 | 核心适应症/给药方案族 |
| DVL-FAM-004 | 局部晚期不可切除 III 期 NSCLC 同步放化疗 | 核心路线扩展候选；需确认 claim 是否具体覆盖 durvalumab |
| DVL-FAM-005 | 人抗 PD-L1 抗体制剂 | 核心制剂层候选；公开 US 申请镜像显示 abandoned，需追踪后续分支 |
| DVL-FAM-006 | Anti-TIGIT + anti-PD-L1 dosing | 边界/竞品通路族，不计入度伐利尤单抗核心族 |
| DVL-FAM-007 | NSCLC ICB biomarker | 边界/邻近标志物族，不等于 durvalumab resistance patent |

## 证据要点

- 原始 B7-H1/PD-L1 家族的公开页面给出 2009-11-24 优先权，并列出 CN、US 等成员；US9493565B2 公开镜像显示 active，但仍需 USPTO/CNIPA 官方确认：<https://patents.google.com/patent/WO2011066389A1/en>、<https://patents.google.com/patent/US9493565B2/en>。
- US20190256603A1 的摘要和家族信息明确描述 durvalumab + tremelimumab 用于 PD-L1 阴性且高 CD8+ TIL 的 NSCLC，并显示 US/CN/WO 等家族成员：<https://patents.google.com/patent/US20190256603A1/en>。
- WO2022248478A1 的公开家族信息还列出 CN117425493A 和 US20240254235A1 等国家阶段公开文本；其公开内容覆盖局部晚期不可切除 III 期 NSCLC 的同步放化疗路线，但国家阶段状态仍需官方复核：<https://patents.google.com/patent/WO2022248478A1/en>。
- WO2024213696A1 公开了可切除 NSCLC 中 durvalumab + 铂类化疗、手术、术后继续给药的周期与剂量结构：<https://patents.google.com/patent/WO2024213696A1/en>。
- US20210054079A1 是制剂层入口，公开镜像显示 US application abandoned；需检查 continuation/divisional 和官方 Patent Center：<https://patents.google.com/patent/US20210054079A1/en>。

## 耐药与生物标志物结论

本次案例不把“免疫治疗耐药”机械等同于单一突变。与小分子激酶抑制剂不同，PD-L1 免疫检查点治疗的失效机制通常需要把肿瘤细胞抗原呈递、IFN/JAK 通路、B2M、肿瘤微环境、T 细胞浸润和替代检查点等证据分层核对。当前仅将 WO2024234348A1 作为 NSCLC ICB biomarker 的邻近入口，不声称它覆盖度伐利尤单抗：<https://patents.google.com/patent/WO2024234348A1/en>。

## 交付物

- `durvalumab-pdl1-nsclc-patent-families.csv`：族级数据，含核心/边界标记和状态置信度；
- `durvalumab-pdl1-nsclc-claim-elements.csv`：初步 claim 要素矩阵；
- `durvalumab-pdl1-nsclc-evidence.csv`：事实、推断、来源和复核动作；
- `durvalumab-pdl1-nsclc-landscape.html`：可按主题、法域和状态筛选的 WIPO 风格 HTML；
- `durvalumab-pdl1-nsclc-roadmap.md`：技术路线、创新空间假设和风险提示；
- `query-matrix.json`、`gap_brief.json`：迁移后的检索编排与缺口驱动补检结果。
