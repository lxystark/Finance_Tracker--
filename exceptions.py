class InsufficientFundsError(Exception):
    """余额不足"""
    pass

class AccountNotFoundError(Exception):
    """账户不存在"""
    pass

class InvalidAmountError(Exception):
    """无效金额"""
    pass
