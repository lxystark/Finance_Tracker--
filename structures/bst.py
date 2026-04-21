"""
二叉搜索树 - Binary Search Tree
支持插入、搜索、范围查询、中序遍历
用于按日期或金额进行范围查询
"""

from typing import Any, List, Optional, Callable


class BSTNode:
    """BST 节点"""

    def __init__(self, key: Any, value: Any):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BST:
    """二叉搜索树"""

    def __init__(self, root: BSTNode = None):
        self.root = root
        self._size = 0

    # ============ 核心操作 ============

    def insert(self, key: Any, value: Any) -> None:
        """插入键值对，键相同时更新值"""
        if self.root is None:
            self.root = BSTNode(key, value)
            self._size += 1
            return

        self._insert_recursive(self.root, key, value)

    def _insert_recursive(self, node: BSTNode, key: Any, value: Any) -> None:
        """递归插入"""
        if key < node.key:
            if node.left is None:
                node.left = BSTNode(key, value)
                self._size += 1
            else:
                self._insert_recursive(node.left, key, value)
        elif key > node.key:
            if node.right is None:
                node.right = BSTNode(key, value)
                self._size += 1
            else:
                self._insert_recursive(node.right, key, value)
        else:
            # 键相同，更新值
            node.value = value

    def search(self, key: Any) -> Optional[Any]:
        """搜索键，返回值，不存在返回 None"""
        return self._search_recursive(self.root, key)

    def _search_recursive(self, node: BSTNode, key: Any) -> Optional[Any]:
        """递归搜索"""
        if node is None:
            return None

        if key < node.key:
            return self._search_recursive(node.left, key)
        elif key > node.key:
            return self._search_recursive(node.right, key)
        else:
            return node.value

    def contains(self, key: Any) -> bool:
        """检查键是否存在"""
        return self.search(key) is not None

    def delete(self, key: Any) -> bool:
        """删除键，成功返回 True，键不存在返回 False"""
        result = self._delete_recursive(self.root, key)
        return result

    def _delete_recursive(self, node: BSTNode, key: Any) -> BSTNode:
        """递归删除"""
        if node is None:
            return None

        if key < node.key:
            node.left = self._delete_recursive(node.left, key)
        elif key > node.key:
            node.right = self._delete_recursive(node.right, key)
        else:
            # 找到要删除的节点
            self._size -= 1

            # 情况1：叶子节点
            if node.left is None and node.right is None:
                return None

            # 情况2：只有一个子节点
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left

            # 情况3：有两个子节点 - 用后继节点替换
            successor = self._find_min(node.right)
            node.key = successor.key
            node.value = successor.value
            node.right = self._delete_recursive(node.right, successor.key)

        return node

    def _find_min(self, node: BSTNode) -> BSTNode:
        """找到最小节点（最左叶子）"""
        while node.left is not None:
            node = node.left
        return node

    # ============ 遍历方法 ============

    def inorder(self) -> List[Any]:
        """中序遍历（升序）"""
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node: BSTNode, result: List) -> None:
        """递归中序遍历"""
        if node is not None:
            self._inorder_recursive(node.left, result)
            result.append((node.key, node.value))
            self._inorder_recursive(node.right, result)

    def preorder(self) -> List[Any]:
        """前序遍历"""
        result = []
        self._preorder_recursive(self.root, result)
        return result

    def _preorder_recursive(self, node: BSTNode, result: List) -> None:
        """递归前序遍历"""
        if node is not None:
            result.append((node.key, node.value))
            self._preorder_recursive(node.left, result)
            self._preorder_recursive(node.right, result)

    def postorder(self) -> List[Any]:
        """后序遍历"""
        result = []
        self._postorder_recursive(self.root, result)
        return result

    def _postorder_recursive(self, node: BSTNode, result: List) -> None:
        """递归后序遍历"""
        if node is not None:
            self._postorder_recursive(node.left, result)
            self._postorder_recursive(node.right, result)
            result.append((node.key, node.value))

    # ============ 范围查询 ============

    def range_query(self, low: Any, high: Any) -> List[Any]:
        """返回键在 [low, high] 范围内的所有值"""
        result = []
        self._range_query_recursive(self.root, low, high, result)
        return result

    def _range_query_recursive(self, node: BSTNode, low: Any, high: Any, result: List) -> None:
        """递归范围查询"""
        if node is None:
            return

        # 如果当前键大于 low，遍历左子树
        if low < node.key:
            self._range_query_recursive(node.left, low, high, result)

        # 如果当前键在范围内
        if low <= node.key <= high:
            result.append(node.value)

        # 如果当前键小于 high，遍历右子树
        if node.key < high:
            self._range_query_recursive(node.right, low, high, result)

    def range_keys(self, low: Any, high: Any) -> List[Any]:
        """返回键在 [low, high] 范围内的所有键"""
        result = []
        self._range_keys_recursive(self.root, low, high, result)
        return result

    def _range_keys_recursive(self, node: BSTNode, low: Any, high: Any, result: List) -> None:
        """递归范围键查询"""
        if node is None:
            return

        if low < node.key:
            self._range_keys_recursive(node.left, low, high, result)

        if low <= node.key <= high:
            result.append(node.key)

        if node.key < high:
            self._range_keys_recursive(node.right, low, high, result)

    # ============ 属性方法 ============

    def size(self) -> int:
        """返回节点数量"""
        return self._size

    def is_empty(self) -> bool:
        """检查是否为空"""
        return self._size == 0

    def height(self) -> int:
        """返回树的高度"""
        return self._height_recursive(self.root)

    def _height_recursive(self, node: BSTNode) -> int:
        """递归计算高度"""
        if node is None:
            return 0
        left_height = self._height_recursive(node.left)
        right_height = self._height_recursive(node.right)
        return max(left_height, right_height) + 1

    def clear(self) -> None:
        """清空树"""
        self.root = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __str__(self) -> str:
        """返回树的可视化字符串"""
        return self._tree_string(self.root, "", True)

    def _tree_string(self, node: BSTNode, prefix: str, is_last: bool) -> str:
        """递归生成树形字符串"""
        if node is None:
            return ""

        result = prefix
        if is_last:
            result += "└── "
            new_prefix = prefix + "    "
        else:
            result += "├── "
            new_prefix = prefix + "│   "

        result += f"{node.key}\n"
        result += self._tree_string(node.left, new_prefix, node.right is None)
        result += self._tree_string(node.right, new_prefix, True)

        return result

    def __repr__(self) -> str:
        return f"BST({self._size} nodes, height={self.height()})"


