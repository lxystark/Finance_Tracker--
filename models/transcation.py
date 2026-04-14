


class Transaction:
    def __init__(self, tid, type, amount, category, date, note=""):
        self.tid = tid          # 交易ID
        self.type = type        # 类型（收入/支出）
        self.amount = amount    # 金额
        self.category = category # 分类
        self.date = date        # 日期
        self.note = note        # 备注
    
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

def delete_transaction(linked_list, tid):
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
def update_transaction(linked_list, tid, **kwargs):
    """根据交易ID修改，kwargs 是要修改的字段"""
    current = linked_list.head
    while current:
        if current.data.tid == tid:
            for key, value in kwargs.items():
                if hasattr(current.data, key):
                    setattr(current.data, key, value)
            print(f"已修改交易 #{tid}")
            return True
        current = current.next
    print(f"未找到交易 #{tid}")
    return False
