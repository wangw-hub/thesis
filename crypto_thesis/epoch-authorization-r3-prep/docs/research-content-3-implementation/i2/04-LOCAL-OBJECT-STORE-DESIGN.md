# LocalObjectStore 设计

布局为 `<root>/objects/<namespace>/sha256/<d0d1>/<d2d3>/<digest>.obj`，另有隔离的 `tmp`、`quarantine`、`audit`。路径只由已验证 namespace 与 digest 派生。

相同内容重复 put 返回相同引用；不同内容产生不同摘要路径。既存目标必须重新验证，损坏或攻击性目标 Fail-Closed 且绝不覆盖。正式 API 不提供 update、overwrite、append 或 truncate。
