# Job领取与SKIP LOCKED

领取在单一事务中使用CTE加`FOR UPDATE SKIP LOCKED`，随后设置CLAIMED、owner、
数据库时间租约并增加row_version。2、4和16 worker测试各处理32个合成任务：
重复领取0、丢失0、非法成功0。被另一事务锁定的任务被跳过，回滚后可再次领取。

