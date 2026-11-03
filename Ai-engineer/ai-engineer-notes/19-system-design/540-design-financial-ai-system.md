---

# 540. Design: Financial AI System
# हिंदी में: Financial AI System का Design

---

## 🔵 Simple Definition (English)
A financial AI system answers questions about accounts, transactions, reports and filings, and helps with tasks like fraud triage or expense categorisation. The key rule: the LLM explains and routes, but all numbers come from databases and calculators (tools), never from model memory.

## 🔵 सरल परिभाषा (Hindi)
Financial AI system accounts, transactions, reports और filings के सवालों के जवाब देता है, और fraud triage या expense categorisation जैसे काम में मदद करता है। मुख्य नियम: LLM समझाता और route करता है, पर सारे numbers database और calculators (tools) से आते हैं, model की याददाश्त से नहीं।

---

## 🔴 Problem it Solves
Analysts spend time pulling data and building summaries. LLMs are bad at exact arithmetic and may invent figures. In finance a wrong number leads to losses, compliance trouble, or false fraud accusations. Systems also face strict regulation, so every output needs traceability.

## 🔴 यह क्यों बना? (Hindi)
Analysts का समय data निकालने और summaries बनाने में जाता है। LLMs सटीक गणित में कमज़ोर हैं और figures गढ़ सकते हैं। Finance में गलत number का मतलब नुकसान, compliance की परेशानी या गलत fraud आरोप है। Regulation सख्त है, इसलिए हर output की traceability चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User asks: "Why did my spending jump in March?" (authenticated, scoped to own data)
Step 2 → LLM plans: needs transactions for March and February, grouped by category
Step 3 → LLM calls a read-only tool: get_spending(period, group_by) (parameters validated)
Step 4 → Tool runs parameterised SQL / API and returns exact figures
Step 5 → Calculations (sum, % change) run in code, not by the LLM
Step 6 → LLM writes the explanation using ONLY tool results; numbers are copied from them
Step 7 → Verifier checks every number in the text appears in tool output
Step 8 → Disclaimer + audit log (inputs, tool calls, outputs, versions); advice-type queries -> compliance rules
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User पूछता है: "March में खर्च क्यों बढ़ा?" (authenticated, सिर्फ अपना data)
Step 2 → LLM plan बनाता है: March और February के transactions, category-wise चाहिए
Step 3 → LLM read-only tool get_spending(period, group_by) चलाता है (parameters validated)
Step 4 → Tool parameterised SQL / API से सटीक figures लौटाता है
Step 5 → गणना (sum, % change) code में होती है, LLM में नहीं
Step 6 → LLM सिर्फ tool results से explanation लिखता है; numbers वहीं से copy होते हैं
Step 7 → Verifier जाँचता है कि text का हर number tool output में है
Step 8 → Disclaimer + audit log; advice वाले सवाल compliance rules से गुजरते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: Duty = value x rate. The classification (code) can come from the LLM pipeline, but the duty amount comes from a calculator using the official rate table and the invoice value, in Decimal. The LLM only explains "Duty is 18% under 8517.62 on 10,000".
**Zomato/Amazon-style**: A seller finance assistant explains "your payout is lower because of Rs 1,240 in returns" using figures from the settlement API.

## 🟡 Real Example Hindi mein
**Tariff System**: Duty = value x rate। Code LLM pipeline से आ सकता है, पर duty की रकम official rate table और invoice value से Decimal में calculator निकालता है। LLM सिर्फ समझाता है "8517.62 पर 10,000 के ऊपर 18% duty है"।
**Zomato/Amazon-style**: Seller finance assistant बताता है "आपका payout कम है क्योंकि Rs 1,240 के returns हैं", और figures settlement API से आते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: compute figures in code with Decimal, then template the explanation (pure Python)
from decimal import Decimal, ROUND_HALF_UP              # exact decimal math, no float errors

DUTY_RATES: dict[str, Decimal] = {"8517.62": Decimal("0.18"), "8518.30": Decimal("0.20")}   # sample rates


def duty(code: str, value: Decimal) -> Decimal:
    """Duty = value x rate, rounded to 2 places."""
    rate = DUTY_RATES[code]                            # KeyError if code unknown (fail loudly)
    return (value * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)   # exact rounding


