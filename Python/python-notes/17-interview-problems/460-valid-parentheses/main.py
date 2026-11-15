"""460. Valid Parentheses - stack (run: python3 main.py)."""
from typing import Dict, List  # type hints

PAIRS: Dict[str, str] = {")": "(", "]": "[", "}": "{"}  # closer -> opener


def is_valid(s: str) -> bool:
    """O(n) time, O(n) space."""
    stack: List[str] = []  # holds unmatched openers
    for ch in s:  # scan left to right
        if ch in PAIRS:  # it is a closer
            if not stack or stack.pop() != PAIRS[ch]:  # nothing to match or wrong type
                return False  # invalid
        elif ch in PAIRS.values():  # it is an opener
            stack.append(ch)  # remember it
    return not stack  # valid only if nothing is left open


if __name__ == "__main__":
    for text in ["()", "()[]{}", "(]", "([)]", "{[]}", "", "(((", ")"]:  # samples
        print(repr(text), is_valid(text))  # show result
    assert is_valid("") is True  # empty is valid
    assert is_valid("()[]{}") and is_valid("{[()]}")  # valid
    assert not is_valid("(]") and not is_valid("([)]")  # wrong order/type
    assert not is_valid("(((") and not is_valid(")")  # unclosed / extra closer
    assert is_valid("a(b)c")  # other characters ignored
    print("all tests passed")
