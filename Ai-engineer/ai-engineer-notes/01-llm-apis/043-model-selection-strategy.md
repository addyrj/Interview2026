---

# 043. Model Selection Strategy
# हिंदी में: Model चुनने की Strategy

---

## 🔵 Simple Definition (English)
Model selection strategy is a repeatable way to pick the right LLM for each task. You compare quality, cost, latency, context size and features (JSON mode, tools, vision). The goal: use the cheapest model that is good enough, and measure it with your own test set.

## 🔵 सरल परिभाषा (Hindi)
Model selection strategy यानी हर task के लिए सही LLM चुनने का एक तय तरीका। आप quality, cost, latency, context size और features (JSON mode, tools, vision) compare करते हैं। लक्ष्य: सबसे सस्ता model जो "काफ़ी अच्छा" हो, और इसे अपने test set से measure करो।

---

## 🔴 Problem it Solves
- Teams pick "the best" model (biggest, most famous) for everything and pay 10-30x more than needed.
- Teams pick a tiny model for a hard task and get wrong answers.
- Choice is based on leaderboards, not on the team's own data.
- A strategy gives a fair, repeatable decision that can be re-run when new models launch.

## 🔴 यह क्यों बना? (Hindi)
- Team हर काम के लिए सबसे बड़ा model चुन लेती है और 10-30x ज़्यादा पैसा देती है।
- कभी hard task के लिए छोटा model चुन लिया जाता है और जवाब गलत आते हैं।
- Choice leaderboard पर होती है, अपने data पर नहीं।
- Strategy से decision fair और दोबारा चलाने लायक बनता है — नया model आए तो फिर test कर लो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define the task and the success metric (accuracy, format validity, latency)
Step 2 → Build a golden test set (50-200 real examples with expected answers)
Step 3 → Shortlist 3-4 candidates (one small, one medium, one large)
Step 4 → Run all candidates on the golden set, record quality, tokens, latency
Step 5 → Compute cost per 1,000 requests for each candidate
Step 6 → Pick the cheapest model that passes the quality bar
Step 7 → Add routing: easy requests -> small model, hard requests -> large model
Step 8 → Re-evaluate every few months or when a new model is released
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Task और success metric तय करो (accuracy, format validity, latency)
Step 2 → Golden test set बनाओ (50-200 असली examples, expected answers के साथ)
Step 3 → 3-4 candidates चुनो (एक small, एक medium, एक large)
Step 4 → सभी को golden set पर चलाओ, quality/tokens/latency note करो
Step 5 → हर candidate की 1,000 requests की cost निकालो
Step 6 → सबसे सस्ता model चुनो जो quality bar पास करे
Step 7 → Routing जोड़ो: आसान request -> small model, कठिन -> large model
Step 8 → हर कुछ महीने या नया model आने पर दोबारा evaluate करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The system has three tasks. (1) Extract product name from a messy invoice line: easy, a small model like `gpt-4o-mini` gets 97% on the golden set. (2) Decide the 8-digit HS code with legal reasoning: hard, small model gets 71%, a larger model gets 90%. (3) Write a short explanation for the customs officer: medium. So we use a small model for task 1 and 3, and the large model only for task 2. Overall cost falls by about 70% with the same final accuracy.

**Zomato-style**: A "summarise 200 reviews of this restaurant" feature uses a cheap long-context model; the "chat support" bot uses a fast model because latency matters more than depth.

## 🟡 Real Example Hindi mein
**Tariff System**: तीन tasks हैं। (1) गंदी invoice line से product name निकालना: आसान, `gpt-4o-mini` golden set पर 97% देता है। (2) 8-digit HS code तय करना (legal reasoning): कठिन, small model 71%, बड़ा model 90%। (3) Customs officer के लिए छोटी explanation: medium। इसलिए task 1 और 3 small model से, और task 2 सिर्फ़ बड़े model से। Final accuracy वही, cost लगभग 70% कम।

