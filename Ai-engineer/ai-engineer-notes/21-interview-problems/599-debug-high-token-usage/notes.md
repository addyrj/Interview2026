---

# 599. Debug High Token Usage
# हिंदी में: ज़्यादा Token Usage Debug करना

---

## 🔵 Simple Definition (English)
Debugging high token usage means breaking each request into parts (system prompt, history, retrieved context, user input, output), finding which part dominates cost, and shrinking it without hurting quality.

## 🔵 सरल परिभाषा (Hindi)
ज़्यादा token usage debug करने का मतलब है हर request को हिस्सों में बाँटना (system prompt, history, retrieved context, user input, output), देखना कौन सा हिस्सा सबसे ज़्यादा cost बना रहा है, और quality बिगाड़े बिना उसे घटाना।

---

## 🔴 Problem it Solves
The bill is a single number. Without a breakdown, teams cannot tell if cost comes from a long system prompt repeated on every call, ever-growing chat history, too many retrieved chunks, or verbose outputs.

## 🔴 यह क्यों बना? (Hindi)
Bill एक ही संख्या होती है। Breakdown के बिना पता नहीं चलता कि cost हर call में दोहराए जाने वाले लंबे system prompt, बढ़ती chat history, ज़्यादा chunks या लंबे outputs से आ रही है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Log per-call token parts: system, history, context, user, output
Step 2 → Group by endpoint (or feature / user) and compute cost
Step 3 → Rank by total cost; look at each part's share of input
Step 4 → Match pattern to fix:
         history big   -> trim / summarise
         system big    -> shorten / prompt caching
         context big   -> lower top-k, rerank, compress
         output big    -> max_tokens, concise format
Step 5 → Apply, re-measure, compare quality on an eval set
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर call के token parts log करो
Step 2 → Endpoint/feature/user से group करके cost निकालो
Step 3 → Cost से rank करो; input में हर हिस्से का share देखो
Step 4 → Pattern के हिसाब से fix: history -> trim/summarise, system -> छोटा/caching, context -> top-k कम, output -> max_tokens
Step 5 → लागू करो, दोबारा नापो, eval set पर quality compare करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: logs show `/summarize` sends 12,000 context tokens per call (cost $0.0487 for one call in the sample), `/chat` carries 6,000-9,000 history tokens, `/classify` has a 900-token system prompt repeated every call. Fixes: chunk-level retrieval for summarise, rolling summary for chat, prompt caching for the static classify prompt.

**Amazon-style**: a support chat that resends the whole order history on every turn; send only fields relevant to the question.

## 🟡 Real Example Hindi mein
**Tariff System**: Logs दिखाते हैं `/summarize` हर call में 12,000 context tokens भेजता है, `/chat` में 6,000-9,000 history tokens हैं, `/classify` में 900-token system prompt हर बार दोहराया जाता है। Fix: summarise के लिए chunk retrieval, chat के लिए rolling summary, classify के लिए prompt caching।

**Amazon**: Support chat हर turn पर पूरी order history भेजती है; सिर्फ ज़रूरी fields भेजो।

---

## 💻 Code Example — Basic
```python
# Which part of the input is biggest? (illustrative numbers)
parts: dict[str, int] = {"system": 900, "history": 6000, "context": 1500, "user": 50}  # tokens

total: int = sum(parts.values())                    # total input tokens
for name, n in sorted(parts.items(), key=lambda kv: -kv[1]):   # biggest first
    print(f"{name:<8}{n:>6}  {n / total:6.1%}")    # share of the input
```

## 💻 Code Example — Advanced
Full file: `main.py` (`Call` dataclass, `analyse`, `advise`). Prices are illustrative. Observed output:
```
/chat       calls=2 cost=$0.0702
/summarize  calls=1 cost=$0.0487
/classify   calls=2 cost=$0.0094
/classify: long system prompt dominates -> shorten or use prompt caching
/chat: history is >50% of input -> summarise/trim old turns
/summarize: retrieved context huge -> lower top-k, rerank, compress
/summarize: long outputs -> set max_tokens, ask for concise format
```
```python
# Excerpt from main.py
def advise(stats: dict[str, dict[str, float]]) -> list[str]:
    tips = []
    for ep, a in stats.items():                      # per endpoint
        inp = a["system_tokens"] + a["history_tokens"] + a["context_tokens"] + a["user_tokens"]
        if a["history_tokens"] / inp > 0.5:          # history dominates input
            tips.append(f"{ep}: history is >50% of input -> summarise/trim old turns")
        if a["output_tokens"] / a["calls"] > 500:    # verbose outputs
            tips.append(f"{ep}: long outputs -> set max_tokens, ask for concise format")
    return tips
```
Async: log lines are written in the request path; use a background task or queue so logging never blocks answers.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, BackgroundTasks
from main import Call, analyse, advise                 # our module

