"""470. Pascal's Triangle (run: python3 main.py)."""
from math import comb  # binomial coefficient (3.8+)
from typing import List  # type hints


def pascal(rows: int) -> List[List[int]]:
    """Build `rows` rows. O(rows^2) time and space."""
    tri: List[List[int]] = []  # all rows
    for r in range(rows):  # row index
        row: List[int] = [1] * (r + 1)  # edges are 1
        for c in range(1, r):  # inner cells
            row[c] = tri[r - 1][c - 1] + tri[r - 1][c]  # sum of two above
        tri.append(row)  # store
    return tri  # triangle


def pascal_row(k: int) -> List[int]:
    """Only row k (0-indexed) using O(k) space."""
    row: List[int] = [1]  # row 0
    for _ in range(k):  # build up
        row = [1] + [a + b for a, b in zip(row, row[1:])] + [1]  # neighbours sum
    return row  # row k


def pretty(rows: int) -> str:
    """Centered text triangle."""
    tri = pascal(rows)  # data
    width = len(" ".join(map(str, tri[-1])))  # last row is widest
    return "\n".join(" ".join(map(str, r)).center(width) for r in tri)  # centered lines


if __name__ == "__main__":
    print(pascal(5))  # list of rows
    print(pretty(5))  # drawn
    print(pascal_row(4))  # [1, 4, 6, 4, 1]
    assert pascal(0) == [] and pascal(1) == [[1]]  # edges
    assert pascal(5)[-1] == [1, 4, 6, 4, 1]  # known row
    for k in range(12):  # cross-check three ways
        assert pascal_row(k) == pascal(k + 1)[-1] == [comb(k, i) for i in range(k + 1)]  # agree
        assert sum(pascal_row(k)) == 2 ** k  # row sums are powers of two
    print("all tests passed")
