---
name: finance-tracker-refactor-plan
overview: 为 Finance_Tracker 项目制定循序渐进的代码重构与功能开发计划，确保每一步都不破坏现有功能
todos:
  - id: complete-ds
    content: 补全 HashMap/BST/Queue/Set/Tree 五个数据结构实现，含独立测试
    status: completed
  - id: integrate-hashmap
    content: 集成 HashMap 作为 tid 索引，改造三个 O(n) 查找函数为 O(1)
    status: completed
    dependencies:
      - complete-ds
  - id: integrate-bst
    content: 集成 BST 实现日期/金额范围查询，改造排序功能，扩展菜单7
    status: completed
    dependencies:
      - integrate-hashmap
  - id: integrate-stack-queue
    content: 集成 Stack 实现 Undo/Redo，集成 Queue 实现通知系统
    status: completed
    dependencies:
      - complete-ds
  - id: integrate-tree-set
    content: 集成 Tree 实现分类层级体系，集成 Set 实现分类名去重
    status: completed
    dependencies:
      - complete-ds
  - id: unify-account
    content: 统一异常定义，联通 Account 与 Transaction 模型
    status: completed
    dependencies:
      - integrate-hashmap
---

## 产品概述

为 Finance_Tracker 项目制定循序渐进的代码重构与功能开发计划，将链表、栈、队列、哈希表、二叉搜索树、多叉树、集合这七种数据结构逐步集成到现有系统中，每一步确保不破坏已有功能。

## 核心功能

- **补全空壳数据结构**：完善 HashMap、BST、Queue、Tree、Set 的完整实现
- **集成 HashMap 索引**：将 tid 查找从 O(n) 优化至 O(1)，改造 transaction.py 中三个遍历函数
- **集成 BST 范围查询**：按日期/金额的范围查询与高效排序，替代现有列表排序
- **集成 Stack 撤销/重做**：为增删改操作提供 Undo/Redo 能力
- **集成 Queue 通知系统**：预算超支、大额交易等实时提醒
- **集成 Tree 分类体系 + Set 去重**：多级分类树与分类名唯一性保证
- **统一异常与 Account 联通**：消除异常重复定义，让 Account 与 Transaction 产生关联

## 技术栈

- Python 3.x 命令行应用
- 现有架构：DoublyLinkedList + Transaction 模型 + JSON 持久化
- 新增数据结构：HashMap、BST、Queue、Tree、Set（均在 structures/ 目录下）

## 实现方案

### 总体策略：增量式集成，渐进式替换

1. **先实现后集成**：每个数据结构先独立实现并通过单元测试，确认无误后再接入主流程
2. **双路径并行**：集成新数据结构时，保留原有 O(n) 函数作为 fallback，新函数以可选参数方式并存，验证通过后再替换
3. **每步可验证**：每个步骤完成后，运行完整菜单流程确认已有功能不受影响

---

### 阶段一：补全数据结构实现（零风险，仅改 structures/）

**目标**：为 5 个空壳文件补全核心方法，每个结构附带 `if __name__ == "__main__"` 独立测试。

**安全保证**：此阶段仅修改 `structures/` 目录，不碰 `main.py` 和 `models/`，对运行中的系统零影响。

#### 步骤 1.1：完善 HashMap（structures/hashmap.py）

**当前代码**（8行空壳）：

```python
class HashMap:
    def __init__(self, size=100):
        self.size = size
        self.map = [None] * self.size
```

**改造为**：

```python
class HashMap:
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]  # 链地址法
        self._size = 0

    def _hash(self, key):
        return hash(key) % self.capacity

    def put(self, key, value):
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1

    def get(self, key):
        idx = self._hash(key)
        for k, v in self.buckets[idx]:
            if k == key:
                return v
        return None

    def remove(self, key):
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._size -= 1
                return True
        return False

    def contains_key(self, key):
        return self.get(key) is not None

    def keys(self):
        return [k for bucket in self.buckets for k, v in bucket]

    def values(self):
        return [v for bucket in self.buckets for k, v in bucket]

    def __len__(self):
        return self._size

    def __str__(self):
        pairs = [f"{k}: {v}" for bucket in self.buckets for k, v in bucket]
        return "{" + ", ".join(pairs) + "}"
```

