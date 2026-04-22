'''
    @Author: Yu Chen
    It's a set module used for hashmap.py
    集合 - Set
    基于 HashMap 实现，元素唯一
    用于保证分类名全局唯一，防止重复添加
'''

from typing import Any, List
from structures.hashmap import HashMap


class Set:
    """集合：基于 HashMap 实现，元素唯一"""

    def __init__(self):
        self._map = HashMap()

    def add(self, item: Any) -> bool:
        """添加元素，已存在则返回 False"""
        if self.contains(item):
            return False
        self._map.put(item, True)
        return True

    def remove(self, item: Any) -> bool:
        """移除元素，成功返回 True"""
        return self._map.remove(item) is not None

    def contains(self, item: Any) -> bool:
        """检查元素是否存在"""
        return self._map.contains_key(item)

    def union(self, other: 'Set') -> 'Set':
        """并集"""
        result = Set()
        for item in self.to_list():
            result.add(item)
        for item in other.to_list():
            result.add(item)
        return result

    def intersection(self, other: 'Set') -> 'Set':
        """交集"""
        result = Set()
        for item in self.to_list():
            if other.contains(item):
                result.add(item)
        return result

    def difference(self, other: 'Set') -> 'Set':
        """差集（self - other）"""
        result = Set()
        for item in self.to_list():
            if not other.contains(item):
                result.add(item)
        return result

    def is_subset(self, other: 'Set') -> bool:
        """判断是否为 other 的子集"""
        for item in self.to_list():
            if not other.contains(item):
                return False
        return True

    def to_list(self) -> List[Any]:
        """返回元素列表"""
        return self._map.keys()

    def is_empty(self) -> bool:
        """检查是否为空"""
        return len(self._map) == 0

    def clear(self) -> None:
        """清空集合"""
        self._map.clear()

    def __len__(self) -> int:
        return len(self._map)

    def __contains__(self, item: Any) -> bool:
        return self.contains(item)

    def __str__(self) -> str:
        return "{" + ", ".join(str(k) for k in self.to_list()) + "}"

    def __repr__(self) -> str:
        return f"Set({len(self)} items)"


# ============ 测试代码 ============
if __name__ == "__main__":
    print("=== 测试 Set ===")

    s = Set()

    # 测试添加
    print(s.add("餐饮"))   # True
    print(s.add("交通"))   # True
    print(s.add("餐饮"))   # False（重复）
    print(f"集合内容: {s}")
    print(f"元素数量: {len(s)}")

    # 测试包含
    print(f"包含 '餐饮': {s.contains('餐饮')}")
    print(f"包含 '娱乐': {s.contains('娱乐')}")

    # 测试并集
    s2 = Set()
    s2.add("交通")
    s2.add("娱乐")
    print(f"s2: {s2}")
    print(f"并集: {s.union(s2)}")

    # 测试交集
    print(f"交集: {s.intersection(s2)}")

    # 测试差集
    print(f"差集: {s.difference(s2)}")

    # 测试移除
    s.remove("交通")
    print(f"移除后: {s}")

    # 测试子集
    s3 = Set()
    s3.add("餐饮")
    print(f"{{餐饮}} 是 {s} 的子集: {s3.is_subset(s)}")
