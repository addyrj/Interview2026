"""467. Count Word Frequency (run: python3 main.py)."""
import re  # tokenizing
from collections import Counter, defaultdict  # counting helpers
from typing import Dict, List, Tuple  # type hints


def tokenize(text: str) -> List[str]:
    """Lowercase words; keep apostrophes (don't) but drop other punctuation."""
    return re.findall(r"[a-z0-9']+", text.lower())  # list of words


def count_manual(words: List[str]) -> Dict[str, int]:
    """Plain dict version (what interviewers expect first)."""
    freq: Dict[str, int] = {}  # word -> count
    for w in words:  # each word
        freq[w] = freq.get(w, 0) + 1  # default 0 then add 1
    return freq  # result


def count_defaultdict(words: List[str]) -> Dict[str, int]:
    """defaultdict(int) version."""
    freq: Dict[str, int] = defaultdict(int)  # missing key -> 0
    for w in words:  # each word
        freq[w] += 1  # no KeyError
    return dict(freq)  # plain dict


def top_n(text: str, n: int) -> List[Tuple[str, int]]:
    """Top n words; ties keep first-seen order (Counter.most_common is stable)."""
    return Counter(tokenize(text)).most_common(n)  # sorted by count desc


if __name__ == "__main__":
    text = "The cat and the hat. The cat's hat, the END!"  # sample
    words = tokenize(text)  # tokens
    print(words)  # token list
    print(count_manual(words))  # dict counts
    print(top_n(text, 2))  # [('the', 4), ('hat', 2)]
    assert tokenize("Hello, hello!") == ["hello", "hello"]  # case + punctuation
    assert count_manual(words) == count_defaultdict(words) == dict(Counter(words))  # all agree
    assert count_manual([]) == {}  # empty
    assert top_n("a b b c c c", 2) == [("c", 3), ("b", 2)]  # ordering
    assert top_n("", 3) == []  # empty text
    print("all tests passed")