**验证方法**：在文件末尾 `if __name__ == "__main__"` 中执行：

```python
hm = HashMap()
hm.put(1, "node1")
hm.put(2, "node2")
assert hm.get(1) == "node1"
assert hm.contains_key(2) == True
hm.remove(1)
assert hm.get(1) is None
assert len(hm) == 1
```

---

#### 步骤 1.2：完善 BST（structures/bst.py）

**当前代码**（5行空壳）：

```python
class BST:
    def __init__(self, root=None):
        self.root = root
```

**改造为**：

```python
class BSTNode:
    def __init__(self, key, data=None):
        self.key = key
        self.data = data    # data 可以是单个 Transaction 或 list
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, key, data=None):
        self.root = self._insert(self.root, key, data)

    def _insert(self, node, key, data):
        if node is None:
            return BSTNode(key, data)
        if key < node.key:
            node.left = self._insert(node.left, key, data)
        elif key > node.key:
            node.right = self._insert(node.right, key, data)
        else:
            # key已存在，将data追加到列表
            if isinstance(node.data, list):
                node.data.append(data)
            else:
                node.data = [node.data, data]
        return node

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        if node is None or node.key == key:
            return node
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)

    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node)
            self._inorder(node.right, result)

    def range_query(self, low, high):
        result = []
        self._range_query(self.root, low, high, result)
        return result

    def _range_query(self, node, low, high, result):
        if node is None:
            return
        if low < node.key:
            self._range_query(node.left, low, high, result)
        if low <= node.key <= high:
            result.append(node)
        if node.key < high:
            self._range_query(node.right, low, high, result)

    def delete(self, key):
        self.root = self._delete(self.root, key)

    def _delete(self, node, key):
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            successor = self._min_node(node.right)
            node.key = successor.key
            node.data = successor.data
            node.right = self._delete(node.right, successor.key)
        return node

    def _min_node(self, node):
        while node.left:
            node = node.left
        return node
```

**验证方法**：`if __name__ == "__main__"` 中执行：

```python
bst = BST()
bst.insert(50, "txn50")
bst.insert(30, "txn30")
bst.insert(70, "txn70")
assert bst.search(30) is not None
assert bst.search(99) is None
assert len(bst.inorder()) == 3
result = bst.range_query(25, 55)
assert all(25 <= n.key <= 55 for n in result)
bst.delete(30)
assert bst.search(30) is None
```

---

#### 步骤 1.3：完善 Queue（structures/queue.py）

**当前代码**（4行空壳）：

```python
class Queue:
    def __init__(self):
        self.items = []
```

**改造为**：

```python
class Queue:
    """队列：先进先出 FIFO"""
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        """入队"""
        self.items.append(item)

    def dequeue(self):
        """出队"""
        if self.is_empty():
            return None
        return self.items.pop(0)

    def peek(self):
        """查看队首"""
        if self.is_empty():
            return None
        return self.items[0]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def __str__(self):
        return "Front → " + " | ".join(str(i) for i in self.items) + " → Rear"
```

**验证方法**：

```python
q = Queue()
q.enqueue("a")
q.enqueue("b")
assert q.peek() == "a"
assert q.dequeue() == "a"
assert q.size() == 1
```

---

#### 步骤 1.4：完善 Tree（structures/tree.py）

**当前代码**（7行空壳）：

```python
class Tree:
    def __init__(self, root=None):
        self.root = root
```

**改造为**：

```python
class TreeNode:
    def __init__(self, name, data=None):
        self.name = name
        self.data = data
        self.children = []
        self.parent = None

    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)

    def get_children(self):
        return self.children

    def find(self, name):
        if self.name == name:
            return self
        for child in self.children:
            result = child.find(name)
            if result:
                return result
        return None

    def traverse(self, level=0):
        result = []
        result.append("  " * level + self.name)
        for child in self.children:
            result.extend(child.traverse(level + 1))
        return result

    def __str__(self):
        return "\n".join(self.traverse())


class Tree:
    def __init__(self, root=None):
        self.root = root

    def add_child(self, parent_name, child_node):
        if self.root is None:
            self.root = child_node
            return
        parent = self.root.find(parent_name)
        if parent:
            parent.add_child(child_node)

    def find(self, name):
        if self.root is None:
            return None
        return self.root.find(name)

    def traverse(self):
        if self.root is None:
            return []
        return self.root.traverse()

    def __str__(self):
        if self.root is None:
            return "(空树)"
        return str(self.root)
```

