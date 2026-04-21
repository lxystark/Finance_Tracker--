"""
哈希表 - Hash Map
采用链地址法（Separate Chaining）解决冲突
键 -> 值 映射，支持 O(1) 查找、插入、删除
"""

from typing import Any, List, Optional


class HashMap:
    """哈希表实现 - 基于链地址法"""

    def __init__(self, size: int = 100):
        self.size = size
        self.map = [None] * size  # 每个槽位是一个链表
        self._length = 0

    def _hash(self, key: Any) -> int:
        """哈希函数：将键映射到数组下标"""
        if isinstance(key, str):
            hash_value = 0
            for char in key:
                hash_value = (hash_value * 31 + ord(char)) % self.size
            return hash_value
        elif isinstance(key, int):
            return hash(key) % self.size
        else:
            # 对其他类型使用字符串哈希
            return hash(str(key)) % self.size

    def put(self, key: Any, value: Any) -> None:
        """插入或更新键值对"""
        index = self._hash(key)
        bucket = self.map[index]

        # 如果桶为空，创建新链表
        if bucket is None:
            self.map[index] = [(key, value)]
        else:
            # 遍历链表查找或更新
            for i, (k, v) in enumerate(bucket):
                if k == key:
                    bucket[i] = (key, value)  # 更新已有键
                    return
            # 键不存在，追加到链表末尾
            bucket.append((key, value))

        self._length += 1

    def get(self, key: Any, default: Any = None) -> Any:
        """根据键获取值，键不存在返回 default"""
        index = self._hash(key)
        bucket = self.map[index]

        if bucket is None:
            return default

        for k, v in bucket:
            if k == key:
                return v

        return default

    def remove(self, key: Any) -> Any | None:
        """删除键值对，返回被删除的值，不存在返回 None"""
        index = self._hash(key)
        bucket = self.map[index]

        if bucket is None:
            return None

        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._length -= 1
                return v

        return None

    def contains_key(self, key: Any) -> bool:
        """检查键是否存在"""
        index = self._hash(key)
        bucket = self.map[index]

        if bucket is None:
            return False

        for k, _ in bucket:
            if k == key:
                return True

        return False

    def keys(self) -> List[Any]:
        """返回所有键的列表"""
        result = []
        for bucket in self.map:
            if bucket:
                for k, _ in bucket:
                    result.append(k)
        return result

    def values(self) -> List[Any]:
        """返回所有值的列表"""
        result = []
        for bucket in self.map:
            if bucket:
                for _, v in bucket:
                    result.append(v)
        return result

    def items(self) -> List[tuple]:
        """返回所有键值对的列表"""
        result = []
        for bucket in self.map:
            if bucket:
                for item in bucket:
                    result.append(item)
        return result

    def size_count(self) -> int:
        """返回键值对数量"""
        return self._length

    def is_empty(self) -> bool:
        """检查是否为空"""
        return self._length == 0

    def clear(self) -> None:
        """清空哈希表"""
        self.map = [None] * self.size
        self._length = 0

    def __len__(self) -> int:
        return self._length

    def __str__(self) -> str:
        items = []
        for bucket in self.map:
            if bucket:
                for k, v in bucket:
                    items.append(f"{k}: {v}")
        return "{" + ", ".join(items) + "}"

    def __repr__(self) -> str:
        return f"HashMap({self._length} items)"


# ============ 测试代码 ============
if __name__ == "__main__":
    print("=== 测试 HashMap ===")

    hm = HashMap()

    # 测试插入
    hm.put("tid_1", "Node1")
    hm.put("tid_2", "Node2")
    hm.put("tid_3", "Node3")
    print(f"插入3个键值对: {hm}")
    print(f"键数量: {len(hm)}")

    # 测试获取
    print(f"获取 tid_2: {hm.get('tid_2')}")
    print(f"获取不存在的键: {hm.get('tid_99', 'NOT_FOUND')}")

    # 测试更新
    hm.put("tid_2", "Node2_Updated")
    print(f"更新后 tid_2: {hm.get('tid_2')}")

    # 测试 contains_key
    print(f"包含 tid_1: {hm.contains_key('tid_1')}")
    print(f"包含 tid_99: {hm.contains_key('tid_99')}")

    # 测试 keys/values
    print(f"所有键: {hm.keys()}")
    print(f"所有值: {hm.values()}")

    # 测试删除
    removed = hm.remove("tid_2")
    print(f"删除 tid_2, 返回值: {removed}")
    print(f"删除后 tid_2: {hm.get('tid_2')}")
    print(f"删除后大小: {len(hm)}")

    # 测试清空
    hm.clear()
    print(f"清空后是否为空: {hm.is_empty()}")