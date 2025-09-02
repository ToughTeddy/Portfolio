import unittest
from mergeS import MergeSort

class TestMergeSort(unittest.TestCase):
    def test_empty_list(self):
        test_case = MergeSort([])
        self.assertEqual(test_case.sorted_items, [])

    def test_single_item(self):
        test_case = MergeSort([42])
        self.assertEqual(test_case.sorted_items, [42])

    def test_already_sorted(self):
        test_case = MergeSort([1, 2, 3, 4])
        self.assertEqual(test_case.sorted_items, [1, 2, 3, 4])

    def test_reverse_sorted(self):
        test_case = MergeSort([5, 4, 3, 2, 1])
        self.assertEqual(test_case.sorted_items, [1, 2, 3, 4, 5])

    def test_with_duplicates(self):
        test_case = MergeSort([3, 1, 2, 1, 4])
        self.assertEqual(test_case.sorted_items, [1, 1, 2, 3, 4])

    def test_with_negative_numbers(self):
        test_case = MergeSort([0, -3, 5, -1, 2])
        self.assertEqual(test_case.sorted_items, [-3, -1, 0, 2, 5])


if __name__ == "__main__":
    unittest.main()