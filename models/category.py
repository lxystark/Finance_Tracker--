'''
    @Author: Erhao Yao
    It's a category function for the project.
    Used for manage transactions
    分类管理器 - CategoryManager
    整合 Tree（多级分类层次） + Set（分类名唯一）
'''
from structures.tree import Tree, TreeNode
from structures.set import Set


class CategoryManager:
    """分类管理器：用 Tree 维护多级分类层次，用 Set 保证分类名唯一"""

    def __init__(self):
        self.tree = Tree(TreeNode("全部分类"))
        self.category_set = Set()
        # 根节点也加入集合
        self.category_set.add("全部分类")

    def add_category(self, parent_name: str, category_name: str) -> bool:
        """
        添加分类到指定父分类下
        返回 True 表示添加成功，False 表示分类名已存在或父分类不存在
        """
        # 检查分类名是否已存在（Set 去重）
        if self.category_set.contains(category_name):
            return False
        # 查找父节点
        parent_node = self.tree.find(parent_name)
        if parent_node is None:
            return False
        # 添加到树和集合
        parent_node.add_child(TreeNode(category_name))
        self.category_set.add(category_name)
        return True

    def init_default_categories(self):
        """初始化默认分类树"""
        # 一级分类
        self.add_category("全部分类", "支出")
        self.add_category("全部分类", "收入")
        # 支出 二级
        self.add_category("支出", "餐饮")
        self.add_category("支出", "交通")
        self.add_category("支出", "娱乐")
        self.add_category("支出", "购物")
        self.add_category("支出", "房租")
        # 餐饮 三级
        self.add_category("餐饮", "外卖")
        self.add_category("餐饮", "堂食")
        # 交通 三级
        self.add_category("交通", "公交")
        self.add_category("交通", "打车")
        # 收入 二级
        self.add_category("收入", "工资")
        self.add_category("收入", "兼职")
        self.add_category("收入", "红包")

    def category_exists(self, name: str) -> bool:
        """检查分类名是否存在"""
        return self.category_set.contains(name)

    def get_all_categories(self):
        """返回所有分类名列表"""
        return self.category_set.to_list()

    def get_subcategories(self, category_name: str):
        """获取指定分类的直接子分类列表"""
        node = self.tree.find(category_name)
        if node:
            return [child.data for child in node.children]
        return []

    def get_leaf_categories(self):
        """获取所有叶子分类（没有子分类的分类）"""
        leaves = self.tree.get_leaves()
        return [leaf.data for leaf in leaves if leaf.data != "全部分类"]

    def display_tree(self):
        """打印分类树"""
        print(self.tree)

    def get_parent_category(self, category_name: str):
        """获取指定分类的父分类"""
        node = self.tree.find(category_name)
        if node and node.parent:
            return node.parent.data
        return None

    def get_category_path(self, category_name: str):
        """获取从根到指定分类的路径"""
        node = self.tree.find(category_name)
        if node:
            return self.tree.get_path(node)
        return []

    def get_descendant_names(self, category_name: str):
        """获取指定分类的所有后代分类名（递归）"""
        node = self.tree.find(category_name)
        if node is None:
            return []
        return [d.data for d in node.descendants()]

    def remove_category(self, category_name: str) -> dict:
        """
        删除分类及其所有子分类
        不允许删除根节点（"全部分类"）
        返回删除快照 dict，包含 parent_name, categories 列表，
        可用于撤销恢复；删除失败返回空 dict
        """
        if category_name == "全部分类":
            return {}
        node = self.tree.find(category_name)
        if node is None:
            return {}
        # 保存快照：父分类名 + 被删除的所有分类（按父子关系记录）
        parent_name = node.parent.data if node.parent else None
        removed_categories = []  # [(name, parent_name), ...]
        # 先记录后代（先记录深层，再记录浅层，这样恢复时先加浅层再加深层）
        descendants = node.descendants()
        for d in descendants:
            d_parent = d.parent.data if d.parent else None
            removed_categories.append((d.data, d_parent))
        # 再记录自身
        removed_categories.append((category_name, parent_name))
        # 从 Set 中移除
        for d in descendants:
            self.category_set.remove(d.data)
        self.category_set.remove(category_name)
        # 从父节点中移除该子树
        if node.parent:
            node.parent.remove_child(node)
        return {"parent_name": parent_name, "categories": removed_categories}

    def restore_category(self, snapshot: dict) -> bool:
        """
        根据删除快照恢复分类（撤销删除）
        快照中的 categories 列表按 先深层后浅层 排列，
        需要逆序恢复（先加浅层父分类，再加深层子分类）
        """
        if not snapshot or "categories" not in snapshot:
            return False
        # 逆序恢复：先恢复浅层（父分类），再恢复深层（子分类）
        for name, parent_name in reversed(snapshot["categories"]):
            # 重新添加到树和集合
            parent_node = self.tree.find(parent_name)
            if parent_node is None:
                # 父节点尚未恢复，跳过
                continue
            if not self.category_set.contains(name):
                parent_node.add_child(TreeNode(name))
                self.category_set.add(name)
        return True

    def _tree_to_dict(self, node):
        """递归将树节点序列化为字典"""
        result = {"name": node.data, "children": []}
        for child in node.children:
            result["children"].append(self._tree_to_dict(child))
        return result

    def _dict_to_tree(self, data, parent_node):
        """递归从字典恢复树节点"""
        for child_data in data.get("children", []):
            child_node = TreeNode(child_data["name"])
            parent_node.add_child(child_node)
            self.category_set.add(child_data["name"])
            self._dict_to_tree(child_data, child_node)

    def to_dict(self):
        """将分类树序列化为字典（用于 JSON 存储）"""
        if self.tree.root is None:
            return {}
        return self._tree_to_dict(self.tree.root)

    def from_dict(self, data):
        """从字典恢复分类树（从 JSON 加载）"""
        if not data:
            return
        # 重建树
        self.tree = Tree(TreeNode(data["name"]))
        self.category_set = Set()
        self.category_set.add(data["name"])
        self._dict_to_tree(data, self.tree.root)

    def get_category_statistics(self, linked_list):
        """按分类汇总金额统计"""
        stats = {}
        current = linked_list.head
        while current:
            cat = current.data.category
            if cat not in stats:
                stats[cat] = {"收入": 0.0, "支出": 0.0, "净额": 0.0, "笔数": 0}
            if current.data.type == "收入":
                stats[cat]["收入"] += current.data.amount
            else:
                stats[cat]["支出"] += current.data.amount
            stats[cat]["净额"] = stats[cat]["收入"] - stats[cat]["支出"]
            stats[cat]["笔数"] += 1
            current = current.next
        return stats

    def __str__(self):
        return str(self.tree)


