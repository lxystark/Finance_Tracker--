"""
通知模块 - Notification System
基于 Queue 实现 FIFO 通知消费
用于预算超支和大额支出提醒
"""

from structures.queue import Queue
from datetime import datetime


class Notification:
    """通知消息"""

    def __init__(self, ntype: str, message: str):
        self.ntype = ntype          # 通知类型：warning / info
        self.message = message      # 通知内容
        self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        icon = "[!]" if self.ntype == "warning" else "[i]"
        return f"[{self.time}] {icon} {self.message}"

    def __repr__(self):
        return f"Notification({self.ntype}: {self.message})"


class NotificationManager:
    """通知管理器 - 基于 Queue 实现"""

    # 大额支出阈值
    LARGE_AMOUNT_THRESHOLD = 1000.0

    def __init__(self):
        self._queue = Queue()
        self._history = []     # 已读通知历史
        self._unread_count = 0

    def send(self, ntype: str, message: str) -> None:
        """发送通知"""
        notification = Notification(ntype, message)
        self._queue.enqueue(notification)
        self._unread_count += 1

    def check_large_expense(self, amount: float, tid) -> None:
        """检查大额支出，超过阈值自动发送警告"""
        if amount >= self.LARGE_AMOUNT_THRESHOLD:
            self.send("warning", f"大额支出提醒：交易 #{tid} 金额 {amount} 元，超过阈值 {self.LARGE_AMOUNT_THRESHOLD} 元")

    def check_negative_amount(self, amount: float, tid) -> None:
        """检查负数金额"""
        if amount < 0:
            self.send("warning", f"异常金额提醒：交易 #{tid} 金额为负数 ({amount} 元)")

    def read(self):
        """读取一条通知（FIFO）"""
        if self._queue.is_empty():
            return None
        notification = self._queue.dequeue()
        self._history.append(notification)
        self._unread_count = max(0, self._unread_count - 1)
        return notification

    def read_all(self):
        """读取所有未读通知"""
        notifications = []
        while not self._queue.is_empty():
            n = self.read()
            if n:
                notifications.append(n)
        return notifications

    def unread_count(self) -> int:
        """返回未读通知数量"""
        return self._unread_count

    def has_unread(self) -> bool:
        """是否有未读通知"""
        return not self._queue.is_empty()

    def history(self):
        """返回已读通知历史"""
        return list(self._history)

    def clear_history(self) -> None:
        """清空已读通知历史"""
        self._history.clear()

    def __str__(self):
        return f"NotificationManager({self._unread_count} unread, {len(self._history)} read)"


# ============ 测试代码 ============
if __name__ == "__main__":
    print("=== 测试 NotificationManager ===")

    nm = NotificationManager()

    # 发送通知
    nm.send("info", "欢迎使用 Finance Tracker")
    nm.send("warning", "您的支出已超过预算")
    nm.send("info", "数据已保存")
    print(f"未读数量: {nm.unread_count()}")

    # 读取所有未读
    print("\n--- 所有未读通知 ---")
    for n in nm.read_all():
        print(f"  {n}")

    print(f"\n读取后未读数量: {nm.unread_count()}")

    # 测试大额支出检查
    print("\n--- 大额支出检查 ---")
    nm.check_large_expense(1500.0, tid=99)
    nm.check_large_expense(500.0, tid=100)
    print(f"大额触发后未读: {nm.unread_count()}")
    for n in nm.read_all():
        print(f"  {n}")

    # 测试负数金额检查
    print("\n--- 负数金额检查 ---")
    nm.check_negative_amount(-50.0, tid=5)
    for n in nm.read_all():
        print(f"  {n}")