---

# 030. Bitwise Operators
# हिंदी में: Bitwise Operators — bits पर काम करने वाले operators

---

## 🔵 Simple Definition (English)
Bitwise operators work on the individual **bits** (0s and 1s) of integers: `&` AND, `|` OR, `^` XOR, `~` NOT (invert), `<<` left shift, `>>` right shift. They are used for flags, permissions, masks, fast maths, and low-level data handling.

## 🔵 सरल परिभाषा (Hindi)
Bitwise operators integers के अलग-अलग **bits** (0 और 1) पर काम करते हैं: `&` AND, `|` OR, `^` XOR, `~` NOT (उलटना), `<<` left shift, `>>` right shift। इनका use flags, permissions, masks, तेज़ गणित और low-level data में होता है।

---

## 🔴 Problem it Solves
Sometimes you need to store many yes/no options in one number (read, write, delete permissions in one integer), pack data tightly (network protocols, IP addresses, colors), or do very fast power-of-two maths. Using separate booleans wastes memory and is slow to transfer. Bit operations do these jobs with a single CPU instruction.

## 🔴 यह क्यों बना? (Hindi)
कई बार बहुत सारे हाँ/ना options को एक ही number में रखना होता है (read, write, delete permissions एक integer में), data को compact pack करना होता है (network protocols, IP address, colors), या 2 की powers वाला गणित तेज़ करना होता है। अलग-अलग booleans memory बर्बाद करते हैं। Bit operations यह काम एक CPU instruction में कर देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python converts each integer to binary:   10 = 1010,   6 = 0110
Step 2 → Operator is applied bit by bit (column by column):
             1010
           & 0110        &  → 1 only if BOTH bits are 1  → 0010 (2)
           | 0110        |  → 1 if ANY bit is 1          → 1110 (14)
           ^ 0110        ^  → 1 if bits are DIFFERENT    → 1100 (12)
