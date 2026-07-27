from datetime import datetime
from typing import Optional, Dict, Any
import uuid
from abc import ABC, abstractmethod

# 统一的抽象基类
class Transaction(ABC):
    def __init__(self, amount: float, date: datetime, description: str, category: Optional[str] = None, transaction_id: Optional[str] = None):
        self._amount = amount
        self._date = date
        self._description = description
        self._category = category
        self._transaction_id = transaction_id or str(uuid.uuid4())[:8]
    
    @property
    def amount(self) -> float:
        return self._amount
    
    @property
    def date(self) -> datetime:
        return self._date
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def category(self) -> Optional[str]:
        return self._category
    
    @property
    def transaction_id(self) -> str:
        return self._transaction_id
    
    @abstractmethod
    def get_transaction_type(self) -> str:
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "type": self.get_transaction_type(),
            "amount": self.amount,
            "category": self.category,
            "date": self.date.isoformat(),
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        date = datetime.fromisoformat(data["date"])
        if data["type"] == "income":
            return Income(data["amount"], date, data["description"], data.get("category"), data.get("transaction_id"))
        elif data["type"] == "expense":
            return Expense(data["amount"], date, data["description"], data.get("category"), data.get("transaction_id"))
        else:
            raise ValueError(f"未知的交易类型: {data['type']}")



def delete_transaction(linked_list, transaction_id):
    """根据交易ID删除"""
    current = linked_list.head
    while current:
        if hasattr(current.data, "transaction_id") and current.data.transaction_id == transaction_id:
            linked_list.remove(current)
            print(f"已删除交易 #{transaction_id}")
            return True
        current = current.next
    print(f"未找到交易 #{transaction_id}")
    return False

def update_transaction(linked_list, transaction_id, **kwargs):
    """根据交易ID修改，kwargs 是要修改的字段"""
    current = linked_list.head
    while current:
        if hasattr(current.data, "transaction_id") and current.data.transaction_id == transaction_id:
            for key, value in kwargs.items():
                if hasattr(current.data, key):
                    setattr(current.data, key, value)
            print(f"已修改交易 #{transaction_id}")
            return True
        current = current.next
    print(f"未找到交易 #{transaction_id}")
    return False


class Income(Transaction):
    """收入类"""
    def __init__(self, amount: float, date: datetime, description: str, category: Optional[str] = None, transaction_id: Optional[str] = None):
        super().__init__(amount, date, description, category, transaction_id)
    def get_transaction_type(self) -> str:
        return "income"

class Expense(Transaction):
    """支出类"""
    def __init__(self, amount: float, date: datetime, description: str, category: Optional[str] = None, transaction_id: Optional[str] = None):
        super().__init__(amount, date, description, category, transaction_id)
    def get_transaction_type(self) -> str:
        return "expense"
