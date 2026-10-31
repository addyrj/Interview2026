---

# 287. Database Query Tool
# हिंदी में: Database Query Tool (LLM से सुरक्षित SQL)

---

## 🔵 Simple Definition (English)
A database query tool lets an LLM read data from your database through a controlled function. The model never gets a raw connection: it calls a tool such as `get_tariff_rate(hs_code)` or `run_readonly_sql(query)`, your code validates it, runs it with a read-only user, and returns a few rows as JSON.

## 🔵 सरल परिभाषा (Hindi)
Database query tool से LLM आपके database का data एक नियंत्रित function के ज़रिए पढ़ता है। Model को सीधा connection नहीं मिलता: वह `get_tariff_rate(hs_code)` जैसा tool call करता है, आपका code validate करके read-only user से query चलाता है और कुछ rows JSON में लौटाता है।

---

## 🔴 Problem it Solves
LLM knowledge is stale and cannot see your private data (tariff rates, orders, customers). Pasting the whole table in the prompt is expensive and hits the context limit. Giving the model a full DB connection is dangerous: `DROP TABLE`, `SELECT * FROM users` or prompt-injected SQL can destroy or leak data.

## 🔴 यह क्यों बना? (Hindi)
LLM का knowledge पुराना होता है और private data (tariff rates, orders) नहीं देख सकता। पूरी table prompt में डालना महँगा है। Model को full DB access देना खतरनाक है: `DROP TABLE`, data leak, SQL injection। इसलिए **controlled, read-only query tool** चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Describe tool + schema (table/column names) to the LLM
Step 2 → User asks: "What is the duty for HS 8517.12?"
Step 3 → LLM returns tool_call: get_tariff_rate(hs_code="8517.12")
Step 4 → Code runs a PARAMETERISED query with a read-only DB user
Step 5 → Limit rows (LIMIT 20) and columns, serialise to JSON
Step 6 → Rows go back as role="tool" message
Step 7 → LLM answers; tokens = schema + call + rows + answer (rows are the big part)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → LLM को tool + schema (table/column नाम) बताओ
Step 2 → User पूछता है: "HS 8517.12 की duty क्या है?"
Step 3 → LLM tool_call देता है: get_tariff_rate(hs_code="8517.12")
Step 4 → Read-only DB user से PARAMETERISED query चलाओ
Step 5 → Rows limit करो (LIMIT 20), JSON बनाओ
Step 6 → Rows role="tool" message में वापस
Step 7 → LLM जवाब देता है; tokens में rows सबसे बड़ा हिस्सा हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: Rates live in a `tariff_rates` table (hs_code, description, duty_pct, country). The LLM classifies the product to an HS code, then calls `get_tariff_rate`. The answer is grounded in the live DB, not in training data, and every query is logged for audit.

**Amazon AI**: "Where is my order 123?" calls `get_order_status(order_id)`, restricted to the logged-in customer's rows only.

## 🟡 Real Example Hindi mein
**Tariff System**: Rates `tariff_rates` table में हैं। LLM product को HS code में classify करता है, फिर `get_tariff_rate` call करता है। जवाब live DB पर आधारित होता है और हर query audit के लिए log होती है।

**Amazon AI**: "मेरा order 123 कहाँ है?" → `get_order_status(order_id)`, सिर्फ़ logged-in customer की rows तक सीमित।

---

## 💻 Code Example — Basic
```python
# Basic DB tool with sqlite3 (standard library, runs offline)
import sqlite3                      # built-in database
import json                         # to return JSON to the LLM
from typing import Any

# Create an in-memory demo DB so the example is self-contained
conn = sqlite3.connect(":memory:")  # temporary database
conn.execute("CREATE TABLE tariff_rates (hs_code TEXT, description TEXT, duty_pct REAL)")
conn.executemany(
    "INSERT INTO tariff_rates VALUES (?, ?, ?)",       # ? = parameter placeholders
    [("8517.12", "Smartphones", 18.0), ("8471.30", "Laptops", 0.0), ("6403.99", "Leather shoes", 25.0)],
)
conn.commit()                       # save inserts

def get_tariff_rate(hs_code: str) -> str:
    """Tool: fetch one tariff row by HS code. Uses a parameterised query."""
    try:
        cur = conn.execute(
            "SELECT hs_code, description, duty_pct FROM tariff_rates WHERE hs_code = ? LIMIT 5",
            (hs_code,),             # value passed separately -> no SQL injection
        )
        rows: list[dict[str, Any]] = [
            {"hs_code": r[0], "description": r[1], "duty_pct": r[2]} for r in cur.fetchall()
        ]
        if not rows:                # tell the LLM clearly when nothing is found
            return json.dumps({"ok": True, "rows": [], "note": "no match"})
        return json.dumps({"ok": True, "rows": rows})
    except sqlite3.Error as exc:    # database problems become an error payload
        return json.dumps({"ok": False, "error": str(exc)})

print(get_tariff_rate("8517.12"))   # one row
print(get_tariff_rate("0000.00"))   # no match
print(get_tariff_rate("1' OR '1'='1"))  # injection attempt: treated as plain text -> no match
```

