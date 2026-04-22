'''
    @Author: Yu Chen
    It's a stack module used for undo statement management.
    栈 - Stack
    后进先出（LIFO）数据结构
    用于撤销/重做功能
'''


from typing import Any, Optional, List


class Stack:
    """栈：后进先出（LIFO）"""

    def __init__(self):
        self._items: List[Any] = []

    def push(self, item: Any) -> None:
        """压栈 - 将元素添加到栈顶"""
        self._items.append(item)

    def pop(self) -> Optional[Any]:
        """弹栈 - 移除并返回栈顶元素，空栈返回 None"""
        if self.is_empty():
            return None
        return self._items.pop()

    def peek(self) -> Optional[Any]:
        """查看栈顶 - 返回栈顶元素但不移除，空栈返回 None"""
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self) -> bool:
        """检查栈是否为空"""
        return len(self._items) == 0

    def size(self) -> int:
        """返回栈中元素数量"""
        return len(self._items)

    def clear(self) -> None:
        """清空栈"""
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)

    def __str__(self) -> str:
        if self.is_empty():
            return "Stack(empty)"
        return f"Stack(top -> {self._items[-1]}, {len(self._items)} items)"

    def __repr__(self) -> str:
        return f"Stack({len(self._items)} items)"


# ============ 测试代码 ============
if __name__ == "__main__":
    print("=== 测试 Stack ===")

    stack = Stack()

    # 测试压栈
    stack.push("操作1")
    stack.push("操作2")
    stack.push("操作3")
    print(f"压入3个: {stack}")
    print(f"大小: {len(stack)}")

    # 测试查看栈顶
    print(f"栈顶: {stack.peek()}")

    # 测试弹栈
    popped = stack.pop()
    print(f"弹出: {popped}")
    print(f"弹出后栈顶: {stack.peek()}")

    # 测试清空
    stack.clear()
    print(f"清空后是否为空: {stack.is_empty()}")