# 因果关系建模与审计规则

本文定义 Patent_skill 双链图中的因果语义。它解决的不是“两个节点是否有关”，而是“在什么证据设计、研究对象和适用范围内，可以把一条有向边解释为原因对结果的影响”。机器可校验字段见 `output-schema.json`，案例输入见 `<case-dir>/causal-relationships.json`。

## 判定顺序

1. 先定义源概念、目标概念、时间顺序、研究对象、比较组和结局。
2. 再判断证据设计是否能识别该效应：随机对照、受控前临床实验、监管机制陈述、观察性研究或专家推断。
3. 只在证据设计与结论层级匹配时使用 `causal` 或 `mechanistic`；否则使用 `associative`、`temporal`、`structural` 或 `evidentiary`。
4. 保存 `evidence_ids`、`source_urls`、`rationale`、`evidence_level`、`confidence` 和适用范围。
5. 如果存在混杂、选择偏倚、测量混合或跨物种外推，降低状态/置信度，或明确标记 `not_causal`。

## 关系类型与允许解释

| relation_kind | 可表达的含义 | 不允许的解释 |
|---|---|---|
| `causal` | 干预或暴露对结局的总效应、直接效应或中介效应 | 仅凭共同出现、引文、时间先后或专利披露宣称因果 |
| `mechanistic` | 有实验或监管依据的分子、细胞或安全机制 | 将机制存在直接等同于人体临床获益 |
| `associative` | 相关、共变或非随机组间差异 | 在未控制混杂时使用“导致” |
| `temporal` | 优先权、继续申请、先后顺序 | 把先发生解释为原因 |
| `evidentiary` | finding 或来源支撑节点/边 | 把“有文献”解释为“结论已证实” |
| `structural` | 族、权利要求、申请人、主题等结构关系 | 科学或临床因果 |

## 证据层级的边界

- `randomized_trial`：可支持试验人群、比较组、给药策略、终点和随访期内的总治疗效应。不能自动外推到未入组人群或不同治疗时序。
- `preclinical_experiment`：可支持受控实验系统内的机制或模型内因果。不得升级为人体生存或临床获益。
- `regulatory_statement`：可支持标签确认的作用机制和已识别安全机制；结论范围必须与当前标签一致。
- `observational_study`：默认编码为 `associative`。只有在混杂控制、时间顺序、选择机制和敏感性分析足以支撑时，才可人工升级并记录识别假设。
- `patent_disclosure`：说明申请人披露或主张了某种用途/机制，不独立证明科学因果。
- `expert_inference`：只能使用 `hypothesized`，必须记录可证伪的推断和下一步验证方式。

## Durvalumab 校准示例

- Durvalumab 阻断 PD-L1 与 PD-1/CD80：`mechanistic / established`，由前临床表征和 FDA 机制陈述共同支持。
- Durvalumab 增强 T 细胞活性、降低异种移植模型肿瘤生长：限定为 `preclinical_experiment`，不得连接成人体生存结局。
- PACIFIC 中化放疗后 Durvalumab 对疾病进展/死亡和总生存的影响：`causal / established / randomized_trial / total_effect`，限定于试验纳入人群和终点。
- 近期胸部放疗与肺炎发生率：`associative / not_causal`，因为放疗暴露并非随机，且结局混合免疫性肺炎与放射性肺炎。

## 审计门槛

`mechanistic` 和 `causal` 边必须满足：

- 源、目标和方向明确；
- `evidence_ids` 与 `source_urls` 非空且能反向定位；
- `rationale` 说明为什么该设计能支持该关系；
- `confidence` 已评估；
- 临床效应保存人群、比较组、终点和效应量；
- 前临床关系保存实验系统与外推限制。

构建器和校验器拒绝缺证据、缺来源、缺理由或未评估置信度的因果边。图形界面同时使用线型、箭头、文本标签和账本字段表达语义，不依赖颜色单独传递结论。

## 主要来源

- [FDA IMFINZI prescribing information, May 2026](https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/761069s053lbl.pdf)
- [MEDI4736 preclinical characterization](https://pubmed.ncbi.nlm.nih.gov/25943534/)
- [PACIFIC randomized trial: progression-free survival](https://pubmed.ncbi.nlm.nih.gov/28885881/)
- [PACIFIC five-year outcomes](https://pubmed.ncbi.nlm.nih.gov/35108059/)
