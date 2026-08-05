# 数据库检索式

## Google Scholar
- 宽：`"temporal access control" OR "temporal authorization" OR "time-based access control"`
- 精确：`("multiple time intervals" OR "periodic time constraints") (canonical OR normalization OR equivalence) authorization`
- 近五年：在精确式后加 `after:2020 before:2027`
- 排除：`-patent -blog -tutorial -cryptocurrency-price -NFT`

## Web of Science
- 宽：`TS=("temporal access control" OR "temporal authorization")`
- 精确：`TS=((blockchain OR "permissioned blockchain") NEAR/3 (authorization OR "access control")) AND TS=(nonce OR replay OR capability OR "state version")`
- 近五年：Timespan=2021-2026，保留Article/Proceedings/Review。
- 排除：`NOT TS=(cryptocurrency trading OR NFT OR medical scheduling)`

## Scopus
- 宽：`TITLE-ABS-KEY("temporal access control" OR "temporal authorization")`
- 精确：`TITLE-ABS-KEY((blockchain W/3 authorization) AND (capability OR nonce OR replay OR "state version"))`
- 近五年：`AND PUBYEAR > 2020 AND PUBYEAR < 2027`
- 排除：`AND NOT TITLE-ABS-KEY("cryptocurrency price" OR NFT OR trading)`

## IEEE Xplore
- 宽：`("All Metadata":"blockchain access control") OR ("All Metadata":"temporal access control")`
- 精确：`("All Metadata":"permissioned blockchain") AND authorization AND (nonce OR replay OR capability)`
- 近五年：Publication Year 2021–2026；Journals & Conferences。
- 排除：人工排除纯价格预测、能源交易和无授权语义的IoT论文。

## ACM Digital Library
- 宽：`[[Abstract: "temporal access control"] OR [Abstract: "temporal authorization"]]`
- 精确：`[[Abstract: blockchain] AND [Abstract: "access control"] AND [Abstract: capability OR nonce OR replay]]`
- 近五年：Publication Date 2021-01-01—2026-07-30。
- 排除：`NOT Abstract:(cryptocurrency OR NFT OR trading)`

## SpringerLink
- 宽：`"temporal role based access control" OR "attribute-based encryption" OR "permissioned blockchain access control"`
- 精确：`"HPKE" AND ("formal analysis" OR interoperability OR "multi recipient")`
- 近五年：Article/Chapter，2021–2026。
- 排除：排除Book Review、Encyclopedia Entry和无安全模型/实验的低相关章节。

## ScienceDirect
- 宽：`("blockchain" AND "access control") OR ("revocable encryption" AND "data sharing")`
- 精确：`("on-chain" AND "off-chain" AND (consistency OR atomicity OR recovery))`
- 近五年：2021–2026，Research/Review articles。
- 排除：`NOT ("cryptocurrency price" OR "energy market" OR NFT)`

## CNKI
- 宽：`主题=(时态访问控制 OR 时间访问控制 OR 周期时间约束)`；`主题=(区块链 AND 访问控制)`
- 精确：`主题=((非连续时间 OR 多时间区间 OR 周期时间) AND (访问控制 OR 授权))`；`主题=((联盟链 OR 许可链) AND (访问控制 OR 授权) AND (重放 OR 随机数 OR 权能))`
- 近五年：发表时间=2021–2026；优先SCI/EI、CSCD、博士论文。
- 排除：不含=(数字货币 OR 价格预测 OR 供应链金融 OR NFT)。