**验证方法**：

```python
root = TreeNode("支出")
food = TreeNode("餐饮")
food.add_child(TreeNode("外卖"))
food.add_child(TreeNode("堂食"))
root.add_child(food)
root.add_child(TreeNode("交通"))
tree = Tree(root)
assert tree.find("外卖") is not None
assert tree.find("不存在") is None
lines = tree.traverse()
assert len(lines) == 5
```

---

#### 步骤 1.5：新建 Set（structures/set.py）

**新建文件**，基于 HashMap 实现：

```python
from structures.hashmap import HashMap

class Set:
    """集合：基于 HashMap 实现，元素唯一"""
    def __init__(self):
        self._map = HashMap()

    def add(self, item):
        if not self.contains(item):
            self._map.put(item, True)

    def remove(self, item):
        return self._map.remove(item)

    def contains(self, item):
        return self._map.contains_key(item)

    def union(self, other):
        result = Set()
        for item in self.to_list():
            result.add(item)
        for item in other.to_list():
            result.add(item)
        return result

    def intersection(self, other):
        result = Set()
        for item in self.to_list():
            if other.contains(item):
                result.add(item)
        return result

    def to_list(self):
        return self._map.keys()

    def __len__(self):
        return len(self._map)

    def __str__(self):
        return "{" + ", ".join(str(k) for k in self.to_list()) + "}"
```

**验证方法**：

```python
s = Set()
s.add("餐饮")
s.add("交通")
s.add("餐饮")  # 重复
assert len(s) == 2
assert s.contains("餐饮")
s.remove("交通")
assert not s.contains("交通")
```

**阶段一验证检查清单**：

- [ ] 运行 `python structures/hashmap.py`，断言全部通过
- [ ] 运行 `python structures/bst.py`，断言全部通过
- [ ] 运行 `python structures/queue.py`，断言全部通过
- [ ] 运行 `python structures/tree.py`，断言全部通过
- [ ] 运行 `python structures/set.py`，断言全部通过
- [ ] 运行 `python main.py`，主菜单所有功能正常（未修改任何主流程代码）

---

### 阶段二：集成 HashMap 索引（O(n)→O(1) 查找）

**目标**：将 `check_tid_exists`、`get_transaction_by_tid`、`delete_transaction` 从 O(n) 优化至 O(1)。

**安全策略**：采用**可选参数**模式，新逻辑与旧逻辑并存，不传 `index` 时回退到遍历。

#### 步骤 2.1：在 transaction.py 新增索引构建函数

在 `models/transaction.py` 末尾新增：

```python
from structures.hashmap import HashMap

def build_tid_index(linked_list: DoublyLinkedList) -> HashMap:
    """遍历链表，建立 tid → Node 的 HashMap 索引"""
    index = HashMap(capacity=200)
    current = linked_list.head
    while current:
        index.put(current.data.tid, current)
        current = current.next
    return index
```

#### 步骤 2.2：改造三个 O(n) 函数为 O(1)

**check_tid_exists** 改造：

```python
def check_tid_exists(linked_list: DoublyLinkedList, tid, index: HashMap = None) -> bool:
    """检查 tid 是否已存在"""
    if index is not None:
        return index.contains_key(tid)
    # fallback: O(n) 遍历
    current = linked_list.head
    while current:
        if current.data.tid == tid:
            return True
        current = current.next
    return False
```

**get_transaction_by_tid** 改造：

```python
def get_transaction_by_tid(linked_list: DoublyLinkedList, tid, index: HashMap = None):
    """根据 tid 获取交易记录"""
    if index is not None:
        node = index.get(tid)
        return node.data if node else None
    # fallback: O(n) 遍历
    current = linked_list.head
    while current:
        if current.data.tid == tid:
            return current.data
        current = current.next
    return None
```

**delete_transaction** 改造：

