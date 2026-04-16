from typing import Any
import json
import os
from structures.linked_list import DoublyLinkedList
from models.transaction import *

DATA_FILE = "data/data.json"


def show_menu():
    print('''
    1. 添加交易记录Add Transcations
    2.删除交易记录
    3.修改交易记录
    4.查看交易记录（JSON）
    5.查看交易记录（双向链表）
    6.EXIT
    7.更多功能
    ''')

# ========== 主程序 ==========
def main():
    # 程序启动：从文件加载数据
    file = load_data()
    print("=== Finance_Tracker ===")
    
    transactions = file.to_list()
    while True:
        show_menu()
        choice = input("请选择 (num): ").strip()

        if choice == "1":
            print("--- 添加交易记录 ---")
            # tid 查重循环
            while True:
                tid = int(input("交易ID: "))
                if check_tid_exists(file, tid):
                    print(f"错误：交易ID {tid} 已存在，请重新输入")
                else:
                    break
            type_ = input("类型(收入/支出): ")
            amount = float(input("金额: "))
            category = input("分类: ")
            date = input("日期(YYYY-MM-DD): ")
            note = input("备注(可留空): ")
            add_transaction(file, tid, type_, amount, category, date, note)
            save_data(file)
            continue

        elif choice == "2":
            print("--- 删除交易记录 ---")
            # tid 存在性检查
            while True:
                tid_input = input("请输入要删除的交易ID (输入 Q 取消，输入 S 查看所有交易记录): ").strip()
                if tid_input.upper() == "Q":
                    print("已取消删除操作")
                    break
                elif tid_input.upper() == "S":
                    print(file)
                    continue
                try:
                    tid = int(tid_input)
                except ValueError:
                    print("错误：请输入有效的tid")
                    continue
                if not check_tid_exists(file, tid):
                    print(f"错误：交易ID {tid} 不存在，无法执行删除操作")
                    continue
                else:
                                
                # 显示待删除的交易详情
                    transaction = get_transaction_by_tid(file, tid)
                    if transaction:
                        print("\n待删除的交易记录：")
                        print(json.dumps(transaction.to_dict(), ensure_ascii=False, indent=2))
                # 确认删除
                    confirm = input("确认删除？(Y/N): ").strip().upper()
                    if confirm == "Y":
                        delete_transaction(file, tid)
                        save_data(file)
                        print(f"交易ID {tid} 已成功删除")
                    else:
                        print("已取消删除操作")
                        continue


        elif choice == "3":
            pass
        
        elif choice == "4":
            print("=== 查看交易记录 ===")
            transactions = file.to_list()
            print(f'共 {len(transactions)} 条交易记录：')
            for t in transactions:
                print(json.dumps(t.to_dict(), ensure_ascii=False, indent=2))
            

        elif choice == "5":
            print(file)
            
        elif choice == "6":   
            print("再见！数据已自动保存。")
            break
        elif choice == "7":
            pass
        else:
            pass
#这里写保存数据的代码
        
    pass
       
    
# ========== 交易数据读写 ==========
def load_data(filepath=DATA_FILE):  # pyright: ignore[reportMissingParameterType]
    """从 JSON 文件读取交易记录，重建链表"""
    linked_list = DoublyLinkedList()
    
    if not os.path.exists(filepath):
        return linked_list  #处理文件不存在的情况，返回空链表
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        if not content.strip():     
            return linked_list    # 读出 [字典1, 字典2, ...]  # pyright: ignore[reportAny]
    data_list = json.loads(content)

    for item in data_list:
        # 关键：把字典变成 Transaction 对象
        transaction = Transaction.from_dict(item)   # ← 类方法在这里发挥作用
        linked_list.append(transaction)
    
    return linked_list

def save_data(linked_list, filepath=DATA_FILE):
    """保存交易记录到 JSON 文件"""
    # 关键：把 Transaction 对象变成字典
    transactions = [t.to_dict() for t in linked_list.to_list()]   # ← 实例方法在这里发挥作用
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()