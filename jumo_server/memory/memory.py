
class MemoryManager:
    def __init__(self):
        self.data = []

    def add(self, data):
        self.data.append(data)

    def get(self):
        return self.data

    def clear(self):
        self.data = []

memory = Memory()
