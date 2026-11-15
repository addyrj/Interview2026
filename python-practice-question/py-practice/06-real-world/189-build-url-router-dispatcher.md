---

# Q189. Build URL Router/Dispatcher
# Category: Real World Problems
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Build a `Router` with a `@route(method, path)` decorator that supports typed path params like `/users/{id:int}`. `dispatch(method, path)` must call the right handler with converted params, return `404 Not Found` for unknown paths and `405 Method Not Allowed` when the path exists but the method does not.

```python
@r.route("GET", "/users/{id:int}")
def get_user(id: int): ...
```

---

## 💡 Quick Concept (2 lines only)
Compile each path template into a regex with named groups, keep a cast function per param, and try routes in order. This is how Flask/FastAPI work internally.
हिंदी: Path template को named-group regex में compile करो, match होने पर params को cast करके handler चलाओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import re  # regex
from typing import Any, Callable  # type hints

class Router:
    CONVERTERS = {"int": (r"\d+", int), "str": (r"[^/]+", str)}  # type -> (regex, cast)

    def __init__(self) -> None:
        self._routes: list[tuple[str, re.Pattern, dict[str, Callable], Callable]] = []  # registered routes

    def route(self, method: str, path: str):
        def deco(fn: Callable) -> Callable:
            casts: dict[str, Callable] = {}  # param -> cast fn
            def repl(m: re.Match) -> str:
                name, _, typ = m.group(1).partition(":")  # "id:int" -> id, int
                rx, cast = self.CONVERTERS[typ or "str"]  # pick converter
                casts[name] = cast  # remember cast
                return f"(?P<{name}>{rx})"  # named capture group
            pattern = re.compile("^" + re.sub(r"\{([^}]+)\}", repl, path) + "$")  # build full regex
            self._routes.append((method.upper(), pattern, casts, fn))  # register
            return fn  # keep function usable
        return deco

    def dispatch(self, method: str, path: str) -> Any:
        path_matched = False  # for 405 vs 404
        for m, pattern, casts, fn in self._routes:
            match = pattern.match(path)  # try path
            if not match:
                continue  # next route
            path_matched = True  # path exists
            if m != method.upper():
                continue  # wrong method
            kwargs = {k: casts[k](v) for k, v in match.groupdict().items()}  # cast params
            return fn(**kwargs)  # call handler
        return "405 Method Not Allowed" if path_matched else "404 Not Found"  # fallbacks

# ============================================
# TEST CASES
# ============================================
r = Router()  # create router
@r.route("GET", "/users/{id:int}")
def get_user(id: int) -> str:
    return f"user {id} ({type(id).__name__})"  # show cast type
@r.route("GET", "/posts/{slug}/comments/{n:int}")
def comments(slug: str, n: int) -> str:
    return f"{slug}#{n}"  # multi params
@r.route("POST", "/users")
def create() -> str:
    return "created"  # static route
print(r.dispatch("GET", "/users/42"))  # Expected: user 42 (int)
print(r.dispatch("GET", "/posts/hello/comments/7"))  # Expected: hello#7
print(r.dispatch("POST", "/users"))  # Expected: created
print(r.dispatch("GET", "/users/abc"))  # Expected: 404 Not Found
print(r.dispatch("GET", "/users"))  # Expected: 405 Method Not Allowed
```

---

## 🔍 Why This Works (3 lines max)
`re.sub` rewrites `{id:int}` into `(?P<id>\d+)`, anchored with `^...$` so partial matches fail. `groupdict()` gives the captured strings, and the stored casts turn them into the right types before calling the handler.
हिंदी: `{id:int}` को `(?P<id>\d+)` regex बनाते हैं, `groupdict()` से values लेकर cast करते हैं और handler चलाते हैं।

---

## ⚡ Alternative Solution
```python
# Simplest: exact-match dict dispatch (no path params)
handlers = {
    ("GET", "/"): lambda: "home",  # (method, path) -> handler
    ("GET", "/about"): lambda: "about",  # another route
}
def dispatch(method: str, path: str) -> str:
    h = handlers.get((method, path))  # O(1) lookup
    return h() if h else "404"  # call or 404
print(dispatch("GET", "/"), dispatch("GET", "/x"))  # Expected: home 404
# match/case with path segments
def route(path: str) -> str:
    match path.strip("/").split("/"):  # split into segments
        case ["users", uid] if uid.isdigit():  # guard on digits
            return f"user {int(uid)}"
        case ["users"]:
            return "all users"
        case _:
            return "404"
print(route("/users/7"), route("/users"), route("/users/x"))  # Expected: user 7 all users 404
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: no anchors -> "/users/42/delete" also matches "/users/{id}" (not run)
# pattern = re.compile(path_regex)               # match() only anchors the START
# ❌ Also: not escaping literal dots, e.g. "/file.txt" where "." matches any char

# ✅ Correct: anchor with ^...$ (or re.fullmatch) and re.escape() static parts if they contain regex chars
```

---

## 🎯 Interview Tip (1 line)
Say: "Compile once at registration, match per request; static routes can use a dict for O(1), dynamic ones a regex or trie."

---

## 🔗 Related Questions
→ Q221 (CRUD endpoints) | Q239 (API versioning with routers) | Q245 (match/case) | Q255 (decorator tricks)
