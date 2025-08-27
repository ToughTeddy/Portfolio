from propose_reject import ProposeReject

G1_T1 = ["Microsoft", "Amazon", "Apple", "Sandia", "Blizzard"]
G2_T1 = ["Mary", "Kevin", "John", "Liz", "Mike"]
P1_T1 = [[4, 3, 5, 2, 1], [2, 3, 1, 5, 4], [3, 2, 1, 5, 4], [5, 1, 2, 3, 4], [1, 2, 3, 4, 5]]
P2_T1 = [[2, 5, 3, 4, 1], [1, 5, 2, 4, 3], [4, 2, 3, 1, 5], [5, 3, 2, 1, 4], [5, 4, 3, 2, 1]]

check_one = ProposeReject(G1_T1, G2_T1, P1_T1, P2_T1, 1)
print(check_one.matches_list)

G1_T2 = ["Microsoft", "Amazon", "Apple", "Sandia", "Blizzard"]
G2_T2 = ["Mary", "Kevin", "John", "Liz", "Mike", "Bowyer", "Dave", "Taylor", "Summer", "Danny"]
P1_T2 = [[0, 4, 2, 1, 3, 5, 7, 8, 9, 6], [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], [0, 9, 8, 7, 6, 5, 4, 3, 2, 1],
         [5, 2, 7, 9, 0, 8, 1, 3, 4, 6], [9, 7, 8, 6, 4, 5, 3, 1, 2, 0]]
P2_T2 = [[2, 5, 3, 4, 1], [1, 5, 2, 4, 3], [4, 2, 3, 1, 5], [5, 3, 2, 1, 4], [5, 4, 3, 2, 1],
      [3, 2, 4, 5, 1], [1, 2, 3, 4, 5], [5, 4, 1, 2, 3], [4, 3, 2, 1, 5], [2, 3, 4, 5, 1]]

check_two = ProposeReject(G1_T2, G2_T2, P1_T2, P2_T2, 2)
print(check_two.matches_list)

G1_T3 = ["Microsoft", "Amazon"]
G2_T3 = ["Mary", "Kevin", "John", "Liz", "Mike"]
P1_T3 = [[4, 3, 5, 2, 1], [2, 3, 1, 5, 4]]
P2_T3 = [[1, 2], [2, 1], [2, 1], [2, 1], [1, 2]]

check_three = ProposeReject(G1_T3, G2_T3, P1_T3, P2_T3, 2)
print(check_three.matches_list)

