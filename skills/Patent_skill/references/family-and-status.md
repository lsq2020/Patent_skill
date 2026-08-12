# 专利族与法律状态参考规则

## 1. 专利族判断

用“优先权申请号 + 申请关系 + 技术主题”三层判断，不用标题或申请人单独判断。

### Simple family

优先权申请集合完全相同的文献，通常归入同一 DOCDB simple family。国际申请及其国家阶段通常属于同一简单族。

### Extended family

只共享部分优先权、存在连续申请/分案关系或存在明确技术延伸的文献，可作为 INPADOC extended family 或相关族展示，但保留不同的 `subfamily_id` 和权利要求主题。

### Continuity branches

- `division`：分案；
- `continuation`：美国继续申请；
- `continuation-in-part`：美国部分继续申请，新增内容可能获得新的优先权；
- `national phase`：PCT 国家阶段；
- `related application`：相关申请，需查看说明书和优先权声明。

新增技术内容有新的优先权时，不能只因同一申请人或同一分子而合并。

## 2. 推荐记录字段

```text
family_id
family_definition
simple_family_id
extended_family_id
subfamily_id
priority_set
earliest_priority
continuity_relation
representative_document
members
claim_theme
jurisdictions
```

## 3. 状态快照

状态必须带法域和日期：

```text
status_as_of = 2026-08-05
jurisdiction = US
status = granted / pending / abandoned / expired / unknown
source = official register URL
```

状态层级：

1. 目标法域官方登记簿/审查档案；
2. EPO Register、USPTO、WIPO 等官方数据；
3. 聚合数据库仅作线索；
4. 没有官方证据时写“待核验”。

“Active”不能单独作为有效性结论；还要检查年费、期限调整、终止/恢复、异议/无效和后续分案。

## 4. 族判断示例

```text
2011 core priority
├── WO international application
├── US national phase/grant
├── CN national phase/grant
└── continuations/divisionals
```

同一核心优先权的国际/国家阶段可归入一个主族；2014 年新增的制剂优先权通常作为另一个简单族，但可在扩展关系或技术路线中与核心族相连。
