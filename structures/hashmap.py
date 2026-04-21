#hashmap
class HashMap:

    def __init__(self, size=100):

        self.size = size

        self.map = [None] * self.size