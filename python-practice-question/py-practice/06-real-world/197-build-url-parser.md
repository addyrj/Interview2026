---

# Q197. Build URL parser
# Category: REAL WORLD PROBLEMS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build `parse_url(url)` that splits an absolute URL into scheme, user/password, host, port, path, query (as a dict) and fragment. Raise `ValueError` for invalid input.

```python
parse_url("https://user:pw@Example.com:8080/a/b?x=1&y=2#top")
# scheme='https', host='example.com', port=8080, path='/a/b', query={'x': '1', 'y': '2'}, fragment='top'
```

---

## 💡 Quick Concept (2 lines only)
A URL is `scheme://user:pw@host:port/path?query#fragment` — one regex with named groups splits it, then convert port to `int` and query to a dict.
हिंदी: URL को regex के named groups से तोड़ो — scheme, host, port, path, query, fragment अलग-अलग मिल जाते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import re                                            # regex for splitting the URL
from dataclasses import dataclass, field             # simple result container

URL_RE = re.compile(                                 # one regex = scheme://user:pw@host:port/path?query#frag
    r"^(?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*)://"       # scheme like https
    r"(?:(?P<user>[^:@/]*)(?::(?P<password>[^@/]*))?@)?"  # optional user:password@
    r"(?P<host>[^:/?#]*)"                            # host name
    r"(?::(?P<port>\d+))?"                           # optional :port
    r"(?P<path>/[^?#]*)?"                            # optional /path
    r"(?:\?(?P<query>[^#]*))?"                       # optional ?query
    r"(?:#(?P<fragment>.*))?$"                       # optional #fragment
)

@dataclass
class ParsedURL:
    scheme: str                                      # e.g. "https"
    host: str                                        # e.g. "example.com"
    port: int | None = None                          # None when not given
    path: str = "/"                                  # default path is "/"
    query: dict[str, str] = field(default_factory=dict)  # parsed ?a=1&b=2
    fragment: str = ""                               # text after '#'
    user: str | None = None                          # optional username
    password: str | None = None                      # optional password

def parse_url(url: str) -> ParsedURL:
    m = URL_RE.match(url)                            # try to match the whole string
    if not m:                                        # not a valid absolute URL
        raise ValueError(f"Invalid URL: {url!r}")    # fail loudly
    g = m.groupdict()                                # named groups -> dict
    query: dict[str, str] = {}                       # result query dict
    for pair in filter(None, (g["query"] or "").split("&")):  # skip empty pairs
        k, _, v = pair.partition("=")                # split on first '='
        query[k] = v                                 # last value wins (no decoding here)
    return ParsedURL(                                # build the result object
        scheme=g["scheme"].lower(),                  # schemes are case-insensitive
        host=g["host"].lower(),                      # hosts are case-insensitive
        port=int(g["port"]) if g["port"] else None,  # convert port to int
        path=g["path"] or "/",                       # default path
        query=query,                                 # parsed query
        fragment=g["fragment"] or "",                # fragment or empty
        user=g["user"],                              # may be None
        password=g["password"],                      # may be None
    )

# ============================================
# TEST CASES
# ============================================
u = parse_url("https://user:pw@Example.com:8080/a/b?x=1&y=2#top")
print(u.scheme, u.host, u.port, u.path)              # Expected: see below
print(u.query, u.fragment, u.user, u.password)
print(parse_url("http://example.com"))               # defaults: path "/", port None
try:
    parse_url("not a url")                           # no scheme -> error
except ValueError as e:
    print(e)

# --- Real output (Python 3.13) ---
# https example.com 8080 /a/b
# {'x': '1', 'y': '2'} top user pw
# ParsedURL(scheme='http', host='example.com', port=None, path='/', query={}, fragment='', user=None, password=None)
# Invalid URL: 'not a url'
```

---

## 🔍 Why This Works (3 lines max)
The regex makes every part after the host optional, so `groupdict()` gives `None` for missing parts and we apply defaults (`/` path, `None` port). Host and scheme are lower-cased because they are case-insensitive. In production prefer `urllib.parse` (see alternative).
हिंदी: Regex हर हिस्से को optional रखता है, missing हिस्से पर default लगा देते हैं।

---

## ⚡ Alternative Solution
```python
# ============================================
# ALTERNATIVE: stdlib urllib.parse (use this in real code)
# ============================================
from urllib.parse import urlsplit, parse_qs          # stdlib parser

u = urlsplit("https://user:pw@Example.com:8080/a/b?x=1&y=2&x=3#top")  # split into parts
print(u.scheme, u.hostname, u.port, u.path)          # hostname is lower-cased automatically
print(parse_qs(u.query))                             # repeated keys -> lists, values URL-decoded
print(u.fragment, u.username, u.password)            # fragment and credentials
print(urlsplit("http://example.com").path == "")     # stdlib keeps path empty, not "/"

# --- Real output (Python 3.13) ---
# https example.com 8080 /a/b
# {'x': ['1', '3'], 'y': ['2']}
# top user pw
# True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: naive split — breaks when a value contains '=' or when there is no '?'
url = "https://a.com/search?q=a=b&x=1"
base, query = url.split("?")                         # fails with ValueError if there are 0 or 2+ '?'
print(dict(p.split("=") for p in query.split("&")))  # p='q=a=b' splits into 3 pieces
# ValueError: dictionary update sequence element #0 has length 3; 2 is required  (real run)

# ✅ Correct: partition on the FIRST '=' only (as the solution does)
k, _, v = "q=a=b".partition("=")                      # k='q', v='a=b'
print(k, v)                                          # q a=b
```

---

## 🎯 Interview Tip (1 line)
Say: "In real code I'd use `urllib.parse.urlsplit` + `parse_qs`; hand-parsing is for understanding — and I know it doesn't decode %-escapes or handle IPv6 hosts."

---

## 🔗 Related Questions
→ Q198 (query string builder) | Q189 (URL router) | Q074 (dotted path) | Q192 (config loader)
