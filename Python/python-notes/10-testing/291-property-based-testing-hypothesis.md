---

# 291. Property Based Testing (Hypothesis)
# हिंदी में: Property Based Testing (Hypothesis से अपने-आप test data बनाना)

---

## 🔵 Simple Definition (English)
In normal tests you write fixed inputs and expected outputs. In property based testing you describe a rule that must always be true (a "property"), and the Hypothesis library generates hundreds of random and edge-case inputs to try to break that rule. When it finds a failure it shrinks the input to the smallest failing case.

## 🔵 सरल परिभाषा (Hindi)
Normal test में हम fixed input और expected output लिखते हैं। Property based testing में हम एक नियम (property) लिखते हैं जो हमेशा सही होना चाहिए, और Hypothesis library सैकड़ों random और edge-case inputs बनाकर उस नियम को तोड़ने की कोशिश करती है। Failure मिलने पर वह input को सबसे छोटे failing case तक shrink कर देती है।

---

## 🔴 Problem it Solves
Example based tests only check the cases the developer imagined: `add(2, 3) == 5`. Real bugs hide in cases nobody imagined: empty list, negative number, emoji in a string, huge integer, remainder paise when splitting a bill. Writing all those cases by hand is slow and always incomplete.

## 🔴 यह क्यों बना? (Hindi)
Example based tests सिर्फ वही cases check करते हैं जो developer ने सोचे थे, जैसे `add(2, 3) == 5`। असली bugs उन cases में छुपे होते हैं जो किसी ने सोचे ही नहीं: खाली list, negative number, string में emoji, बहुत बड़ा integer, bill बाँटते समय बचे हुए paise। इन सबको हाथ से लिखना धीमा और हमेशा अधूरा रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write a test and decorate it with @given(strategy, ...)
Step 2 → A strategy describes the data shape (integers, text, lists, builds(...))
Step 3 → Hypothesis generates many examples (default 100) incl. nasty edge cases
Step 4 → Your test body asserts a property (rule) for each example
Step 5 → On failure Hypothesis SHRINKS the input to the minimal failing example
Step 6 → It saves the failure in .hypothesis/ database and replays it next run
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप test लिखते हैं और उस पर @given(strategy, ...) लगाते हैं
Step 2 → Strategy data का आकार बताती है (integers, text, lists, builds(...))
Step 3 → Hypothesis कई examples (default 100) बनाता है, कठिन edge cases सहित
Step 4 → आपका test हर example पर एक property (नियम) assert करता है
Step 5 → Fail होने पर Hypothesis input को सबसे छोटे failing example तक SHRINK करता है
Step 6 → Failure .hypothesis/ database में save होती है और अगली run में फिर चलती है
```

---

## 🟡 Real World Example
Razorpay-style bill splitting: "sum of all shares must equal the total". Example tests with 100 / 3 pass, but Hypothesis quickly finds `total=1, people=2` where integer division loses a paisa. Other uses: `decode(encode(x)) == x` for JSON/serialisers, "sorting twice equals sorting once", and "any integer path param returns 200" for a FastAPI route.

## 🟡 Real Example Hindi mein
Razorpay जैसा bill splitting: "सबके shares का जोड़ total के बराबर होना चाहिए"। 100 / 3 वाले example test pass हो जाते हैं, पर Hypothesis जल्दी ही `total=1, people=2` ढूँढ लेता है जहाँ integer division से एक paisa गुम हो जाता है। और उपयोग: serializer के लिए `decode(encode(x)) == x`, "दो बार sort करना = एक बार sort करना", और FastAPI route के लिए "कोई भी integer path param 200 दे"।

---

## 💻 Code Example — Basic
```python
# Basic Hypothesis example (pip install hypothesis pytest)
from hypothesis import given, strategies as st  # given runs test many times, st makes data


def add(a: int, b: int) -> int:  # function under test
    return a + b  # simple addition


@given(st.integers(), st.integers())  # generate random int pairs
def test_add_commutative(a: int, b: int) -> None:  # property: order does not matter
    assert add(a, b) == add(b, a)  # must hold for every pair


@given(st.lists(st.integers()))  # generate random lists of ints
def test_sorted_is_ordered(xs: list[int]) -> None:  # property of sorted()
    out = sorted(xs)  # sort the list
    assert all(x <= y for x, y in zip(out, out[1:]))  # every neighbour is ordered
    assert len(out) == len(xs)  # no item was lost


@given(st.text())  # random unicode strings (emoji, empty, etc.)
def test_upper_twice(s: str) -> None:  # idempotent check
    assert s.upper().upper() == s.upper()  # upper twice == upper once


