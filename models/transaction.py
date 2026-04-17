




from datetime import datetime
from structures.linked_list import DoublyLinkedList


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



def delete_transaction(linked_list: DoublyLinkedList, tid):
    """根据交易ID删除"""
    current = linked_list.head
    while current:
        if current.data.tid == tid:
            linked_list.remove(current)
            print(f"已删除交易 #{tid}")
            return True
        current = current.next
    print(f"未找到交易 #{tid}")
    return False

def check_tid_exists(linked_list: DoublyLinkedList, tid) -> bool:
    """检查 tid 是否已存在"""
    current = linked_list.head
    while current:
        if current.data.tid == tid:
            return True
        current = current.next
    return False


def get_transaction_by_tid(linked_list: DoublyLinkedList, tid):
    """根据 tid 获取交易记录"""
    current = linked_list.head
    while current:
        if current.data.tid == tid:
            return current.data
        current = current.next
    return None


def add_transaction(linked_list: DoublyLinkedList, tid, type, amount, category, date, note=""):
    """添加交易"""
    t = Transaction(tid,type,amount,category,date,note)
    linked_list.prepend(t)
    print(f"已添加交易#{tid}")


def update_transaction(linked_list: DoublyLinkedList, target_tid, **kwargs):
    """根据交易ID修改，kwargs 是要修改的字段"""
    # 允许修改的字段白名单
    ALLOWED_FIELDS = {"tid","type", "amount", "category", "date", "note"}

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