```python
def delete_transaction(linked_list: DoublyLinkedList, tid, index: HashMap = None):
    """根据交易ID删除"""
    if index is not None:
        node = index.get(tid)
        if node:
            linked_list.remove(node)
            index.remove(tid)
            print(f"已删除交易 #{tid}")
            return True
        print(f"未找到交易 #{tid}")
        return False
    # fallback: O(n) 遍历
    current = linked_list.head
    while current:
        if current.data.tid == tid:
            linked_list.remove(current)
            print(f"已删除交易 #{tid}")
            return True
        current = current.next
    print(f"未找到交易 #{tid}")
    return False
```

#### 步骤 2.3：改造 add_transaction 和 update_transaction 同步索引

**add_transaction** 改造：

```python
def add_transaction(linked_list: DoublyLinkedList, tid, type, amount, category, date, note="", index: HashMap = None):
    """添加交易"""
    t = Transaction(tid, type, amount, category, date, note)
    linked_list.prepend(t)
    if index is not None:
        index.put(tid, linked_list.head)  # head就是刚prepend的节点
    print(f"已添加交易#{tid}")
```

**update_transaction** 改造（tid变更时需同步索引）：

```python
def update_transaction(linked_list: DoublyLinkedList, target_tid, index: HashMap = None, **kwargs):
    """根据交易ID修改，kwargs 是要修改的字段"""
    ALLOWED_FIELDS = {"tid", "type", "amount", "category", "date", "note"}

    if index is not None:
        node = index.get(target_tid)
        if node:
            old_tid = target_tid
            for key, value in kwargs.items():
                if key not in ALLOWED_FIELDS:
                    print(f"key:'{key}' is not allowed to update")
                    continue
                if hasattr(node.data, key):
                    setattr(node.data, key, value)
            # 如果 tid 被修改，需更新索引
            new_tid = kwargs.get('tid', old_tid)
            if new_tid != old_tid:
                index.remove(old_tid)
                index.put(new_tid, node)
            print(f"已修改交易 #{target_tid}")
            return True
        print(f"未找到交易 #{target_tid}")
        return False

    # fallback: O(n) 遍历
    current = linked_list.head
    while current:
        if current.data.tid == target_tid:
            for key, value in kwargs.items():
                if key not in ALLOWED_FIELDS:
                    print(f"key:'{key}' is not allowed to update")
                    continue
                if hasattr(current.data, key):
                    setattr(current.data, key, value)
            print(f"已修改交易 #{target_tid}")
            return True
        current = current.next
    print(f"未找到交易 #{target_tid}")
    return False
```

**注意**：`update_transaction` 的参数顺序变更（`index` 移到 `**kwargs` 之前），所有调用处需要同步更新。

#### 步骤 2.4：在 main.py 中构建和维护索引

在 `main.py` 顶部导入：

```python
from structures.hashmap import HashMap
```

修改 `main()` 函数：

```python
def main():
    file = load_data()
    tid_index = build_tid_index(file)  # 新增：构建索引
    print("=== Finance_Tracker ===")
    # ...后续所有调用 check_tid_exists / get_transaction_by_tid / delete_transaction / 
    # add_transaction / update_transaction 的地方，传入 tid_index 参数
```

需要在 main.py 中修改的调用点：

- line 37: `check_tid_exists(file, tid)` → `check_tid_exists(file, tid, tid_index)`
- line 66: `check_tid_exists(file, tid)` → `check_tid_exists(file, tid, tid_index)`
- line 72: `get_transaction_by_tid(file, tid)` → `get_transaction_by_tid(file, tid, tid_index)`
- line 79: `delete_transaction(file, tid)` → `delete_transaction(file, tid, tid_index)`
- line 46: `add_transaction(file, ...)` → `add_transaction(file, ..., tid_index)`
- line 103: `check_tid_exists(file, tid)` → `check_tid_exists(file, tid, tid_index)`
- line 107: `get_transaction_by_tid(file, tid)` → `get_transaction_by_tid(file, tid, tid_index)`
- line 119: `check_tid_exists(file, new_tid)` → `check_tid_exists(file, new_tid, tid_index)`
- line 154: `update_transaction(file, tid, **kwargs)` → `update_transaction(file, tid, tid_index, **kwargs)`

