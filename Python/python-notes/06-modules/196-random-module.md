---

# 196. random Module
# हिंदी में: random Module (random numbers, shuffle और sampling)

---

## 🔵 Simple Definition (English)
`random` generates pseudo-random numbers and makes random choices: a float, an integer in a range, a random item from a list, a shuffled list, or a sample. "Pseudo" means it follows a formula (Mersenne Twister) starting from a seed, so it looks random but is predictable. It is NOT safe for passwords, OTPs or tokens (use `secrets`).

## 🔵 सरल परिभाषा (Hindi)
`random` pseudo-random numbers बनाता है और random चुनाव करता है: float, range में integer, list से random item, shuffled list या sample। "Pseudo" का मतलब है कि यह एक formula (Mersenne Twister) से seed से शुरू होकर चलता है, इसलिए random दिखता है पर अनुमान लगाया जा सकता है। Passwords, OTP या tokens के लिए यह सुरक्षित नहीं है (`secrets` इस्तेमाल करें)।

---

## 🔴 Problem it Solves
Programs need unpredictability for simulations, games, sampling test data, A/B tests, load balancing and retry jitter. Writing your own generator is hard and gives biased results. `random` provides a well-tested generator and handy tools (`choice`, `sample`, `shuffle`, `gauss`) and a seed so experiments can be repeated exactly.

## 🔴 यह क्यों बना? (Hindi)
Simulations, games, test data sampling, A/B tests, load balancing और retry jitter के लिए अनिश्चितता चाहिए। अपना generator लिखना कठिन है और नतीजे biased होते हैं। `random` एक tested generator और काम के tools (`choice`, `sample`, `shuffle`, `gauss`) देता है, और seed से experiments हू-ब-हू दोहराए जा सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A hidden generator object holds an internal state (Mersenne Twister)
Step 2 → seed(x) sets that state; same seed → same sequence forever
Step 3 → No seed → Python seeds from the OS (urandom) at import time
Step 4 → random() gives floats in [0, 1); other functions are built on top of it
Step 5 → Module level functions share one global generator (not thread-isolated state you control)
Step 6 → random.Random(seed) makes your own independent generator (best for tests)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक छिपा generator object internal state (Mersenne Twister) रखता है
Step 2 → seed(x) उस state को तय करता है; वही seed → हमेशा वही sequence
Step 3 → seed न दें तो import के समय Python OS (urandom) से seed लेता है
Step 4 → random() [0, 1) में float देता है; बाकी functions इसी पर बने हैं
Step 5 → Module level functions एक साझा global generator इस्तेमाल करते हैं
Step 6 → random.Random(seed) अपना independent generator बनाता है (tests के लिए सबसे अच्छा)
```

---

## 🟡 Real World Example
A Swiggy A/B test uses a stable hash of the user id (not `random`) to pick a variant. A Razorpay client adds random jitter to retry delays so thousands of retries do not hit the server together. A data scientist splits a dataset with a seeded `Random` so results are reproducible. A game or quiz app picks a random question. OTPs and API keys use `secrets`, never `random`.

## 🟡 Real Example Hindi mein
Swiggy का A/B test variant चुनने के लिए user id का stable hash इस्तेमाल करता है (`random` नहीं)। Razorpay client retry delays में random jitter जोड़ता है ताकि हज़ारों retries एक साथ server पर न गिरें। Data scientist seeded `Random` से dataset बाँटता है ताकि नतीजे दोहराए जा सकें। Game या quiz app random question चुनती है। OTP और API keys के लिए `secrets` लें, `random` कभी नहीं।

---

## 💻 Code Example — Basic
```python
# Basic random examples - every line commented
# Seeded so the output is repeatable (values below are from Python 3.13)
import random  # pseudo-random numbers

random.seed(42)  # fix the starting point -> same sequence every run
print(random.random())  # float in [0.0, 1.0)
print(random.randint(1, 6))  # int in [1, 6] BOTH ends included (like a dice)
print(random.randrange(0, 10, 2))  # like range(): 0, 2, 4, 6 or 8 (10 excluded)
print(round(random.uniform(1.5, 3.5), 4))  # float between two numbers

