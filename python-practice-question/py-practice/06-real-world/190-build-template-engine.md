---

# Q190. Build Template Engine
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build `render(template, ctx)` that replaces `{{ name }}` placeholders with values from `ctx`. Support dotted paths (`{{ user.name }}`), a small set of filters (`{{ name | upper }}`) and render missing variables as an empty string.

```python
render("Hello {{ name }}!", {"name": "Aditya"})  # 'Hello Aditya!'
```

---

## 💡 Quick Concept (2 lines only)
One regex finds every `{{ ... }}` token and `re.sub` with a function replaces each. Look up dotted paths segment by segment (dict key or attribute).
हिंदी: एक regex से हर `{{ }}` ढूँढो, `re.sub` में function से value भरो; filter whitelist से ही चलाओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import re  # regex
from typing import Any, Callable  # type hints

FILTERS: dict[str, Callable[[Any], Any]] = {"upper": str.upper, "title": str.title, "len": len}  # allowed filters
TOKEN = re.compile(r"\{\{\s*([\w.]+)\s*(?:\|\s*(\w+))?\s*\}\}")  # {{ name.path | filter }}

def lookup(ctx: Any, path: str) -> Any:
    for part in path.split("."):  # walk dotted path
        ctx = ctx[part] if isinstance(ctx, dict) else getattr(ctx, part)  # dict key or attribute
    return ctx  # final value

def render(template: str, ctx: dict[str, Any]) -> str:
    def sub(m: re.Match) -> str:
        path, flt = m.groups()  # variable path + optional filter
        try:
            val = lookup(ctx, path)  # resolve value
        except (KeyError, AttributeError):
            return ""  # missing -> empty string
        if flt:
            val = FILTERS[flt](val)  # apply filter
        return str(val)  # always a string
    return TOKEN.sub(sub, template)  # replace every token

# ============================================
# TEST CASES
# ============================================
print(render("Hello {{ name }}!", {"name": "Aditya"}))  # Expected: Hello Aditya!
print(render("{{ user.name | upper }} has {{ user.langs | len }} langs", {"user": {"name": "ravi", "langs": ["py", "js"]}}))  # Expected: RAVI has 2 langs
print(render("Missing: [{{ nope }}]", {}))  # Expected: Missing: []
print(render("{{name|title}}", {"name": "john doe"}))  # Expected: John Doe
```

---

## 🔍 Why This Works (3 lines max)
`TOKEN.sub(func, text)` calls `func` for every match, so one pass handles all placeholders. Filters come from a whitelist dict, so templates can never execute arbitrary code (never use `eval` here).
हिंदी: `re.sub` हर match पर function बुलाता है; filters whitelist में हैं, इसलिए `eval` की ज़रूरत नहीं।

---

## ⚡ Alternative Solution
```python
from string import Template  # stdlib templates

t = Template("Hello $name, you owe $$${amount}")  # $name, ${amount}, $$ = literal $
print(t.substitute(name="Aditya", amount=50))  # Expected: Hello Aditya, you owe $50
print(t.safe_substitute(name="Ravi"))  # Expected: Hello Ravi, you owe $${amount} (missing key left as-is)
try:
    t.substitute(name="X")  # missing key
except KeyError as e:
    print("KeyError", e)  # Expected: KeyError 'amount'
# str.format_map based "template"
print("{a} + {b}".format_map({"a": 1, "b": 2}))  # Expected: 1 + 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using eval() on the placeholder -> remote code execution (not run)
# re.sub(r"\{\{(.+?)\}\}", lambda m: str(eval(m.group(1), ctx)), template)
# a template containing {{ __import__('os').system('rm -rf /') }} runs it!

# ❌ Also: forgetting to HTML-escape values when rendering HTML -> XSS (use html.escape)

# ✅ Correct: safe lookup of dotted names + whitelisted filters (+ html.escape for HTML output)
```

---

## 🎯 Interview Tip (1 line)
Say: "Never eval user templates; whitelist filters, and escape output by default — that's what Jinja2 does."

---

## 🔗 Related Questions
→ Q243 (advanced f-strings) | Q074 (get value by dotted path) | Q257 (string method tricks) | Q274 (template method pattern)