**阶段二验证检查清单**：

- [ ] 运行 `python main.py`，执行菜单 1-7 全部功能，行为与改造前完全一致
- [ ] 在 `delete_transaction` 中添加临时 print 确认走了 HashMap 路径（测试后移除）
- [ ] 测试 tid 修改：修改某交易 tid 后，确认新 tid 可被查找、旧 tid 不再存在
- [ ] 测试删除后索引同步：删除某交易后，确认 check_tid_exists 返回 False
- [ ] 测试添加后索引同步：添加新交易后，确认 check_tid_exists 返回 True
- [ ] 移除所有临时调试 print

---

### 阶段三：集成 BST 范围查询与排序

**目标**：用 BST 实现按日期/金额的高效范围查询，改造排序功能。

**安全策略**：新增查询函数和菜单项，不修改现有排序逻辑。

#### 步骤 3.1：在 transaction.py 新增 BST 索引构建和查询函数

```python
from structures.bst import BST, BSTNode

def build_date_index(linked_list: DoublyLinkedList) -> BST:
    """按日期建 BST，key=日期字符串(YYYY-MM-DD可比), data=Transaction"""
    bst = BST()
    current = linked_list.head
    while current:
        bst.insert(current.data.date, current.data)
        current = current.next
    return bst

def build_amount_index(linked_list: DoublyLinkedList) -> BST:
    """按金额建 BST，key=金额, data=Transaction"""
    bst = BST()
    current = linked_list.head
    while current:
        bst.insert(current.data.amount, current.data)
        current = current.next
    return bst

def query_by_date_range(bst: BST, start_date: str, end_date: str):
    """查询日期范围内的交易"""
    nodes = bst.range_query(start_date, end_date)
    results = []
    for node in nodes:
        if isinstance(node.data, list):
            results.extend(node.data)
        else:
            results.append(node.data)
    return results

def query_by_amount_range(bst: BST, min_amount: float, max_amount: float):
    """查询金额范围内的交易"""
    nodes = bst.range_query(min_amount, max_amount)
    results = []
    for node in nodes:
        if isinstance(node.data, list):
            results.extend(node.data)
        else:
            results.append(node.data)
    return results
```

#### 步骤 3.2：在 main.py 菜单 7 中新增查询子项

扩展菜单 7：

```python
elif choice == "7":
    print("--- 更多功能 ---")
    print("1. 按交易ID升序排列（从小到大）")
    print("2. 按交易日期降序排列（从新到旧）")
    print("3. 按日期范围查询交易")
    print("4. 按金额范围筛选交易")
    print("0. 返回主菜单")
    sort_choice = input("请选择: ").strip()
    if sort_choice == "1":
        sort_transactions(file, mode="tid_asc")
        save_data(file)
    elif sort_choice == "2":
        sort_transactions(file, mode="date_desc")
        save_data(file)
    elif sort_choice == "3":
        date_bst = build_date_index(file)
        start = input("起始日期(YYYY-MM-DD): ").strip()
        end = input("结束日期(YYYY-MM-DD): ").strip()
        results = query_by_date_range(date_bst, start, end)
        print(f"\n找到 {len(results)} 条记录：")
        for t in results:
            print(json.dumps(t.to_dict(), ensure_ascii=False, indent=2))
    elif sort_choice == "4":
        amount_bst = build_amount_index(file)
        min_amt = float(input("最小金额: ").strip())
        max_amt = float(input("最大金额: ").strip())
        results = query_by_amount_range(amount_bst, min_amt, max_amt)
        print(f"\n找到 {len(results)} 条记录：")
        for t in results:
            print(json.dumps(t.to_dict(), ensure_ascii=False, indent=2))
    elif sort_choice == "0":
        pass
    else:
        print("无效选择，请重新输入")
```

**阶段三验证检查清单**：

- [ ] 菜单 7 原有排序（1、2）功能不变
- [ ] 菜单 7 新增查询（3、4）正确返回范围结果
- [ ] 日期格式为 YYYY-MM-DD 字符串，字典序比较正确
- [ ] 金额相同的多条交易（BST insert 中 data 为 list）都能正确返回
- [ ] 空结果时打印"找到 0 条记录"

