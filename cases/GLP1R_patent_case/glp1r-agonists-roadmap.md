# GLP-1 受体（GLP1R）技术路线图

## 技术路线

flowchart LR
  Need[糖尿病/肥胖/心血管需求] --> Mech[GLP1R 靶点机制]
  Mech --> Peptide[肽类 GLP-1 类似物<br/>F10 F11 F12 F18]
  Mech --> Dual[双/三靶点激动剂<br/>GIP/GLP-1 F02 F09 F12 F13 F14 F20<br/>GCG/GLP-1/GIP F14]
  Mech --> SmallMol[小分子口服 GLP-1R<br/>F03 F04 F05 F06 F07 F15 F16]
  Peptide --> OralSNAC[口服 SNAC 固体组合物 F01]
  SmallMol --> Crystal[晶型/盐型续案 F06]
  Dual --> Formulation[制剂/组合物 F13 F20]
  SmallMol --> Combo[联合用药<br/>F03 F08]
  SmallMol --> Topical[局部给药 F19]
  Dual --> Antibody[抗体型激动剂 F17]


## 说明
- 节点绑定 family_id；日期与状态见 02-patent-family-map-report.md。
- 保护层（专利族）与研发事实层（临床/竞品）分离；研发阶段以公开信息为上下文，不替代权利要求范围。

（详细节点-族-证据映射见 03-technology-roadmap-report.md）