items = ["red", "green", "blue", "yellow"]  # sample list
print(random.choice(items))  # one random element
print(random.choices(items, k=3))  # k picks WITH replacement (repeats possible)
print(random.sample(items, k=2))  # k picks WITHOUT replacement (all different)

deck = list(range(1, 8))  # numbers 1..7
random.shuffle(deck)  # shuffles IN PLACE and returns None
print(deck)  # shuffled list

print(random.choices(["A", "B"], weights=[90, 10], k=10))  # weighted choice (about 90% A)
print(round(random.gauss(0, 1), 4))  # normal distribution: mean 0, std dev 1

random.seed(42)  # same seed again ...
print(random.random())  # ... gives the SAME first number as before

rng = random.Random(7)  # independent generator object (does not touch the global one)
print(rng.randint(1, 100), rng.randint(1, 100))  # reproducible per generator
print(len(random.randbytes(4)))  # 4 random bytes (3.9+)
```

Output (verified by running; ids/timestamps/paths may vary):
```
0.6394267984578837
1
4
1.9898
green
['blue', 'blue', 'yellow']
['red', 'blue']
[2, 3, 7, 5, 6, 1, 4]
['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A']
-0.292
0.6394267984578837
42 20
4
```

## 💻 Code Example — Advanced
```python
# Production style: secure tokens, reproducible tests, weighted sampling, jitter, A/B buckets
import hashlib  # stable hashing for A/B buckets
import random  # pseudo-random
import secrets  # cryptographically secure random
import string  # character sets
from typing import List, Sequence, TypeVar  # type hints

T = TypeVar("T")  # generic item type


def make_otp(digits: int = 6) -> str:
    """OTP must be unpredictable -> secrets, NOT random."""
    return "".join(secrets.choice(string.digits) for _ in range(digits))  # CSPRNG digits


def make_token(nbytes: int = 16) -> str:
    """URL safe API/session token."""
    return secrets.token_urlsafe(nbytes)  # secure random string


otp = make_otp()  # sample OTP
print(len(otp), otp.isdigit(), len(make_token()) >= 20, len(secrets.token_hex(8)))  # 6 True True 16
print(secrets.compare_digest("abc", "abc"))  # constant-time comparison for secrets


def backoff_delay(attempt: int, base: float = 0.5, cap: float = 30.0, rng: random.Random = random.Random()) -> float:
    """Exponential backoff with full jitter (avoids thundering herd)."""
    return rng.uniform(0, min(cap, base * 2 ** attempt))  # random wait up to the limit


r = random.Random(1)  # reproducible generator for the demo
print([round(backoff_delay(a, rng=r), 3) for a in range(5)])  # growing upper bounds


def bucket(user_id: str, experiment: str, buckets: int = 100) -> int:
    """Stable A/B bucket: same user -> same bucket on every machine and every restart."""
    h = hashlib.sha256(f"{experiment}:{user_id}".encode()).hexdigest()  # deterministic hash
    return int(h, 16) % buckets  # 0..99


print(bucket("user-42", "new-checkout"), bucket("user-42", "new-checkout"))  # same twice
print("variant B" if bucket("user-42", "new-checkout") < 20 else "control")  # 20% rollout


def pick_server(servers: Sequence[T], weights: Sequence[float], rng: random.Random) -> T:
    """Weighted load balancing."""
    return rng.choices(servers, weights=weights, k=1)[0]  # one weighted pick


rng = random.Random(0)  # fixed for the demo
counts = {"a": 0, "b": 0, "c": 0}  # tally
for _ in range(10_000):  # many picks
    counts[pick_server(["a", "b", "c"], [70, 20, 10], rng)] += 1  # count each
print({k: round(v / 10_000, 1) for k, v in counts.items()})  # about 0.7 / 0.2 / 0.1


def shuffled(items: Sequence[T], seed: int) -> List[T]:
    """Return a shuffled COPY; never mutate the caller's list."""
    out: List[T] = list(items)  # copy
    random.Random(seed).shuffle(out)  # local generator, no global state
    return out  # result