**Zomato-style**: "200 reviews का summary" के लिए सस्ता long-context model; "chat support" bot के लिए fast model क्योंकि latency ज़्यादा ज़रूरी है।

---

## 💻 Code Example — Basic
```python
# Basic: score candidate models on a golden set (mock LLM, runs offline)
from dataclasses import dataclass  # lightweight data container

@dataclass  # holds one candidate model's info
class Candidate:
    name: str  # model name
    price_in: float  # USD per 1M input tokens (illustrative)
    price_out: float  # USD per 1M output tokens (illustrative)
    skill: float  # mock "accuracy" between 0 and 1

# Golden set: (input text, expected HS chapter) pairs
GOLDEN: list[tuple[str, str]] = [
    ("Apple iPhone 15 smartphone", "85"),  # electronics
    ("Cotton t-shirt men", "61"),  # apparel
    ("Basmati rice 5kg", "10"),  # cereals
    ("Laptop bag leather", "42"),  # leather goods
]

def mock_llm(candidate: Candidate, text: str, expected: str, i: int) -> str:
    # Deterministic fake: correct if (i / total) is below skill
    return expected if (i / len(GOLDEN)) < candidate.skill else "00"

def evaluate(candidate: Candidate) -> dict[str, float]:
    correct = 0  # counter for right answers
    for i, (text, expected) in enumerate(GOLDEN):  # loop over golden set
        answer = mock_llm(candidate, text, expected, i)  # call the (mock) model
        correct += int(answer == expected)  # count a hit
    accuracy = correct / len(GOLDEN)  # fraction correct
    # Assume 400 input + 50 output tokens per request
    cost_1k = 1000 * (400 * candidate.price_in + 50 * candidate.price_out) / 1_000_000
    return {"accuracy": accuracy, "cost_per_1k": round(cost_1k, 4)}  # result row

candidates = [
    Candidate("small", 0.15, 0.60, 0.75),  # cheap model
    Candidate("large", 2.50, 10.00, 1.0),  # expensive model
]
for c in candidates:  # evaluate each candidate
    print(c.name, evaluate(c))  # show the comparison
# Rule: pick the cheapest one whose accuracy >= your bar (e.g. 0.9)
```

## 💻 Code Example — Advanced
```python
# Production-style: async evaluation harness with cost, latency and error handling
import asyncio  # run many requests concurrently
import time  # measure latency
from dataclasses import dataclass, field  # structured results
from openai import AsyncOpenAI, APIError  # openai>=1 async client

client = AsyncOpenAI()  # reads OPENAI_API_KEY from environment

@dataclass
class EvalResult:
    model: str  # model under test
    accuracy: float  # fraction correct
    avg_latency_s: float  # mean seconds per call
    cost_per_1k: float  # USD per 1000 requests
    errors: int = 0  # failed calls
    details: list[str] = field(default_factory=list)  # debug notes

PRICES: dict[str, tuple[float, float]] = {  # illustrative USD per 1M tokens (in, out)
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
}

async def classify(model: str, text: str) -> tuple[str, int, int, float]:
    start = time.perf_counter()  # start timer
    resp = await client.chat.completions.create(  # one API call
        model=model,
        messages=[
            {"role": "system", "content": "Return only the 2-digit HS chapter."},
            {"role": "user", "content": text},
        ],
        max_tokens=5,  # answer is tiny, cap output cost
        temperature=0,  # deterministic for evaluation
    )
    latency = time.perf_counter() - start  # elapsed seconds
    usage = resp.usage  # token usage object
    answer = (resp.choices[0].message.content or "").strip()  # model answer
    return answer, usage.prompt_tokens, usage.completion_tokens, latency

async def evaluate(model: str, golden: list[tuple[str, str]]) -> EvalResult:
    sem = asyncio.Semaphore(5)  # limit concurrency to avoid rate limits

    async def one(text: str, expected: str):
        async with sem:  # wait for a free slot
            try:
                return expected, await classify(model, text)  # run call
            except APIError as exc:  # API failure: do not crash whole eval
                return expected, exc

    rows = await asyncio.gather(*(one(t, e) for t, e in golden))  # run all
    ok, errors, tin, tout, lat = 0, 0, 0, 0, 0.0  # accumulators
    for expected, out in rows:
        if isinstance(out, Exception):  # count failures
            errors += 1
            continue
        answer, pin, pout, latency = out  # unpack tuple
        ok += int(answer == expected)  # correct?
        tin, tout, lat = tin + pin, tout + pout, lat + latency  # sum
    n = max(len(rows) - errors, 1)  # avoid division by zero
    p_in, p_out = PRICES[model]  # price per 1M
    cost_1k = 1000 * ((tin / n) * p_in + (tout / n) * p_out) / 1_000_000
    return EvalResult(model, ok / n, lat / n, round(cost_1k, 4), errors)

async def pick_model(golden: list[tuple[str, str]], bar: float = 0.9) -> str:
    results = [await evaluate(m, golden) for m in PRICES]  # test all models
    good = [r for r in results if r.accuracy >= bar]  # pass quality bar
    if not good:  # nobody passed
        raise RuntimeError("No model meets the quality bar; improve prompt or data")
    return min(good, key=lambda r: r.cost_per_1k).model  # cheapest passing

# asyncio.run(pick_model(GOLDEN_SET))  # run with a real API key
```

