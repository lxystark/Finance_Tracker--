from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import pickle
import uuid
from abc import ABC, abstractmethod
from structures.linked_list import DoublyLinkedList
from transcation import Transaction, Income, Expense



class Stack:
    """自定义栈（文档5.2要求）"""
    def __init__(self):
        self._items = []
    
    def push(self, item: Any) -> None:
        self._items.append(item)
    
    def pop(self) -> Any:
        if not self.is_empty():
            return self._items.pop()
        return None
    
    def peek(self) -> Any:
        if not self.is_empty():
            return self._items[-1]
        return None
    
    def is_empty(self) -> bool:
        return len(self._items) == 0
    
    def size(self) -> int:
        return len(self._items)

class Queue:
    """自定义队列（文档5.2要求）"""
    def __init__(self):
        self._items = []
    
    def enqueue(self, item: Any) -> None:
        self._items.append(item)
    
    def dequeue(self) -> Any:
        if not self.is_empty():
            return self._items.pop(0)
        return None
    
    def is_empty(self) -> bool:
        return len(self._items) == 0
    
    def size(self) -> int:
        return len(self._items)

# 主Account类
class Account:
    """账户类 - 个人理财系统的核心类"""
    
    def __init__(self, account_id: str, name: str, initial_balance: float = 0.0, 
                 account_type: str = "checking"):
        """
        初始化账户
        
        参数:
            account_id: 账户唯一标识
            name: 账户名称
            initial_balance: 初始余额
            account_type: 账户类型（checking: 活期, savings: 储蓄, credit: 信用卡, investment: 投资）
        """
        # 封装的基本属性
        self._account_id = account_id
        self._name = name
        self._balance = initial_balance
        self._account_type = account_type
        self._created_date = datetime.now()
        
        # 自定义数据结构（文档5.2要求）
        self._transactions = DoublyLinkedList()  # 双链表：按时间顺序存储交易
        self._undo_stack = Stack()               # 栈：用于撤销操作
        self._redo_queue = Queue()               # 队列：用于重做操作
        
        # 用于快速查找的数据结构（文档5.2要求）
        self._transaction_map = {}               # 哈希表：transaction_id -> 交易对象
        self._transactions_by_date = []          # 列表：按日期排序的交易
        
    # 属性访问器（封装）
    @property
    def account_id(self) -> str:
        return self._account_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, new_name: str) -> None:
        """修改账户名称"""
        if not new_name or not new_name.strip():
            raise ValueError("账户名称不能为空")
        self._name = new_name.strip()
    
    @property
    def balance(self) -> float:
        return self._balance
    
    @property
    def account_type(self) -> str:
        return self._account_type
    
    @property
    def created_date(self) -> datetime:
        return self._created_date
    
    def deposit(self, amount: float, description: str = "", category: str = "") -> str:
        """
        存款操作
        
        参数:
            amount: 存款金额
            description: 描述
            category: 分类
            
        返回:
            交易ID
        """
        if amount <= 0:
            raise ValueError("存款金额必须大于0")
        
        # 创建收入交易
        transaction = Income(amount, datetime.now(), description, category)
        
        # 更新余额
        self._balance += amount
        
        # 记录交易
        self._add_transaction(transaction)
        
        # 保存到撤销栈
        self._save_to_undo_stack('deposit', {
            'transaction_id': transaction.transaction_id,
            'amount': amount
        })
        
        return transaction.transaction_id
    
    def withdraw(self, amount: float, description: str = "", category: str = "") -> str:
        """
        取款/支出操作
        
        参数:
            amount: 取款金额
            description: 描述
            category: 分类
            
        返回:
            交易ID
            
        异常:
            InsufficientBalanceError: 余额不足
        """
        if amount <= 0:
            raise ValueError("取款金额必须大于0")
        
        if self._balance < amount:
            raise InsufficientBalanceError(self._balance, amount)
        
        # 创建支出交易
        transaction = Expense(amount, datetime.now(), description, category)
        
        # 更新余额
        self._balance -= amount
        
        # 记录交易
        self._add_transaction(transaction)
        
        # 保存到撤销栈
        self._save_to_undo_stack('withdraw', {
            'transaction_id': transaction.transaction_id,
            'amount': amount
        })
        
        return transaction.transaction_id
    
    def transfer(self, target_account: 'Account', amount: float, 
                 description: str = "") -> tuple[str, str]:
        """
        转账到另一个账户
        
        参数:
            target_account: 目标账户
            amount: 转账金额
            description: 描述
            
        返回:
            (转出交易ID, 转入交易ID)
        """
        if amount <= 0:
            raise ValueError("转账金额必须大于0")
        
        if self._balance < amount:
            raise InsufficientBalanceError(self._balance, amount)
        
        # 从本账户支出
        from_transaction_id = self.withdraw(
            amount, 
            f"转账到 {target_account.name}: {description}", 
            "transfer_out"
        )
        
        # 向目标账户存款
        to_transaction_id = target_account.deposit(
            amount, 
            f"从 {self.name} 转入: {description}", 
            "transfer_in"
        )
        
        return from_transaction_id, to_transaction_id
    
    def _add_transaction(self, transaction: Transaction) -> None:
        """添加交易到数据结构中"""
        # 添加到双链表
        self._transactions.append(transaction)
        
        # 添加到哈希表
        self._transaction_map[transaction.transaction_id] = transaction
        
        # 添加到按日期排序的列表
        self._transactions_by_date.append(transaction)
        self._transactions_by_date.sort(key=lambda x: x.date)
    
    def _save_to_undo_stack(self, action: str, data: Dict[str, Any]) -> None:
        """保存操作到撤销栈"""
        self._undo_stack.push({
            'action': action,
            'data': data,
            'timestamp': datetime.now(),
            'balance_before': self._balance - (
                data['amount'] if action == 'deposit' else -data['amount']
            )
        })
        # 执行新操作时清空重做队列
        while not self._redo_queue.is_empty():
            self._redo_queue.dequeue()
    
    def undo(self) -> bool:
        """撤销上一次操作"""
        if self._undo_stack.is_empty():
            return False
        
        last_action = self._undo_stack.pop()
        
        if last_action['action'] == 'deposit':
            # 撤销存款 = 支出相同的金额
            transaction_id = last_action['data']['transaction_id']
            if transaction_id in self._transaction_map:
                transaction = self._transaction_map[transaction_id]
                self._balance -= transaction.amount
                self._transactions.remove(transaction_id)
                del self._transaction_map[transaction_id]
                self._transactions_by_date = [
                    t for t in self._transactions_by_date 
                    if t.transaction_id != transaction_id
                ]
        
        elif last_action['action'] == 'withdraw':
            # 撤销取款 = 存款相同的金额
            transaction_id = last_action['data']['transaction_id']
            if transaction_id in self._transaction_map:
                transaction = self._transaction_map[transaction_id]
                self._balance += transaction.amount
                self._transactions.remove(transaction_id)
                del self._transaction_map[transaction_id]
                self._transactions_by_date = [
                    t for t in self._transactions_by_date 
                    if t.transaction_id != transaction_id
                ]
        
        # 保存到重做队列
        self._redo_queue.enqueue(last_action)
        return True
    
    def redo(self) -> bool:
        """重做上一次撤销的操作"""
        if self._redo_queue.is_empty():
            return False
        
        action_to_redo = self._redo_queue.dequeue()
        
        if action_to_redo['action'] == 'deposit':
            # 重做存款
            self.deposit(
                action_to_redo['data']['amount'],
                f"重做: 存款 {action_to_redo['data']['amount']}",
                "redo"
            )
        elif action_to_redo['action'] == 'withdraw':
            # 重做取款
            self.withdraw(
                action_to_redo['data']['amount'],
                f"重做: 取款 {action_to_redo['data']['amount']}",
                "redo"
            )
        
        return True
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """通过ID查找交易（使用哈希表实现快速查找）"""
        return self._transaction_map.get(transaction_id)
    
    def get_transactions(self, start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None) -> List[Transaction]:
        """获取交易记录，可指定时间范围"""
        if not start_date and not end_date:
            return self._transactions.to_list()
        
        result = []
        for transaction in self._transactions_by_date:
            if start_date and transaction.date < start_date:
                continue
            if end_date and transaction.date > end_date:
                break
            result.append(transaction)
        
        return result
    
    def get_transactions_by_type(self, transaction_type: str) -> List[Transaction]:
        """按交易类型筛选交易"""
        if transaction_type not in ['income', 'expense']:
            raise ValueError("交易类型必须是 'income' 或 'expense'")
        
        return [
            t for t in self._transactions.to_list() 
            if t.get_transaction_type() == transaction_type
        ]
    
    def get_transactions_by_category(self, category: str) -> List[Transaction]:
        """按分类筛选交易"""
        return [
            t for t in self._transactions.to_list() 
            if t.category and t.category.lower() == category.lower()
        ]
    
    def get_balance_history(self) -> List[Dict[str, Any]]:
        """获取余额历史记录"""
        balance = 0.0
        history = []
        
        for transaction in self._transactions.to_list():
            if transaction.get_transaction_type() == 'income':
                balance += transaction.amount
            else:
                balance -= transaction.amount
            
            history.append({
                'date': transaction.date,
                'transaction': transaction,
                'balance': balance
            })
        
        return history
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于序列化（文档3要求）"""
        return {
            'account_id': self._account_id,
            'name': self._name,
            'balance': self._balance,
            'account_type': self._account_type,
            'created_date': self._created_date.isoformat(),
            'transactions': [t.to_dict() for t in self._transactions.to_list()]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Account':
        """从字典创建Account对象，用于反序列化（文档3要求）"""
        from datetime import datetime
        account = cls(
            data['account_id'],
            data['name'],
            data['balance'],
            data.get('account_type', 'checking')
        )
        account._created_date = datetime.fromisoformat(data['created_date'])
        
        # 恢复交易记录
        for t_data in data.get('transactions', []):
            transaction = Transaction.from_dict(t_data)
            account._add_transaction(transaction)
        
        return account
    
    def __str__(self) -> str:
        return f"账户: {self._name} (ID: {self._account_id[:8]}...) 余额: {self._balance:.2f}"
    
    def __repr__(self) -> str:
        return f"Account(name='{self._name}', balance={self._balance:.2f}, type='{self._account_type}')"


# 使用示例
if __name__ == "__main__":
    # 创建账户
    my_account = Account("ACC001", "我的储蓄账户", 1000.0, "savings")
    
    # 存款
    print("初始余额:", my_account.balance)
    
    deposit_id = my_account.deposit(500.0, "工资", "income")
    print("存款后余额:", my_account.balance)
    
    # 取款
    try:
        withdraw_id = my_account.withdraw(200.0, "购物", "shopping")
        print("取款后余额:", my_account.balance)
    except InsufficientBalanceError as e:
        print("错误:", e)
    
    # 获取交易记录
    transactions = my_account.get_transactions()
    print(f"共有 {len(transactions)} 笔交易")
    
    # 按类型筛选
    incomes = my_account.get_transactions_by_type("income")
    print(f"收入交易: {len(incomes)} 笔")
    
    # 测试撤销/重做
    print("\n测试撤销/重做:")
    print("当前余额:", my_account.balance)
    my_account.undo()  # 撤销取款
    print("撤销取款后余额:", my_account.balance)
    my_account.redo()  # 重做取款
    print("重做取款后余额:", my_account.balance)
    
    # 序列化/反序列化测试
    print("\n序列化测试:")
    account_dict = my_account.to_dict()
    print("序列化后的数据:", account_dict)
    
    # 测试从字典恢复
    restored_account = Account.from_dict(account_dict)
    print("恢复后的账户:", restored_account)