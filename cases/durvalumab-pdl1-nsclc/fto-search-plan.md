# FTO 防侵权检索计划：durvalumab-pdl1-nsclc

> 本文件用于公开专利候选初筛与后续 claim chart 准备，不构成侵权/不侵权法律意见。

## 1. 技术方案

肿瘤免疫治疗监测，具体涉及 PD-L1 抑制剂度伐利尤单抗在非小细胞肺癌中的免疫相关不良反应风险评估。度伐利尤单抗与 PD-L1 结合并阻断 PD-1/PD-L1 通路，结合肺部体征、血液生化、胸部影像和腹泻分级监测，识别器官特异性免疫毒性并在结肠炎进展时启动皮质类固醇治疗。

## 2. 技术特征

| ID | 类型 | 重要性 | 技术特征 | 分类号 |
|---|---|---|---|---|
| F01 | technical_domain | context | 肿瘤免疫治疗监测，具体涉及 PD-L1 抑制剂度伐利尤单抗在非小细胞肺癌中的免疫相关不良反应风险评估。 | A61P11/00, A61P43/00, A61K39/395, C07K16/28, A61P37/04, G16H50/30, A61P35/00, C07K16/2818 |
| F02 | core | core | 度伐利尤单抗与 PD-L1 结合并阻断 PD-1/PD-L1 通路，以触发免疫相关不良反应的风险识别。 | A61K39/395, C07K16/28, G01N33/68, A61P35/02, A61P35/00, C07K16/2818, A61P37/02 |
| F03 | core | core | 免疫系统在 PD-1/PD-L1 通路被阻断后对肺部正常组织、肠道黏膜或实质器官产生异常攻击，用于判定器官特异性毒性机制。 | A61P11/00, A61P1/00, A61K39/395, G01N33/50, C07K16/28, A61K45/06, G01N33/68, G01N33/5091, A61P35/00, A61P37/02 |
| F04 | necessary | necessary | 治疗期间对肺部体征进行连续监测，以识别免疫相关性肺炎的呼吸系统异常表现。 | A61B5/00, G16H30/40, G16H30/20, A61B6/00, A61B5/08, G16H50/20, A61B5/4848, A61B6/03 |
| F05 | necessary | necessary | 基线及治疗期间对 ALT、AST、肌酐、TSH、游离 T4 及血糖进行生化检测，以评估肝脏、肾脏及内分泌腺体受累状态。 | G01N33/50, G01N33/68, G01N33/573, G16H50/30, A61P1/16, G01N33/74, A61P13/12, G01N33/53, A61P3/10, G01N33/70 |
| F06 | support | support | 胸部影像学检查显示磨玻璃样影或斑片状浸润影，用于辅助判定免疫相关性肺炎。 | A61B5/00, G16H30/40, A61B6/00, G16H30/20, G16H50/20, A61B6/03, A61B6/032, G06T7/0012 |
| F07 | support | support | 根据腹泻分级启动皮质类固醇治疗，用于控制免疫相关性结肠炎进展。 | A61K31/573, A61P1/00, A61P1/04, A61P37/00, A61P37/06, A61K45/06, A61P29/00 |

## 3. 扩展关键词

| 词簇 | 基础词 | 扩展词 | 关联特征 | 来源 |
|---|---|---|---|---|
| 度伐利尤单抗 | 度伐利尤单抗、durvalumab | 德瓦鲁单抗、度伐鲁单抗、PD-L1抑制剂、Imfinzi、MEDI4736、MEDI-4736、PD-L1 inhibitor | F01, F02, F04, F05 | user-provided aliases + product/development code |
| 非小细胞肺癌 | 非小细胞肺癌、NSCLC、non small cell lung cancer | 肺腺癌、肺鳞癌、肺癌、lung adenocarcinoma、lung carcinoma、non-small-cell lung cancer | F01, F04, F05 | user-provided disease aliases |
| PD-L1 | PD-L1、程序性死亡配体1 | CD274、B7-H1、programmed death ligand 1、programmed death-ligand 1 | F02, F03 | target/protein/gene aliases |
| 阻断 | 阻断、blockade | 拮抗、结合抑制、通路阻断、block、inhibit、antagonize | F02, F03 | mechanism/action terms |
| 免疫相关不良反应 | 免疫相关不良反应、irAE、immune related adverse event | 自身免疫反应、免疫毒性、autoimmune reaction、immunotoxicity、immune-related adverse event | F01, F03, F07 | clinical safety terminology |
| 器官受损 | 器官受损、组织损伤、organ toxicity | 靶器官毒性、实质器官攻击、tissue damage、organ injury、adverse effect | F03 | organ toxicity terminology |
| 肺炎/肺毒性 | 肺炎、pneumonitis | 间质性肺病、肺部炎症、肺毒性、interstitial lung disease、pneumonia、pulmonary toxicity | F04, F06 | pulmonary irAE terminology |
| 体征监测 | 体征监测、monitoring | 呼吸监测、肺部听诊、连续监护、respiratory monitoring、physical sign tracking、surveillance | F04, F06 | monitoring workflow terminology |
| 生化检测 | 生化检测、biochemical test | 生化筛查、血液生化、生化分析、biochemical assay、blood chemistry、serum analysis | F05 | diagnostic/test terminology |
| 生化指标 | ALT、AST、肌酐、TSH、游离T4、血糖 | transaminase、creatinine、free T4、blood glucose、alanine aminotransferase、aspartate aminotransferase、thyroid stimulating hormone | F05 | user-provided analytes + standard English names |
| 胸部影像 | 胸部影像、胸部CT、chest imaging | 肺部影像、胸片、chest CT、thoracic imaging、chest radiograph | F06 | imaging modality terminology |
| 磨玻璃影 | 磨玻璃影、GGO、ground glass opacity | 斑片状浸润、磨玻璃样密度影、patchy infiltrates、ground glass density | F06 | radiology terminology |
| 结肠炎/腹泻 | 结肠炎、colitis | 肠道炎症、腹泻、肠毒性、diarrhea、bowel inflammation、enterocolitis | F07 | gastrointestinal irAE terminology |
| 皮质类固醇 | 皮质类固醇、corticosteroid | 糖皮质激素、激素治疗、类固醇、glucocorticoid、steroid、prednisone | F07 | irAE management terminology |

