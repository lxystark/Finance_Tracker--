class Stack:
    """栈：后进先出 LIFO"""
    def __init__(self):
        self.items = []          # 用列表存储
    
    def push(self, item):
        """压栈"""
        self.items.append(item)
    
    def pop(self):
        """弹栈"""
        if self.is_empty():
            return None
        return self.items.pop()
    
    def peek(self):
        """查看栈顶"""
        if self.is_empty():
            return None
        return self.items[-1]
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)