"""
双向链表 - Doubly Linked List
用于存储交易记录，支持O(1)头部插入
"""

class Node:
    """节点"""
    def __init__(self, data):
        self.data = data      # 存储的数据
        self.next = None      # 指向下一个节点
        self.prev = None      # 指向上一个节点


class DoublyLinkedList:
    """双向链表"""
    
    def __init__(self):
        self.head = None      # 头节点
        self.tail = None      # 尾节点
        self.size = 0         # 节点数量
    
    def append(self, data):
        """在尾部添加"""
        node = Node(data)
        
        if self.head is None:        # 链表是空的
            self.head = node
            self.tail = node
        else:                         # 链表不是空的
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        
        self.size += 1
    
    def prepend(self, data):
        """在头部添加 - O(1)"""
        node = Node(data)
        
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
        
        self.size += 1
    
    def remove(self, node):
        """删除节点"""
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        
        self.size -= 1
    
    def __str__(self):
        """打印链表"""
        items = []
        current = self.head
        while current:
            items.append(str(current.data))
            current = current.next
        return " <-> ".join(items)
    
    def to_list(self):
        """转换为普通列表"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result


# ============ 测试代码 ============
if __name__ == "__main__":
    print("=== 测试双向链表 ===")
    
    ll = DoublyLinkedList()
    
    ll.append("交易1")
    ll.append("交易2")
    ll.append("交易3")
    print("添加3个:", ll)
    
    ll.prepend("交易0")
    print("头部添加:", ll)
    
    # 删除第二个节点
    current = ll.head.next
    ll.remove(current)
    print("删除第二个:", ll)
    
    print("转为列表:", ll.to_list())
  
'''
  保存方向（对象 → 字典 → JSON）         读取方向（JSON → 字典 → 对象）
  ─────────────────────────           ─────────────────────────

  Transaction 对象                     JSON 文件中的字典
       │                                    │
       ▼                                    ▼
  t.to_dict()                         json.load(f)
       │                                    │
       ▼                                    ▼
  {"tid": 1, "type": "支出", ...}      {"tid": 1, "type": "支出", ...}
       │                                    │
       ▼                                    ▼
  json.dump()                         Transaction.from_dict(data)
       │                                    │
       ▼                                    ▼
  data.json 文件                       Transaction 对象
'''