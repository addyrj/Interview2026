---

# Q270. Adapter Pattern
# Category: Design Patterns
# Difficulty: ⭐ Easy

---

## ❓ Question
Your app expects payment gateways with a `pay(amount_rupees: float) -> str` method. A third-party `StripeSDK` has `charge_paise(paise: int) -> dict`. Write an adapter so the app can use Stripe without changing either side.

---

## 💡 Quick Concept (2 lines only)
Adapter wraps an incompatible class and translates its interface into the one the client expects. Composition (wrap) is preferred over inheritance.
हिंदी: Adapter एक पुरानी/बाहरी class को wrap करके उसे उस interface जैसा बना देता है जो आपका code चाहता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Protocol  # Step 1: the target interface


class PaymentGateway(Protocol):  # what our app expects
    def pay(self, amount_rupees: float) -> str: ...  # returns a receipt id


class StripeSDK:  # Step 2: third-party class we cannot change
    def charge_paise(self, paise: int) -> dict:
        return {"id": f"ch_{paise}", "status": "ok"}  # fake SDK response


class StripeAdapter:  # Step 3: adapter implements PaymentGateway
    def __init__(self, sdk: StripeSDK) -> None:
        self._sdk = sdk  # wrap the adaptee (composition)

    def pay(self, amount_rupees: float) -> str:
        paise = round(amount_rupees * 100)  # Step 4: convert rupees -> paise
        resp = self._sdk.charge_paise(paise)  # call the incompatible API
        return resp["id"]  # convert dict result -> str receipt


def checkout(gw: PaymentGateway, amount: float) -> str:  # client code
    return gw.pay(amount)  # only knows pay()


# ============================================
# TEST CASES
# ============================================
gw = StripeAdapter(StripeSDK())  # wrap the SDK
print(checkout(gw, 12.5))  # Expected: ch_1250
print(checkout(gw, 0.1 + 0.2))  # Expected: ch_30  (round() avoids 30.000000000000004)
```

---

## 🔍 Why This Works (3 lines max)
The client depends only on the `pay()` shape. The adapter converts units and the return type, so neither the app nor the SDK changes. `round()` prevents float drift when converting to paise.
हिंदी: Client सिर्फ `pay()` जानता है; adapter units और return type बदलकर दोनों तरफ का code सुरक्षित रखता है।

---

## ⚡ Alternative Solution
```python
# Function adapter: wrap a callable to change its signature
from collections.abc import Callable  # type hint


def adapt(fn: Callable[[int], dict]) -> Callable[[float], str]:
    def pay(amount: float) -> str:  # new signature
        return fn(round(amount * 100))["id"]  # translate in and out
    return pay  # return adapted function


pay = adapt(lambda p: {"id": f"ch_{p}"})  # adapt a lambda "SDK"
print(pay(2.5))  # Expected: ch_250
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: int(amount * 100) truncates because of float error
print(int(0.29 * 100))  # Output: 28   <- one paisa lost!

# ✅ Correct: round() first
print(round(0.29 * 100))  # Output: 29
```

---

## 🎯 Interview Tip (1 line)
Say: "Adapter converts one interface to another so legacy or third-party code plugs in; I wrap with composition and keep the client unchanged."

---

## 🔗 Related Questions
→ Q262 (factory) | Q265 (decorator pattern) | Q266 (proxy)
