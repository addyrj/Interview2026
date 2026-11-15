"""Group Anagrams - sorted key vs count key. Run: python main.py"""
from collections import defaultdict  # auto-creating lists
from typing import DefaultDict, List, Tuple  # type hints


def group_anagrams_sorted(words: List[str]) -> List[List[str]]:
    """Key = sorted letters. O(n * k log k), k = word length."""
    groups: DefaultDict[str, List[str]] = defaultdict(list)  # key -> words
    for word in words:
        key: str = "".join(sorted(word))  # 'eat' and 'tea' both -> 'aet'
        groups[key].append(word)  # file under the key
    return list(groups.values())  # dicts keep insertion order


def group_anagrams_count(words: List[str]) -> List[List[str]]:
    """Key = 26-letter count tuple (lowercase a-z). O(n * k)."""
    groups: DefaultDict[Tuple[int, ...], List[str]] = defaultdict(list)
    for word in words:
        counts: List[int] = [0] * 26  # one slot per letter
        for ch in word:
            counts[ord(ch) - ord("a")] += 1  # count letter
        groups[tuple(counts)].append(word)  # lists are unhashable -> use a tuple
    return list(groups.values())


def normalise(groups: List[List[str]]) -> List[List[str]]:
    """Sort inside and across groups so tests do not depend on order."""
    return sorted(sorted(g) for g in groups)


def main() -> None:
    words: List[str] = ["eat", "tea", "tan", "ate", "nat", "bat"]
    expected: List[List[str]] = [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
    assert normalise(group_anagrams_sorted(words)) == expected
    assert normalise(group_anagrams_count(words)) == expected
    assert group_anagrams_sorted([]) == []  # empty input
    assert group_anagrams_sorted([""]) == [[""]]  # empty string is its own group
    assert normalise(group_anagrams_sorted(["a", "a"])) == [["a", "a"]]  # duplicates kept
    print(group_anagrams_sorted(words))
    print("All group-anagrams tests passed")


if __name__ == "__main__":
    main()