## 4. IPC/CPC

A61P11/00, A61P43/00, A61K39/395, C07K16/28, A61P37/04, G16H50/30, A61P35/00, C07K16/2818, G01N33/68, A61P35/02, A61P37/02, A61P1/00, G01N33/50, A61K45/06, G01N33/5091, A61B5/00, G16H30/40, G16H30/20, A61B6/00, A61B5/08, G16H50/20, A61B5/4848, A61B6/03, G01N33/573, A61P1/16, G01N33/74, A61P13/12, G01N33/53, A61P3/10, G01N33/70, A61B6/032, G06T7/0012, A61K31/573, A61P1/04, A61P37/00, A61P37/06, A61P29/00

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
| R1 关键词组合检索 | 锁定研究对象、靶点、适应症和风险/监测场景同时出现的文献。 | title, abstract, claims | primary_or_status_check, discovery_and_cross_check | `("度伐利尤单抗" OR "durvalumab") AND ("PD-L1" OR "程序性死亡配体1") AND ("非小细胞肺癌" OR "NSCLC" OR "non small cell lung cancer") AND ("免疫相关不良反应" OR "irAE" OR "immune related adverse event" OR "器官受损" OR "组织损伤" OR "organ toxicity")` | planned |
| R2 机制与通路扩展 | 扩大到 PD-1/PD-L1 结合、阻断、免疫毒性和器官损伤表述。 | full_text, claims, CPC/IPC | primary_or_status_check, discovery_and_cross_check | `("度伐利尤单抗" OR "durvalumab" OR "德瓦鲁单抗" OR "度伐鲁单抗" OR "PD-L1抑制剂" OR "Imfinzi" OR "MEDI4736" OR "MEDI-4736" OR "PD-L1 inhibitor") AND ("PD-L1" OR "程序性死亡配体1" OR "CD274" OR "B7-H1" OR "programmed death ligand 1" OR "programmed death-ligand 1" OR "阻断" OR "blockade" OR "拮抗" OR "结合抑制" OR "通路阻断" OR "block" OR "inhibit" OR "antagonize") AND ("免疫相关不良反应" OR "irAE" OR "immune related adverse event" OR "自身免疫反应" OR "免疫毒性" OR "autoimmune reaction" OR "immunotoxicity" OR "immune-related adverse event" OR "器官受损" OR "组织损伤" OR "organ toxicity" OR "靶器官毒性" OR "实质器官攻击" OR "tissue damage" OR "organ injury" OR "adverse effect")` | planned |
| R3 肺部不良事件专项 | 覆盖免疫相关性肺炎、间质性肺病、肺毒性和呼吸体征连续监测。 | claims, description | primary_or_status_check, discovery_and_cross_check, context_only | `("度伐利尤单抗" OR "durvalumab" OR "德瓦鲁单抗" OR "度伐鲁单抗" OR "PD-L1抑制剂" OR "Imfinzi" OR "MEDI4736" OR "MEDI-4736" OR "PD-L1 inhibitor" OR "非小细胞肺癌" OR "NSCLC" OR "non small cell lung cancer" OR "肺腺癌" OR "肺鳞癌" OR "肺癌" OR "lung adenocarcinoma") AND ("肺炎" OR "pneumonitis" OR "间质性肺病" OR "肺部炎症" OR "肺毒性" OR "interstitial lung disease" OR "pneumonia" OR "pulmonary toxicity") AND ("体征监测" OR "monitoring" OR "呼吸监测" OR "肺部听诊" OR "连续监护" OR "respiratory monitoring" OR "physical sign tracking" OR "surveillance" OR "胸部影像" OR "胸部CT" OR "chest imaging" OR "肺部影像" OR "胸片" OR "chest CT" OR "thoracic imaging" OR "chest radiograph")` | planned |
| R4 生化指标与内分泌监测 | 覆盖 ALT/AST、肌酐、TSH、游离 T4、血糖等基线和治疗期监测。 | claims, abstract, full_text | primary_or_status_check, discovery_and_cross_check, context_only | `("度伐利尤单抗" OR "durvalumab" OR "德瓦鲁单抗" OR "度伐鲁单抗" OR "PD-L1抑制剂" OR "Imfinzi" OR "MEDI4736" OR "MEDI-4736" OR "PD-L1 inhibitor" OR "非小细胞肺癌" OR "NSCLC" OR "non small cell lung cancer" OR "肺腺癌" OR "肺鳞癌" OR "肺癌" OR "lung adenocarcinoma") AND ("生化检测" OR "biochemical test" OR "生化筛查" OR "血液生化" OR "生化分析" OR "biochemical assay" OR "blood chemistry" OR "serum analysis" OR "ALT" OR "AST" OR "肌酐" OR "TSH" OR "游离T4" OR "血糖" OR "transaminase" OR "creatinine")` | planned |
| R5 结肠炎与处置方案 | 覆盖腹泻分级、结肠炎、皮质类固醇和治疗决策。 | claims, description | primary_or_status_check, discovery_and_cross_check, context_only | `("度伐利尤单抗" OR "durvalumab" OR "德瓦鲁单抗" OR "度伐鲁单抗" OR "PD-L1抑制剂" OR "Imfinzi" OR "MEDI4736" OR "MEDI-4736" OR "PD-L1 inhibitor") AND ("结肠炎" OR "colitis" OR "肠道炎症" OR "腹泻" OR "肠毒性" OR "diarrhea" OR "bowel inflammation" OR "enterocolitis") AND ("皮质类固醇" OR "corticosteroid" OR "糖皮质激素" OR "激素治疗" OR "类固醇" OR "glucocorticoid" OR "steroid" OR "prednisone")` | planned |
| R6 IPC/CPC 组合检索 | 用分类号补足检测、抗体、免疫治疗和医疗数据分析类漏检。 | IPC, CPC, claims | classification_navigation, primary_or_status_check, discovery_and_cross_check | `("PD-L1" OR "程序性死亡配体1" OR "CD274" OR "B7-H1" OR "programmed death ligand 1" OR "programmed death-ligand 1" OR "非小细胞肺癌" OR "NSCLC" OR "non small cell lung cancer" OR "肺腺癌" OR "肺鳞癌" OR "肺癌" OR "lung adenocarcinoma" OR "lung carcinoma" OR "non-small-cell lung cancer") AND ("体征监测" OR "monitoring" OR "呼吸监测" OR "肺部听诊" OR "连续监护" OR "respiratory monitoring" OR "physical sign tracking" OR "surveillance" OR "生化检测" OR "biochemical test" OR "生化筛查" OR "血液生化" OR "生化分析" OR "biochemical assay" OR "blood chemistry" OR "serum analysis") AND ("A61P11/00" OR "A61P43/00" OR "A61K39/395" OR "C07K16/28" OR "A61P37/04" OR "G16H50/30" OR "A61P35/00" OR "C07K16/2818" OR "G01N33/68" OR "A61P35/02" OR "A61P37/02" OR "A61P1/00" OR "G01N33/50" OR "A61K45/06" OR "G01N33/5091" OR "A61B5/00" OR "G16H30/40" OR "G16H30/20" OR "A61B6/00" OR "A61B5/08" OR "G16H50/20" OR "A61B5/4848" OR "A61B6/03" OR "G01N33/573")` | planned |
| R7 关系与边界扩展 | 从高相关文献扩展同族、申请人、引用、分案/继续申请和邻近技术。 | family, assignee, citations, legal_events | primary_or_status_check, discovery_and_cross_check | `已命中文献的 family / assignee / citation / continuity expansion; 不使用自由文本替代权利要求核验` | planned |

## 7. 初筛规则

- 核心特征命中 + 权利要求类别相关：进入高优先级人工复核。
- 必要特征命中但缺少核心对象或法域成员：标记为边界候选。
- 仅说明书/摘要或相邻分类号命中：作为线索，不升级为覆盖结论。
- 状态来自聚合镜像时标记待核验；以目标法域官方登记簿和审查档案为准。

## 8. 待补证据

- 用户给出的 IPC/CPC 作为候选分类号导入；正式检索前应按目标法域分类版本和命中文献反向确认。
- “风险评估”与“发生机制”是技术特征候选，不代表所有相关专利都以风险评估为独立权利要求。
- irAE 监测与处置方案需要单独核对诊断/监测方法、治疗方法、给药方案和组合物权利要求。
- 每一轮的真实结果数量、纳排决定和官方法律状态需要在检索后回填。
- FTO 风险必须基于目标法域的完整独立权利要求和截至日期状态复核。
