---

# Q080. Transform dict keys (snake_case to camelCase)
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `camelize(obj)` that converts every key of a nested dict (including dicts inside lists) from `snake_case` to `camelCase`. Values must stay unchanged.

```python
camelize({"user_name": "a", "home_address": {"zip_code": 1}})
# {'userName': 'a', 'homeAddress': {'zipCode': 1}}
```

---

## 💡 Quick Concept (2 lines only)
Split the key on `_`, keep the first word, capitalize the rest, and join. Recurse into values so nested dicts and lists are converted too (common when a Python API talks to a JS frontend).
हिंदी: Key को `_` पर split करो, पहला शब्द वैसा रखो, बाकी capitalize करके जोड़ दो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Any                                 # type hint

def to_camel(s: str) -> str:
    first, *rest = s.split("_")                        # Step 1: first word + remaining words
    return first + "".join(w.capitalize() for w in rest)  # Step 2: capitalize the rest and join

def camelize(obj: Any) -> Any:
    if isinstance(obj, dict):                          # Step 3: dict -> convert keys, recurse into values
        return {to_camel(k) if isinstance(k, str) else k: camelize(v) for k, v in obj.items()}  # non-str keys untouched
    if isinstance(obj, list):                          # Step 4: list -> convert each element
        return [camelize(i) for i in obj]
    return obj                                         # Step 5: scalars unchanged

# ============================================
# TEST CASES
# ============================================
sample = {"user_name": "a", "home_address": {"zip_code": 1, "_private": 2},
          "items_list": [{"item_id": 1}], "already": 1, "a_b_c_d": 2}  # nested sample
print(camelize(sample))                                # Expected: {'userName': 'a', 'homeAddress': {'zipCode': 1, 'Private': 2}, 'itemsList': [{'itemId': 1}], 'already': 1, 'aBCD': 2}
print(to_camel("user_name"), to_camel("_private"), to_camel("a__b"))  # Expected: userName Private aB
print(to_camel("user_id2"), to_camel("HTTP_status"))   # Expected: userId2 HTTPStatus
```

---

## 🔍 Why This Works (3 lines max)
`split("_")` gives the words; `capitalize()` upper-cases the first letter and lower-cases the rest of each word. The recursion rebuilds the dict so only keys change — values and non-string keys pass through.
हिंदी: split + capitalize से key बदलती है, recursion से nested dicts/lists भी बदल जाते हैं।

---

## ⚡ Alternative Solution
```python
# Regex version: upper-case the letter after each underscore
import re                                              # regular expressions

def to_camel_re(s: str) -> str:
    return re.sub(r"_([a-z0-9])", lambda m: m.group(1).upper(), s)  # "_x" -> "X"

print(to_camel_re("user_name"), to_camel_re("_private"), to_camel_re("a_b_c"), to_camel_re("a__b"))  # Expected: userName Private aBC a_B
print("user_name".title().replace("_", ""))            # Expected: UserName  (that is PascalCase, not camelCase)

def to_snake(s: str) -> str:                           # reverse direction
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()  # underscore before each capital (not at start)
print(to_snake("homeAddressZip"))                      # Expected: home_address_zip
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: str.title() capitalizes the FIRST word too (gives PascalCase) and only converts top-level keys
d = {"user_name": "a", "home_address": {"zip_code": 1}}  # sample
bad = {k.title().replace("_", ""): v for k, v in d.items()}  # ❌ no recursion, wrong casing
print(bad)                                             # Output: {'UserName': 'a', 'HomeAddress': {'zip_code': 1}}
# ✅ Correct: keep the first word as-is, capitalize the rest, and recurse (camelize above)
```

---

## 🎯 Interview Tip (1 line)
Mention edge cases (leading underscores, double underscores, non-string keys) and that Pydantic does this for you with `alias_generator=to_camel`.

---

## 🔗 Related Questions
→ Q073 (flatten dict) | Q223 (Pydantic validation) | Q257 (string method tricks) | Q233 (response models)
