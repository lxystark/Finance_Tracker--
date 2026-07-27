'''
    @Author: Xinyuan Lin
    It's a main function for the project. Finance Tracker.
    We combined all the data structures and models in this main program.
    We finished end-to-end testing. on this main program.

'''
from typing import Any
import json
import os
from structures.linked_list import DoublyLinkedList
from structures.hashmap import HashMap
from structures.bst import BST
from structures.stack import Stack
from models.transaction import *
from models.notification import NotificationManager
from models.category import CategoryManager
from models.account import Account, SavingsAccount, CreditAccount
from exceptions import InsufficientFundsError, InvalidAmountError, AccountNotFoundError

DATA_FILE = "data/data.json"
CATEGORY_FILE = "data/categories.json"
ACCOUNT_FILE = "data/accounts.json"


def show_menu(unread=0):
    notify_hint = f" ({unread}条未读)" if unread > 0 else ""
    print(f'''
    1. 添加交易记录|| Add Transaction
    2. 删除交易记录|| Delete Transaction
    3. 修改交易记录|| Update Transaction
    4. 查看交易记录（JSON） || Display Transaction in JSON
    5. 查看交易记录（双向链表）|| Display Transaction in Doubly Linked List
    6. EXIT
    7. 更多功能 || More Function
    8. 撤销操作 || Undo Operation
    9. 查看通知{notify_hint} || Notification
    10. 分类管理 || Category Management
    11. 账户管理 || Account management
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
    # 分类管理器：Tree + Set
    category_mgr = CategoryManager()
    load_categories(category_mgr)
    # 账户管理：HashMap 存储 account_id -> Account
    accounts = load_accounts()
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
            # 展示可选分类列表
            print(f"可选分类: {category_mgr.get_all_categories()}")
            category = input("分类(输入已有分类名或自定义新分类): ").strip()
            # 如果分类不存在，自动添加到树中
            if category and not category_mgr.category_exists(category):
                # 根据交易类型确定父分类
                parent = "支出" if type_ == "支出" else "收入"
                if category_mgr.add_category(parent, category):
                    print(f"已自动添加新分类 '{category}' 到 '{parent}' 下")
                    save_categories(category_mgr)
            date = input("日期(YYYY-MM-DD): ")
            note = input("备注(可留空): ")
            # 关联账户（可选）
            account_id = None
            if len(accounts) > 0:
                print(f"已有账户: {list(accounts.keys())}")
                aid_input = input("关联账户ID (回车跳过): ").strip()
                if aid_input and aid_input in accounts:
                    account_id = aid_input
                    # 自动更新账户余额
                    acct = accounts[account_id]
                    try:
                        if type_ == "收入":
                            acct.deposit(amount)
                        elif type_ == "支出":
                            acct.withdraw(amount)
                        save_accounts(accounts)
                    except (InsufficientFundsError, InvalidAmountError) as e:
                        print(f"账户操作失败: {e}")
                        continue
                elif aid_input:
                    print(f"账户 {aid_input} 不存在，交易将不关联账户")
            add_transaction(file, tid, type_, amount, category, date, note, tid_index, account_id)
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
                # 先 peek 展示待撤销操作详情，让用户确认
                op = undo_stack.peek()
                print(f"待撤销的操作类型: {op['action']}")
                print("-" * 40)
                if op["action"] == "add":
                    tid = op["tid"]
                    tx = get_transaction_by_tid(tid, tid_index)
                    print(f"操作: 添加了交易 #{tid}")
                    if tx:
                        print(f"详情: #{tx.tid} | {tx.type} | {tx.amount}元 | 分类:{tx.category} | {tx.date}")
                    print("撤销效果: 将删除该交易记录")
                elif op["action"] == "delete":
                    data = op["data"]
                    print(f"操作: 删除了交易 #{data['tid']}")
                    print(f"详情: #{data['tid']} | {data['type']} | {data['amount']}元 | 分类:{data['category']} | {data['date']} | {data.get('note', '')}")
                    print("撤销效果: 将恢复该交易记录")
                elif op["action"] == "update":
                    old_data = op["old_data"]
                    print(f"操作: 修改了交易 #{old_data['tid']}")
                    print(f"原始值: #{old_data['tid']} | {old_data['type']} | {old_data['amount']}元 | 分类:{old_data['category']} | {old_data['date']} | {old_data.get('note', '')}")
                    print("撤销效果: 将恢复为上述原始值")
                elif op["action"] == "delete_category":
                    snapshot = op["snapshot"]
                    cats = snapshot.get("categories", [])
                    cat_names = [name for name, _ in cats]
                    print(f"操作: 删除了分类（共 {len(cats)} 个）")
                    print(f"被删分类: {cat_names}")
                    print("撤销效果: 将恢复上述分类到分类树中")
                elif op["action"] == "delete_account":
                    print(f"操作: 创建了账户 {op['account_id']}")
                    print("撤销效果: 将删除该账户")
                elif op["action"] == "restore_account":
                    print(f"操作: 删除了账户 {op['account_data']['account_id']}")
                    print("撤销效果: 将恢复该账户")
                elif op["action"] == "account_deposit":
                    print(f"操作: 向账户 {op['account_id']} 存入 {op['amount']:.2f}")
                    print(f"撤销效果: 将余额恢复为 {op['old_balance']:.2f}")
                elif op["action"] == "account_withdraw":
                    print(f"操作: 从账户 {op['account_id']} 取出 {op['amount']:.2f}")
                    print(f"撤销效果: 将余额恢复为 {op['old_balance']:.2f}")
                print("-" * 40)
                confirm = input("确认执行撤销？(Y/N): ").strip().upper()
                if confirm != "Y":
                    print("已取消撤销")
                    continue
                # 确认后 pop 执行
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
                                    data["date"], data.get("note", ""), tid_index,
                                    data.get("account_id"))
                    # 恢复账户余额
                    if data.get("account_id") and data["account_id"] in accounts:
                        acct = accounts[data["account_id"]]
                        try:
                            if data["type"] == "收入":
                                acct.deposit(data["amount"])
                            elif data["type"] == "支出":
                                acct.withdraw(data["amount"])
                            save_accounts(accounts)
                        except (InsufficientFundsError, InvalidAmountError):
                            pass
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
                elif op["action"] == "delete_category":
                    # 撤销分类删除 = 恢复分类树
                    snapshot = op["snapshot"]
                    category_mgr.restore_category(snapshot)
                    save_categories(category_mgr)
                    print(f"已撤销：恢复了分类（共 {len(snapshot.get('categories', []))} 个）")
                elif op["action"] == "delete_account":
                    # 撤销创建账户 = 删除该账户
                    aid = op["account_id"]
                    if aid in accounts:
                        del accounts[aid]
                        save_accounts(accounts)
                        print(f"已撤销：删除了账户 {aid}")
                    else:
                        print(f"无法撤销：账户 {aid} 已不存在")
                elif op["action"] == "restore_account":
                    # 撤销删除账户 = 恢复该账户
                    acct_data = op["account_data"]
                    acct = Account.from_dict(acct_data)
                    accounts[acct_data["account_id"]] = acct
                    save_accounts(accounts)
                    print(f"已撤销：恢复了账户 {acct_data['account_id']}")
                elif op["action"] == "account_deposit":
                    # 撤销存款 = 恢复余额
                    aid = op["account_id"]
                    if aid in accounts:
                        accounts[aid]._balance = op["old_balance"]
                        save_accounts(accounts)
                        print(f"已撤销：恢复了账户 {aid} 存款前余额 {op['old_balance']:.2f}")
                    else:
                        print(f"无法撤销：账户 {aid} 已不存在")
                elif op["action"] == "account_withdraw":
                    # 撤销取款 = 恢复余额
                    aid = op["account_id"]
                    if aid in accounts:
                        accounts[aid]._balance = op["old_balance"]
                        save_accounts(accounts)
                        print(f"已撤销：恢复了账户 {aid} 取款前余额 {op['old_balance']:.2f}")
                    else:
                        print(f"无法撤销：账户 {aid} 已不存在")

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

        elif choice == "10":
            while True:
                print("--- 分类管理 ---")
                print("1. 查看分类树")
                print("2. 添加分类")
                print("3. 删除分类")
                print("4. 分类统计")
                print("0. 返回主菜单")
                cat_choice = input("请选择功能: ").strip()
                if cat_choice == "1":
                    print("=== 分类树 ===")
                    category_mgr.display_tree()
                    continue
                elif cat_choice == "2":
                    print("--- 添加分类 ---")
                    print(f"当前已有分类: {category_mgr.get_all_categories()}")
                    parent_name = input("请输入父分类名称: ").strip()
                    if not category_mgr.category_exists(parent_name):
                        print(f"错误：父分类 '{parent_name}' 不存在")
                        continue
                    else:
                        new_cat = input("请输入新分类名称: ").strip()
                        if category_mgr.add_category(parent_name, new_cat):
                            print(f"成功：分类 '{new_cat}' 已添加到 '{parent_name}' 下")
                            continue
                        else:
                            print(f"错误：分类 '{new_cat}' 已存在，无法重复添加")
                            continue
                elif cat_choice == "3":
                    print("--- 删除分类 ---")
                    category_mgr.display_tree()
                    del_cat = input("请输入要删除的分类名称: ").strip()
                    if del_cat == "全部分类":
                        print("错误：不允许删除根分类")
                        continue
                    elif not category_mgr.category_exists(del_cat):
                        print(f"错误：分类 '{del_cat}' 不存在")
                        continue
                    else:
                        # 1. 展示待删除的分类及其所有子分类
                        all_descendants = category_mgr.get_descendant_names(del_cat)
                        affected_cats = [del_cat] + all_descendants
                        print(f"\n{'='*50}")
                        print(f"待删除分类: {del_cat}")
                        if all_descendants:
                            print(f"包含子分类: {all_descendants}")
                        print(f"受影响分类共 {len(affected_cats)} 个: {affected_cats}")
                        # 2. 展示所有关联交易记录详情
                        related_txs = []
                        current_node = file.head
                        while current_node:
                            if current_node.data.category in affected_cats:
                                related_txs.append(current_node.data)
                            current_node = current_node.next
                        if related_txs:
                            print(f"\n该分类下共有 {len(related_txs)} 条关联交易记录：")
                            print("-" * 50)
                            for tx in related_txs:
                                print(f"  #{tx.tid} | {tx.type} | {tx.amount}元 | 分类:{tx.category} | {tx.date} | {tx.note}")
                        else:
                            print("\n该分类下无关联交易记录")
                        # 3. 二次确认
                        print(f"{'='*50}")
                        confirm = input(f"⚠ 确认删除分类 '{del_cat}' 及其所有子分类？此操作可通过菜单8撤销。(Y/N): ").strip().upper()
                        if confirm == "Y":
                            snapshot = category_mgr.remove_category(del_cat)
                            if snapshot:
                                # 压入撤销栈
                                undo_stack.push({"action": "delete_category", "snapshot": snapshot})
                                save_categories(category_mgr)
                                print(f"成功：分类 '{del_cat}' 及其子分类已删除（可通过菜单8撤销）")
                            else:
                                print(f"错误：删除失败")
                            continue
                        else:
                            print("已取消删除")
                            continue
                elif cat_choice == "4":
                    print("--- 分类统计 ---")
                    stats = category_mgr.get_category_statistics(file)
                    if not stats:
                        print("暂无交易记录")
                        continue
                    else:
                        print(f"{'分类':<10}{'收入':>10}{'支出':>10}{'净额':>10}{'笔数':>6}")
                        print("-" * 50)
                        for cat, data in stats.items():
                            print(f"{cat:<10}{data['收入']:>10.2f}{data['支出']:>10.2f}{data['净额']:>10.2f}{data['笔数']:>6}")
                elif cat_choice == "0":
                    break
                else:
                    print("无效选择，请重新输入")
                    continue
        
        elif choice == "11":
            while True:
                print("--- 账户管理 ---")
                print("1. 查看所有账户")
                print("2. 创建储蓄账户")
                print("3. 创建信用账户")
                print("4. 存款")
                print("5. 取款")
                print("6. 查看账户余额")
                print("7. 计算利息")
                print("8. 删除账户")
                print("9. 查看账户关联交易")
                print("0. 返回主菜单")
                acct_choice = input("请选择功能: ").strip()
                
                if acct_choice == "1":
                    # 查看所有账户
                    if not accounts:
                        print("暂无账户")
                    else:
                        print(f"共 {len(accounts)} 个账户：")
                        print("-" * 60)
                        for aid, acct in accounts.items():
                            print(f"  {acct}")
                    continue
                
                elif acct_choice == "2":
                    # 创建储蓄账户
                    aid = input("账户ID: ").strip()
                    if aid in accounts:
                        print(f"错误：账户ID {aid} 已存在")
                        continue
                    owner = input("持有人姓名: ").strip()
                    balance_str = input("初始余额 (默认0): ").strip()
                    balance = float(balance_str) if balance_str else 0.0
                    rate_str = input("年利率 (默认0.03): ").strip()
                    interest_rate = float(rate_str) if rate_str else 0.03
                    acct = SavingsAccount(aid, owner, balance, interest_rate)
                    accounts[aid] = acct
                    save_accounts(accounts)
                    print(f"成功：储蓄账户 {aid} 已创建")
                    # 撤销：删除该账户
                    undo_stack.push({"action": "delete_account", "account_id": aid})
                    continue
                
                elif acct_choice == "3":
                    # 创建信用账户
                    aid = input("账户ID: ").strip()
                    if aid in accounts:
                        print(f"错误：账户ID {aid} 已存在")
                        continue
                    owner = input("持有人姓名: ").strip()
                    balance_str = input("初始余额 (默认0): ").strip()
                    balance = float(balance_str) if balance_str else 0.0
                    limit_str = input("信用额度 (默认5000): ").strip()
                    credit_limit = float(limit_str) if limit_str else 5000.0
                    acct = CreditAccount(aid, owner, balance, credit_limit)
                    accounts[aid] = acct
                    save_accounts(accounts)
                    print(f"成功：信用账户 {aid} 已创建")
                    # 撤销：删除该账户
                    undo_stack.push({"action": "delete_account", "account_id": aid})
                    continue
                
                elif acct_choice == "4":
                    # 存款
                    aid = input("账户ID: ").strip()
                    if aid not in accounts:
                        print(f"错误：账户 {aid} 不存在")
                        continue
                    amount_str = input("存入金额: ").strip()
                    try:
                        amount = float(amount_str)
                        acct = accounts[aid]
                        old_balance = acct.get_balance()
                        acct.deposit(amount)
                        save_accounts(accounts)
                        print(f"成功：已存入 {amount:.2f}，当前余额 {acct.get_balance():.2f}")
                        # 撤销：恢复余额
                        undo_stack.push({"action": "account_deposit", "account_id": aid, "old_balance": old_balance, "amount": amount})
                    except InvalidAmountError as e:
                        print(f"错误：{e}")
                    continue
                
                elif acct_choice == "5":
                    # 取款
                    aid = input("账户ID: ").strip()
                    if aid not in accounts:
                        print(f"错误：账户 {aid} 不存在")
                        continue
                    amount_str = input("取出金额: ").strip()
                    try:
                        amount = float(amount_str)
                        acct = accounts[aid]
                        old_balance = acct.get_balance()
                        acct.withdraw(amount)
                        save_accounts(accounts)
                        print(f"成功：已取出 {amount:.2f}，当前余额 {acct.get_balance():.2f}")
                        # 撤销：恢复余额
                        undo_stack.push({"action": "account_withdraw", "account_id": aid, "old_balance": old_balance, "amount": amount})
                    except (InsufficientFundsError, InvalidAmountError) as e:
                        print(f"错误：{e}")
                    continue
                
                elif acct_choice == "6":
                    # 查看账户余额
                    aid = input("账户ID: ").strip()
                    if aid not in accounts:
                        print(f"错误：账户 {aid} 不存在")
                        continue
                    acct = accounts[aid]
                    print(f"账户 {aid} 余额: {acct.get_balance():.2f}")
                    continue
                
                elif acct_choice == "7":
                    # 计算利息
                    aid = input("账户ID: ").strip()
                    if aid not in accounts:
                        print(f"错误：账户 {aid} 不存在")
                        continue
                    acct = accounts[aid]
                    # 显示账户默认利率信息
                    if isinstance(acct, SavingsAccount):
                        print(f"账户默认年利率: {acct.interest_rate * 100:.1f}%")
                    else:
                        print(f"信用账户欠款利率: 20.0%")
                    rate_input = input("输入自定义年利率(%%，直接回车使用默认利率): ").strip()
                    if rate_input:
                        try:
                            custom_rate = float(rate_input) / 100
                            if custom_rate < 0:
                                print("错误：利率不能为负数")
                                continue
                            if isinstance(acct, SavingsAccount):
                                interest = acct.get_balance() * custom_rate
                                print(f"账户 {aid} (储蓄) 按利率 {custom_rate*100:.1f}% 计算利息: {interest:.2f}")
                            else:
                                if acct.get_balance() < 0:
                                    interest = abs(acct.get_balance()) * custom_rate
                                    print(f"账户 {aid} (信用) 按利率 {custom_rate*100:.1f}% 计算欠款利息: {interest:.2f}")
                                else:
                                    print(f"账户 {aid} (信用) 当前无欠款，利息为 0.00")
                        except ValueError:
                            print("错误：请输入有效的数字")
                    else:
                        interest = acct.calculate_interest()
                        print(f"账户 {aid} ({acct.get_account_type()}) 计算利息: {interest:.2f}")
                        if isinstance(acct, SavingsAccount):
                            print(f"  （当前余额 {acct.get_balance():.2f}，利率 {acct.interest_rate*100:.1f}%）")
                        elif acct.get_balance() < 0:
                            print(f"  （当前欠款 {abs(acct.get_balance()):.2f}，利率20%）")
                    continue
                
                elif acct_choice == "8":
                    # 删除账户
                    aid = input("账户ID: ").strip()
                    if aid not in accounts:
                        print(f"错误：账户 {aid} 不存在")
                        continue
                    acct = accounts[aid]
                    print(f"\n待删除账户：{acct}")
                    # 检查有关联交易
                    related_count = 0
                    current_node = file.head
                    while current_node:
                        if current_node.data.account_id == aid:
                            related_count += 1
                        current_node = current_node.next
                    if related_count > 0:
                        print(f"⚠ 该账户有 {related_count} 条关联交易记录，删除后这些交易将不再关联账户")
                    confirm = input("确认删除？(Y/N): ").strip().upper()
                    if confirm == "Y":
                        old_acct_data = acct.to_dict()
                        del accounts[aid]
                        save_accounts(accounts)
                        # 将关联交易的 account_id 置为 None
                        current_node = file.head
                        while current_node:
                            if current_node.data.account_id == aid:
                                current_node.data.account_id = None
                            current_node = current_node.next
                        save_data(file)
                        # 撤销：恢复账户
                        undo_stack.push({"action": "restore_account", "account_data": old_acct_data})
                        print(f"成功：账户 {aid} 已删除")
                    else:
                        print("已取消删除")
                    continue
                
                elif acct_choice == "9":
                    # 查看账户关联交易
                    aid = input("账户ID: ").strip()
                    if aid not in accounts:
                        print(f"错误：账户 {aid} 不存在")
                        continue
                    related_txs = []
                    current_node = file.head
                    while current_node:
                        if current_node.data.account_id == aid:
                            related_txs.append(current_node.data)
                        current_node = current_node.next
                    if related_txs:
                        print(f"\n账户 {aid} 关联交易共 {len(related_txs)} 条：")
                        print("-" * 50)
                        for tx in related_txs:
                            print(f"  #{tx.tid} | {tx.type} | {tx.amount}元 | 分类:{tx.category} | {tx.date} | {tx.note}")
                    else:
                        print(f"账户 {aid} 暂无关联交易记录")
                    continue
                
                elif acct_choice == "0":
                    break
                else:
                    print("无效选择，请重新输入")
                    continue


    
       
    
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

# ========== 分类数据读写 ==========
def load_categories(category_mgr, filepath=CATEGORY_FILE):
    """从 JSON 文件加载分类树，文件不存在则使用默认分类"""
    if not os.path.exists(filepath):
        category_mgr.init_default_categories()
        save_categories(category_mgr, filepath)
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if not content.strip():
        category_mgr.init_default_categories()
        save_categories(category_mgr, filepath)
        return
    data = json.loads(content)
    category_mgr.from_dict(data)

def save_categories(category_mgr, filepath=CATEGORY_FILE):
    """保存分类树到 JSON 文件"""
    data = category_mgr.to_dict()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ========== 账户数据读写 ==========
def load_accounts(filepath=ACCOUNT_FILE) -> dict:
    """从 JSON 文件加载账户数据，返回 {account_id: Account} 字典"""
    accounts = {}
    if not os.path.exists(filepath):
        return accounts
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if not content.strip():
        return accounts
    data_list = json.loads(content)
    for item in data_list:
        acct = Account.from_dict(item)
        accounts[acct.account_id] = acct
    return accounts

def save_accounts(accounts: dict, filepath=ACCOUNT_FILE):
    """保存账户数据到 JSON 文件"""
    data = [acct.to_dict() for acct in accounts.values()]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()