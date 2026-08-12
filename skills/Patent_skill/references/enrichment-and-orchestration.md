# 结构化情报富集与可恢复编排参考

本参考提取可迁移的工作模式，不复制任何第三方数据库、API 地址、密钥、源码或商业排序算法。

## 1. 可迁移模式

| 模式 | 迁移到医药专利 Skill 的用法 | 约束 |
|---|---|---|
| 实体消歧 | 先解析分子/代号/靶点/疾病/申请人，再检索 | 不要默认采用第一条自动补全结果 |
| 范围暂停点 | 在正式检索前确认法域、时间、技术主题、深度和语言 | 范围未确认时降低结论强度 |
| AUTO/PAUSE 分工 | 脚本负责规范化、去重、统计、组装；模型负责范围、语义分类、claim 解读和缺口判断 | 模型不单独决定法律状态 |
| 关系扩展 | 从核心族扩展同族、分案、引证、申请人、靶点邻居和适应症竞品 | 扩展结果要分核心/边界/排除 |
| 缺口分析 | 根据已采集字段缺失自动生成下一轮检索任务 | “没有数据”不等于“事件不存在” |
| 分层竞争 | 直接竞争、同类/亚型、通路邻近、标准治疗 | 专利族地图中的技术相关不等于法律同族 |
| 分段写作 | 摘要、专利景观、研发上下文、战略洞察分别形成可验证片段 | 最终统一引用和免责声明 |
| 可恢复状态 | state.json + 阶段清单 + 产物最小校验 + 调用日志 | 不要覆盖已有有效产物 |
| HTML/PDF 双交付 | HTML 负责交互和钻取，PDF 负责归档/答辩 | PDF 不应丢失来源与限制说明 |

## 2. 可选的搜索富集层

### 实体解析

若存在授权的结构化药物数据库，优先使用实体 ID 进行：

- drug/compound detail；
- target detail/target analysis；
- disease/indication/organization autocomplete；
- mechanism-of-action 和 drug-type resolution。

如果没有连接器，用公开名称词表、官方注册号、临床注册号、论文 DOI 和专利文本自行建立 `entity_resolution.json`。

### 竞争与通路

建议将相关研发对象分成四层：

1. **Direct**：同一靶点、同一适应症、相近作用机制；
2. **Class/isoform**：同靶点家族、亚型或同类机制；
3. **Pathway**：上游、下游、旁路或合成致死节点；
4. **Standard of care**：临床路径中的化疗、抗体或标准治疗。

这些层级用于技术路线和竞品背景，不替代专利族判断。每个对象记录 `entity_id | relation_type | evidence | source | confidence`。

### 临床、交易、新闻和文献

作为专利解释层，可追加：

- 临床：阶段、注册号、患者人群、终点、公开结果；
- 交易：许可方/被许可方、时间、区域、金额、权利范围；
- 新闻：公司、项目、临床、监管和负面事件；
- 文献：机制、耐药、药效、安全性、转化医学。

这些内容分别进入 `context/clinical`、`context/deals`、`context/news`、`context/literature`，并在主报告中明确标注为研发/商业事实，不得用来证明专利保护范围。

## 3. 缺口驱动的补检

自动或人工生成 gap brief，至少检查：

| 缺口 | 典型补检 |
|---|---|
| 关键试验只有注册号 | ClinicalTrials.gov、ChiCTR、监管公开资料 |
| 专利族有成员但状态不明 | CNIPA、USPTO Patent Center、EPO Register |
| 耐药机制只有专利描述 | PubMed、综述、原始研究、临床队列 |
| 交易没有金额或区域 | 公司公告、SEC 文件、交易双方公告 |
| 申请人有同靶点项目但未命中 | 公司 pipeline、专利申请人/发明人扩展 |
| 结构/序列检索不可用 | 骨架、取代基、功能描述和 claims/full text |

每个 gap task 保存：`id | priority | objective | rationale | suggested_queries | output_file | status`。

## 4. 调用与来源日志

结构化数据或网页检索统一记录 JSONL：

```json
{
  "call_id": "SRC-001",
  "timestamp": "2026-08-05T00:00:00+08:00",
  "source_type": "official_register|patent_text|structured_db|web|literature",
  "source": "CNIPA/USPTO/WIPO/EPO/other",
  "query_or_endpoint": "...",
  "parameters": {},
  "result_count": 0,
  "notes": "..."
}
```

API 调用日志用于复现和审计，不应把任何访问凭证、token 或私有响应原文写入报告。

## 5. 输出编排

推荐阶段：

```text
scope → identity → core_search → family_normalization
→ claim_extraction → status_snapshot → optional_context
→ gap_brief → roadmap_and_risk → visualization
→ compose_html → export_pdf → finalize
```

每一阶段产生文件并做最小校验；失败时指出缺失文件、证据缺口和回退位置。最终报告同时给出“已确认事实、来源、推断、未解决问题”。
