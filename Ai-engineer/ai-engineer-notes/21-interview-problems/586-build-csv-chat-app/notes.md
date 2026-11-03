---

# 586. Build CSV Chat App
# हिंदी में: CSV Chat App बनाना

---

## 🔵 Simple Definition (English)
A CSV chat app lets users ask questions about a table in plain language. The LLM does not run code: it returns a small JSON "query plan" (filter, aggregation, column) and our code validates it against a whitelist before computing the answer.

## 🔵 सरल परिभाषा (Hindi)
CSV chat app में user table के बारे में सामान्य भाषा में सवाल पूछता है। LLM code नहीं चलाता, वह एक छोटा JSON "query plan" (filter, aggregation, column) देता है, और हमारा code उसे whitelist से validate करके जवाब निकालता है।

---

## 🔴 Problem it Solves
Naive "text-to-pandas" apps run `eval`/`exec` on LLM output: a prompt like "drop the table" or a prompt injection becomes remote code execution. LLMs also do arithmetic badly, so asking them to sum a column directly gives wrong numbers.

## 🔴 यह क्यों बना? (Hindi)
Naive "text-to-pandas" apps LLM के output पर `eval`/`exec` चलाते हैं: "drop the table" जैसा prompt या injection सीधा code execution बन जाता है। LLM गणित में कमज़ोर भी है, इसलिए sum खुद करवाने पर गलत number आता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → load(): parse CSV text, convert numeric-looking columns to float
Step 2 → mock_llm_plan(question): returns a JSON plan {filter, agg, column}
Step 3 → json.loads the plan (bad JSON -> JSONDecodeError)
Step 4 → execute(): agg must be in {sum, mean, count, max}, column must exist
Step 5 → Apply the equality filter, compute with trusted Python code
Step 6 → Empty filter result -> ValueError
Step 7 → chat() turns errors into "Could not answer safely: ..." (never raised)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → load(): CSV parse करो, numeric columns को float बनाओ
Step 2 → mock_llm_plan(question): JSON plan {filter, agg, column} देता है
Step 3 → plan को json.loads करो (गलत JSON -> JSONDecodeError)
Step 4 → execute(): agg {sum, mean, count, max} में हो, column मौजूद हो
Step 5 → equality filter लगाओ, भरोसेमंद Python से compute करो
Step 6 → filter में कोई row न मिले तो ValueError
Step 7 → chat() errors को "Could not answer safely: ..." बना देता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: a customs analyst uploads last month's shipments CSV and asks "What is the total duty on smartphone?". The LLM plans `{"filter": {"product": "smartphone"}, "agg": "sum", "column": "duty_usd"}` and the code returns 380.0 (200 + 180).

**Other**: Zomato ops asks "average order value in Delhi"; same pattern, same whitelist.

## 🟡 Real Example Hindi mein
**Tariff System**: customs analyst पिछले महीने की shipments CSV upload करके पूछता है "smartphone पर total duty?"। LLM plan बनाता है और code 380.0 (200 + 180) लौटाता है।

**Other**: Zomato ops पूछता है "Delhi का average order value"; वही pattern, वही whitelist।

---

## 💻 Code Example — Basic
```python
import csv
import io

TEXT = "product,duty_usd\nsmartphone,200\nsmartphone,180\nlaptop,0\n"

rows = list(csv.DictReader(io.StringIO(TEXT)))           # list of dicts (values are strings)
total = sum(float(r["duty_usd"]) for r in rows if r["product"] == "smartphone")  # we compute, not the LLM
print(total)                                              # 380.0
```

## 💻 Code Example — Advanced
Run: `python3 main.py`. Observed output of my run:
```
What is the total duty on smartphone? -> Result: 380.0
average value? -> Result: 862.5
drop the table -> Could not answer safely: aggregation 'delete_all' not allowed
```
Excerpt from `main.py` (the validator):
```python
from statistics import mean
from typing import Any

ALLOWED_AGG = {"sum", "mean", "count", "max"}


def execute(rows: list[dict[str, Any]], plan: dict[str, Any]) -> float:
    """Validate the plan against the schema/whitelist, then compute."""
    agg, col = plan.get("agg"), plan.get("column")
    if agg not in ALLOWED_AGG:
        raise ValueError(f"aggregation {agg!r} not allowed")   # whitelist, no eval
    if col not in rows[0]:
        raise ValueError(f"unknown column {col!r}")            # schema check
    sel = [r for r in rows if all(r.get(k) == v for k, v in plan.get("filter", {}).items())]
    if agg == "count":
        return float(len(sel))
    vals = [r[col] for r in sel]
    if not vals:
        raise ValueError("filter matched no rows")
    return {"sum": sum, "mean": mean, "max": max}[agg](vals)
```

