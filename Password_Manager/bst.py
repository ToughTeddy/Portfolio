import json

ALPH_DICT = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9, "J": 10,
             "K": 11, "L": 12, "M": 13, "N": 14, "O": 15, "P": 16, "Q": 17, "R": 18, "S": 19,
             "T": 20, "U": 21, "V": 22, "W": 23, "X": 24, "Y": 25, "Z": 26}

class BinaryTree:
    def __init__(self):
        try:
            with open("data.json", 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = {}
            with open("data.json", 'w') as file:
                json.dump(self.data, file, indent=4)

    def add(self, name, password, email):
        try:
            first_letter = ALPH_DICT[name[0].upper()]
            last_letter = ALPH_DICT[name[-1].upper()]
            index = int(f"{first_letter}{last_letter}")
        except:
            index = 27
        new_data = {
            name: {
                "email": email,
                "password": password,
                "index": index,
                "parent": None,
                "left_child": None,
                "right_child": None
            }
        }
        try:
            with open("data.json", 'r') as file:
                self.data = json.load(file)
                self.data.update(new_data)
        except FileNotFoundError:
            with open("data.json", "w") as file:
                json.dump(new_data, file, indent=4)
        else:
            with open("data.json", "w") as file:
                json.dump(self.data, file, indent=4)
        self.treeify()

    def treeify(self):
        try:
            with open("data.json", 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            return
        if not self.data:
            return

        for node in self.data.values():
            node["parent"] = node["left_child"] = node["right_child"] = None

        root_name = next(iter(self.data))

        def _insert(current_name: str, new_name: str) -> None:
            cur_idx = self.data[current_name]["index"]
            new_idx = self.data[new_name]["index"]

            if new_idx < cur_idx:
                child = self.data[current_name]["left_child"]
                if child is None:
                    self.data[current_name]["left_child"] = new_name
                    self.data[new_name]["parent"] = current_name
                else:
                    _insert(child, new_name)
            else:
                child = self.data[current_name]["right_child"]
                if child is None:
                    self.data[current_name]["right_child"] = new_name
                    self.data[new_name]["parent"] = current_name
                else:
                    _insert(child, new_name)

        for name in self.data:
            if name == root_name:
                continue
            _insert(root_name, name)

        with open("data.json", "w") as f:
            json.dump(self.data, f, indent=4)

    def search_tree(self, name):
        try:
            first_letter = ALPH_DICT[name[0].upper()]
            last_letter = ALPH_DICT[name[-1].upper()]
            target_index = int(f"{first_letter}{last_letter}")
        except (KeyError, IndexError):
            return None

        try:
            with open("data.json", "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            return None

        if not self.data:
            return None

        current_name = next(iter(self.data))

        while current_name is not None:
            current_node = self.data[current_name]
            current_index = current_node["index"]

            if current_index == target_index:
                return {
                    "email": current_node["email"],
                    "password": current_node["password"],
                }
            elif target_index < current_index:
                current_name = current_node["left_child"]
            else:
                current_name = current_node["right_child"]

        return None