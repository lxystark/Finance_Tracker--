




from datetime import datetime
from structures.linked_list import DoublyLinkedList
from structures.hashmap import HashMap


class Transaction:
    def __init__(self, tid, type, amount, category, date, note=""):
        self.tid = tid          # 交易ID
        self.type = type        # 类型（收入/支出）
        self.amount = amount    # 金额
        self.category = category # 分类
        self.date = date        # 日期
        self.note = note        # 备注
    
    # 在 Transaction 类中添加
    def __str__(self):

        return f"#{self.tid} {self.type} {self.amount}元 [{self.category}] {self.date}"

    def to_dict(self):
        """对象 → 字典（便于 JSON 存储）"""
        return {
            "tid": self.tid,
            "type": self.type,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "note": self.note
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """字典 → 对象（便于从 JSON 加载）"""
        return cls(
            tid=data["tid"],
            type=data["type"],
            amount=data["amount"],
            category=data["category"],
            date=data["date"],
            note=data.get("note", "")
        )



def build_tid_index(linked_list: DoublyLinkedList) -> HashMap:
    """根据链表构建 tid -> Node 的哈希索引，查找从 O(n) 提升为 O(1)"""
    index = HashMap()
    current = linked_list.head
    while current:
        index.put(current.data.tid, current)
        current = current.next
    return index


def check_tid_exists(tid, index: HashMap) -> bool:
    """检查 tid 是否已存在（通过 HashMap 索引 O(1) 查找）"""
    return index.contains_key(tid)


def get_transaction_by_tid(tid, index: HashMap):
    """根据 tid 获取交易记录（通过 HashMap 索引 O(1) 查找）"""
    node = index.get(tid)
    if node is not None:
        return node.data
    return None


def delete_transaction(linked_list: DoublyLinkedList, tid, index: HashMap):
    """根据交易ID删除（通过 HashMap 索引定位，并同步更新索引）"""
    node = index.get(tid)
    if node is not None:
        linked_list.remove(node)
        index.remove(tid)
        print(f"已删除交易 #{tid}")
        return True
    print(f"未找到交易 #{tid}")
    return False


def add_transaction(linked_list: DoublyLinkedList, tid, type, amount, category, date, note="", index: HashMap = None):
    """添加交易（同步更新 HashMap 索引）"""
    t = Transaction(tid, type, amount, category, date, note)
    linked_list.prepend(t)
    if index is not None:
        # prepend 后 head 就是新节点
        index.put(tid, linked_list.head)
    print(f"已添加交易#{tid}")


def update_transaction(linked_list: DoublyLinkedList, target_tid, index: HashMap, **kwargs):
    """根据交易ID修改，kwargs 是要修改的字段（通过 HashMap 索引定位，并同步更新索引）"""
    # 允许修改的字段白名单
    ALLOWED_FIELDS = {"tid", "type", "amount", "category", "date", "note"}

    node = index.get(target_tid)
    if node is None:
        print(f"未找到交易 #{target_tid}")
        return False
    for key, value in kwargs.items():
        if key not in ALLOWED_FIELDS:
            print(f"key:'{key}' is not allowed to update")
            continue
        if hasattr(node.data, key):
            setattr(node.data, key, value)
    # 如果 tid 被修改，需要更新索引中的键
    if 'tid' in kwargs and kwargs['tid'] != target_tid:
        index.remove(target_tid)
        index.put(kwargs['tid'], node)
    print(f"已修改交易 #{target_tid}")
    return True


def _parse_date(date_str):
    """安全解析日期字符串，支持 YYYY-M-D 和 YYYY-MM-DD"""
    return datetime.strptime(date_str, "%Y-%m-%d")


def sort_transactions(linked_list: DoublyLinkedList, mode="tid_asc"):
    """
    对双向链表中的交易记录进行排序（原地排序）

    参数:
        linked_list: 双向链表
        mode: 排序模式
            - "tid_asc": 按交易ID升序（默认）
            - "date_desc": 按交易日期降序（从新到旧）
    """
    if linked_list.head is None or linked_list.size <= 1:
        print("数据不足，无需排序")
        return

    # 第一步：将链表节点提取为列表（保留节点对象）
    nodes = []
    current = linked_list.head
    while current:
        nodes.append(current)
        current = current.next

    # 第二步：安全排序（成功后才重连，防止异常破坏链表）
    try:
        if mode == "tid_asc":
            nodes.sort(key=lambda node: node.data.tid)
        elif mode == "date_desc":
            nodes.sort(key=lambda node: _parse_date(node.data.date), reverse=True)
        else:
            print(f"未知排序模式: {mode}")
            return
    except Exception as e:
        print(f"排序失败: {e}")
        return  # 排序失败，链表保持原样

    # 第三步：排序成功，重新连接链表指针
    for i, node in enumerate(nodes):
        node.prev = nodes[i - 1] if i > 0 else None
        node.next = nodes[i + 1] if i < len(nodes) - 1 else None

    linked_list.head = nodes[0]
    linked_list.tail = nodes[-1]

    mode_name = "交易ID升序" if mode == "tid_asc" else "交易日期降序"
    print(f"已按【{mode_name}】排列完成，共 {len(nodes)} 条记录")






