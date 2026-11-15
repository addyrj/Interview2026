# LRU Cache: OrderedDict version, hand-built doubly-linked-list version, TTL variant
from __future__ import annotations
import time
from collections import OrderedDict
from typing import Generic, Hashable, Optional, TypeVar

K = TypeVar("K", bound=Hashable)                  # key type
V = TypeVar("V")                                  # value type


class LRUCache(Generic[K, V]):
    """O(1) get/put using OrderedDict (most recent at the end)."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._cap = capacity
        self._data: OrderedDict[K, V] = OrderedDict()

    def get(self, key: K) -> Optional[V]:
        if key not in self._data:
            return None                           # miss
        self._data.move_to_end(key)               # mark as most recently used
        return self._data[key]

    def put(self, key: K, value: V) -> None:
        if key in self._data:
            self._data.move_to_end(key)           # refresh position
        self._data[key] = value
        if len(self._data) > self._cap:
            self._data.popitem(last=False)        # evict least recently used (front)


class _DNode:
    __slots__ = ("key", "val", "prev", "next")    # save memory per node

    def __init__(self, key: int = 0, val: int = 0) -> None:
        self.key, self.val = key, val
        self.prev: Optional[_DNode] = None
        self.next: Optional[_DNode] = None


class ManualLRU:
    """Same behaviour built from dict + doubly linked list (the classic interview answer)."""

    def __init__(self, capacity: int) -> None:
        self._cap = capacity
        self._map: dict[int, _DNode] = {}
        self._head, self._tail = _DNode(), _DNode()   # sentinels
        self._head.next, self._tail.prev = self._tail, self._head

    def _remove(self, n: _DNode) -> None:
        n.prev.next, n.next.prev = n.next, n.prev     # type: ignore[union-attr]

    def _add_front(self, n: _DNode) -> None:          # right after head = most recent
        n.next, n.prev = self._head.next, self._head
        self._head.next.prev = n                      # type: ignore[union-attr]
        self._head.next = n

    def get(self, key: int) -> int:
        n = self._map.get(key)
        if n is None:
            return -1
        self._remove(n); self._add_front(n)           # move to front
        return n.val

    def put(self, key: int, val: int) -> None:
        if key in self._map:
            self._remove(self._map[key])
        n = self._map[key] = _DNode(key, val)
        self._add_front(n)
        if len(self._map) > self._cap:
            lru = self._tail.prev                     # least recently used
            self._remove(lru)                         # type: ignore[arg-type]
            del self._map[lru.key]                    # type: ignore[union-attr]


class TTLCache(LRUCache[K, V]):
    """LRU plus expiry, like a Redis key with EXPIRE."""

    def __init__(self, capacity: int, ttl: float) -> None:
        super().__init__(capacity)
        self._ttl = ttl
        self._exp: dict[K, float] = {}

    def put(self, key: K, value: V) -> None:
        super().put(key, value)
        self._exp[key] = time.monotonic() + self._ttl

    def get(self, key: K) -> Optional[V]:
        if key in self._exp and time.monotonic() > self._exp[key]:
            self._data.pop(key, None); del self._exp[key]   # lazily expire
            return None
        return super().get(key)


if __name__ == "__main__":
    c: LRUCache[str, int] = LRUCache(2)
    c.put("a", 1); c.put("b", 2)
    assert c.get("a") == 1                        # a is now most recent
    c.put("c", 3)                                 # evicts b
    assert c.get("b") is None and c.get("c") == 3 and c.get("a") == 1

    m = ManualLRU(2)
    m.put(1, 1); m.put(2, 2)
    assert m.get(1) == 1
    m.put(3, 3)
    assert m.get(2) == -1 and m.get(3) == 3
    m.put(4, 4)
    assert m.get(1) == -1 and m.get(3) == 3 and m.get(4) == 4

    t: TTLCache[str, int] = TTLCache(2, ttl=0.05)
    t.put("x", 1)
    assert t.get("x") == 1
    time.sleep(0.08)
    assert t.get("x") is None
    print("all LRU tests passed")
