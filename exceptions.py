'''
    @Author: Xinyuan Lin
    It's a custum exceptions module for the project.
    We combined all the exceptions in this program.
    自定义异常定义（项目统一异常源）

'''


class InsufficientFundsError(Exception):
    """余额/额度不足异常"""
    def __init__(self, current_balance: float = 0, requested_amount: float = 0, message: str = ""):
        self.current_balance = current_balance
        self.requested_amount = requested_amount
        if message:
            super().__init__(message)
        else:
            super().__init__(f"余额不足！当前余额: {current_balance:.2f}, 请求金额: {requested_amount:.2f}")


class AccountNotFoundError(Exception):
    """账户不存在"""
    pass


class InvalidAmountError(Exception):
    """无效金额（负数或零）"""
    pass


class InvalidTransactionError(Exception):
    """无效交易异常"""
    pass


# 向后兼容别名
InsufficientBalanceError = InsufficientFundsError