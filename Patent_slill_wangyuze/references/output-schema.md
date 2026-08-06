# 机器可读输出 Schema

完整 JSON Schema 位于 `references/output-schema.json`。每个案例运行必须生成 `case-output.json`，它是报告、CSV 和来源日志之间的稳定接口。

## 顶层结构

```text
case-output.json
├── schema_version
├── case                  # 研究对象、法域、日期、深度
├── run                   # run_id、Skill 版本、生成时间、流水线
├── metrics               # 族、claim、证据、来源和报告计数
├── records
│   ├── families          # family_id、代表文献、申请人、时间、状态、claim 类别
│   ├── claims            # family_id、document、claim_category、element、coverage、定位
│   ├── evidence          # finding_id、事实/推断、来源、定位、置信度、复核动作
│   └── ranking           # FTO 复核优先级、排序依据、命中特征和状态来源
├── uncertainty           # 全局摘要和逐项不确定性
├── failure_cases         # 已观察或预定义失败模式及降级路径
├── reports               # 每个模块的 md/html 路径和生成状态
├── reproducibility       # 输入/输出哈希、命令、运行环境
└── contract              # Schema 版本和路径
```

## 字段规则

- `confidence` 只能表达证据可信度，不能表达侵权概率；
- `official_status` 必须带 `status_as_of`、`status_source` 和法域；
- `claim_location` 为空时必须生成不确定性条目；
- `source_url`、`document`、`family_id` 或 `finding_id` 至少保留一个可回溯键；
- `failure_cases.observed=false` 仍要保留触发条件和 fallback，避免只展示成功路径；
- 报告可以是中文或英文，但机器字段名固定为英文 snake_case。