## 💻 Code Example — Advanced
```python
# Production: read-only SQL guard + async + row limits + tool loop
import asyncio, json, re, sqlite3
from typing import Any
from openai import AsyncOpenAI

client = AsyncOpenAI()                          # needs OPENAI_API_KEY
DB_PATH = "tariff.db"                           # use a READ-ONLY database user in real Postgres
FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|attach|pragma|replace)\b", re.I)
MAX_ROWS = 20                                   # cap rows to control tokens

def validate_sql(sql: str) -> str:
    """Allow a single SELECT statement only."""
    cleaned = sql.strip().rstrip(";")           # remove trailing semicolon
    if ";" in cleaned:                          # no stacked statements
        raise ValueError("multiple statements not allowed")
    if not cleaned.lower().startswith("select"):
        raise ValueError("only SELECT is allowed")
    if FORBIDDEN.search(cleaned):               # defence in depth
        raise ValueError("forbidden keyword")
    return cleaned

def _run_query_sync(sql: str) -> list[dict[str, Any]]:
    """Blocking DB call (run it in a thread from async code)."""
    uri = f"file:{DB_PATH}?mode=ro"             # open file in read-only mode
    with sqlite3.connect(uri, uri=True, timeout=3) as con:   # timeout avoids hanging
        con.row_factory = sqlite3.Row           # rows behave like dicts
        cur = con.execute(f"SELECT * FROM ({validate_sql(sql)}) LIMIT {MAX_ROWS}")
        return [dict(r) for r in cur.fetchall()]

async def run_readonly_sql(sql: str) -> dict[str, Any]:
    """Async tool wrapper with structured errors."""
    try:
        rows = await asyncio.wait_for(asyncio.to_thread(_run_query_sync, sql), timeout=5)
        return {"ok": True, "rows": rows, "truncated": len(rows) == MAX_ROWS}
    except asyncio.TimeoutError:
        return {"ok": False, "error": "query timed out"}
    except (ValueError, sqlite3.Error) as exc:
        return {"ok": False, "error": str(exc)}   # LLM can fix its SQL and retry

TOOLS: list[dict[str, Any]] = [{
    "type": "function",
    "function": {
        "name": "run_readonly_sql",
        "description": "Run a SELECT on table tariff_rates(hs_code TEXT, description TEXT, duty_pct REAL, country TEXT).",
        "parameters": {"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]},
    },
}]

async def answer(question: str) -> str:
    """Tool loop: model -> SQL tool -> model."""
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "Answer using the database. Never guess rates."},
        {"role": "user", "content": question},
    ]
    for _ in range(3):                           # max 3 rounds
        resp = await client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=TOOLS)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content or ""
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            result = await run_readonly_sql(args.get("sql", ""))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    return "Stopped after 3 rounds."
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

app = FastAPI()

class Question(BaseModel):
    question: str = Field(min_length=3, max_length=500)

def current_user() -> str:
    """Placeholder auth dependency: real code would verify a JWT."""
    return "user-42"

@app.post("/tariff/ask")
async def ask(q: Question, user: str = Depends(current_user)) -> dict:
    """LLM + DB tool behind an authenticated endpoint."""
    try:
        return {"answer": await answer(q.question), "user": user}
    except Exception as exc:                     # LLM or DB failure
        raise HTTPException(status_code=502, detail=str(exc))

@app.get("/tariff/{hs_code}")
async def rate(hs_code: str) -> dict:
    """Deterministic endpoint: no LLM needed for a known HS code."""
    result = await run_readonly_sql(f"SELECT * FROM tariff_rates WHERE hs_code = '{hs_code.replace(chr(39), '')}'")
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
```
Note: prefer the typed `get_tariff_rate(hs_code)` tool with `?` parameters for known lookups; free-form SQL is for analytics only.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase          # SQLAlchemy wrapper
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool

db = SQLDatabase.from_uri("sqlite:///tariff.db")               # use a read-only DB user in prod
query_tool = QuerySQLDatabaseTool(db=db)                       # ready-made SQL tool

@tool
def get_tariff_rate(hs_code: str) -> str:
    """Return the duty percentage for an HS code."""
    return db.run("SELECT duty_pct FROM tariff_rates WHERE hs_code = :c", parameters={"c": hs_code})
