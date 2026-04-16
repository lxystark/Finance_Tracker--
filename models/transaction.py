




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
        """对象 → 字典（便于 JSON 存储）
          to_dict()            from_dict()
  实例方法              类方法
  ────────            ──────────
  对象 → 字典          字典 → 对象
  需要 self            不需要 self，用 cls
  先有对象才能调         不需要先有对象
  保存时用              读取时用
            """
        return {
            "tid": self.tid,
            "type": self.type,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "note": self.note
        }
    @classmethod
    def from_dict(cls, data):
        """字典 → 对象（从 JSON 恢复时用）"""
        return cls(
            tid=data["tid"],
            type=data["type"],
            amount=data["amount"],
            category=data["category"],
            date=data["date"],
            note=data.get("note", "")  # 用 get 防止旧数据没有这个字段
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


def update_transaction(linked_list: DoublyLinkedList, tid, **kwargs):
    """根据交易ID修改，kwargs 是要修改的字段"""
     # 不允许修改 tid
    if "tid" in kwargs:
        print("错误：不能修改交易ID")
        return False
    # 允许修改的字段白名单
    ALLOWED_FIELDS = {"type", "amount", "category", "date", "note"}    
    
    current = linked_list.head

    while current:
        if current.data.tid == tid:
            for key, value in kwargs.items():
                if key not in ALLOWED_FIELDS:
                    print(f"key:'{key}' is not allowed to update")
                    continue
                
                if hasattr(current.data, key):
                    setattr(current.data, key, value)
            print(f"已修改交易 #{tid}")
            return True
        current = current.next
    print(f"未找到交易 #{tid}")
    return False