# ============ 测试代码 ============
if __name__ == "__main__":
    print("=== 测试 BST ===")

    bst = BST()

    # 测试插入
    bst.insert(50, "节点50")
    bst.insert(30, "节点30")
    bst.insert(70, "节点70")
    bst.insert(20, "节点20")
    bst.insert(40, "节点40")
    bst.insert(60, "节点60")
    bst.insert(80, "节点80")
    print(f"插入7个节点: size={bst.size()}, height={bst.height()}")
    print(bst)

    # 测试搜索
    print(f"搜索 40: {bst.search(40)}")
    print(f"搜索 99: {bst.search(99)}")

    # 测试中序遍历（排序）
    print(f"中序遍历: {bst.inorder()}")

    # 测试范围查询
    print(f"键在 [30, 60] 范围内: {bst.range_keys(30, 60)}")
    print(f"值在 [30, 60] 范围内: {bst.range_query(30, 60)}")

    # 测试删除
    bst.delete(20)
    print(f"删除 20 后 size={bst.size()}")
    bst.delete(30)
    print(f"删除 30 后中序: {bst.inorder()}")
    bst.delete(50)  # 删除根节点
    print(f"删除 50 后中序: {bst.inorder()}")

    # 测试清空
    bst.clear()
    print(f"清空后是否为空: {bst.is_empty()}")