---

## 🟠 FastAPI Integration
Expose `chat` as an endpoint; because errors are returned as text, the route stays simple. Add a row-count limit and auth in production.

```python
from fastapi import FastAPI

from main import chat                                    # our module

app = FastAPI()


@app.get("/csv/ask")
async def csv_ask(q: str) -> dict:
    answer = await chat(q)                               # never raises for bad plans
    return {"question": q, "answer": answer}
```

---

## 🔗 LangChain / LangGraph Connection
Use structured output so the model must return the plan schema. This replaces `mock_llm_plan`.

```python
from typing import Literal

from pydantic import BaseModel


class QueryPlan(BaseModel):
    filter: dict[str, str | float] = {}
    agg: Literal["sum", "mean", "count", "max"]          # schema enforces the whitelist too
    column: str


# llm = ChatOpenAI(model="gpt-4o-mini").with_structured_output(QueryPlan)
# plan = llm.invoke(question)  -> then pass plan.model_dump() to execute()
```
In LangGraph: `plan -> validate -> execute -> explain`, with a retry edge from validate back to plan.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `eval(llm_output)` or letting the LLM write pandas code.
✅ Correct: LLM emits data (JSON plan), your trusted code executes it.

```python
# Wrong
result = eval(llm_code)
# Right
result = execute(rows, json.loads(plan_text))   # whitelist + schema check
```

❌ Mistake 2: Not validating column names; a hallucinated column crashes with KeyError.
✅ Correct: check `col in rows[0]` (done in `execute`).

❌ Mistake 3: Letting the LLM do the arithmetic. Always compute in code.

---

## 🧠 Tricky Interview Question
**Q**: "The plan is valid but the filter value is 'Smartphone' (capital S) and the CSV has 'smartphone'. What happens?"

**Answer**: `execute` uses exact equality, so no rows match and it raises "filter matched no rows" (the user sees a safe message, not a wrong 0). Fix by normalising case in `load` and in the filter, or by giving the LLM the allowed distinct values per column in the prompt. Never silently return 0 for an empty match.

---

## ⚫ Interview Questions + Answers

Q1: Why a JSON plan instead of generated code?
A1: Data cannot execute. We only run whitelisted operations, so injection cannot become code execution.

Q2: Why return an error string from `chat` instead of raising?
A2: The user gets a safe explanation; the API does not return 500 for a bad model plan.

Q3: What does `load` do to numbers?
A3: Tries `float(v)` for each cell and keeps strings when conversion fails, so `duty_usd` becomes numeric but `product` stays text.

Q4: How would you support group-by or joins?
A4: Extend the plan schema (`group_by`) and implement it in `execute`; or translate the plan into parameterised SQL on a read-only connection.

Q5 (Hard): How do you scale to a 5 GB CSV?
A5: Load into DuckDB/SQLite, send the LLM only the schema plus a few sample rows, and execute the validated plan as a parameterised read-only query with timeouts and row limits.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users ask aggregate questions over a known table
- Safety matters (no code execution)

❌ Avoid when:
- Questions need free-form analysis or charts (use a sandbox with strict isolation)

---

## 📊 Visual Diagram
```
 question ─► LLM (structured output) ─► JSON plan
                                           │
                                           ▼
                       ┌─────────── validate ───────────┐
                       │ agg in whitelist? column known? │
                       └───────┬───────────────┬────────┘
                          ok   │               │ fail
                               ▼               ▼
                      trusted Python      "Could not answer
                      compute (sum..)         safely: ..."
```

---

## 💰 Cost Impact
Only the plan generation costs tokens (a small prompt with the schema, a tiny output). Computation is free. Send only column names and a few sample rows, not the whole CSV, and use a small model for planning.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Query plan | JSON description of the computation | Computation का JSON नक्शा |
| Whitelist | Only listed operations allowed | अनुमत चीज़ों की सूची |
| Structured output | LLM returns schema-valid JSON | Schema वाला JSON output |
| Injection | Malicious instruction in input | Input में छुपा दुर्भावनापूर्ण निर्देश |
| Aggregation | sum, mean, count, max | कई rows से एक value |

---

## ⚡ 3-Line Summary
English: The LLM writes a JSON plan, never code. Our code validates it with a whitelist and computes the result. Bad plans produce a safe explanation.
Hindi: LLM JSON plan लिखता है, code नहीं। हमारा code whitelist से validate करके result निकालता है। गलत plan पर सुरक्षित message मिलता है।

---

## ➡️ Next Topic
**587. Build Code Review Agent** — another place where deterministic checks beat blind LLM output: reviewing code with AST rules first.
