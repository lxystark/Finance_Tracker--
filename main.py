from typing import Any
import json
import os
from structures.linked_list import DoublyLinkedList
from structures.hashmap import HashMap
from structures.bst import BST
from structures.stack import Stack
from models.transaction import *
from models.notification import NotificationManager

DATA_FILE = "data/data.json"


def show_menu(unread=0):
    notify_hint = f" ({unread}条未读)" if unread > 0 else ""
    print(f'''
    1. 添加交易记录
    2. 删除交易记录
    3. 修改交易记录
    4. 查看交易记录（JSON）
    5. 查看交易记录（双向链表）
    6. EXIT
    7. 更多功能
    8. 撤销操作
    9. 查看通知{notify_hint}
    ''')

# ========== 主程序 ==========
def main():
    # 程序启动：从文件加载数据
    file = load_data()
    # 构建 tid 索引，查找从 O(n) 提升为 O(1)
    tid_index = build_tid_index(file)
    # 构建 BST 索引，支持 O(log n) 范围查询
    date_index = build_date_index(file)
    amount_index = build_amount_index(file)
    # 撤销栈：记录反向操作
    undo_stack = Stack()
    # 通知管理器：大额/异常提醒
    notifier = NotificationManager()
    notifier.send("info", "欢迎使用 Finance Tracker！数据已加载完成。")
    print("=== Finance_Tracker ===")
    
    transactions = file.to_list()
    while True:
        show_menu(unread=notifier.unread_count())
        choice = input("请选择 (num): ").strip()

        if choice == "1":
            print("--- 添加交易记录 ---")
            # tid 查重循环
            while True:
                tid = int(input("交易ID: "))
                if check_tid_exists(tid, tid_index):
                    print(f"错误：交易ID {tid} 已存在，请重新输入")
                else:
                    break
            type_ = input("类型(收入/支出): ")
            amount = float(input("金额: "))
            category = input("分类: ")
            date = input("日期(YYYY-MM-DD): ")
            note = input("备注(可留空): ")
            add_transaction(file, tid, type_, amount, category, date, note, tid_index)
            save_data(file)
            # 记录撤销操作：撤销添加 = 删除
            undo_stack.push({"action": "add", "tid": tid})
            # 通知检查
            if type_ == "支出":
                notifier.check_large_expense(amount, tid)
            notifier.check_negative_amount(amount, tid)
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
                if not check_tid_exists(tid, tid_index):
                    print(f"错误：交易ID {tid} 不存在，无法执行删除操作")
                    continue
                else:
                    # 显示待删除的交易详情
                    transaction = get_transaction_by_tid(tid, tid_index)
                    if transaction:
                        print("\n待删除的交易记录：")
                        print(json.dumps(transaction.to_dict(), ensure_ascii=False, indent=2))
                    # 确认删除
                    confirm = input("确认删除？(Y/N): ").strip().upper()
                    if confirm == "Y":
                        # 保存删除前的完整数据用于撤销
                        old_data = transaction.to_dict() if transaction else None
                        delete_transaction(file, tid, tid_index)
                        save_data(file)
                        print(f"交易ID {tid} 已成功删除")
                        # 记录撤销操作：撤销删除 = 重新添加
                        if old_data:
                            undo_stack.push({"action": "delete", "data": old_data})
                    else:
                        print("已取消删除操作")
                    break


        elif choice == "3":#根据tid定向修改交易记录的功能，tid也可修改
            print("--- 修改交易记录 ---")
            # tid 存在性检查
            while True:
                tid_input = input("请输入要修改的交易ID (输入 Q 取消，输入 S 查看所有交易记录): ").strip()
                if tid_input.upper() == "Q":
                    print("已取消修改操作")
                    break
                elif tid_input.upper() == "S":
                    print(file)
                    continue
                try:
                    tid = int(tid_input)
                except ValueError:
                    print("错误：请输入有效的tid")
                    continue
                if not check_tid_exists(tid, tid_index):
                    print(f"错误：交易ID {tid} 不存在，无法执行修改操作")
                    continue
                else:
                    transaction = get_transaction_by_tid(tid, tid_index)
                    if transaction:
                        # 保存修改前的完整数据用于撤销
                        old_data = transaction.to_dict()
                        print("\n待修改的交易记录：")
                        print(json.dumps(old_data, ensure_ascii=False, indent=2))
                        # 逐字段询问，用户回车保留原值
                        kwargs = {}
                        current = transaction.to_dict()
                        # 交易ID
                        new_tid_str = input(f"交易ID [当前值: {current['tid']}, 回车跳过]: ").strip()
                        if new_tid_str:
                            try:
                                new_tid = int(new_tid_str)
                                if check_tid_exists(new_tid, tid_index) and new_tid != current['tid']:
                                    print(f"错误：交易ID {new_tid} 已存在，请重新操作")
                                    continue
                                kwargs['tid'] = new_tid
                            except ValueError:
                                print("错误：交易ID 必须为整数，请重新操作")
                                continue
                        # 类型
                        new_type = input(f"类型 [当前值: {current['type']}, 回车跳过]: ").strip()
                        if new_type:
                            kwargs['type'] = new_type
                        # 金额
                        new_amount_str = input(f"金额 [当前值: {current['amount']}, 回车跳过]: ").strip()
                        if new_amount_str:
                            try:
                                kwargs['amount'] = float(new_amount_str)
                            except ValueError:
                                print("错误：金额必须为数字，请重新操作")
                                continue
                        # 分类
                        new_category = input(f"分类 [当前值: {current['category']}, 回车跳过]: ").strip()
                        if new_category:
                            kwargs['category'] = new_category
                        # 日期
                        new_date = input(f"日期 [当前值: {current['date']}, 回车跳过]: ").strip()
                        if new_date:
                            kwargs['date'] = new_date
                        # 备注
                        new_note = input(f"备注 [当前值: {current['note']}, 回车跳过]: ").strip()
                        if new_note:
                            kwargs['note'] = new_note
                        # 执行修改
                        if not kwargs:
                            print("未做任何修改")
                        else:
                            update_transaction(file, tid, tid_index, **kwargs)
                            save_data(file)
                            print(f"已修改交易 #{tid}")
                            # 记录撤销操作：撤销修改 = 恢复原值
                            undo_stack.push({"action": "update", "old_data": old_data})
                            # 通知检查
                            new_amount = kwargs.get('amount', old_data['amount'])
                            new_type = kwargs.get('type', old_data['type'])
                            if new_type == "支出":
                                notifier.check_large_expense(new_amount, kwargs.get('tid', old_data['tid']))
                            notifier.check_negative_amount(new_amount, kwargs.get('tid', old_data['tid']))
                    break
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
            print("--- 更多功能 ---")
            print("1. 按交易ID升序排列（从小到大）")
            print("2. 按交易日期降序排列（从新到旧）")
            print("3. 按日期范围查询交易记录")
            print("4. 按金额范围筛选交易记录")
            print("0. 返回主菜单")
            sort_choice = input("请选择功能: ").strip()
            if sort_choice == "1":
                sort_transactions(file, mode="tid_asc")
                save_data(file)
            elif sort_choice == "2":
                sort_transactions(file, mode="date_desc")
                save_data(file)
            elif sort_choice == "3":
                print("--- 按日期范围查询 ---")
                start_date = input("起始日期 (YYYY-MM-DD): ").strip()
                end_date = input("结束日期 (YYYY-MM-DD): ").strip()
                try:
                    results = query_by_date_range(date_index, start_date, end_date)
                    if results:
                        print(f"\n共找到 {len(results)} 条记录：")
                        for t in results:
                            print(json.dumps(t.to_dict(), ensure_ascii=False, indent=2))
                    else:
                        print("该日期范围内无交易记录")
                except ValueError as e:
                    print(f"日期格式错误: {e}")
            elif sort_choice == "4":
                print("--- 按金额范围筛选 ---")
                try:
                    min_amount = float(input("最小金额: "))
                    max_amount = float(input("最大金额: "))
                    results = query_by_amount_range(amount_index, min_amount, max_amount)
                    if results:
                        print(f"\n共找到 {len(results)} 条记录：")
                        for t in results:
                            print(json.dumps(t.to_dict(), ensure_ascii=False, indent=2))
                    else:
                        print("该金额范围内无交易记录")
                except ValueError:
                    print("错误：金额必须为数字")
            elif sort_choice == "0":
                pass
            else:
                print("无效选择，请重新输入")

        elif choice == "8":
            print("--- 撤销操作 ---")
            if undo_stack.is_empty():
                print("没有可撤销的操作")
            else:
                op = undo_stack.pop()
                if op["action"] == "add":
                    # 撤销添加 = 删除该交易
                    tid = op["tid"]
                    if check_tid_exists(tid, tid_index):
                        delete_transaction(file, tid, tid_index)
                        save_data(file)
                        print(f"已撤销：删除了交易 #{tid}")
                    else:
                        print(f"无法撤销：交易 #{tid} 已不存在")
                elif op["action"] == "delete":
                    # 撤销删除 = 重新添加
                    data = op["data"]
                    add_transaction(file, data["tid"], data["type"],
                                    data["amount"], data["category"],
                                    data["date"], data.get("note", ""), tid_index)
                    save_data(file)
                    print(f"已撤销：恢复了交易 #{data['tid']}")
                elif op["action"] == "update":
                    # 撤销修改 = 恢复原值
                    old_data = op["old_data"]
                    old_tid = old_data["tid"]
                    if check_tid_exists(old_tid, tid_index):
                        # 逐字段恢复
                        for key, value in old_data.items():
                            if key != "tid":  # tid 单独处理
                                t = get_transaction_by_tid(old_tid, tid_index)
                                if t and hasattr(t, key):
                                    setattr(t, key, value)
                        save_data(file)
                        print(f"已撤销：恢复了交易 #{old_tid} 的原始值")
                    else:
                        # tid 被修改过，需要通过当前值找到再改回
                        print(f"无法自动撤销交易 #{old_tid} 的修改（tid 可能已被更改）")

        elif choice == "9":
            print("--- 通知中心 ---")
            if notifier.has_unread():
                print(f"有 {notifier.unread_count()} 条未读通知：")
                for n in notifier.read_all():
                    print(f"  {n}")
            else:
                print("暂无未读通知")
            # 显示历史通知
            history = notifier.history()
            if history:
                print(f"\n已读通知 ({len(history)} 条)：")
                for n in history[-5:]:  # 只显示最近5条
                    print(f"  {n}")

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