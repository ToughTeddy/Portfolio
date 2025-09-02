import json
import os

class Stack:
    def __init__(self, filename = "stack.json"):
        self.filename = filename
        self.items = self._load_data()

    def _load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []

    def _save_data(self):
        with open(self.filename, "w") as file:
            json.dump(self.items, file)

    def is_empty(self):
        return len(self.items) == 0

    def push(self, item):
        self.items.append(item)
        self._save_data()

    def pop(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        item = self.items.pop()
        self._save_data()
        return item

    def peek(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items[-1]

    def size(self):
        return len(self.items)

    def __str__(self):
        return f"Stack({self.items})"