
class ProposeReject:
    """
            Stable Matching Algo. where group1 proposes to group2.
            Supports 1-to-1 matching or many-to-1 matching (group1 capacity >= 1, group2 capacity = 1).

            Args:
                group1 : list["str"]
                group2 : list["str"]
                pref1 : list[list[int]]
                pref2 : list[list[int]]
                one_or_many : int

            Raises:
                AssertionError : If pref1 / pref2 row counts don't match group sizes.
                ValueError : If preference row contains out of range int or mixed/invalid indexing.

            Attributes:
                size1 (int) : Size of group1.
                size2 (int) : Size of group2.
                cap_g1 (list[int]) : Capacity of group1 members. All = one_or_many
                cap_g2 (list[int]) : Capacity of group2 members. All = 1
                pref1_idx (list[list[int]]) : Normalized 0-based preferences of group1 over group2.
                pref2_idx (list[list[int]]) : Normalized 0-based preferences of group2 over group1.
                match_g1 (list[list[int]]) : For each group1 index, list of matched group2.
                match_g2 (list[int]) : For each group2 index, matched group1.
                matches_list (list[list[str]]) : Final matches as converted to names.
                    each row = ["group1_name", "group2_name1", "group2_name2", ...] (group1 name first)
                matches_list_idx (list[list[int]]) : Same as indices.

            Example:
                G1 = ["Microsoft", "Amazon"]
                G2 = ["Mary", "Kevin", "John"]
                P1 = [[2, 1, 3], [1, 2, 3]]
                P2 = [[1, 2], [2, 1], [1, 2]]
                pr = ProposeReject(G1, G2, P1, P2, one_or_many=2)
                print(pr.matches_list)

                output:
                [['Microsoft', 'Kevin', 'Mary'], ['Amazon', 'John']]
            """

    def __init__(self, group1 : list, group2 : list, pref1: list, pref2 : list,
                 one_or_many : int = 1):
        """Constructor. See class docstring for full parameter details."""
        self.group1, self.group2 = list(group1), list(group2)
        self.pref1, self.pref2 = pref1, pref2
        self.size1, self.size2 = len(group1), len(group2)

        cap = int(one_or_many) if one_or_many >= 1 else 1
        self.cap_g1 = [cap] * self.size1
        self.cap_g2 = [1] * self.size2

        self.free1 = [True] * self.size1
        self.idx_next = [0] * self.size1

        self.pref1_idx = self._base_normalize(
            self.pref1, max_id=self.size2, owner="pref1 (group1→group2)"
        )
        self.pref2_idx = self._base_normalize(
            self.pref2, max_id=self.size1, owner="pref2 (group2→group1)"
        )

        assert len(self.pref1_idx) == self.size1, "pref1 must have one list per member of group1"
        assert len(self.pref2_idx) == self.size2, "pref2 must have one list per member of group2"

        self.match_g1 = [[] for _ in range(self.size1)]
        self.match_g2 = [-1] * self.size2

        self.rank_g2_over_g1 = [dict() for _ in range(self.size2)]
        for j, lst in enumerate(self.pref2_idx):
            for pos, g1_idx in enumerate(lst, start=1):
                self.rank_g2_over_g1[j][g1_idx] = pos

        self.rank_g1_over_g2 = [dict() for _ in range(self.size1)]
        for i, lst in enumerate(self.pref1_idx):
            for pos, g2_idx in enumerate(lst, start=1):
                self.rank_g1_over_g2[i][g2_idx] = pos

        while True:
            step = self._next_match()
            if step is None:
                break
            i, j = step
            self._g2_pref_check(i, j)

        self.matches_list_idx = [[i] + list(self.match_g1[i]) for i in range(self.size1)]
        self.matches_list = [
            [self.group1[i]] + [self.group2[j] for j in self.match_g1[i]]
            for i in range(self.size1)
        ]

    def _base_normalize(self, prefs: list, *, max_id: int, owner: str) -> list[list[int]]:
        norm: list[list[int]] = []

        for r, row in enumerate(prefs):
            if not row:
                norm.append([])
                continue
            mn, mx = min(row), max(row)
            ok0 = (0 <= mn) and (mx <= max_id - 1)
            ok1 = (1 <= mn) and (mx <= max_id)

            if ok0 and not ok1:
                base = 0
            elif ok1 and not ok0:
                base = 1
            elif ok0 and ok1:
                if 0 in row:
                    base = 0
                elif max_id in row:
                    base = 1
                else:
                    base = 1
            else:
                raise ValueError(
                    f"{owner} row {r}: IDs must be 0..{max_id - 1} (0-based) or 1..{max_id} (1-based). "
                    f"Received min={mn}, max={mx}.")
            if base == 1:
                conv = [v - 1 for v in row]
                if not conv or min(conv) < 0 or max(conv) > max_id - 1:
                    raise ValueError(f"{owner} row {r}: invalid 1-based IDs after conversion.")
                norm.append(conv)
            else:
                norm.append(list(row))
        return norm

    def _next_match(self):
        for i in range(self.size1):
            self.free1[i] = (len(self.match_g1[i]) < self.cap_g1[i])

            if not self.free1[i]:
                continue

            if self.idx_next[i] >= len(self.pref1_idx[i]):
                continue

            j = self.pref1_idx[i][self.idx_next[i]]
            self.idx_next[i] += 1
            return i, j

        return None

    def _g2_pref_check(self, i: int, j: int) -> None:
        cur = self.match_g2[j]
        if cur == -1:
            self._match(i, j)
            return

        r_new = self.rank_g2_over_g1[j].get(i, float("inf"))
        r_cur = self.rank_g2_over_g1[j].get(cur, float("inf"))

        if r_new < r_cur:
            self._match_change(i, j)
        else:
            pass

    def _match(self, i: int, j: int) -> None:
        self.match_g2[j] = i

        if j not in self.match_g1[i]:
            self.match_g1[i].append(j)

        self.free1[i] = (len(self.match_g1[i]) < self.cap_g1[i])

    def _match_change(self, i: int, j: int) -> None:
        old_i = self.match_g2[j]
        if old_i != -1:
            if j in self.match_g1[old_i]:
                self.match_g1[old_i].remove(j)
            self.free1[old_i] = (len(self.match_g1[old_i]) < self.cap_g1[old_i])
        self.match_g2[j] = i
        if j not in self.match_g1[i]:
            self.match_g1[i].append(j)
        self.free1[i] = (len(self.match_g1[i]) < self.cap_g1[i])

