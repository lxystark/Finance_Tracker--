import json
from structures.linked_list import DoublyLinkedList
from models.transcation import *

with open('data.data.json', 'r') as file:
    data = json.load(file)

def load_data(filepath="data/data.json"):  # pyright: ignore[reportMissingParameterType]
    linked_list = DoublyLinkedList()
    
    with open(filepath, "r", encoding="utf-8") as f:
        data_list = json.load(f)          # 读出 [字典1, 字典2, ...]  # pyright: ignore[reportAny]
    
    for item in data_list:
        # 关键：把字典变成 Transaction 对象
        transaction = Transaction.from_dict(item)   # ← 类方法在这里发挥作用
        linked_list.append(transaction)
    
    return linked_list
# ========== 程序启动时 ========== transcation逻辑
# 从文件读取，重建链表
linked_list = load_data("data/data.json")

# ========== 添加新交易 ==========
new_t = Transaction(tid=3, type="支出", amount=20, category="交通", date="2026-04-15")
linked_list.prepend(new_t)  # 新交易放头部

# ========== 修改交易 ==========
update_transaction(linked_list, tid=2, amount=5500, note="涨薪了！")

# ========== 删除交易 ==========
delete_transaction(linked_list, tid=1)

# ========== 程序退出时 ==========
# 保存到文件
def save_data(linked_list, filepath="data/data.json"):
    # 关键：把 Transaction 对象变成字典
    transactions = [t.to_dict() for t in linked_list.to_list()]   # ← 实例方法在这里发挥作用
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)