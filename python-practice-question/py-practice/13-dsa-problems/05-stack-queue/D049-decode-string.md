---

# D049. Decode String
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #394 | Asked: Amazon, Google, Meta, Microsoft

---

## ❓ Problem
Decode a string encoded as `k[encoded]`, meaning `encoded` repeated `k` times. Encodings can be nested.

```
Input:  "3[a]2[bc]"      Output: "aaabcbc"
Input:  "3[a2[c]]"       Output: "accaccacc"
Input:  "2[abc]3[cd]ef"  Output: "abcabccdcdcdef"
```

---

## 💡 Quick Concept (2 lines only)
Use a stack. On `[` push the (string so far, repeat count) and start fresh; on `]` pop and set current = previous + current * count.
हिंदी: `[` पर अब तक का string और count stack में रखो; `]` पर pop करके current को count बार दोहराकर पुराने से जोड़ दो।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — repeatedly expand the innermost k[...]
# O(n * depth) time, O(n) space
# ============================================
import re                                       # regex for innermost brackets


def decode_brute(s: str) -> str:
    pattern = re.compile(r"(\d+)\[([a-z]*)\]")  # innermost: digits [ letters-only ]
    while True:                                 # until nothing left to expand
        new = pattern.sub(lambda m: m.group(2) * int(m.group(1)), s)  # expand all innermost
        if new == s:                            # no change -> fully decoded
            return new                          # done
        s = new                                 # repeat with the expanded string


# ============================================
# APPROACH 2: Stack of (prev_string, count) — O(output) time ✅ PREFERRED
# ============================================
def decode_string(s: str) -> str:
    stack: list[tuple[str, int]] = []           # saved (string before '[', repeat count)
    cur = ""                                    # string being built
    num = 0                                     # number being read (may be multi-digit)
    for ch in s:                                # scan characters
        if ch.isdigit():                        # part of a number
            num = num * 10 + int(ch)            # build multi-digit counts like 12
        elif ch == "[":                         # start of a group
            stack.append((cur, num))            # save context
            cur, num = "", 0                    # start fresh inside the brackets
        elif ch == "]":                         # end of a group
            prev, k = stack.pop()               # restore context
            cur = prev + cur * k                # repeat group and append to previous
        else:
            cur += ch                           # normal letter
    return cur                                  # fully decoded string


# ============================================
# TEST CASES
# ============================================
print(decode_brute("3[a2[c]]"))                 # accaccacc
print(decode_string("3[a]2[bc]"))               # aaabcbc
print(decode_string("3[a2[c]]"))                # accaccacc
print(decode_string("2[abc]3[cd]ef"))           # abcabccdcdcdef
print(decode_string("abc"))                     # abc
print(len(decode_string("10[a]")))              # 10
print(decode_string("2[a2[b]]c"))               # abbabbc
```

---

## 🔍 Why It Works
```
s = "3[a2[c]]"
'3' num=3 | '[' push ("",3) cur="" | 'a' cur="a" | '2' num=2
'[' push ("a",2) cur="" | 'c' cur="c"
']' pop ("a",2): cur = "a" + "c"*2 = "acc"
']' pop ("",3):  cur = "" + "acc"*3 = "accaccacc"
```
हिंदी: Nested bracket में हर level का अपना context stack में सुरक्षित रहता है और बाहर आते ही वापस जुड़ता है।

---

## 📊 Complexity
```
Brute force: Time O(n * depth) | Space O(n)
Stack:       Time O(output length) | Space O(n) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Recursive descent — parse(i) returns (decoded, next_index)
def decode_rec(s: str) -> str:
    def parse(i: int) -> tuple[str, int]:
        out, num = "", 0                        # result and pending number
        while i < len(s):                       # until the string ends
            ch = s[i]                           # current char
            if ch.isdigit():                    # accumulate count
                num = num * 10 + int(ch)        # multi-digit support
            elif ch == "[":                     # recurse into group
                inner, i = parse(i + 1)         # decode inside, i lands on ']'
                out += inner * num              # repeat the group
                num = 0                         # reset count
            elif ch == "]":                     # group ends
                return out, i                   # hand back to caller
            else:
                out += ch                       # plain letter
            i += 1                              # next char
        return out, i                           # top level finished
    return parse(0)[0]                          # decoded string
print(decode_rec("3[a2[c]]"))                   # accaccacc

# VARIANT 2: Encode a string (reverse problem) — run-length encoding
# VARIANT 3: Compute only the decoded length without building it
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: reading a single digit only — "12[a]" would repeat 2 times
#    num = int(ch)        # should be num = num * 10 + int(ch)
# ❌ Wrong: forgetting to reset num after '[' -> counts leak into the next group
# ✅ Correct: accumulate digits and reset cur/num after pushing to the stack
```

---

## 🎯 Interview Tip
Say: "Nesting means a stack: save the string and multiplier at `[`, and at `]` combine. I accumulate digits for multi-digit counts." Mention recursion as an equivalent approach.

---

## 🔗 Related Problems
→ D042 (Valid Parentheses) | D047 (Evaluate Reverse Polish Notation) | D043 (Min Stack)
