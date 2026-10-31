---

# 064. ChainMap
# हिंदी में: ChainMap (कई Dicts का Layered View)

---

## 🔵 Simple Definition (English)
`ChainMap` groups several dicts into one view without copying them. Lookups search the dicts in order and return the first match. Writes go only to the first dict. It is perfect for layered settings: command-line args over environment variables over defaults.

## 🔵 सरल परिभाषा (Hindi)
`ChainMap` कई dicts को बिना copy किए एक view में जोड़ता है। Lookup dicts में क्रम से खोजता है और पहला match लौटाता है। Write सिर्फ पहले dict में जाता है। Layered settings के लिए बढ़िया: command-line args > environment variables > defaults।

---

## 🔴 Problem it Solves
To combine config layers you could do `{**defaults, **env, **cli}`. That copies everything, loses the layers, and later changes in `env` do not show up in the merged copy. ChainMap keeps the layers separate and live: change one layer and the combined view changes instantly; you can also see which layer provided a value and add or remove layers cheaply.

## 🔴 यह क्यों बना? (Hindi)
Config layers जोड़ने के लिए `{**defaults, **env, **cli}` सब कुछ copy करता है, layers खो जाती हैं, और बाद में `env` बदलने पर merged copy नहीं बदलती। ChainMap layers अलग और live रखता है: एक layer बदलो तो view तुरंत बदलता है; और नई layer जोड़ना सस्ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → cm = ChainMap(cli, env, defaults)   → stores a list of the dicts (no copy): cm.maps
Step 2 → cm["port"]                           → looks in cli, then env, then defaults; first hit wins
Step 3 → cm["x"] = 1                          → writes ONLY to cm.maps[0] (the first dict)
Step 4 → del cm["x"]                          → deletes only from the first dict (KeyError if not there)
Step 5 → cm.new_child({...})                  → new ChainMap with an extra first layer (like a new scope)
Step 6 → cm.parents                           → ChainMap without the first layer
```

## 🟢 कैसे काम करता है? (Hindi)
```
ChainMap(cli, env, defaults) → dicts की list रखता है (copy नहीं): cm.maps
cm["port"] → cli, फिर env, फिर defaults; पहला match जीतता है
cm["x"] = 1 → सिर्फ पहले dict में लिखता है
new_child() → ऊपर नई layer (नया scope)
parents → पहली layer हटाकर बाकी
```

---

## 🟡 Real World Example
A FastAPI app reads settings from three places: a CLI override, environment variables, and built-in defaults. `ChainMap(cli_args, os.environ_subset, defaults)` gives one lookup object with the right priority. Template engines and interpreters use the same idea for variable scopes (local → enclosing → global).

## 🟡 Real Example Hindi mein
FastAPI app तीन जगह से settings पढ़ता है: CLI override, environment variables, और default values। `ChainMap(cli_args, env_subset, defaults)` सही priority के साथ एक lookup object देता है। Template engines और interpreters variable scopes (local → enclosing → global) के लिए यही idea use करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: ChainMap lookup order and writes
from collections import ChainMap             # import the class

defaults: dict[str, object] = {"color": "blue", "size": "M", "debug": False}   # lowest priority
user: dict[str, object] = {"color": "red"}   # higher priority

cm: ChainMap[str, object] = ChainMap(user, defaults)   # first dict has top priority
print(cm["color"])                           # Output: red   (found in user first)
print(cm["size"])                            # Output: M     (falls back to defaults)
print(cm.get("missing", "none"))             # Output: none  (get works like dict)

cm["size"] = "L"                             # write goes ONLY to the first dict
print(user)                                  # Output: {'color': 'red', 'size': 'L'}
print(defaults["size"])                      # Output: M     (defaults untouched)

defaults["debug"] = True                     # change a lower layer later
print(cm["debug"])                           # Output: True  (view is live)

print(len(cm))                               # Output: 3  (unique keys across all layers)
print(sorted(cm))                            # Output: ['color', 'debug', 'size']

print(cm.maps[0] is user)                    # Output: True  (original dicts are kept)
```

## 💻 Code Example — Advanced
```python
# Advanced: layered settings (CLI > ENV > defaults) and scoped contexts
from __future__ import annotations           # modern hints
from collections import ChainMap             # layered mapping
from typing import Any                       # value type


def build_settings(cli: dict[str, Any], env: dict[str, str]) -> ChainMap[str, Any]:
    """Create settings with priority: cli > env > defaults."""
    defaults: dict[str, Any] = {"host": "127.0.0.1", "port": 8000, "debug": False}   # lowest
    env_clean: dict[str, Any] = {                    # keep only known keys from env
        k.lower().removeprefix("app_"): v            # APP_PORT -> port
        for k, v in env.items()
        if k.lower().startswith("app_")
    }
    if "port" in env_clean:                          # env values are strings
        env_clean["port"] = int(env_clean["port"])   # convert port to int
    return ChainMap(cli, env_clean, defaults)        # highest priority first


settings = build_settings({"debug": True}, {"APP_PORT": "9000", "HOME": "/root"})
print(settings["host"], settings["port"], settings["debug"])   # Output: 127.0.0.1 9000 True

# Which layer provided the value?
def source_of(cm: ChainMap[str, Any], key: str) -> int:
    """Return index of the layer containing key, or -1."""
    for i, layer in enumerate(cm.maps):              # walk the layers in priority order
        if key in layer:                             # first layer that has it
            return i                                 # report layer index
    return -1                                        # not found

print(source_of(settings, "debug"), source_of(settings, "port"), source_of(settings, "host"))   # Output: 0 1 2

# Scoped contexts with new_child / parents (like function scopes)
global_scope: ChainMap[str, Any] = ChainMap({"x": 1, "y": 2})   # global variables
local_scope: ChainMap[str, Any] = global_scope.new_child({"x": 10})   # local shadows x
print(local_scope["x"], local_scope["y"])            # Output: 10 2
local_scope["z"] = 99                                # new variables go to the local layer
print("z" in global_scope)                           # Output: False
print(local_scope.parents["x"])                      # Output: 1  (view without local layer)

# Deleting works only in the first layer
try:                                                 # 'y' lives in a lower layer
    del local_scope["y"]                             # cannot delete from lower layers
except KeyError as err:                              # expected failure
    print("KeyError:", err)                          # Output: KeyError: "Key not found in the first mapping: 'y'"

# Flatten when you need a real dict (for JSON/FastAPI response):
flat: dict[str, Any] = dict(local_scope)             # copies merged view
print(flat)                                          # Output: {'x': 10, 'y': 2, 'z': 99}
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
from collections import ChainMap
cm = ChainMap({"a": 1}, {"a": 0, "b": 2})
print(cm["a"], cm["b"])              # 1 2  (layers, no copying)
```