app = FastAPI()
LOGS: list[Call] = []                                  # use a real store in production


def log_call(c: Call) -> None:
    LOGS.append(c)                                     # persist for later analysis


@app.post("/chat")
async def chat(msg: str, bg: BackgroundTasks) -> dict:
    # real code: read response.usage; numbers below are placeholders
    bg.add_task(log_call, Call("/chat", 400, 1000, 0, len(msg) // 4, 100))
    return {"ok": True}


@app.get("/admin/token-report")
async def report() -> dict:
    if not LOGS:                                       # nothing to analyse yet
        return {"tips": []}
    return {"tips": advise(analyse(LOGS))}
```

---

## 🔗 LangChain / LangGraph Connection
Use `trim_messages` to cap history inside a chain, and callbacks for usage logging.

```python
from langchain_core.messages import HumanMessage, AIMessage, trim_messages

history = [HumanMessage("q1 " * 100), AIMessage("a1 " * 100), HumanMessage("q2")]
trimmed = trim_messages(
    history,
    max_tokens=50,                                      # budget for history
    token_counter=lambda ms: sum(len(str(m.content)) // 4 for m in ms),  # approx counter
    strategy="last",                                    # keep the most recent turns
)
```
In LangGraph, add a "summarise old messages" node when state exceeds a threshold.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Sending the full chat history every turn.
✅ Correct: last N turns plus a rolling summary.
```python
# Wrong
messages = full_history + [new_msg]
# Right
messages = [summary_msg] + full_history[-6:] + [new_msg]
```

❌ Mistake 2: No `max_tokens`, so a runaway answer costs a lot.
✅ Correct: set a cap and request a concise format.

❌ Mistake 3: Cutting prompts blindly and losing quality. Always compare against an eval set before and after.

---

## 🧠 Tricky Interview Question
**Q**: "You halved the prompt but total cost rose. How?"

**Answer**: Possible causes: the shorter prompt made the model produce longer outputs (output tokens cost more); quality dropped so users retried; you broke prompt-cache prefix reuse (static part no longer first/identical); or retries and tool-call loops increased calls. Compare cost per successful task, not per call.

---

## ⚫ Interview Questions + Answers

Q1: What are the parts of a request's tokens?
A1: System prompt, history, retrieved context, user input, and output.

Q2: Which tokens are usually costlier?
A2: Output tokens typically have a higher per-token price than input tokens.

Q3: How does prompt caching help?
A3: A repeated static prefix (system prompt, few-shot examples) is billed at a reduced rate after the first call; put static text first.

Q4: How do you shrink retrieved context?
A4: Lower top-k, rerank and keep the best, smaller chunks, remove boilerplate, or compress/summarise chunks.

Q5 (Hard): Cost per user varies 100x. How do you investigate and control?
A5: Group logs by user and feature; find power users or loops (agent retries, long histories); add per-user budgets and rate limits, cap agent steps and `max_tokens`, route simple queries to a small model, and alert on anomalies.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Bill grows faster than traffic; margins matter

❌ Avoid when:
- Tokens are tiny relative to engineering cost; do not over-optimise early

---

## 📊 Visual Diagram
```
 one /chat call (input 9,950 tokens)
 ┌──────────────────────────────────────────────────┐
 │ system 400 │ history 9000 ████████████ │ ctx 1500 │ user 50 │
 └──────────────────────────────────────────────────┘
        biggest share = history  ->  trim / summarise
 + output 500 tokens (priced higher per token)
```

---

## 💰 Cost Impact
Using the illustrative prices in `main.py` ($3 per 1M input, $15 per 1M output): the `/summarize` sample call (12,230 input, 800 output) costs about $0.0487. Cutting context from 12,000 to 3,000 tokens saves 9,000 x $3 / 1M = $0.027 per call, about 55 percent of that call. Combine with prompt caching, a small model for easy routes, and output caps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Input tokens | Tokens sent to model | Model को भेजे tokens |
| Output tokens | Tokens generated | Model के बनाए tokens |
| Prompt caching | Discount on repeated prefix | दोहराए prefix पर छूट |
| Rolling summary | Short summary of old turns | पुरानी बातों का छोटा सार |
| max_tokens | Output cap | Output की सीमा |

---

## ⚡ 3-Line Summary
English: Break tokens into parts per endpoint and find the dominant one. Trim history, shrink context, cache static prompts, cap outputs. Verify quality after every cut.
Hindi: हर endpoint के tokens हिस्सों में बाँटकर सबसे बड़ा हिस्सा ढूँढो। History trim, context छोटा, static prompt cache, output cap करो। हर कटौती के बाद quality जाँचो।

---

## ➡️ Next Topic
**600. Design: Complete AI System** — combine everything into one end-to-end design.
