---

# Q192. Build Config Loader (env + defaults)
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build `load_config()` that returns a typed `Config` dataclass. Priority (low to high): defaults, then environment variables like `APP_PORT`, then explicit keyword overrides. Env strings must be cast to the field's type (including booleans), and a bad value must raise.

```python
load_config({"APP_PORT": "9000"}, workers=4)
```

---

## 💡 Quick Concept (2 lines only)
Env vars are always strings, so cast by the field type; `bool("false")` is `True`, so booleans need a custom parser. Layer: defaults < env < explicit args.
हिंदी: Env values हमेशा string होती हैं — type के हिसाब से cast करो; priority: default < env < explicit।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import os  # env access
from dataclasses import dataclass, fields  # typed config
from typing import Any, Mapping  # type hints

@dataclass
class Config:
    host: str = "localhost"  # default
    port: int = 8000  # default
    debug: bool = False  # default
    workers: int = 1  # default

def to_bool(v: str) -> bool:
    return v.strip().lower() in {"1", "true", "yes", "on"}  # common truthy strings

def load_config(env: Mapping[str, str] = os.environ, prefix: str = "APP_", **overrides: Any) -> Config:
    cfg = Config()  # start from defaults
    for f in fields(Config):  # each field
        raw = env.get(prefix + f.name.upper())  # APP_PORT etc.
        if raw is not None:
            cast = to_bool if f.type is bool else f.type  # bool needs custom parse
            setattr(cfg, f.name, cast(raw))  # env overrides default
    for k, v in overrides.items():
        setattr(cfg, k, v)  # explicit args win over env
    return cfg  # final config

# ============================================
# TEST CASES
# ============================================
print(load_config({}))  # Expected: Config(host='localhost', port=8000, debug=False, workers=1)
print(load_config({"APP_PORT": "9000", "APP_DEBUG": "true"}))  # Expected: Config(host='localhost', port=9000, debug=True, workers=1)
print(load_config({"APP_PORT": "9000"}, port=1234, workers=4))  # Expected: Config(host='localhost', port=1234, debug=False, workers=4)
try:
    load_config({"APP_PORT": "abc"})  # bad value
except ValueError as e:
    print("ValueError:", e)  # Expected: ValueError: invalid literal for int() with base 10: 'abc'
```

---

## 🔍 Why This Works (3 lines max)
`fields()` lets the loader be generic: add a field and it's automatically read from `APP_<NAME>`. Passing `env` as a parameter (default `os.environ`) makes it testable without touching real environment variables.
हिंदी: `fields()` से loader generic रहता है; `env` parameter होने से test में असली environment नहीं छूना पड़ता।

---

## ⚡ Alternative Solution
```python
from collections import ChainMap  # layered lookup

defaults = {"host": "localhost", "port": 8000}  # lowest priority
env = {"port": 9000}  # middle
cli = {"host": "0.0.0.0"}  # highest
cfg = ChainMap(cli, env, defaults)  # first match wins
print(dict(cfg))  # Expected: {'host': '0.0.0.0', 'port': 9000}
print(cfg["port"], cfg["host"])  # Expected: 9000 0.0.0.0
# For production, pydantic-settings' BaseSettings does env parsing + validation for you.
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: bool() of a non-empty string is always True (not run)
# debug = bool(os.environ.get("DEBUG", "false"))   # "false" -> True !!
# port = os.environ.get("PORT", 8000)              # str when set, int when not

# ✅ Correct: parse booleans explicitly (to_bool) and cast every env value to the declared type
```

---

## 🎯 Interview Tip (1 line)
Say: "12-factor config: env over file over defaults, typed and validated at startup so the app fails fast."

---

## 🔗 Related Questions
→ Q072 (deep merge two dicts) | Q246 (dataclasses) | Q252 (collections) | Q223 (Pydantic validation)