def explain(code: str, value: Decimal) -> str:
    """Numbers are inserted by code, never invented."""
    d = duty(code, value)                              # calculated amount
    return f"On value {value} with code {code} at {DUTY_RATES[code]:.0%}, duty is {d}."   # templated text


print(explain("8517.62", Decimal("10000")))            # show result
print(0.1 + 0.2)                                       # float problem: 0.30000000000000004
print(Decimal("0.1") + Decimal("0.2"))                 # Decimal is exact: 0.3
```

## 💻 Code Example — Advanced
```python
# Production style: tool-based answer with number verification and audit
import asyncio                                         # async
import re                                              # find numbers in text
from decimal import Decimal                            # exact math
from typing import Any                                 # generic type


async def get_spending(user_id: str, period: str) -> dict[str, Any]:
    """Read-only tool: parameterised query in prod."""
    await asyncio.sleep(0)                             # pretend DB call
    data = {"2025-02": {"food": "4200.00", "travel": "1000.00"},
            "2025-03": {"food": "7900.00", "travel": "1100.00"}}   # fake data
    return {"user": user_id, "period": period, "by_category": data[period]}   # structured result


def pct_change(old: Decimal, new: Decimal) -> Decimal:
    if old == 0:                                       # avoid divide by zero
        raise ValueError("old value is zero")
    return ((new - old) / old * 100).quantize(Decimal("0.1"))   # percent, 1 decimal


def numbers_in(text: str) -> set[str]:
    return set(re.findall(r"\d[\d,]*\.?\d*", text.replace(",", "")))   # extract numeric tokens


def verify(text: str, facts: dict[str, str]) -> bool:
    """Every number the model wrote must come from our facts."""
    allowed = {v.rstrip("0").rstrip(".") if "." in v else v for v in facts.values()}   # normalise facts
    found = {n.rstrip("0").rstrip(".") if "." in n else n for n in numbers_in(text)}   # normalise text
    return found <= allowed                            # subset check


async def explain_spending(user_id: str, llm) -> str:
    """Fetch, calculate, draft, verify."""
    feb, mar = await asyncio.gather(get_spending(user_id, "2025-02"), get_spending(user_id, "2025-03"))   # parallel tools
    f_old, f_new = Decimal(feb["by_category"]["food"]), Decimal(mar["by_category"]["food"])   # exact values
    facts = {"old": str(f_old), "new": str(f_new), "pct": str(pct_change(f_old, f_new))}      # facts for LLM
    draft = await llm(f"Explain this using only these numbers: {facts}")   # model writes text
    if not verify(draft, facts):                       # guard against invented numbers
        return f"Food spending went from {f_old} to {f_new} ({facts['pct']}%)."   # safe template fallback
    return draft                                       # verified draft
```

---

## 🟠 FastAPI Integration
Authenticate, scope every query to the caller, rate limit, and return the facts used alongside the text so the UI can show them.

```python
from fastapi import FastAPI, Depends                   # FastAPI
from pydantic import BaseModel                         # models

app = FastAPI()                                        # app


class Q(BaseModel):
    question: str                                      # user question


async def user() -> str:
    return "u1"                                        # stub: verify JWT in prod


@app.post("/finance/ask")
async def ask(q: Q, uid: str = Depends(user)) -> dict:
    # text = await explain_spending(uid, llm)          # real call
    return {"answer": "stub", "facts": {}, "disclaimer": "Informational only, not financial advice."}
```

---

## 🔗 LangChain / LangGraph Connection
Expose tools with `@tool` and let a tool-calling agent use them. Add a LangGraph node after the LLM that runs `verify` and loops back or falls back to a template when it fails. For anything that moves money, use `interrupt` for explicit user/human approval.

```python
# LangChain tools (pip install langchain-core)
from langchain_core.tools import tool                  # decorator


@tool
def get_balance(account_id: str) -> str:
    """Return the account balance as an exact decimal string."""   # tool description for the model
    return "12500.50"                                  # stub


