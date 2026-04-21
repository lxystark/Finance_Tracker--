"""
队列 - Queue
先进先出（FIFO）数据结构
用于通知提醒系统（FIFO消费）
"""

from typing import Any, Optional, List


class Queue:
    """队列：先进先出（FIFO）"""

    def __init__(self):
        self._items: List[Any] = []

    def enqueue(self, item: Any) -> None:
        """入队 - 将元素添加到队尾"""
        self._items.append(item)

    def dequeue(self) -> Optional[Any]:
        """出队 - 移除并返回队首元素，空队返回 None"""
        if self.is_empty():
            return None
        return self._items.pop(0)

    def peek(self) -> Optional[Any]:
        """查看队首 - 返回队首元素但不移除，空队返回 None"""
        if self.is_empty():
            return None
        return self._items[0]

    def rear(self) -> Optional[Any]:
        """查看队尾 - 返回队尾元素但不移除，空队返回 None"""
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self) -> bool:
        """检查队列是否为空"""
        return len(self._items) == 0

    def size(self) -> int:
        """返回队列中元素数量"""
        return len(self._items)

    def clear(self) -> None:
        """清空队列"""
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)

    def __str__(self) -> str:
        if self.is_empty():
            return "Queue(empty)"
        return f"Queue(front -> {self._items[0]}, {len(self._items)} items)"

    def __repr__(self) -> str:
        return f"Queue({len(self._items)} items)"


# ============ 测试代码 ============
if __name__ == "__main__":
    print("=== 测试 Queue ===")

    queue = Queue()

    # 测试入队
    queue.enqueue("通知1")
    queue.enqueue("通知2")
    queue.enqueue("通知3")
    print(f"入队3个: {queue}")
    print(f"大小: {len(queue)}")

    # 测试查看队首/队尾
    print(f"队首: {queue.peek()}")
    print(f"队尾: {queue.rear()}")

    # 测试出队
    dequeued = queue.dequeue()
    print(f"出队: {dequeued}")
    print(f"出队后队首: {queue.peek()}")

    # 测试清空
    queue.clear()
    print(f"清空后是否为空: {queue.is_empty()}")