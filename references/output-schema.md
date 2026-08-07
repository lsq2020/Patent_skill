# case-output.json 数据契约

`case-output.json` 是 CSV、证据链、报告和图谱之间的稳定接口。当前版本为 `1.1`，在 `1.0` 的报告契约上增加稳定 claim ID、文献记录和一等关系边。

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
- 图节点 ID 使用命名空间：`family:*`、`document:*`、`claim:*`、`finding:*`。

## 关系字段

族记录统一包含：

```json
{
  "members": ["US123A1", "US123B2"],
  "priority_set": ["US62/123456"],
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

允许的族间关系包括 `CONTINUATION_OF`、`CONTINUATION_IN_PART_OF`、`DIVISIONAL_OF`、`NATIONAL_PHASE_OF` 和 `RELATED_TO`。不从 `notes` 或自然语言族描述自动推断这些边。

Evidence 记录统一包含：

```json
{
  "finding_id": "FIND-001",
  "family_ids": ["FAM-001"],
  "claim_ids": ["CLM-..."],
  "link_methods": ["document_no"]
}
```

优先使用输入的 `family_ids` / `claim_ids`。缺失时只允许通过完全规范化的 `document_no` 或相同 `source_url` 建立规则关系；无法匹配时保留孤立 finding 并写入质量缺口。

## 一等关系边

每条 `records.relations[]` 包含：

```text
relation_id | source_id | relation_type | target_id
assertion | link_methods | evidence_ids | properties
```

`assertion` 只允许：

- `direct_fact`：输入字段显式给出；
- `rule_derived`：由文献号或 URL 的确定性匹配得到；
- `model_inference`：模型推断，默认不由构建器自动产生。

边只存一次。反向链接由图谱视图根据入边动态计算。

## 兼容和校验

- 旧 CSV 不必立即新增列；构建器会补 `claim_id`、数组字段和可确定的规则关系。
- 新采集优先直接写 `claim_id`、`members`、`priority_set`、`family_relations`、`family_ids` 和 `claim_ids`。
- `validate_output_schema.py` 检查 ID 唯一性、数组字段、悬空边和 assertion 枚举。
- `confidence` 表示证据可信度，不表示侵权概率或法律状态结论。