data = [1, 2, 3, 4, 5]  # original
print(shuffled(data, 5) == shuffled(data, 5), data)  # True and original untouched

try:  # sample larger than population
    random.sample([1, 2, 3], k=5)  # impossible without replacement
except ValueError as exc:  # expected
    print("ValueError:", exc)  # message
try:  # sample from a set (removed in 3.11)
    random.sample({1, 2, 3}, k=2)  # sets are not sequences
except TypeError as exc:  # expected
    print("TypeError:", exc)  # message
print(random.sample(sorted({1, 2, 3}), k=2) is not None)  # fix: convert to a sequence first
print(random.Random(3).binomialvariate(10, 0.5) in range(11))  # 3.12+: coin flips count
```

Output (verified by running; ids/timestamps/paths may vary):
```
6 True True 16
True
[0.067, 0.847, 1.528, 1.02, 3.963]
81 81
control
{'a': 0.7, 'b': 0.2, 'c': 0.1}
True [1, 2, 3, 4, 5]
ValueError: Sample larger than population or is negative
TypeError: Population must be a sequence.  For dicts or sets, use sorted(d).
True
True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import random
random.random()                    # float in [0, 1)
random.randint(1, 6)               # 1..6 inclusive
random.choice(["a", "b", "c"])     # random item
random.shuffle(lst)                # in place
random.seed(42)                    # reproducible
```

```javascript
// JavaScript
Math.random();                                         // float in [0, 1), cannot be seeded
Math.floor(Math.random() * 6) + 1;                     // 1..6 inclusive
arr[Math.floor(Math.random() * arr.length)];           // random item
// shuffle: Fisher-Yates by hand, or lodash _.shuffle
crypto.getRandomValues(new Uint32Array(1));            // secure (like Python secrets)
```

Key differences: Python has ready-made `randint`, `choice`, `sample`, `shuffle` and a seed; JavaScript's `Math.random` has only the basic float and can't be seeded. Python's `randint(a, b)` includes both ends. JS `crypto.getRandomValues` is the counterpart of `secrets`.

---

## 🟠 FastAPI Connection
FastAPI services use `random` for non-sensitive things: sampling a subset for monitoring, jitter in retries, demo data and shuffling quiz questions. Anything security related (OTP, reset links, session ids, API keys) must use `secrets`. Seeded `random.Random` instances make pytest tests deterministic.

```python
# FastAPI: OTP and tokens with secrets, random pick for a demo (pip install fastapi httpx)
import random  # non-security randomness
import secrets  # security randomness
from typing import Dict  # type hints
from fastapi import FastAPI  # app

app: FastAPI = FastAPI()  # create app
TIPS = ["Drink water", "Use type hints", "Write tests"]  # harmless content


@app.post("/otp")  # POST /otp  (sends OTP by SMS in real life)
def otp() -> Dict[str, int]:
    code: str = "".join(secrets.choice("0123456789") for _ in range(6))  # secure OTP
    return {"digits": len(code)}  # never return the OTP in the response!


@app.get("/tip")  # GET /tip
def tip() -> Dict[str, str]:
    return {"tip": random.choice(TIPS)}  # random is fine for non-security use
```

Output (verified by running; ids/timestamps/paths may vary):
```
{'digits': 6} True
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `random` for security
```python
# Wrong - Mersenne Twister is predictable after seeing ~624 outputs
# otp = str(random.randint(100000, 999999))

# Correct
# otp = "".join(secrets.choice("0123456789") for _ in range(6))
# token = secrets.token_urlsafe(32)
```

❌ Mistake 2: `shuffle` returns None, and `randint` bounds
```python
# Wrong - x becomes None
# x = random.shuffle(items)
# random.randint(0, len(items))      # IndexError possible: upper bound is INCLUDED

# Correct
# random.shuffle(items)                       # in place
# shuffled = random.sample(items, k=len(items))   # new list
# random.randrange(len(items))                # upper bound excluded
```

