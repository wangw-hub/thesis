# A7 事件流

隔离链真实 `EpochAdvanced` → scanner 标准化事件 → resolver 得到受影响资源 → agent 预冻结 `HEADER_ONLY` 任务 → 当前 Header 提交 → 固定块 CompositeState 复核。重复扫描同一区块只命中已存在事件，不新增任务或业务效果。
