# GLP1R_patent_case 模块化报告索引

> 生成时间：2026-08-07T06:40:29.657750+00:00 · 结构化数据目录：`/data/siqing/2026_workpalce/20260731/GLP1R_patent_case`

## FTO 风格统计入口

- [打开交互式统计总览](report-visuals.html)
- [查看图表数据清单](visuals/manifest.json)
- [公开来源访问与检索审计](public-source-search-report.md)
- [公开来源实际检索执行](public-source-search-results-report.md)

## 报告清单

- [执行摘要](00-executive-summary.md)
- [权利要求与要素抽取报告](01-extraction-report.md)
- [专利族地图报告](02-patent-family-map-report.md)
- [技术路线图报告](03-technology-roadmap-report.md)
- [风险与 FTO 报告](04-risk-and-fto-report.md)
- [创新空间假设报告](05-innovation-space-report.md)
- [证据链报告](06-evidence-chain-report.md)
- [来源目录报告](07-source-catalog-report.md)

## 输入与过程数据

- `research_scope.json` / `identity.json`：研究范围和实体消歧
- `*-patent-families.csv`：族级数据
- `*-claim-elements.csv`：权利要求要素
- `*-evidence.csv`：证据链
- `fto-search-plan.json`：FTO 特征、检索轮次和来源目录
- `fto-candidate-ranking.csv`：候选排序
- `source-log.jsonl`：实际访问日志
- `source-portal-overrides.json`：新版检索入口/浏览器确认入口
- `source-search-portals.json`：本案例公开来源检索协议
- `public-source-search-audit.*`：来源访问与公开检索审计
- `public-source-search-results.*`：实际检索执行台账
- `case-output.json`：机器可读 Schema、指标、不确定性和失败案例
- `reproducibility-report.json` / `reproducibility-runs/`：本地重放记录和快照
- `visuals/`：依赖无外部图库的 SVG 统计图和 manifest

## 总体限制

报告将未核验的国家阶段、聚合状态、缺失 claim 和未采集结构明确标出；不把模块报告升级为法律意见。