```javascript
// JavaScript: closest are spread (copies) or prototype chain (live)
const defaults = { a: 0, b: 2 };
const merged = { ...defaults, a: 1 };            // copy: not live
const layered = Object.create(defaults);         // live: lookups fall back to prototype
layered.a = 1;
console.log(layered.a, layered.b);               // 1 2
```

Key difference: JS spread creates a copy; the prototype chain is live but hard to inspect and affects all property behaviour. Python ChainMap is explicit, inspectable (`.maps`) and does not touch the original dicts. FastAPI link: pydantic-settings does layered settings (env, .env file, defaults) the same way; ChainMap is the plain-Python version.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting writes to update the layer that holds the key
```python
# cm = ChainMap({}, {"a": 1}); cm["a"] = 2
# Only the FIRST dict changed. cm.maps[1]["a"] is still 1.
```

❌ Mistake 2: Putting layers in the wrong order
```python
# Wrong: ChainMap(defaults, user)   # defaults win, user overrides ignored
# Correct: ChainMap(user, defaults) # highest priority FIRST
```

❌ Mistake 3: Deleting or popping a key from a lower layer
```python
# del cm["y"]  -> KeyError if 'y' is not in the first mapping
# Correct: del cm.maps[1]["y"]  (delete explicitly in that layer)
```

---

## 🧠 Tricky Interview Question

**Q**: "`a = {'x': 1}; b = {'x': 2}; cm = ChainMap(a, b); cm['x'] = 5; del cm['x']; print(cm['x'])` — what is printed?"

**Answer**: `2`. The write `cm['x'] = 5` changes only `a` (the first map). `del cm['x']` removes `x` from `a` (first map only). After that, `a` is empty, so lookup falls through to `b`, where `x` is `2`. So deleting the top value "reveals" the lower layer's value. That is the shadowing behaviour of layered scopes.

---

## ⚫ Interview Questions + Answers

Q1: What is ChainMap and why not just merge dicts?
A1: ChainMap links dicts into a single view with lookups going layer by layer. Merging with `{**a, **b}` makes a copy, which is O(n), loses layer info, and goes stale if sources change. ChainMap is O(1) to create, live, and keeps the originals intact.

Q2: How do reads and writes differ in ChainMap?
A2: Reads search all maps in order and return the first match. Writes, deletes, `pop`, and `update` affect only the first map. This is intentional: lower layers (defaults) stay read-only in effect.

Q3: What is the time complexity of lookup?
A3: O(m) where m is the number of layers, since it tries each dict in order (each lookup in a dict is O(1)). With a handful of layers this is fine. Iteration and `len` build a merged view of keys, so they cost O(total keys).

Q4: What are `new_child()` and `parents` used for?
A4: `new_child(m)` returns a new ChainMap with `m` (or a fresh `{}`) as the new first layer: perfect to simulate a nested scope. `parents` returns a ChainMap of everything except the first layer, simulating "leave the scope".

Q5: What happens with iteration order and duplicates?
A5: Iteration yields each key once. Order is from the LAST map to the first (due to how it merges), so do not rely on it. When you need a stable plain dict, convert with `dict(cm)`, where the first layer's value wins for duplicate keys.

---

## 🔷 When to Use ChainMap

✅ Use when:
- Layered configuration (CLI > env > defaults)
- Simulating variable scopes (interpreters, templates)
- You want a live combined view without copying

❌ Avoid when:
- You need a single flat dict many times (convert once with `dict(cm)`)
- You need writes to hit lower layers
- Many layers and very frequent lookups (cost grows with layers)

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Layer / map | One dict inside the ChainMap | ChainMap के अंदर एक dict |
| Shadowing | Upper layer hides lower value | ऊपर की layer नीचे की value छुपा देती है |
| `maps` | List of the underlying dicts | अंदर के dicts की list |
| `new_child` | Add a new top layer | ऊपर नई layer जोड़ना |
| `parents` | View without first layer | पहली layer हटाकर view |
| Live view | Reflects later changes | बाद के बदलाव दिखाने वाला |

---

## ⚡ 3-Line Summary
English: ChainMap stacks dicts into one live view; reads check layers in order, writes touch only the first. Perfect for config priority (CLI > env > defaults) and scope simulation. Use `dict(cm)` when you need a flat copy.
Hindi: ChainMap dicts को एक live view में stack करता है; read layers के क्रम में खोजता है, write सिर्फ पहली layer में। Config priority (CLI > env > defaults) और scope simulation के लिए बढ़िया। Flat copy चाहिए तो `dict(cm)`।

---

## ➡️ Next Topic
**066. Set Methods** — `add`, `remove`, `discard`, `union`, `intersection`, `difference` and set algebra.