if __name__ == "__main__":  # run directly with python
    test_add_commutative()  # decorated test can be called with no args
    test_sorted_is_ordered()  # runs ~100 generated examples
    test_upper_twice()  # runs ~100 generated examples
    print("all properties held")  # success message
# Output: all properties held
# Also: pytest -q basic.py  ->  3 passed (time varies)
```

## 💻 Code Example — Advanced
```python
# Production style: round trip + custom strategy + a real bug found + settings
import json  # serialisation
from dataclasses import dataclass  # domain object
from hypothesis import given, settings, strategies as st  # core API


@dataclass(frozen=True)  # immutable so it is comparable and hashable
class Order:  # an order in an e-commerce service
    order_id: int  # unique id
    items: tuple[str, ...]  # item names
    amount_paise: int  # money as integer paise (never float)


def encode(o: Order) -> str:  # serialise to JSON string
    return json.dumps({"order_id": o.order_id, "items": list(o.items), "amount_paise": o.amount_paise})


def decode(s: str) -> Order:  # parse back to Order
    d = json.loads(s)  # JSON -> dict
    return Order(d["order_id"], tuple(d["items"]), d["amount_paise"])  # dict -> Order


orders = st.builds(  # custom strategy that builds valid Orders
    Order,  # class to construct
    order_id=st.integers(min_value=1, max_value=10**9),  # realistic ids
    items=st.lists(st.text(min_size=1, max_size=20), max_size=5).map(tuple),  # list -> tuple
    amount_paise=st.integers(min_value=0, max_value=10**7),  # non-negative money
)


@settings(max_examples=200, deadline=None)  # 200 cases, no per-example time limit
@given(orders)  # feed generated Orders
def test_round_trip(o: Order) -> None:  # property: decode(encode(x)) == x
    assert decode(encode(o)) == o  # must always be equal


def split_bill(total: int, people: int) -> list[int]:  # BUGGY on purpose
    share = total // people  # integer division drops the remainder
    return [share] * people  # shares no longer add up to total


@given(st.integers(0, 10**6), st.integers(1, 20))  # any total, 1..20 people
def test_split_sums(total: int, people: int) -> None:  # property: shares sum to total
    assert sum(split_bill(total, people)) == total  # fails for total=1, people=2


if __name__ == "__main__":  # run directly
    test_round_trip()  # passes
    print("round trip ok")  # report
    try:  # expect Hypothesis to find the bug
        test_split_sums()  # raises AssertionError with a falsifying example
    except AssertionError:  # caught here for the demo
        print("bug found by hypothesis")  # report
# Output:
# round trip ok
# bug found by hypothesis
# Hypothesis's own report (stderr) shows the shrunk case: total=1, people=2
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: Hypothesis
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_reverse_twice(xs: list[int]) -> None:
    assert list(reversed(list(reversed(xs)))) == xs
```

```javascript
// JavaScript: fast-check (the closest library)
import fc from "fast-check";

test("reverse twice", () => {
  fc.assert(
    fc.property(fc.array(fc.integer()), (xs) => {
      expect([...xs].reverse().reverse()).toEqual(xs);
    })
  );
});
```

Key differences: both libraries do the same idea (generate, check, shrink). Hypothesis is a decorator (`@given`) and keeps a failure database on disk; fast-check uses `fc.assert(fc.property(...))` and prints a seed to replay.

---

## 🟠 FastAPI Connection
Use Hypothesis to fuzz routes: any valid integer in a path should return 200, and any invalid input should return 422, never 500. Combine with `TestClient`. Note: with Starlette 1.x the `TestClient` prints a deprecation warning about `httpx`; it still works (verified here with FastAPI 0.162).

```python
# FastAPI + Hypothesis (pip install fastapi httpx hypothesis)
from fastapi import FastAPI  # web framework
from fastapi.testclient import TestClient  # in-process client
from hypothesis import given, strategies as st  # property testing

app: FastAPI = FastAPI()  # create app


@app.get("/items/{item_id}")  # path with typed param
def get_item(item_id: int) -> dict[str, int]:  # int validated by FastAPI
    return {"item_id": item_id}  # echo it


client: TestClient = TestClient(app)  # client


@given(st.integers(min_value=-10**6, max_value=10**6))  # many ints
def test_any_int(n: int) -> None:  # property: always 200 and echoes
    r = client.get(f"/items/{n}")  # call endpoint
    assert r.status_code == 200 and r.json() == {"item_id": n}  # check