# ============ 测试代码 ============
if __name__ == "__main__":
    print("=== 测试 CategoryManager ===")

    cm = CategoryManager()
    cm.init_default_categories()

    # 测试显示树
    print("--- 分类树 ---")
    cm.display_tree()

    # 测试子分类
    print(f"\n支出的子分类: {cm.get_subcategories('支出')}")
    print(f"餐饮的子分类: {cm.get_subcategories('餐饮')}")
    print(f"工资的子分类: {cm.get_subcategories('工资')}")

    # 测试分类存在性
    print(f"\n'餐饮' 存在: {cm.category_exists('餐饮')}")
    print(f"'健身' 存在: {cm.category_exists('健身')}")

    # 测试添加重复分类（应失败）
    print(f"\n添加重复 '餐饮': {cm.add_category('支出', '餐饮')}")

    # 测试添加新分类
    print(f"添加新分类 '健身': {cm.add_category('支出', '健身')}")
    print(f"添加后 '健身' 存在: {cm.category_exists('健身')}")

    # 测试叶子分类
    print(f"\n叶子分类: {cm.get_leaf_categories()}")

    # 测试路径
    print(f"\n'外卖' 的路径: {cm.get_category_path('外卖')}")
    print(f"'外卖' 的父分类: {cm.get_parent_category('外卖')}")
