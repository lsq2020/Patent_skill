# case-output.json 数据契约

`case-output.json` 是 CSV、证据链、报告和图谱之间的稳定接口。当前版本为 `1.2`，在 `1.1` 的一等关系边上增加因果概念、统一关系语义和证据门槛。

## 顶层结构

```text
case-output.json
├── schema_version
├── case
├── run
├── metrics
├── records
│   ├── families
│   ├── documents
│   ├── claims
│   ├── evidence
│   ├── concepts
│   ├── relations
│   └── ranking
├── uncertainty
├── failure_cases
├── reports
├── reproducibility
└── contract
```

## 稳定 ID

- `family_id`：沿用族 CSV 的人工稳定 ID，例如 `TFR-FAM-001`。
- `claim_id`：优先沿用输入值；缺失时由 family、document、类别、定位、要素和 coverage 的规范化指纹生成 `CLM-*`。调整 CSV 行顺序不会改变 ID。
- `finding_id`：沿用 evidence CSV 的人工稳定 ID。
- `relation_id`：由 `source_id + relation_type + target_id` 生成 `REL-*`。
- `concept_id`：沿用 `causal-relationships.json` 中的人工稳定 ID。
- 图节点 ID 使用命名空间：`family:*`、`document:*`、`claim:*`、`finding:*`、`concept:*`。

## 关系字段

族记录统一包含：

```json
{
  "representative_document_assignee": "Example Bio LLC",
  "family_ownership_summary": "Example Bio LLC; parent-group ownership requires separate evidence",
  "members": ["US123A1", "US123B2"],
  "priority_set": ["US62/123456"],
  "member_relations": [
    {
      "source_document": "US123A1",
      "relation_type": "NATIONAL_PHASE_OF",
      "target_document": "WO2020123456A1",
      "evidence_ids": ["FIND-001"],
      "source_url": "https://example.test/patent/US123A1",
      "notes": ""
    }
  ],
  "family_relations": [
    {
      "target_family_id": "FAM-001",
      "relation_type": "DIVISIONAL_OF",
      "evidence_ids": ["FIND-001"],
      "notes": ""
    }
  ]
}
```

- `representative_document_assignee` 只记录代表文献来源直接支持的申请人/受让人；图谱的申请人节点优先使用该字段。
- `family_ownership_summary` 用于记录集团归属、转让链或族层汇总，不等同于代表文献的当前受让人。
- `member_relations` 表达同一族内文献之间的 `NATIONAL_PHASE_OF`、`PRIORITY_TO` 等关系，生成 `document:* → document:*` 边。
- `family_relations` 表达不同规范化族之间的 `CONTINUATION_OF`、`CONTINUATION_IN_PART_OF`、`DIVISIONAL_OF`、`NATIONAL_PHASE_OF` 和 `RELATED_TO`，生成 `family:* → family:*` 边。

不从 `notes` 或自然语言族描述自动推断上述关系。旧 `applicant_or_assignee` 字段继续保留；缺少新字段时构建器会以它作为兼容回退。

Evidence 记录统一包含：

```json
{
  "finding_id": "FIND-001",
  "family_ids": ["FAM-001"],
  "claim_ids": ["CLM-..."],
  "concept_ids": ["CONCEPT-..."],
  "link_methods": ["document_no"]
}
```

优先使用输入的 `family_ids` / `claim_ids` / `concept_ids`。缺失时只允许通过完全规范化的 `document_no` 或相同 `source_url` 建立规则关系；无法匹配时保留孤立 finding 并写入质量缺口。

## 一等关系边

每条 `records.relations[]` 包含：

```text
relation_id | source_id | relation_type | target_id
assertion | link_methods | evidence_ids | properties
relation_kind | causal_status | polarity | directness
evidence_level | confidence | rationale | source_urls
```

`assertion` 只允许：

- `direct_fact`：输入字段显式给出；
- `rule_derived`：由文献号或 URL 的确定性匹配得到；
- `model_inference`：模型推断，默认不由构建器自动产生。

边只存一次。反向链接由图谱视图根据入边动态计算。

`relation_kind` 将边分为 `structural`、`evidentiary`、`temporal`、`associative`、`mechanistic` 和 `causal`。只有 `mechanistic` / `causal` 可以表达因果，且必须同时具备非空 `evidence_ids`、`source_urls`、`rationale` 和已评估的 `confidence`。`causal_status` 区分 `established`、`supported` 与 `hypothesized`；专利披露、同族、优先权、引用或共现不得自动升级为因果。

`evidence_level` 记录证据设计，而不是单纯来源名称：`randomized_trial`、`preclinical_experiment`、`regulatory_statement`、`observational_study`、`patent_disclosure`、`structured_metadata` 或 `expert_inference`。随机试验的因果结论必须保留入组人群与终点范围；前临床机制不得外推为人体临床获益。

完整的判定顺序、层级边界和 Durvalumab 校准示例见 [因果关系建模与审计规则](causal-relation-model.md)。

## 兼容和校验

- 旧 CSV 不必立即新增列；构建器会补 `claim_id`、数组字段和可确定的规则关系。
- 新采集优先直接写 `claim_id`、`representative_document_assignee`、`family_ownership_summary`、`members`、`priority_set`、`member_relations`、`family_relations`、`family_ids`、`claim_ids`、`concept_ids` 和完整关系语义。
- `validate_output_schema.py` 检查 ID 唯一性、数组字段、悬空边、关系枚举、证据引用完整性和因果门槛。
- `confidence` 表示证据可信度，不表示侵权概率或法律状态结论。