# agent = create_react_agent(model, [get_balance])     # from langgraph.prebuilt; model = chat model
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using float for money
✅ Correct: use `Decimal` (or integer paise/cents).

```python
# Wrong: total = 0.1 + 0.2  -> 0.30000000000000004
# Right: total = Decimal("0.1") + Decimal("0.2")  -> Decimal("0.3")
```

❌ Mistake 2: Letting the model do arithmetic
✅ Correct: call a calculator tool and verify numbers in the final text.

❌ Mistake 3: Giving write tools (transfer money) with no confirmation
✅ Correct: separate read tools from write tools, require explicit user confirmation and limits, log everything.

---

## 🧠 Tricky Interview Question
**Q**: "The assistant says the user's portfolio is up 12.5%, but the real figure is 11.9%. Tools were used. What went wrong?"

**Answer**: Possible causes: the LLM re-computed or rounded a number instead of copying it; tool returned data for a different period or currency; time-weighted vs simple return confusion; stale cache. Fixes: compute metrics in code with a clear definition, pass them as facts, run a number verifier, include period and currency with each figure, and test with golden cases. Also store the tool outputs in the audit log to reproduce the issue.

---

## ⚫ Interview Questions + Answers

Q1: Why not let the LLM calculate?
A1: LLMs predict text and can make arithmetic errors. Code is exact and testable.

Q2: Why Decimal instead of float?
A2: Binary floats cannot represent many decimal fractions exactly, causing rounding errors in money.

Q3: What is an audit trail in this system?
A3: A record of user, input, tool calls, data returned, model and prompt version, and output, so any answer can be explained to auditors.

Q4: How do you handle fraud detection with LLMs?
A4: Use classic ML or rules for scoring (fast, cheap). Use the LLM to summarise evidence for an analyst, never as the sole decision-maker for blocking accounts.

Q5: (Hard) How do you manage risk when advice-like questions come in ("should I buy this stock?")?
A5: Classify the intent; route advice requests to a compliant flow with disclaimers or refuse and offer factual data; keep prompts and outputs reviewed by compliance; log and monitor; avoid personalised recommendations unless the product is licensed and supervised. Check the local regulation (for example SEBI in India, SEC/FINRA in the US).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Explaining reports, categorising transactions, summarising filings, analyst support

❌ Avoid when:
- Autonomous trading or money movement without checks
- Exact figures required but no reliable data source exists

---

## 📊 Visual Diagram
```
 User ─▶ Auth/scope ─▶ LLM (plan) ─▶ Tool: SQL/API (read-only)
                                           │ exact data
                                  Calculator (Decimal)
                                           │ facts
                          LLM writes explanation from facts
                                           │
                       Number verifier ──✗──▶ template fallback
                                           │✓
                         Answer + facts + disclaimer ─▶ Audit log
```

---

## 💰 Cost Impact
Tool-using flows take 2-3 LLM calls (plan, explain, maybe retry), plus tool results in the prompt. Large tables inflate tokens; send aggregates, not raw rows (illustrative).
Optimize: pre-aggregate in SQL, return only needed columns, cache frequent reports, small model for routing, template responses for common questions (no LLM call), cap tool loop steps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Decimal | Exact decimal number type | सटीक दशमलव type |
| Tool calling | Model asks code to run a function | Model code से function चलवाता है |
| Verifier | Checks output against facts | Output को facts से जाँचने वाला |
| Audit trail | Record for regulators | नियामकों के लिए रिकॉर्ड |
| Read-only tool | Cannot change data | जो data नहीं बदल सकता |
| Compliance | Following financial regulations | वित्तीय नियमों का पालन |

---

## ⚡ 3-Line Summary
English: Numbers come from tools and calculators, never from model memory. Use Decimal, verify every figure in the final text, and log everything. Separate read tools from write tools and require approval for money movement.
Hindi: Numbers tools और calculators से आते हैं, model की याददाश्त से नहीं। Decimal इस्तेमाल करो, final text का हर figure verify करो और सब कुछ log करो। Read और write tools अलग रखो और पैसे के लेन-देन पर approval लो।

---

## ➡️ Next Topic
**541. Dockerizing AI Apps**: package these services so they run the same everywhere.