test_any_int()  # run the property
print("fastapi ok")  # Output: fastapi ok
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Re-implementing the function inside the test
```python
# Wrong - the test just copies the code, so it can never disagree
@given(st.integers(), st.integers())
def test_add(a, b):
    assert add(a, b) == a + b   # same logic as the function

# Right - test a PROPERTY (commutative, associative, identity)
@given(st.integers())
def test_add_zero(a):
    assert add(a, 0) == a
```

❌ Mistake 2: Flaky tests from `deadline` or hidden randomness
```python
# Wrong - slow first call fails with DeadlineExceeded / uses random.random() inside
# Right - set @settings(deadline=None) for slow code, and avoid random/time in the test
```

❌ Mistake 3: Using `assume()` to throw away most inputs
```python
# Wrong - Hypothesis gives up (FailedHealthCheck) when most examples are rejected
@given(st.integers())
def test_x(n):
    assume(n % 1000 == 0)

# Right - build the right data directly
@given(st.integers().map(lambda n: n * 1000))
def test_x(n): ...
```

---

## 🧠 Tricky Interview Question

**Q**: Why does Hypothesis report `total=1, people=2` and not the first random failure it found?

```python
@given(st.integers(0, 10**6), st.integers(1, 20))
def test_split_sums(total, people):
    assert sum([total // people] * people) == total
```

**Answer**:
Hypothesis found some big failing pair first (for example `total=912345, people=7`), then it SHRANK it: it keeps trying smaller values that still fail. The smallest failing input is `total=1, people=2` (1 // 2 = 0, sum = 0 != 1). Shrinking makes the bug report easy to understand. The failing case is also stored in `.hypothesis/examples` and re-run first next time, so the bug does not "disappear".

---

## ⚫ Interview Questions + Answers

Q1: What is a property in property based testing?
A1: A rule that must hold for all valid inputs, such as `decode(encode(x)) == x`, "output is sorted", or "applying twice equals once" (idempotence).

Q2: What is shrinking?
A2: After a failure, Hypothesis simplifies the failing input step by step (smaller numbers, shorter lists) while it still fails, and reports the minimal one.

Q3: Does Hypothesis replace normal unit tests?
A3: No. Use both. Example tests document specific business cases (`GST 18% on 100 = 118`); property tests explore the unknown. Use `@example(...)` to keep important fixed cases inside a property test.

Q4: How do you make tests reproducible?
A4: Hypothesis stores failures in a local database and prints `@reproduce_failure` / seed info. In CI use `@settings(derandomize=True)` or a profile with a fixed seed.

Q5: What are common properties to test?
A5: Round trip, idempotence, invariants (length preserved), commutativity, "oracle" comparison against a slow-but-simple implementation, and "never raises an unexpected exception".

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You have parsers, serialisers, validators, money maths, sorting or encoding code
- You want to find edge cases (empty, unicode, huge numbers) automatically
- You can state a rule about the output instead of one exact value

❌ Avoid when:
- The test needs a slow network/database call per example (100 examples = 100 calls)
- No clear property exists (pure UI text, one fixed business rule)
- You cannot make the code deterministic

---

## 📊 Visual Diagram

```
@given(strategy)
     │
     ▼
 generate 100 inputs ──► run test body ──► all pass ──► ✅ done
                              │
                              ▼ one fails
                        shrink input (smaller & smaller)
                              │
                              ▼
                 report minimal case: total=1, people=2
                 save to .hypothesis/ and replay next run
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Property | Rule true for all inputs | ऐसा नियम जो हर input पर सही हो |
| Strategy | Recipe to generate data | data बनाने की विधि |
| Shrinking | Reduce to smallest failing input | failing input को छोटा करना |
| Idempotent | Doing twice = doing once | दो बार करना = एक बार करना |
| Round trip | Encode then decode returns original | encode-decode के बाद वही data |
| Falsifying example | Input that breaks the property | वह input जो नियम तोड़ दे |

---

## ⚡ 3-Line Summary
English: Property based testing checks rules, not single examples. Hypothesis generates many inputs with `@given` and strategies, then shrinks any failure to a minimal case. Use it for parsers, money, serialisers and API fuzzing, next to normal unit tests.
Hindi: Property based testing single example नहीं, बल्कि नियम check करती है। Hypothesis `@given` और strategies से कई inputs बनाता है और failure को सबसे छोटे case तक shrink करता है। Parsers, पैसे के हिसाब, serializers और API fuzzing के लिए normal unit tests के साथ इस्तेमाल करें।

---

## ➡️ Next Topic
**292. Performance Testing (locust)** — simulate thousands of users hitting your API.
