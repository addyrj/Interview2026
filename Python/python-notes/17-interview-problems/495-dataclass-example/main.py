"""Dataclass Example: defaults, field(), frozen, slots, __post_init__, ordering, asdict. Python 3.10+."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone


@dataclass(order=True, slots=True)
class Product:
    price: float
    name: str = field(compare=False)  # order only by price
    tags: list[str] = field(default_factory=list, compare=False)  # NEVER tags=[]
    sku: str = field(init=False, default="", compare=False, repr=False)

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError("price must be >= 0")
        self.sku = self.name.upper().replace(" ", "-")  # derived field


@dataclass(frozen=True, slots=True)
class Money:
    amount: int  # paise
    currency: str = "INR"

    def __add__(self, other: "Money") -> "Money":
        if other.currency != self.currency:
            raise ValueError("currency mismatch")
        return Money(self.amount + other.amount, self.currency)


@dataclass
class Order:
    id: int
    items: list[Product] = field(default_factory=list)
    created: datetime = field(default_factory=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc))

    @property
    def total(self) -> float:
        return sum(p.price for p in self.items)


if __name__ == "__main__":
    a, b = Product(99.0, "Mouse pad"), Product(499.0, "Keyboard", ["usb"])
    print(a, a.sku)
    print(a < b, sorted([b, a])[0].name)
    o = Order(1, [a, b])
    print(o.total, asdict(o)["items"][1]["name"])
    m = Money(500) + Money(250)
    print(m)
    try:
        m.amount = 1  # type: ignore[misc]
    except Exception as e:
        print(type(e).__name__)
    print(replace(a, price=79.0).price, a.price)  # replace makes a modified copy
    print({m: "hashable because frozen"}[Money(750)])
    try:
        Product(-1, "x")
    except ValueError as e:
        print("ValueError:", e)
    assert Order(2).items is not Order(3).items  # default_factory gives separate lists
    print("all ok")