❌ Mistake 3: Seeding the global generator in library or request code
```python
# Wrong - makes every caller in the process predictable and breaks other code
# random.seed(42)    # inside a function used by a web server

# Correct - own generator
# rng = random.Random(42)
# rng.choice(items)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import random
random.seed(1); a = [random.randint(1, 10) for _ in range(3)]
random.seed(1); b = [random.randint(1, 10) for _ in range(3)]
print(a == b)
x = [1, 2, 3]
print(random.shuffle(x), sorted(x))
print(len(random.choices([1, 2, 3], k=5)), len(set(random.sample(range(10), 10))))
print(random.sample({1, 2, 3}, k=2))
```

**Answer**:
```
True
None [1, 2, 3]
5 10
TypeError: Population must be a sequence.  For dicts or sets, use sorted(d).
```
The same seed gives the same sequence. `shuffle` works in place and returns `None`. `choices` samples with replacement (so `k` can exceed the list length), while `sample` of the full range without replacement gives 10 distinct values. Sampling from a set raises `TypeError` since Python 3.11 (older versions deprecated it); convert with `sorted(...)` or `list(...)` first. (Verified by running; the last line raises, so the program stops there.)

---

## ⚫ Interview Questions + Answers

Q1: Is `random` truly random?
A1: No. It is a deterministic pseudo-random generator (Mersenne Twister, period 2^19937−1). Fine for simulations, not for security.

Q2: `random` vs `secrets`?
A2: `secrets` uses the OS secure source (`os.urandom`), so values cannot be predicted. Use it for passwords, OTPs, tokens, salts. Use `random` for everything else.

Q3: `choice` vs `choices` vs `sample`?
A3: `choice` returns one item. `choices` returns `k` items WITH replacement and supports `weights`. `sample` returns `k` DISTINCT items (without replacement) and raises `ValueError` if `k` is larger than the population.

Q4: How do you make tests with random data repeatable?
A4: Create `rng = random.Random(seed)` and pass it into your function, or call `random.seed(...)` in the test setup. Prefer the injected `Random` object because it does not disturb global state.

Q5: Is `random` thread-safe?
A5: The module level functions are safe to call from several threads (each call is atomic enough), but the sequence each thread sees depends on scheduling. For reproducibility give each thread its own `Random`. For multiprocessing, seed each worker differently.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Simulations, games, quizzes, sampling
- Test data and reproducible experiments with a seed
- Retry jitter and load balancing

❌ Avoid when:
- Passwords, OTPs, tokens, salts, encryption keys (use `secrets`)
- Lotteries or anything where predictability costs money
- Large numeric arrays (use `numpy.random.default_rng`)

---

## 📊 Visual Diagram

```
seed(42) ──► [ Mersenne Twister state ] ──► 0.639 ─► 0.025 ─► 0.275 ...
                    ▲                         same seed = same list every run
                    └── no seed: from OS entropy

random()      0 ──────────────────── 1   float [0,1)
randint(1,6)  1 2 3 4 5 6                 both ends included
randrange(6)  0 1 2 3 4 5                 upper end excluded
secrets.*     ► OS secure random ► unpredictable (use for security)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pseudo-random | Looks random, formula based | नकली-random (formula से) |
| Seed | Starting value of the generator | generator की शुरुआती value |
| With replacement | An item can be picked again | चुना हुआ दोबारा चुना जा सकता है |
| CSPRNG | Cryptographically secure generator | सुरक्षित random generator |
| Jitter | Random delay added on purpose | जानबूझकर जोड़ा random delay |
| Entropy | Real unpredictability from the OS | असली अनिश्चितता |

---

## ⚡ 3-Line Summary
English: `random` is a fast, seedable, pseudo-random toolkit (`random`, `randint`, `choice`, `sample`, `shuffle`). Use your own `random.Random(seed)` for repeatable tests and `secrets` for anything security related.
Hindi: `random` तेज़, seed होने वाला pseudo-random toolkit है (`random`, `randint`, `choice`, `sample`, `shuffle`)। दोहराए जाने वाले tests के लिए अपना `random.Random(seed)` और security वाली हर चीज़ के लिए `secrets` इस्तेमाल करें।

---

## ➡️ Next Topic
**197. hashlib Module** — turn data into fixed-size fingerprints (hashes) for checksums and passwords.
