
class MergeSort:
    def __init__(self, items):
        self.items = items
        self.sorted_items = self._merge_sort(self.items)

    def _merge(self, left, right):
        result = []
        i, j = 0, 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def _merge_sort(self, items):
        if len(items) <= 1:
            return items
        mid = len(items) // 2
        left = self._merge_sort(items[:mid])
        right = self._merge_sort(items[mid:])
        return self._merge(left, right)