Step 3 → ~x  inverts every bit; for Python ints  ~x == -x - 1
Step 4 → x << n  shifts bits left (x * 2**n);  x >> n  shifts right (x // 2**n)
Step 5 → Result is a normal Python int (arbitrary size, negatives act like
         infinite two's complement)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर integer binary बनता है:  10 = 1010,  6 = 0110
Step 2 → Operator हर bit-column पर लगता है:
         &  → दोनों 1 हों तभी 1      → 0010 (2)
         |  → कोई भी 1 हो तो 1      → 1110 (14)
         ^  → bits अलग हों तो 1      → 1100 (12)
Step 3 → ~x सब bits उलट देता है; Python में ~x == -x - 1
Step 4 → x << n = x * 2**n,   x >> n = x // 2**n
Step 5 → Result सामान्य Python int होता है
```

---

## 🟡 Real World Example
Unix file permissions (`chmod 755`) are bit flags: read=4, write=2, execute=1. A SaaS app stores user permissions in one integer: `READ | WRITE`. IP networking uses masks: `ip & netmask` gives the network address. Feature flags, bloom filters, Redis bitmaps ("which users were active today") and checksums use bits too. In interviews: "find the single number that appears once" is solved with XOR.

## 🟡 Real Example Hindi mein
Unix file permissions (`chmod 755`) असल में bit flags हैं: read=4, write=2, execute=1। SaaS app user permissions एक integer में रखती है: `READ | WRITE`। IP networking में `ip & netmask` से network address मिलता है। Feature flags, bloom filters, Redis bitmaps ("आज कौन active था") और checksums भी bits use करते हैं। Interview में "वह अकेला number ढूँढो जो एक बार आया" XOR से हल होता है।

---

## 💻 Code Example — Basic
```python
# Bitwise operators basics

a: int = 10                           # binary 1010
b: int = 6                            # binary 0110

# See the binary form
print(bin(a), bin(b))                 # Output: 0b1010 0b110
print(format(a, "04b"))               # Output: 1010   (padded to 4 digits)

# AND: 1 only where both have 1
print(a & b)                          # Output: 2     (0010)

# OR: 1 where either has 1
print(a | b)                          # Output: 14    (1110)

# XOR: 1 where bits differ
print(a ^ b)                          # Output: 12    (1100)

# NOT: flips all bits; for Python ints ~x == -x - 1
print(~a)                             # Output: -11

# Left shift: multiply by 2**n
print(a << 1, a << 3)                 # Output: 20 80

# Right shift: floor-divide by 2**n
print(a >> 1, a >> 2)                 # Output: 5 2

# Check if a number is even or odd (last bit)
n: int = 7
print("odd" if n & 1 else "even")     # Output: odd

# Power of two check: only one bit is set
x: int = 16
print(x > 0 and x & (x - 1) == 0)     # Output: True

# Swap two numbers without a temp variable using XOR
p, q = 5, 9
p ^= q                                # p = p xor q
q ^= p                                # q = original p
p ^= q                                # p = original q
print(p, q)                           # Output: 9 5

# Hex and octal literals are just different ways to write ints
print(0b1010, 0o12, 0xA)              # Output: 10 10 10
```

## 💻 Code Example — Advanced
```python
# Advanced: permission flags with IntFlag, masks, bit counting, XOR trick
from enum import IntFlag                 # flags that behave like ints


class Perm(IntFlag):
    """Permissions stored as bits."""

    NONE = 0                             # no permission
    READ = 1                             # 0001
    WRITE = 2                            # 0010
    DELETE = 4                           # 0100
    ADMIN = 8                            # 1000
    EDITOR = READ | WRITE                # combined role


def can(user_perm: Perm, needed: Perm) -> bool:
    """True only if ALL needed bits are present."""
    return (user_perm & needed) == needed      # mask then compare


def grant(user_perm: Perm, extra: Perm) -> Perm:
    """Turn bits ON."""
    return user_perm | extra


def revoke(user_perm: Perm, removed: Perm) -> Perm:
    """Turn bits OFF: AND with the inverted mask."""
    return user_perm & ~removed


def toggle(user_perm: Perm, flag: Perm) -> Perm:
    """Flip bits with XOR."""
    return user_perm ^ flag


def count_bits(n: int) -> int:
    """Count 1-bits (Kernighan's algorithm: n & (n-1) clears the lowest set bit)."""
    count: int = 0                             # how many ones
    while n:                                   # until no bits remain
        n &= n - 1                             # clear lowest set bit
        count += 1
    return count


def single_number(nums: list[int]) -> int:
    """Find the value that appears once; others appear twice (XOR cancels pairs)."""
    result: int = 0                            # x ^ 0 = x
    for n in nums:
        result ^= n                            # x ^ x = 0
    return result


def ip_to_int(ip: str) -> int:
    """Pack 'a.b.c.d' into one 32-bit integer using shifts."""
    a, b, c, d = (int(p) for p in ip.split("."))
    return (a << 24) | (b << 16) | (c << 8) | d


def int_to_ip(value: int) -> str:
    """Unpack the integer back using shifts and masks."""
    return ".".join(str((value >> shift) & 0xFF) for shift in (24, 16, 8, 0))


def main() -> None:
    user: Perm = Perm.EDITOR                       # READ + WRITE
    print(user, int(user))                         # Output: 3 3   (in 3.11+, str() of an IntFlag shows the number)
    print(can(user, Perm.READ))                    # Output: True
    print(can(user, Perm.READ | Perm.DELETE))      # Output: False
    user = grant(user, Perm.DELETE)                # add delete
    print(int(user), bool(user & Perm.DELETE))     # Output: 7 True
    user = revoke(user, Perm.WRITE)                # remove write
    print(int(user))                               # Output: 5
    print(int(toggle(user, Perm.ADMIN)))           # Output: 13

    print(count_bits(0b10110111), bin(183).count("1"), (183).bit_count())
    # Output: 6 6 6    (int.bit_count() needs Python 3.10+)

    print(single_number([4, 1, 2, 1, 2]))          # Output: 4

    packed: int = ip_to_int("192.168.1.10")
    print(packed)                                  # Output: 3232235786
    print(int_to_ip(packed))                       # Output: 192.168.1.10
    print(ip_to_int("192.168.1.77") & 0xFFFFFF00 == ip_to_int("192.168.1.0"))
    # Output: True  (same /24 network)

    # Bit masks for small sets: bit i means item i is present
    seen: int = 0
    for item in (3, 5, 3):                         # add 3, 5, 3 again
        seen |= 1 << item                          # set bit `item`
    print(bin(seen), bool(seen & (1 << 5)))        # Output: 0b101000 True

    # Negative numbers: infinite two's complement, so use a mask for fixed width
    print(-5 & 0xFF)                               # Output: 251  (8-bit view of -5)
    print(~5 & 0xFF)                               # Output: 250


if __name__ == "__main__":
    main()                                         # run only when executed directly
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: ints have unlimited size
print(5 & 3, 5 | 3, 5 ^ 3)     # 1 7 6
print(~5)                      # -6
print(1 << 40)                 # 1099511627776 (no overflow)
print(-8 >> 1)                 # -4  (arithmetic shift)
print(2 ** 32 | 1)             # 4294967297
print(bin(10))                 # 0b1010
```
```javascript
// JavaScript: bitwise operators convert to 32-bit signed integers!
console.log(5 & 3, 5 | 3, 5 ^ 3);   // 1 7 6
console.log(~5);                    // -6
console.log(1 << 40);               // 256  (shift count wraps mod 32!)
console.log(-8 >> 1);               // -4
console.log(-8 >>> 1);              // 2147483644 (unsigned shift, Python has none)
console.log(2 ** 32 | 1);           // 1  (2**32 truncated to 32 bits)
console.log((10).toString(2));      // "1010"
console.log(1n << 40n);             // 1099511627776n (BigInt needed)
```

Key differences: JS silently truncates to 32 bits, so large numbers break; Python ints are arbitrary size. JS has `>>>` (unsigned right shift); Python has no such operator. In Python, `&`, `|`, `~` are also used by NumPy/pandas/SQLAlchemy for elementwise logic. `|` is also the union operator for `set`, `dict` (3.9+) and types (`int | None`).

---

## 🟠 FastAPI Connection
Bitwise `|` is used in FastAPI/Pydantic type hints: `str | None` means optional. Permission flags (as an `IntFlag`) are a compact way to store roles in a JWT or database column. SQLAlchemy uses `&` and `|` between conditions, and `set | set` merges scopes (OAuth scopes). Always put brackets around comparisons when using `&`, `|`.

```python
# FastAPI example (needs: pip install fastapi)
from enum import IntFlag                        # permission bits
from fastapi import FastAPI, HTTPException      # framework + errors


class Perm(IntFlag):
    READ = 1                                    # 001
    WRITE = 2                                   # 010
    DELETE = 4                                  # 100


app: FastAPI = FastAPI()                        # create app
USER_PERMS: dict[int, Perm] = {1: Perm.READ | Perm.WRITE, 2: Perm.READ}


@app.delete("/files/{file_id}")                 # DELETE /files/10?user_id=1
async def delete_file(file_id: int, user_id: int) -> dict[str, int]:
    perms: Perm = USER_PERMS.get(user_id, Perm(0))     # unknown user = no bits
    if not perms & Perm.DELETE:                        # is the DELETE bit off?
        raise HTTPException(status_code=403, detail="No delete permission")
    return {"deleted": file_id}                        # JSON response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Confusing `&` with `and`
```python
# Wrong: & is bitwise
print(1 & 2)               # Output: 0

# Right: and for boolean logic
print(1 and 2)             # Output: 2
```

❌ Mistake 2: Forgetting that shifts bind LOWER than `+`
```python
# Wrong: looks like (1 << 2) + 1 = 5, but it is 1 << (2 + 1)
print(1 << 2 + 1)          # Output: 8

# Right: add brackets so the reader (and Python) agree
print((1 << 2) + 1)        # Output: 5
```

❌ Mistake 3: Expecting ~x to be a positive flip
```python
# Wrong: ~5 is not 2 (binary 010)
print(~5)                  # Output: -6   (because ~x == -x - 1)

# Right: mask to a fixed width when you need unsigned bits
print(~5 & 0b111)          # Output: 2
```

❌ Mistake 4: Shifting by a negative amount
```python
# Wrong: raises ValueError: negative shift count
# print(1 << -1)

# Right: validate shift
n: int = 3
print(1 << n if n >= 0 else 0)   # Output: 8
```

---

## 🧠 Tricky Interview Question

```python
print(5 & 3 | 4)
print(1 << 2 + 1)
print(~0, ~-1)
print(-7 >> 1, 7 >> 1)
print(6 ^ 6, 6 ^ 0)
print(True & False | True)
print({1, 2} | {2, 3}, {1, 2} & {2, 3}, {1, 2} ^ {2, 3})
```

**Answer:**
```
5
8
-1 0
-4 3
0 6
True
{1, 2, 3} {2} {1, 3}
```
Precedence: `&` is higher than `|`, so `5 & 3 | 4` is `(5 & 3) | 4 = 1 | 4 = 5`. Shift is *lower* than `+`, so `1 << 2 + 1` is `1 << 3 = 8`. `~0 = -1` and `~-1 = 0`. `>>` is an arithmetic (floor) shift: `-7 >> 1` is `floor(-3.5) = -4`. `x ^ x` is always 0 and `x ^ 0` is `x`. On `bool`, `&` and `|` return `bool`. For sets the same symbols mean intersection, union and symmetric difference.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `&` and `and`?
A1: `&` is bitwise: operates on every bit of integers (or elementwise on arrays/sets). `and` is logical: uses truthiness, short-circuits, and returns an operand. `5 & 3 = 1` but `5 and 3 = 3`. For booleans both give the right answer, but `&` does not short-circuit and has higher precedence than comparisons, so brackets are required.

Q2: How do you check, set, clear and toggle the nth bit?
A2: Check: `(x >> n) & 1` or `x & (1 << n)`. Set: `x | (1 << n)`. Clear: `x & ~(1 << n)`. Toggle: `x ^ (1 << n)`. These four are the core bit-manipulation toolkit and the basis for flags, bitmasks and many interview problems.

Q3: How do you find the single non-repeating number in a list where all others appear twice?
A3: XOR everything. `x ^ x = 0` and `x ^ 0 = x`, and XOR is commutative, so pairs cancel and the unique number remains. O(n) time, O(1) space. Example: `reduce(xor, [4, 1, 2, 1, 2]) == 4`.

Q4: How does `~x` work for Python ints and why is `~5 == -6`?
A4: Python ints behave as infinite two's complement numbers, so inverting all bits of `x` gives `-x - 1`. To see a fixed-width result, mask it: `~5 & 0xFF == 250`. This differs from C where `~5` on an unsigned byte gives 250 directly.

Q5: When should you use `IntFlag` instead of raw integers?
A5: When you represent permissions or options as combinable bits. `IntFlag` gives names, readable `repr`, safe combination with `|`, and behaves like an int for storage in a DB column or JWT. Use plain `Enum` if values are exclusive (only one at a time). Use `Flag` if you do not need int compatibility.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Permission/feature flags in one integer (`IntFlag`)
- Networking: IP and subnet masks, binary protocols
- Hashing, checksums, bitmaps, compact sets of small ints
- Interview tricks: XOR single number, power of two, bit counting

❌ Avoid when:
- A list of booleans or a set of enum values is clearer
- You need more readable business logic (bits are cryptic)
- You can use `and`/`or` for boolean logic
- Storing very sparse or very large flag sets (use sets/bitarray libraries)

---

## 📊 Visual Diagram
```
  a = 10 → 1 0 1 0
  b =  6 → 0 1 1 0
           ───────
  a & b  → 0 0 1 0  = 2
  a | b  → 1 1 1 0  = 14
  a ^ b  → 1 1 0 0  = 12

  a << 1 → 1 0 1 0 0 = 20   (shift left, add 0 on the right)
  a >> 1 →   1 0 1   = 5    (shift right, drop last bit)

  Permission bits:   DELETE WRITE READ
                       1      0     1    = 5  (can delete and read)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bit | Smallest unit: 0 or 1 | सबसे छोटी इकाई: 0 या 1 |
| Mask | Number used to select/clear bits | Bits चुनने/हटाने वाला number |
| AND `&` | 1 if both bits are 1 | दोनों 1 हों तो 1 |
| OR `\|` | 1 if either bit is 1 | कोई भी 1 हो तो 1 |
| XOR `^` | 1 if bits differ | bits अलग हों तो 1 |
| Shift `<<` `>>` | Move bits left/right | Bits को खिसकाना |
| Two's complement | How negative ints are stored | Negative numbers का representation |
| Flag | One bit meaning yes/no option | एक bit का हाँ/ना option |

---

## ⚡ 3-Line Summary
English: Bitwise operators (`& | ^ ~ << >>`) work on the binary digits of integers and are ideal for flags, masks, IP maths and XOR tricks. Python ints have unlimited size, `~x == -x - 1`, and `<<`/`>>` multiply/divide by powers of two. Use `IntFlag` for readable permission bits and brackets around bitwise expressions.
Hindi: Bitwise operators (`& | ^ ~ << >>`) integers के binary digits पर चलते हैं और flags, masks, IP गणित और XOR tricks में काम आते हैं। Python ints की size unlimited है, `~x == -x - 1`, और `<<`/`>>` 2 की power से गुणा/भाग करते हैं। Permission bits के लिए `IntFlag` और bitwise expressions में brackets लगाओ।

---

## ➡️ Next Topic
**031. Assignment Operators** — `=`, augmented assignment (`+=`), chained and unpacking assignment, and the walrus `:=`.
