# 专利景观可视化参考

## 1. 页面/图表组合

### 总览

显示族数、文献数、申请人、国家、技术主题、优先权年份和状态。总览中的每个数字必须来自结构化数据，不得手工估算。

### 时间线

横轴为优先权/公开/授权年份；行按申请人或技术主题排列。显示 `family_id`，而不是把同族国家文献画成多个独立创新。

### 专利族关系图

节点表示代表文献或子族，边表示 `priority`、`national phase`、`division`、`continuation` 或 `related`。不同关系使用不同线型，并提供图例。

### 技术主题矩阵

推荐列：`compound | salt/polymorph | formulation | indication | regimen | combination | resistance | diagnostic | process`。

单元格展示“明确覆盖/可能覆盖/未见/不确定”，点击后回到 claim 和证据。

### 技术路线图

推荐结构：

```text
disease/need → target/mechanism → compound series → candidate
→ formulation/regimen → indication/biomarker → resistance
→ next-generation strategy → whitespace hypothesis
```

## 2. 推荐数据字段

```text
family_id
representative_document
applicant
inventor
earliest_priority
publication_date
grant_date
jurisdiction
status
claim_theme
mutation_or_biomarker
indication
combination
source_url
confidence
```

## 3. 交互规则

- 筛选器：法域、申请人、年份、技术主题、突变/生物标志物、状态；
- 点击族：显示成员、优先权链、关键权利要求、状态来源和备注；
- 点击主题：显示对应族、claim 要素和证据；
- 导出：CSV/JSON/PDF/PNG；
- 任何风险色彩必须附文字标签和证据，不得用颜色代替法律结论。

## 4. WIPO 风格但不复制

可以参考 WIPO 专利景观的“报告 + 交互式 dashboard + 证据明细”信息架构；不得复制其源码、专有数据库、商业算法或受限制的数据。研究报告应使用独立检索数据和可回溯来源。

参考案例：[WIPO Patent Landscape on COVID-19 Vaccines and Therapeutics](https://www.wipo.int/en/web/patent-analytics/patent-landscape-on-covid-19-vaccines-and-therapeutics)。本 Skill 的 V2 采用可复核的“技术景观图”：横轴为最早优先权年份，纵轴为技术保护层，圆点为专利族，大小表示法域/保护层广度，颜色和线型区分状态与核心/边界族。