---

### 阶段四：集成 Stack 撤销/重做 + Queue 通知

**安全策略**：新增功能模块，不修改已有菜单选项的行为。

#### 步骤 4.1：定义 Operation 数据类

在 `models/transaction.py` 中新增：

```python
class Operation:
    """记录操作历史，用于撤销/重做"""
    def __init__(self, op_type, tid, old_data=None):
        self.op_type = op_type  # "add" / "delete" / "update"
        self.tid = tid
        self.old_data = old_data  # 对于 update，保存修改前的 to_dict()
```

#### 步骤 4.2：在 main.py 集成 Undo/Redo

```python
from structures.stack import Stack

# 在 main() 中：
undo_stack = Stack()
redo_stack = Stack()

# 添加交易时（choice "1"）：
old_data = None  # 新增操作无旧数据
add_transaction(file, tid, type_, amount, category, date, note, tid_index)
undo_stack.push(Operation("add", tid))  # 逆操作是删除
redo_stack = Stack()  # 新操作清空 redo

# 删除交易时（choice "2" 确认删除后）：
transaction = get_transaction_by_tid(file, tid, tid_index)
old_data = transaction.to_dict()
delete_transaction(file, tid, tid_index)
undo_stack.push(Operation("delete", tid, old_data))
redo_stack = Stack()

# 修改交易时（choice "3" 执行修改前）：
transaction = get_transaction_by_tid(file, tid, tid_index)
old_data = transaction.to_dict()
update_transaction(file, tid, tid_index, **kwargs)
undo_stack.push(Operation("update", tid, old_data))
redo_stack = Stack()

# 新增菜单 8：撤销
elif choice == "8":
    if undo_stack.is_empty():
        print("没有可撤销的操作")
    else:
        op = undo_stack.pop()
        if op.op_type == "add":
            delete_transaction(file, op.tid, tid_index)
            print(f"已撤销添加交易 #{op.tid}")
        elif op.op_type == "delete":
            t = Transaction.from_dict(op.old_data)
            add_transaction(file, t.tid, t.type, t.amount, t.category, t.date, t.note, tid_index)
            print(f"已撤销删除交易 #{op.tid}")
        elif op.op_type == "update":
            current = get_transaction_by_tid(file, op.tid, tid_index)
            if current:
                redo_data = current.to_dict()
                for key, value in op.old_data.items():
                    setattr(current, key, value)
                # 如果 tid 被修改过，需更新索引
                if op.old_data.get('tid') != op.tid:
                    tid_index.remove(op.tid)
                    tid_index.put(op.old_data['tid'], ???)
                redo_stack.push(Operation("update", op.tid, redo_data))
            print(f"已撤销修改交易 #{op.tid}")
        redo_stack.push(op)
        save_data(file)
```

**注意**：撤销操作中 tid 变更的索引同步较复杂，需要仔细处理。简化方案：update 的 undo 直接用 old_data 重建整条记录。

#### 步骤 4.3：新建通知系统

新建 `models/notification.py`：

```python
from structures.queue import Queue

class NotificationSystem:
    def __init__(self):
        self.queue = Queue()

    def add_notification(self, message):
        self.queue.enqueue(message)

    def check_budget(self, transactions, category_budgets):
        """检查各类别是否超支"""
        spending = {}
        for t in transactions:
            if t.type == "支出":
                spending[t.category] = spending.get(t.category, 0) + t.amount
        for cat, budget in category_budgets.items():
            if spending.get(cat, 0) > budget:
                self.add_notification(f"⚠ {cat} 超出预算！已花费 {spending[cat]:.2f}，预算 {budget:.2f}")

    def check_large_transaction(self, transaction, threshold=1000):
        if transaction.type == "支出" and transaction.amount >= threshold:
            self.add_notification(f"⚠ 大额支出提醒：{transaction.category} {transaction.amount:.2f}元")

    def show_notifications(self):
        if self.queue.is_empty():
            print("暂无新通知")
            return
        count = 0
        while not self.queue.is_empty():
            msg = self.queue.dequeue()
            print(msg)
            count += 1
        print(f"共 {count} 条通知")
```