```
LangGraph agents (`create_react_agent(llm, [get_tariff_rate])`) call it in a loop. LangChain's `create_sql_agent` builds a full text-to-SQL agent, but needs the same read-only safeguards.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building SQL by string formatting
✅ Correct: Parameterised queries.

```python
# Wrong — SQL injection:
conn.execute(f"SELECT * FROM tariff_rates WHERE hs_code = '{hs_code}'")
# Right:
conn.execute("SELECT * FROM tariff_rates WHERE hs_code = ?", (hs_code,))
```

❌ Mistake 2: Returning thousands of rows to the LLM
✅ Correct: `LIMIT`, select only needed columns, summarise.

```python
# Wrong — 50,000 rows = huge token bill, context overflow:
rows = conn.execute("SELECT * FROM orders").fetchall()
# Right:
rows = conn.execute("SELECT id, status FROM orders WHERE user_id = ? LIMIT 20", (uid,)).fetchall()
```

❌ Mistake 3: Using an admin DB user. Always use a read-only role with row-level security.

---

## 🧠 Tricky Interview Question

**Q**: "You validate that the SQL starts with SELECT, yet a user still reads another customer's data. How?"

**Answer**: Validation checks the statement type, not authorisation. `SELECT * FROM orders` returns every customer's rows. Fix: enforce access in the database (read-only role, row-level security, views filtered by tenant), or inject the `user_id` from the authenticated session in your code instead of letting the LLM write the WHERE clause. Never trust the model to scope data.

---

## ⚫ Interview Questions + Answers

Q1: Why not give the LLM a direct DB connection? (Easy)
A1: It could run destructive or leaking queries, especially under prompt injection. A tool layer validates, limits and logs every query.

Q2: What is a parameterised query? (Easy)
A2: SQL with placeholders (`?` or `:name`) where values are passed separately, so input is never parsed as SQL. It prevents SQL injection.

Q3: Typed tools or free-form SQL? (Medium)
A3: Typed tools (`get_tariff_rate(hs_code)`) are safer, cheaper and more reliable for known questions. Free-form text-to-SQL is flexible but needs schema in the prompt, validation, read-only access and row limits. Use typed tools for core paths, SQL for analytics.

Q4: How do you keep token cost down with DB results? (Medium)
A4: `LIMIT`, select specific columns, aggregate in SQL, return compact JSON, and tell the LLM when results are truncated so it can refine.

Q5: Design a multi-tenant text-to-SQL feature. (Hard)
A5: Read-only role per tenant or row-level security; schema subset in the prompt (only relevant tables, found via embeddings); single-statement SELECT validator using a SQL parser (e.g. sqlglot) rather than regex; statement timeout; row cap; audit log; retry loop where SQL errors go back to the model (max 2 retries); evaluation set of questions with expected results.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Answers depend on live or private structured data
- Data is too big to place in the prompt
- You need auditable, grounded answers

❌ Avoid when:
- Data is unstructured text (use RAG with a vector store)
- A fixed lookup is enough and you can skip the LLM
- You cannot enforce read-only access

---

## 📊 Visual Diagram
```
User question
     │
     ▼
 ┌───────┐ tool_call(hs_code) ┌──────────────┐  param query  ┌──────────┐
 │  LLM  │ ─────────────────► │ Tool wrapper │ ────────────► │ DB (RO)  │
 └───────┘                    │ validate     │ ◄──────────── │          │
     ▲                        │ limit rows   │   rows        └──────────┘
     │   JSON rows (<=20)     └──────────────┘
     └────────────────────────────┘
     │
     ▼
 Grounded answer
```

---

## 💰 Cost Impact
Biggest driver: result rows. 20 rows of 5 columns is about 300-500 tokens; 500 rows is about 10K tokens ($0.0015 per call on gpt-4o-mini input, but multiplied by every loop round). Schema in the system prompt costs tokens on every request.

Optimize: LIMIT and column selection, aggregate in SQL, send only relevant table schemas, cache frequent lookups (Redis), skip the LLM for exact HS-code lookups, and use `max_tokens`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Text-to-SQL | LLM writes SQL from a question | सवाल से SQL बनाना |
| Parameterised query | Values passed separately from SQL | अलग से values वाली query |
| SQL injection | Malicious input altering a query | SQL में दुर्भावनापूर्ण input |
| Read-only role | DB user that cannot write | सिर्फ़ पढ़ने वाला user |
| Row-level security | DB rule filtering rows per user | Row स्तर की सुरक्षा |
| Grounding | Answer based on real data | असली data पर आधारित जवाब |

---

## ⚡ 3-Line Summary
English: A DB query tool lets the LLM fetch live data without a raw connection. Use parameterised queries, a read-only user, single-statement validation and row limits. Rows returned are the main token cost, so keep them small.
Hindi: DB query tool से LLM को raw connection दिए बिना live data मिलता है। Parameterised queries, read-only user, single SELECT validation और row limit ज़रूरी हैं। Rows ही token cost का बड़ा हिस्सा हैं, इन्हें छोटा रखो।

---

## ➡️ Next Topic
**288. API Call Tool** — letting the LLM call external REST APIs (exchange rates, shipping) with timeouts and safe allowlists.
