# 先定义自定义异常（根据文档5.1要求）
class InsufficientBalanceError(Exception):
    """余额不足异常"""
    def __init__(self, current_balance: float, requested_amount: float):
        self.current_balance = current_balance
        self.requested_amount = requested_amount
        super().__init__(f"余额不足！当前余额: {current_balance:.2f}, 请求金额: {requested_amount:.2f}")


class AccountNotFoundError(Exception):
    """账户不存在"""
    pass

class InvalidAmountError(Exception):
    """无效金额"""
    pass

class InvalidTransactionError(Exception):
    """无效交易异常"""
    pass