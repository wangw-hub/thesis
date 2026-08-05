# 04 符号审计（SYMBOL AUDIT）

## 发现的冲突（M7）

| 符号 | 冲突来源 | 处理 |
|---|---|---|
| U | RC1 时间槽总数 vs RC2 用户状态五元组 | RC2 用户五元组改为 U_u |
| R | RC1 冗余度 vs RC2 资源状态七元组 | RC1 冗余度改为 R_d；RC2 资源状态保持 R |
| B | RC1 策略规范字节串 B(P) vs RC2 能力待签字节 B | RC2 能力待签字节改为 B_cap |

## 修复结果

- RC1：U（时间槽总数）、B(P)（策略规范字节）、R_d（冗余度）保持/改名；I*、C(P)、c、k、n、T、Δ、t0 不变。
- RC2：R（资源状态七元组）、U_u（用户状态五元组）、B_cap（能力待签规范字节）。
- RC3：headerCoreDigest/headerObjectDigest/bodyObjectDigest、CK、N_j、AAD(ctx,j)、D_H、enc/ct 不变。

GLOBAL_SYMBOL_CONFLICT = 0。

## 一致性核验

- 式(7)/式(8) 与算法4/5 中的能力待签字节统一为 B_cap；
- 正文“冗余度 R_d∈{1,2,4,8}”与实验描述一致；
- 用户五元组 U_u 仅在研究内容二出现一次定义，后续正文使用中文描述，不参与公式运算，无其他引用冲突。
