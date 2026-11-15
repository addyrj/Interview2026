"""FizzBuzz - classic, generator, rule-table versions. Run: python main.py"""
from typing import Dict, Iterator, List  # type hints


def fizzbuzz(n: int) -> List[str]:
    """Classic version: check 15 FIRST, otherwise 3 and 5 would swallow it."""
    out: List[str] = []  # result list
    for i in range(1, n + 1):  # 1..n inclusive
        if i % 15 == 0:  # divisible by both 3 and 5
            out.append("FizzBuzz")
        elif i % 3 == 0:  # only 3
            out.append("Fizz")
        elif i % 5 == 0:  # only 5
            out.append("Buzz")
        else:  # neither
            out.append(str(i))
    return out


def fizzbuzz_concat(n: int) -> List[str]:
    """Concatenation trick: no explicit '15' check."""
    out: List[str] = []
    for i in range(1, n + 1):
        word: str = ("Fizz" if i % 3 == 0 else "") + ("Buzz" if i % 5 == 0 else "")  # build word
        out.append(word or str(i))  # empty string is falsy -> use the number
    return out


def fizzbuzz_rules(n: int, rules: Dict[int, str]) -> Iterator[str]:
    """Extensible: any divisor->word rules, lazy generator (O(1) memory)."""
    for i in range(1, n + 1):
        word: str = "".join(w for d, w in rules.items() if i % d == 0)  # all matching words
        yield word or str(i)


def main() -> None:
    expected: List[str] = ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz",
                           "11", "Fizz", "13", "14", "FizzBuzz"]
    assert fizzbuzz(15) == expected
    assert fizzbuzz_concat(15) == expected
    assert list(fizzbuzz_rules(15, {3: "Fizz", 5: "Buzz"})) == expected
    assert fizzbuzz(0) == []  # edge case: nothing
    assert list(fizzbuzz_rules(7, {3: "Fizz", 5: "Buzz", 7: "Bazz"}))[-1] == "Bazz"
    print(", ".join(fizzbuzz(15)))
    print("All FizzBuzz tests passed")


if __name__ == "__main__":
    main()
