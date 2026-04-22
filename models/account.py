from abc import ABC, abstractmethod  # 导入抽象类工具
from exceptions import InsufficientFundsError, InvalidAmountError


# ========== 抽象基类 ==========
class Account(ABC):  # 继承ABC，表示这是抽象类，不能直接创建对象
    """
    账户抽象基类
    体现：抽象类、封装
    """

    def __init__(self, account_id, owner, balance=0.0):
        self.account_id = account_id    # 公开属性：账户ID
        self.owner = owner              # 公开属性：账户持有人
        self._balance = balance         # 私有属性：余额（_表示外部不应直接修改）

    # ---- 抽象方法（子类必须实现）----
    @abstractmethod
    def get_account_type(self):
        """返回账户类型字符串，子类必须实现"""
        pass

    @abstractmethod
    def calculate_interest(self):
        """计算利息，子类必须实现"""
        pass

    # ---- 通用方法（所有子类共用）----
    def deposit(self, amount):
        """存钱"""
        if amount <= 0:
            raise InvalidAmountError("存入金额必须大于0")
        self._balance += amount

    def withdraw(self, amount):
        """取钱"""
        if amount <= 0:
            raise InvalidAmountError("取出金额必须大于0")
        if amount > self._balance:
            raise InsufficientFundsError(
                current_balance=self._balance,
                requested_amount=amount
            )
        self._balance -= amount

    def get_balance(self):
        """查看余额（通过方法访问私有属性）"""
        return self._balance

    def __str__(self):
        """打印账户信息"""
        return (f"[{self.get_account_type()}] "
                f"ID:{self.account_id} "
                f"持有人:{self.owner} "
                f"余额:{self._balance:.2f}")

    def to_dict(self):
        """转成字典，用于保存到JSON"""
        return {
            "account_id": self.account_id,
            "owner": self.owner,
            "balance": self._balance,
            "type": self.get_account_type()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Account':
        """字典 → 账户对象（根据 type 字段选择正确的子类）"""
        from models.account import SavingsAccount, CreditAccount
        account_type = data.get("type", "savings")
        if account_type == "credit":
            return CreditAccount(
                account_id=data["account_id"],
                owner=data["owner"],
                balance=data.get("balance", 0.0),
                credit_limit=data.get("credit_limit", 5000.0)
            )
        else:
            return SavingsAccount(
                account_id=data["account_id"],
                owner=data["owner"],
                balance=data.get("balance", 0.0),
                interest_rate=data.get("interest_rate", 0.03)
            )


# ========== 储蓄账户 ==========
class SavingsAccount(Account):
    """
    储蓄账户：有利息（3%）
    体现：继承、多态
    """

    def __init__(self, account_id, owner, balance=0.0, interest_rate=0.03):
        super().__init__(account_id, owner, balance)  # 调用父类__init__
        self.interest_rate = interest_rate            # 储蓄账户特有属性

    def get_account_type(self):
        return "savings"

    def calculate_interest(self):
        """计算年利息"""
        return self._balance * self.interest_rate

    def to_dict(self):
        """储蓄账户多存一个interest_rate字段"""
        d = super().to_dict()
        d["interest_rate"] = self.interest_rate
        return d



# ========== 信用账户 ==========
class CreditAccount(Account):
    """
    信用账户：有信用额度，余额可以为负
    体现：继承、多态、重写父类方法
    """

    def __init__(self, account_id, owner, balance=0.0, credit_limit=5000.0):
        super().__init__(account_id, owner, balance)
        self.credit_limit = credit_limit   # 信用额度

    def get_account_type(self):
        return "credit"

    def calculate_interest(self):
        """欠款部分收取20%利息"""
        if self._balance < 0:
            return abs(self._balance) * 0.20
        return 0.0

    def withdraw(self, amount):
        """重写取钱方法：余额不够可以用信用额度"""
        if amount <= 0:
            raise InvalidAmountError("取出金额必须大于0")
        if self._balance - amount < -self.credit_limit:
            raise InsufficientFundsError(
                current_balance=self._balance,
                requested_amount=amount,
                message=f"超出信用额度！当前余额:{self._balance:.2f}, 信用额度:{self.credit_limit:.2f}"
            )
        self._balance -= amount

    def to_dict(self):
        """信用账户多存一个credit_limit字段"""
        d = super().to_dict()
        d["credit_limit"] = self.credit_limit
        return d


# ========== 测试代码 ==========
if __name__ == "__main__":
    print("=== 测试账户类 ===\n")

    # 创建3种账户
    s = SavingsAccount("A001", "张三", 10000)

    cr = CreditAccount("A003", "王五", 1000, credit_limit=3000)

    # 打印
    print(s)
    print(cr)

    # 存钱
    s.deposit(500)
    print(f"\n张三存入500后余额: {s.get_balance()}")

    # 信用账户取钱（超出余额但在信用额度内）
    cr.withdraw(3000)
    print(f"王五取出3000后余额: {cr.get_balance()}")

    # 利息
    print(f"\n张三年利息: {s.calculate_interest()}")
    print(f"王五利息（欠款利息）: {cr.calculate_interest()}")

    # 测试异常
    print("\n=== 测试异常 ===")
    try:
        s.withdraw(999999)
    except InsufficientFundsError as e:
        print(f"捕获异常: {e}")

    try:
        s.deposit(-100)
    except InvalidAmountError as e:
        print(f"捕获异常: {e}")