---

## 🟠 FastAPI Integration
Expose a router endpoint: the API picks a model per request based on a difficulty hint, so the client does not need to know model names. The chosen model is returned for observability.

```python
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel, Field  # validation (pydantic v2)
from openai import AsyncOpenAI, APIError  # async client

app = FastAPI()  # create app
client = AsyncOpenAI()  # shared client

class ClassifyIn(BaseModel):
    description: str = Field(min_length=3, max_length=2000)  # product text
    high_stakes: bool = False  # True when legal accuracy matters

def choose_model(req: ClassifyIn) -> str:
    # Simple rule router: big model only for high stakes or long input
    if req.high_stakes or len(req.description) > 1200:
        return "gpt-4o"
    return "gpt-4o-mini"

@app.post("/classify")
async def classify(req: ClassifyIn) -> dict:
    model = choose_model(req)  # pick the model
    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": f"HS code for: {req.description}"}],
            max_tokens=100,
        )
    except APIError as exc:  # upstream failure -> 502
        raise HTTPException(status_code=502, detail=str(exc))
    return {"model": model, "answer": resp.choices[0].message.content,
            "tokens": resp.usage.total_tokens}  # token usage for cost tracking
```

---

## 🔗 LangChain / LangGraph Connection
LangChain makes models swappable: every chat model has the same `invoke/ainvoke` interface, so evaluation and routing code does not change. `init_chat_model` creates a model by name, and LangGraph can have a router node that picks a small or large model.

