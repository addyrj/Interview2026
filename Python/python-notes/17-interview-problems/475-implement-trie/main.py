# Trie (prefix tree): insert, search, starts_with, autocomplete, delete
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class TrieNode:
    children: dict[str, "TrieNode"] = field(default_factory=dict)   # char -> child
    is_end: bool = False                          # True if a word ends here


class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()                    # empty root

    def insert(self, word: str) -> None:          # O(L)
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())   # create path as needed
        node.is_end = True                        # mark the end of a word

    def _walk(self, s: str) -> TrieNode | None:   # follow s, or None if path breaks
        node = self.root
        for ch in s:
            nxt = node.children.get(ch)
            if nxt is None:
                return None
            node = nxt
        return node

    def search(self, word: str) -> bool:          # exact word?
        n = self._walk(word)
        return n is not None and n.is_end

    def starts_with(self, prefix: str) -> bool:   # any word with this prefix?
        return self._walk(prefix) is not None

    def autocomplete(self, prefix: str, limit: int = 5) -> list[str]:
        start = self._walk(prefix)
        out: list[str] = []
        if start is None:
            return out
        stack: list[tuple[TrieNode, str]] = [(start, prefix)]
        while stack and len(out) < limit:         # DFS, alphabetical via sorted
            node, path = stack.pop()
            if node.is_end:
                out.append(path)
            for ch in sorted(node.children, reverse=True):   # reversed -> pop gives smallest
                stack.append((node.children[ch], path + ch))
        return out

    def delete(self, word: str) -> bool:
        def rec(node: TrieNode, i: int) -> bool:  # returns True if child can be pruned
            if i == len(word):
                if not node.is_end:
                    return False
                node.is_end = False
                return not node.children
            ch = word[i]
            child = node.children.get(ch)
            if child is None:
                return False
            if rec(child, i + 1):
                del node.children[ch]             # prune dead branch
                return not node.is_end and not node.children
            return False
        if not self.search(word):
            return False
        rec(self.root, 0)
        return True


if __name__ == "__main__":
    t = Trie()
    for w in ["car", "card", "care", "cat", "dog"]:
        t.insert(w)
    assert t.search("car") and not t.search("ca")
    assert t.starts_with("ca") and not t.starts_with("cx")
    assert t.autocomplete("car") == ["car", "card", "care"]
    assert t.autocomplete("ca", limit=2) == ["car", "card"]
    assert t.delete("card") and not t.search("card") and t.search("car")
    assert not t.delete("zzz")
    print("all trie tests passed")
