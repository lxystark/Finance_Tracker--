"""
多叉树 - Tree
支持任意数量的子节点
用于构建多级分类体系（如：支出 > 餐饮 > 外卖）
"""

from typing import Any, Optional, List
from collections import deque


class TreeNode:
    """树节点"""

    def __init__(self, data: Any):
        self.data = data
        self.children: List[TreeNode] = []
        self.parent: Optional[TreeNode] = None

    def add_child(self, child: 'TreeNode') -> 'TreeNode':
        """添加子节点"""
        child.parent = self
        self.children.append(child)
        return child

    def remove_child(self, child: 'TreeNode') -> bool:
        """移除子节点，成功返回 True"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            return True
        return False

    def is_leaf(self) -> bool:
        """检查是否为叶子节点"""
        return len(self.children) == 0

    def is_root(self) -> bool:
        """检查是否为根节点"""
        return self.parent is None

    def depth(self) -> int:
        """返回节点深度（根节点深度为 0）"""
        depth = 0
        node = self.parent
        while node is not None:
            depth += 1
            node = node.parent
        return depth

    def descendants(self) -> List['TreeNode']:
        """返回所有后代节点"""
        result = []
        stack = [self]
        while stack:
            node = stack.pop()
            for child in node.children:
                result.append(child)
                stack.append(child)
        return result

    def subtree_size(self) -> int:
        """返回子树节点数（包括自身）"""
        size = 1
        for child in self.children:
            size += child.subtree_size()
        return size


class Tree:
    """多叉树"""

    def __init__(self, root: Optional[TreeNode] = None):
        self.root = root
        self._size = 0

    def set_root(self, data: Any) -> TreeNode:
        """设置根节点"""
        self.root = TreeNode(data)
        self._size = 1
        return self.root

    def is_empty(self) -> bool:
        """检查树是否为空"""
        return self.root is None

    def size(self) -> int:
        """返回节点总数"""
        return self._size

    def height(self) -> int:
        """返回树的高度（根节点高度为 0）"""
        if self.root is None:
            return -1
        return self._height_recursive(self.root)

    def _height_recursive(self, node: TreeNode) -> int:
        """递归计算节点高度"""
        if node.is_leaf():
            return 0
        max_child_height = -1
        for child in node.children:
            child_height = self._height_recursive(child)
            max_child_height = max(max_child_height, child_height)
        return max_child_height + 1

    # ============ 遍历方法 ============

    def traverse_bfs(self) -> List[TreeNode]:
        """广度优先遍历"""
        if self.root is None:
            return []
        result = []
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            result.append(node)
            queue.extend(node.children)
        return result

    def traverse_dfs(self) -> List[TreeNode]:
        """深度优先遍历（先序遍历）"""
        if self.root is None:
            return []
        result = []
        self._dfs_recursive(self.root, result)
        return result

    def _dfs_recursive(self, node: TreeNode, result: List[TreeNode]) -> None:
        """递归 DFS"""
        result.append(node)
        for child in node.children:
            self._dfs_recursive(child, result)

    def traverse_levels(self) -> List[List[TreeNode]]:
        """按层级返回节点"""
        if self.root is None:
            return []
        result = []
        current_level = [self.root]
        while current_level:
            result.append(current_level)
            next_level = []
            for node in current_level:
                next_level.extend(node.children)
            current_level = next_level
        return result

    # ============ 查找方法 ============

    def find(self, data: Any) -> Optional[TreeNode]:
        """查找第一个匹配 data 的节点"""
        if self.root is None:
            return None
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            if node.data == data:
                return node
            queue.extend(node.children)
        return None

    def find_all(self, data: Any) -> List[TreeNode]:
        """查找所有匹配 data 的节点"""
        if self.root is None:
            return []
        result = []
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            if node.data == data:
                result.append(node)
            queue.extend(node.children)
        return result

    def find_by_path(self, path: List[Any]) -> Optional[TreeNode]:
        """按路径查找节点，如 ['支出', '餐饮', '外卖']"""
        if self.root is None or not path:
            return None
        if self.root.data != path[0]:
            return None

        node = self.root
        for data in path[1:]:
            found = False
            for child in node.children:
                if child.data == data:
                    node = child
                    found = True
                    break
            if not found:
                return None
        return node

    def get_path(self, node: TreeNode) -> List[Any]:
        """获取从根到节点的路径数据"""
        path = []
        current = node
        while current is not None:
            path.append(current.data)
            current = current.parent
        return list(reversed(path))

    def get_leaves(self) -> List[TreeNode]:
        """返回所有叶子节点"""
        if self.root is None:
            return []
        result = []
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            if node.is_leaf():
                result.append(node)
            queue.extend(node.children)
        return result

    # ============ 辅助方法 ============

    def __len__(self) -> int:
        return self._size

    def __str__(self) -> str:
        if self.root is None:
            return "Tree(empty)"
        return self._tree_string(self.root, "", True)

    def _tree_string(self, node: TreeNode, prefix: str, is_last: bool) -> str:
        """递归生成树形字符串"""
        result = prefix
        if prefix:  # 非根节点
            result += "└── " if is_last else "├── "
        result += f"{node.data}\n"

        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(node.children):
            is_last_child = (i == len(node.children) - 1)
            result += self._tree_string(child, child_prefix, is_last_child)

        return result

    def __repr__(self) -> str:
        return f"Tree(root={self.root.data if self.root else None}, size={self._size})"


# ============ 测试代码 ============
if __name__ == "__main__":
    print("=== 测试 Tree ===")

    # 构建分类树
    tree = Tree()
    root = tree.set_root("支出")

    # 一级分类
    food = TreeNode("餐饮")
    travel = TreeNode("交通")
    root.add_child(food)
    root.add_child(travel)

    # 二级分类
    breakfast = TreeNode("早餐")
    lunch = TreeNode("午餐")
    dinner = TreeNode("晚餐")
    food.add_child(breakfast)
    food.add_child(lunch)
    food.add_child(dinner)

    bus = TreeNode("公交")
    taxi = TreeNode("打车")
    travel.add_child(bus)
    travel.add_child(taxi)

    print(f"树高度: {tree.height()}")
    print(f"节点总数: {tree.size()}")
    print()
    print(tree)

    # 测试查找
    print(f"查找 '午餐': {tree.find('午餐')}")
    print(f"按路径查找: {tree.find_by_path(['支出', '餐饮', '午餐'])}")
    print(f"午餐的路径: {tree.get_path(lunch)}")

    # 测试遍历
    print(f"BFS遍历: {[n.data for n in tree.traverse_bfs()]}")
    print(f"叶子节点: {[n.data for n in tree.get_leaves()]}")