```python
from langchain.chat_models import init_chat_model  # provider-agnostic factory
from langchain_core.prompts import ChatPromptTemplate  # prompt template
from langchain_core.output_parsers import StrOutputParser  # to plain string

prompt = ChatPromptTemplate.from_template("HS chapter for: {item}")  # shared prompt
small = init_chat_model("gpt-4o-mini", model_provider="openai")  # cheap model
large = init_chat_model("gpt-4o", model_provider="openai")  # strong model

def build_chain(hard: bool):
    llm = large if hard else small  # route by difficulty
    return prompt | llm | StrOutputParser()  # LCEL chain

# result = await build_chain(hard=False).ainvoke({"item": "cotton shirt"})
# In LangGraph: add a "router" node that returns "small" or "large",
# then use add_conditional_edges to send the state to the right LLM node.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Choosing by leaderboard or brand only
✅ Correct: Evaluate on your own golden set.

```python
# Wrong: model = "biggest-model-available"  # no evidence
# Right: pick_model(golden_set, bar=0.9)  # measured on YOUR data
```

❌ Mistake 2: Comparing only price per token
✅ Correct: Compare cost per correct answer, including retries and token usage (a cheap model that needs 3 retries or long prompts can cost more).

```python
# Wrong: cheapest = min(models, key=lambda m: m.price_out)
# Right: cost_per_correct = total_cost / correct_answers
```

---

## 🧠 Tricky Interview Question
**Q**: "A new model launches that is 2x cheaper than your current one and tops the benchmarks. Your manager says switch today. What do you do?"

**Answer**: Do not switch blindly. Benchmarks measure general tasks, not your tariff data and prompts. Run the new model on the golden set, compare accuracy, format validity, latency and cost per correct answer. Test prompts too: prompts tuned for one model may behave differently on another. Then roll out with a canary (5% traffic) and a fallback to the old model. Switch fully only if the metrics hold.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Why not always use the biggest model?
A1: It costs more and is slower. Many tasks (extraction, classification, simple Q&A) are solved equally well by small models. Use the biggest only where it measurably helps.

Q2: [Easy] What is a golden set?
A2: A fixed collection of real inputs with known correct outputs. It is used to compare models and prompts fairly and to catch regressions.

Q3: [Medium] Which factors do you compare besides accuracy?
A3: Cost per 1M tokens, latency (time to first token and total), context window size, rate limits, supported features (structured output, tool calling, vision), data-privacy terms, and region availability.

Q4: [Medium] What is model routing?
A4: Sending each request to a different model depending on difficulty, user tier, or task type. A cheap classifier or rule decides. It cuts cost while keeping quality for hard cases.

Q5: [Hard] How do you keep the model choice from rotting over time?
A5: Treat it as a continuous process: pin model versions, keep the golden set in CI, run evals nightly or on every prompt change, log production quality signals (user thumbs, human review samples), and re-run the comparison when providers release or deprecate models. Abstract the model behind a config so switching is a one-line change.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have more than one task or a large monthly bill
- A new model is released or an old one is deprecated
- You need to justify cost to management

❌ Avoid when:
- Prototype phase with 10 requests a day (just pick a good default)
- You have no test data yet (build the golden set first)

---

## 📊 Visual Diagram
```
 Task + success metric
          |
          v
 Golden set (50-200 examples)
          |
   +------+-------+---------+
   v              v         v
 small          medium     large
   |              |         |
   +------> accuracy / latency / cost <------+
                  |
                  v
     cheapest model that passes quality bar
                  |
                  v
       Router: easy -> small, hard -> large
```

---

## 💰 Cost Impact
- Token usage: model choice does not change token count much, but changes price per token by up to 30x (illustrative: small about $0.15 in / $0.60 out per 1M; large about $2.50 / $10).
- Example: 1M requests a month at 400 in + 50 out tokens. Small: about $90. Large: about $1,500. Routing 80% to small: about $90*0.8 + $1,500*0.2 = $372.
- Optimise: route by difficulty, cap `max_tokens`, shorten prompts, cache repeated answers, use Batch API for offline jobs. Always check current provider pricing; numbers change.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Golden set | Test inputs with correct answers | सही जवाबों वाला test set |
| Model routing | Choose model per request | हर request के लिए model चुनना |
| Quality bar | Minimum acceptable accuracy | न्यूनतम स्वीकार्य accuracy |
| Canary rollout | Send small traffic to new model | थोड़े traffic पर नया model आज़माना |
| Cost per correct answer | Total cost / correct outputs | सही जवाब पर खर्च |
| Context window | Max tokens model can read | Model कितना पढ़ सकता है |

---

## ⚡ 3-Line Summary
English: Pick models using your own golden set, not hype. Choose the cheapest model that passes the quality bar and route hard cases to a bigger one. Re-evaluate regularly because models and prices change.
Hindi: Model अपने golden set से चुनो, hype से नहीं। सबसे सस्ता model लो जो quality bar पास करे और कठिन cases बड़े model को भेजो। Models और prices बदलते रहते हैं, इसलिए बार-बार evaluate करो।

---

## ➡️ Next Topic
**044. Cost Optimization — Models** — once the right model is chosen, how to cut the bill further with caching, prompt trimming, routing and batching.
