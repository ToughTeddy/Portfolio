
class Greedy:
    def __init__(self, fill : list, coverage : float, pack_or_distance : int = 0):
        self.fill, self.coverage = fill, coverage
        self.style = pack_or_distance

        if self.style == 0:
            self.value = self._pack(self.fill, self.coverage)
        elif self.style == 1:
            self.placements, self.value = self._distance(self.fill, self.coverage)

    def _pack(self, fll, cov):
        temp = 0
        total = 0
        for item in fll:
            if temp + item > cov:
                total += 1
                temp = item
            else:
                temp += item
        return total

    def _distance(self, fll, cov):
        points = sorted(fll)
        total = 0
        placement = []
        i = 0
        n = len(points)
        while i < n:
            x = points[i]
            center = x + cov
            placement.append(center)
            total += 1
            limit = center + cov
            i += 1
            while i < n and points[i] <= limit:
                i += 1
        return placement, total
