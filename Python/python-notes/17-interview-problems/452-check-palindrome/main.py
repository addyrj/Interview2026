"""Check Palindrome - three approaches, with tests. Run: python main.py"""
from typing import Callable, List, Tuple  # type hints


def is_palindrome_slice(s: str) -> bool:
    """Pythonic: clean the string, compare with its reverse. O(n) time, O(n) space."""
    cleaned: str = "".join(ch.lower() for ch in s if ch.isalnum())  # keep letters/digits only
    return cleaned == cleaned[::-1]  # equal to its reverse?


def is_palindrome_two_pointers(s: str) -> bool:
    """Interview favourite: O(n) time, O(1) extra space (no new string)."""
    left: int = 0  # pointer at the start
    right: int = len(s) - 1  # pointer at the end
    while left < right:  # until pointers meet
        while left < right and not s[left].isalnum():  # skip junk on the left
            left += 1  # move right
        while left < right and not s[right].isalnum():  # skip junk on the right
            right -= 1  # move left
        if s[left].lower() != s[right].lower():  # mismatch -> not a palindrome
            return False  # early exit
        left += 1  # shrink window
        right -= 1  # shrink window
    return True  # all pairs matched


def is_palindrome_recursive(s: str) -> bool:
    """Recursive version (for learning; depth = n/2, so avoid for huge input)."""
    cleaned: str = "".join(ch.lower() for ch in s if ch.isalnum())  # normalise once

    def helper(lo: int, hi: int) -> bool:  # compare s[lo] and s[hi]
        if lo >= hi:  # base case: nothing left to compare
            return True
        if cleaned[lo] != cleaned[hi]:  # outer pair differs
            return False
        return helper(lo + 1, hi - 1)  # check the inner part

    return helper(0, len(cleaned) - 1)  # start from both ends


def is_integer_palindrome(n: int) -> bool:
    """Number palindrome without converting to str (reverse the digits)."""
    if n < 0:  # negatives are never palindromes (the '-' sign)
        return False
    original: int = n  # remember the input
    reversed_n: int = 0  # build the reversed number
    while n > 0:  # peel digits one by one
        reversed_n = reversed_n * 10 + n % 10  # append last digit
        n //= 10  # drop last digit
    return original == reversed_n  # compare


def main() -> None:
    cases: List[Tuple[str, bool]] = [  # (input, expected)
        ("madam", True),
        ("A man, a plan, a canal: Panama", True),
        ("hello", False),
        ("", True),  # empty string is a palindrome
        ("a", True),  # single char
        ("No 'x' in Nixon", True),
        ("race a car", False),
    ]
    funcs: List[Callable[[str], bool]] = [
        is_palindrome_slice, is_palindrome_two_pointers, is_palindrome_recursive,
    ]
    for fn in funcs:  # every approach must agree
        for text, expected in cases:
            assert fn(text) is expected, (fn.__name__, text)  # fail loudly
    assert is_integer_palindrome(121) and not is_integer_palindrome(123)
    assert not is_integer_palindrome(-121) and is_integer_palindrome(0)
    print("All palindrome tests passed")  # Output: All palindrome tests passed


if __name__ == "__main__":
    main()
