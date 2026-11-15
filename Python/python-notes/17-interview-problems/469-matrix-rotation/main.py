"""469. Matrix Rotation 90 degrees clockwise (run: python3 main.py)."""
from typing import List  # type hints

Matrix = List[List[int]]  # alias


def rotate_new(m: Matrix) -> Matrix:
    """New matrix, one line: reverse rows then transpose. O(n*m) space."""
    return [list(row) for row in zip(*m[::-1])]  # zip(*reversed rows) = columns


def rotate_inplace(m: Matrix) -> None:
    """N x N only, O(1) extra space: transpose then reverse each row."""
    n: int = len(m)  # size
    for i in range(n):  # transpose
        for j in range(i + 1, n):  # upper triangle only
            m[i][j], m[j][i] = m[j][i], m[i][j]  # swap across diagonal
    for row in m:  # reverse each row
        row.reverse()  # in place


def rotate_ccw(m: Matrix) -> Matrix:
    """Counter-clockwise: transpose then reverse the row order."""
    return [list(row) for row in zip(*m)][::-1]  # columns, bottom-up


if __name__ == "__main__":
    grid: Matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]  # sample
    print(rotate_new(grid))  # [[7,4,1],[8,5,2],[9,6,3]]
    g2 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]  # fresh copy
    rotate_inplace(g2)  # mutate
    print(g2)  # same result
    print(rotate_new([[1, 2, 3], [4, 5, 6]]))  # rectangle -> [[4,1],[5,2],[6,3]]
    assert rotate_new(grid) == g2 == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]  # both agree
    assert rotate_new([[1, 2, 3], [4, 5, 6]]) == [[4, 1], [5, 2], [6, 3]]  # non-square
    assert rotate_new([[5]]) == [[5]]  # 1x1
    assert rotate_ccw(grid) == [[3, 6, 9], [2, 5, 8], [1, 4, 7]]  # ccw
    m = [[1, 2], [3, 4]]  # four rotations return the original
    for _ in range(4):  # rotate 4 times
        rotate_inplace(m)  # in place
    assert m == [[1, 2], [3, 4]]  # identity
    print("all tests passed")