在 main.py 中新增菜单 9："查看通知"

**阶段四验证检查清单**：

- [ ] 菜单 1-7 功能不受影响
- [ ] 菜单 8：添加交易后撤销，确认交易被删除
- [ ] 菜单 8：删除交易后撤销，确认交易恢复
- [ ] 菜单 8：修改交易后撤销，确认字段恢复原值
- [ ] 菜单 8：无操作时撤销，提示"没有可撤销的操作"
- [ ] 菜单 9：无通知时显示"暂无新通知"
- [ ] 菜单 9：添加大额支出后查看通知，正确显示提醒

---

### 阶段五：集成 Tree 分类体系 + Set 去重

#### 步骤 5.1：新建分类管理模块

新建 `models/category.py`：

```python
from structures.tree import Tree, TreeNode
from structures.set import Set

class CategoryManager:
    def __init__(self):
        self.tree = Tree(TreeNode("全部分类"))
        self.category_set = Set()

    def add_category(self, parent_name, category_name):
        """添加分类节点"""
        if self.category_set.contains(category_name):
            return False
        self.tree.add_child(parent_name, TreeNode(category_name))
        self.category_set.add(category_name)
        return True

    def init_default_categories(self):
        """初始化默认分类"""
        self.add_category("全部分类", "支出")
        self.add_category("全部分类", "收入")
        self.add_category("支出", "餐饮")
        self.add_category("支出", "交通")
        self.add_category("支出", "娱乐")
        self.add_category("餐饮", "外卖")
        self.add_category("餐饮", "堂食")
        self.add_category("交通", "公交")
        self.add_category("交通", "打车")
        self.add_category("收入", "工资")
        self.add_category("收入", "兼职")

    def get_all_categories(self):
        return self.category_set.to_list()

    def get_subcategories(self, category_name):
        node = self.tree.find(category_name)
        if node:
            return [child.name for child in node.get_children()]
        return []

    def display_tree(self):
        print(self.tree)

    def get_category_statistics(self, transactions):
        """按分类汇总金额"""
        stats = {}
        for t in transactions:
            cat = t.category
            if cat not in stats:
                stats[cat] = 0.0
            if t.type == "支出":
                stats[cat] += t.amount
            else:
                stats[cat] -= t.amount
        return stats
```

#### 步骤 5.2：在 main.py 中集成分类管理

新增菜单项"分类统计"，改造添加交易的分类输入（可选从分类树选择）。

**阶段五验证检查清单**：

- [ ] 分类树正确展示多级结构
- [ ] 重复分类名被 Set 拦截
- [ ] 分类统计金额计算正确
- [ ] 已有交易的分类不受影响

---

### 阶段六：统一异常 + Account 联通

**目标**：消除异常重复定义，让 Account 与 Transaction 产生关联。

#### 步骤 6.1：统一异常定义

- `exceptions.py` 保留为唯一异常源，增加 `InsufficientFundsError`
- `account.py` 中删除 `InsufficientFundsError` 和 `InvalidAmountError`，改为 `from exceptions import InsufficientFundsError, InvalidAmountError`
- 修正命名不一致：`exceptions.py` 中的 `InsufficientBalanceError` 改为 `InsufficientFundsError`（与 account.py 对齐）

**具体修改**：

1. `exceptions.py`：删除 `InsufficientBalanceError`，新增 `InsufficientFundsError`
2. `account.py`：删除 line 4-10 的异常定义，添加 `from exceptions import InsufficientFundsError, InvalidAmountError`

**验证**：运行 `python models/account.py` 的测试代码，确认异常仍能正确抛出和捕获。

#### 步骤 6.2：Transaction 增加 account_id 字段

- 在 `Transaction.__init__` 中添加 `self.account_id = account_id`，默认为 `None`
- 在 `to_dict` 和 `from_dict` 中同步处理 `account_id`
- 向后兼容：`account_id` 默认 None，不传时 JSON 中不存储（用 `data.get("account_id")` 读取）

#### 步骤 6.3：Account 维护交易列表

