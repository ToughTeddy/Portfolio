from typing import List, Dict, Tuple, Optional
from collections import deque

RankPairs = List[Tuple[int, str]]
PrefsDict  = Dict[str, RankPairs]
INF = 10**9

class ProposeReject:
    """
    label:
      - "one_one"  : group1 cap = 1, group2 cap = 1
      - "many_one" : group1 cap = 1, group2 cap from cap_g2 (default 1 per node)
    """
    def __init__(self, group1: PrefsDict, group2: PrefsDict, label: str = "one_one",
                 strict: bool = False, *, cap_g2: Optional[Dict[str, int]] = None):
        self.label = str(label)

        # ---- names/sets ----
        self.group1_names = list(group1.keys())
        self.group2_names = list(group2.keys())
        self.S1, self.S2 = set(self.group1_names), set(self.group2_names)

        # ---- prefs: rank-pairs -> tiers (ties allowed) ----
        self.group1_tiers = {
            p: self._tiers_from_rank_pairs(group1[p], allowed=self.S2, owner=p, strict=strict)
            for p in self.group1_names
        }
        self.group2_tiers = {
            b: self._tiers_from_rank_pairs(group2[b], allowed=self.S1, owner=b, strict=strict)
            for b in self.group2_names
        }

        # ---- rank maps (smaller rank = better) ----
        self.group1_rank_of_group2 = {
            p: self._rank_map_from_tiers(self.group1_tiers[p]) for p in self.group1_names
        }
        self.group2_rank_of_group1 = {
            b: self._rank_map_from_tiers(self.group2_tiers[b]) for b in self.group2_names
        }

        # ---- capacities (only one_one or many_one) ----
        if self.label == "one_one":
            self.cap_g2 = {b: 1 for b in self.group2_names}
        elif self.label == "many_one":
            self.cap_g2 = {b: (cap_g2[b] if (cap_g2 and b in cap_g2) else 1) for b in self.group2_names}
        else:
            raise ValueError("label must be 'one_one' or 'many_one'")

        # group1 capacity is always 1 in both modes
        self.cap_g1 = {p: 1 for p in self.group1_names}

        # ---- state: matches (lists for uniformity), free flags, proposal pointers ----
        self.match_g1: Dict[str, List[str]] = {p: [] for p in self.group1_names}
        self.match_g2: Dict[str, List[str]] = {b: [] for b in self.group2_names}
        self.free_g1: Dict[str, bool] = {p: True for p in self.group1_names}
        self.free_g2: Dict[str, bool] = {b: True for b in self.group2_names}

        self._ri: Dict[str, int] = {p: 0 for p in self.group1_names}  # rank tier index per g1
        self._ti: Dict[str, int] = {p: 0 for p in self.group1_names}  # index inside current tier

    # ---------- preference helpers ----------

    def _tiers_from_rank_pairs(self, pairs: RankPairs, *, allowed: set, owner: str, strict: bool) -> List[List[str]]:
        by_rank: Dict[int, List[str]] = {}
        seen: set = set()
        for r, name in pairs:
            if not isinstance(r, int) or r < 1:
                raise ValueError(f"prefs for {owner!r}: rank must be positive int, got {r!r}")
            if name not in allowed:
                raise ValueError(f"prefs for {owner!r}: unknown name {name!r}")
            if name in seen:
                raise ValueError(f"prefs for {owner!r}: duplicate entry for {name!r}")
            seen.add(name)
            by_rank.setdefault(r, []).append(name)

        if strict and seen != allowed:
            missing = sorted(allowed - seen)
            extra   = sorted(seen - allowed)
            msg = f"prefs for {owner!r}: strict mode requires ranking all opponents exactly once"
            if missing: msg += f"; missing={missing}"
            if extra:   msg += f"; extras={extra}"
            raise ValueError(msg)

        return [list(by_rank[r]) for r in sorted(by_rank)]

    @staticmethod
    def _rank_map_from_tiers(tiers: List[List[str]]) -> Dict[str, int]:
        ranks: Dict[str, int] = {}
        for r, tier in enumerate(tiers, start=1):
            for name in tier:
                ranks[name] = r
        return ranks

    # ---------- utility ----------

    def _has_capacity_g1(self, p: str) -> bool:
        return len(self.match_g1[p]) < self.cap_g1[p]

    def _has_capacity_g2(self, b: str) -> bool:
        return len(self.match_g2[b]) < self.cap_g2[b]

    def _rank_at_g2(self, b: str, p: str) -> int:
        return self.group2_rank_of_group1[b].get(p, INF)  # unranked => worst

    def _worst_current_at_g2(self, b: str) -> Tuple[str, int]:
        worst_p = None
        worst_r = -1
        for p in self.match_g2[b]:
            r = self._rank_at_g2(b, p)
            if r > worst_r:
                worst_p, worst_r = p, r
        return worst_p, worst_r

    def _next_target(self, p: str) -> Optional[str]:
        tiers = self.group1_tiers[p]
        ri, ti = self._ri[p], self._ti[p]
        while ri < len(tiers):
            tier = tiers[ri]
            if ti < len(tier):
                b = tier[ti]
                self._ti[p] += 1
                return b
            ri += 1
            self._ri[p] = ri
            self._ti[p] = 0
        return None

    # ---------- matching (group1 proposes) ----------

    def match(self) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
        """
        Gale–Shapley style with capacities constrained to one_one or many_one.
        Tie policy at group2: keep current on equal rank (weakly stable).
        """
        # reset state in case of re-run
        self.match_g1 = {p: [] for p in self.group1_names}
        self.match_g2 = {b: [] for b in self.group2_names}
        self.free_g1  = {p: True for p in self.group1_names}
        self.free_g2  = {b: True for b in self.group2_names}
        self._ri = {p: 0 for p in self.group1_names}
        self._ti = {p: 0 for p in self.group1_names}

        Q = deque([p for p in self.group1_names if self._has_capacity_g1(p)])

        while Q:
            p = Q.popleft()
            if not self._has_capacity_g1(p):
                continue
            b = self._next_target(p)
            if b is None:
                continue  # no one left to propose to

            if self._has_capacity_g2(b):
                # accept
                self.match_g1[p].append(b)
                self.match_g2[b].append(p)
                self.free_g1[p] = not self._has_capacity_g1(p)
                self.free_g2[b] = not self._has_capacity_g2(b)
                if self._has_capacity_g1(p):
                    Q.append(p)
            else:
                # b full: see if p beats b's worst current match
                worst_p, worst_r = self._worst_current_at_g2(b)
                r_new = self._rank_at_g2(b, p)
                if r_new < worst_r:
                    # replace worst with p
                    self.match_g2[b].remove(worst_p)
                    self.match_g1[worst_p].remove(b)
                    self.free_g1[worst_p] = True  # dumped; can propose again
                    self.match_g2[b].append(p)
                    self.match_g1[p].append(b)
                    self.free_g1[p] = not self._has_capacity_g1(p)
                    self.free_g2[b] = not self._has_capacity_g2(b)
                    if self._has_capacity_g1(worst_p):
                        Q.append(worst_p)
                    if self._has_capacity_g1(p):
                        Q.append(p)
                elif r_new == worst_r:
                    # tie with worst: keep current set; p tries next
                    Q.append(p)
                else:
                    # worse: p tries next
                    Q.append(p)

        return self.match_g1, self.match_g2