- `Account.__init__` 中增加 `self._transactions = DoublyLinkedList()`
- `deposit` 时自动创建一笔收入类型 Transaction 并追加到 `_transactions`
- `withdraw` 时自动创建一笔支出类型 Transaction 并追加到 `_transactions`
- 新增 `get_transactions()` 方法返回交易列表

#### 步骤 6.4：新增账户管理菜单

在 main.py 中新增菜单项"账户管理"，支持：

- 创建储蓄/信用账户
- 存款/取款（自动生成交易记录）
- 查看余额和利息
- 查看账户关联的交易记录

**阶段六验证检查清单**：

- [ ] `python models/account.py` 测试通过（异常从 exceptions.py 导入）
- [ ] 已有交易记录加载正常（account_id 为 None，不影响）
- [ ] 创建账户 → 存款 → 查看，交易记录自动生成
- [ ] 信用账户取款超出余额但在信用额度内，正常执行
- [ ] 取款超出信用额度，正确抛出 InsufficientFundsError

---

## 六种数据结构应用场景汇总

| 数据结构 | 当前状态 | 应用场景 | 涉及模块 | 性能提升 |
| --- | --- | --- | --- | --- |
| 链表 DoublyLinkedList | ✅ 已在用 | 交易记录主存储，保持插入顺序 | transaction.py, main.py | O(1)头部插入/节点删除 |
| 哈希表 HashMap | ❌ 空壳 | tid→Node索引，O(1)查找/删除/查重 | transaction.py | O(n)→O(1) |
| 二叉搜索树 BST | ❌ 空壳 | 按日期/金额范围查询与排序 | transaction.py, main.py | O(n)→O(log n)查询 |
| 栈 Stack | ✅ 已实现 | 撤销/重做操作历史 | main.py | 操作回退O(1) |
| 队列 Queue | ❌ 空壳 | 预算超支/大额交易通知队列 | notification.py | FIFO通知消费 |
| 多叉树 Tree | ❌ 空壳 | 多级分类体系，层级汇总统计 | category.py | 层级遍历O(n) |
| 集合 Set | 🆕 新建 | 分类名去重，标签唯一性 | category.py | O(1)成员检测 |


## 目录结构

```
Finance_Tracker/
├── main.py                               [MODIFY] 每阶段更新菜单和索引维护
├── exceptions.py                         [MODIFY] 阶段六：统一为唯一异常源
├── data/
│   └── data.json                         不修改
├── models/
│   ├── transaction.py                    [MODIFY] 阶段二：HashMap索引；阶段三：BST查询；阶段四：Operation类；阶段六：account_id字段
│   ├── account.py                        [MODIFY] 阶段六：删除重复异常，增加交易列表
│   ├── notification.py                   [NEW] 阶段四：通知系统
│   └── category.py                       [NEW] 阶段五：分类树管理
└── structures/
    ├── linked_list.py                    不修改（已完善）
    ├── stack.py                          不修改（已完善）
    ├── hashmap.py                        [MODIFY] 阶段一：补全全部方法
    ├── bst.py                            [MODIFY] 阶段一：补全BSTNode+全部方法
    ├── queue.py                          [MODIFY] 阶段一：补全全部方法
    ├── tree.py                           [MODIFY] 阶段一：补全TreeNode+全部方法
    └── set.py                            [NEW] 阶段一：基于HashMap的集合实现
```

## 实现注意事项

- **HashMap 负载因子**：当元素数 > 容量 * 0.75 时自动扩容（rehash），防止链过长退化
- **BST 退化为链表**：未引入 AVL/红黑树平衡，数据量大时可能退化；当前数据规模（几十条）可接受
- **索引同步一致性**：增/删/改操作必须同步更新 HashMap 索引和 BST 索引，建议在 transaction.py 中封装统一的同步逻辑
- **排序安全性**：sort_transactions 已有"先排序后重连"的安全策略，BST 替换时保持同样策略
- **main.py 冗余代码**：line 27 的 `transactions = file.to_list()` 和 line 190-192 的冗余 pass 应在重构中清理
- **update_transaction 参数顺序**：`index` 参数必须在 `**kwargs` 之前，调用处需同步更新
- **Undo 中 tid 变更的索引同步**：update 的 undo 如果涉及 tid 修改，需同时更新 HashMap 索引