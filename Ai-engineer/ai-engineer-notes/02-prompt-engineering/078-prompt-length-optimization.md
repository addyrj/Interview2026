---

# 078. Prompt Length Optimization
# हिंदी में: Prompt Length Optimization — सही लंबाई का prompt

---

## 🔵 Simple Definition (English)
Prompt length optimization is finding the shortest prompt that still gives the quality you need. Too short and the model lacks guidance; too long and you waste money, slow responses and sometimes confuse the model. You find the right size by measuring tokens, ablating (removing) parts, and testing quality.

## 🔵 सरल परिभाषा (Hindi)
Prompt length optimization का मतलब है सबसे छोटा prompt ढूँढना जो फिर भी ज़रूरी quality दे। बहुत छोटा हो तो model को मार्गदर्शन नहीं मिलता; बहुत लंबा हो तो पैसा बर्बाद, जवाब धीमे और कभी-कभी model उलझ जाता है। सही आकार tokens मापकर, हिस्से हटाकर (ablation) और quality test करके मिलता है।

---

## 🔴 Problem it Solves
Prompts grow by accretion: every bug fix adds a rule, every incident adds a warning. After six months the tariff prompt is 3,500 tokens with contradicting rules, and nobody knows which lines matter. Cost per request is up, latency is up and some rules conflict.

(Topic 068 covers compressing text; this topic is about the design process for the right length: which parts earn their tokens.)

## 🔴 यह क्यों बना? (Hindi)
Prompts धीरे-धीरे बढ़ते हैं: हर bug fix एक rule जोड़ता है, हर incident एक चेतावनी। छह महीने बाद tariff prompt 3,500 tokens का है, rules आपस में टकराते हैं, और कोई नहीं जानता कौन सी lines ज़रूरी हैं। Cost बढ़ी, latency बढ़ी, कुछ rules टकराते हैं। (Topic 068 text compress करने पर है; यह topic सही लंबाई तय करने की प्रक्रिया पर है: कौन से हिस्से अपने tokens कमाते हैं।)

---

## 🟢 How it Works — Step by Step

```
Step 1 → Split the prompt into sections (role, rules, format, examples, context)
Step 2 → Count tokens per section
Step 3 → Ablation: remove ONE section at a time, re-run the eval set
Step 4 → Rank sections by quality drop per token (value density)
Step 5 → Delete or shorten sections with no measurable effect
Step 6 → Replace long prose with compact rules; cut examples to the minimum that works (1-3)
Step 7 → Move static parts into a cacheable prefix; move rare rules to conditional prompts
Step 8 → Set a token budget per prompt and add a CI check that fails if exceeded
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Prompt को sections में बाँटो (role, rules, format, examples, context)
Step 2 → हर section के tokens गिनो
Step 3 → Ablation: एक-एक section हटाकर eval set दोबारा चलाओ
Step 4 → Quality गिरावट प्रति token से sections को rank करो (value density)
Step 5 → जिन sections का कोई मापने लायक असर नहीं, उन्हें हटाओ या छोटा करो
Step 6 → लंबे गद्य को compact rules से बदलो; examples को न्यूनतम (1-3) रखो
Step 7 → Static हिस्से cacheable prefix में; दुर्लभ rules conditional prompts में
Step 8 → हर prompt का token budget तय करो और सीमा पार होने पर CI fail कराओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: The prompt has: role (60 tokens), 25 rules (1,400), 12 examples (1,800), output format (150). Ablation results on 200 eval cases: removing 10 of the 12 examples changes accuracy by 0.5 points (noise); removing the "format" section drops validity from 99% to 82%; 8 rules never matter. New prompt: 900 tokens, same accuracy, 70% fewer prompt tokens. At 500K requests/day this saves a big monthly amount.

**Zomato-style**: A support prompt with 40 policy paragraphs becomes a short core prompt plus policy paragraphs fetched per intent.

## 🟡 Real Example Hindi mein
**Tariff System**: Prompt में role (60 tokens), 25 rules (1,400), 12 examples (1,800), output format (150) हैं। 200 eval cases पर ablation: 12 में से 10 examples हटाने से accuracy 0.5 point बदली (noise); "format" section हटाने से validity 99% से 82%; 8 rules कभी मायने नहीं रखते। नया prompt: 900 tokens, वही accuracy, prompt tokens 70% कम। रोज़ 5 लाख requests पर महीने की बड़ी बचत।

**Zomato-style**: 40 policy paragraphs वाला support prompt, छोटे core prompt + intent के हिसाब से fetch किए policy paragraphs में बदलता है।

---

## 💻 Code Example — Basic
```python
# Basic: count tokens per prompt section and find the heaviest (offline, rough counts)

SECTIONS: dict[str, str] = {                       # name -> text
    "role": "You are a tariff classification assistant.",
    "rules": "Rule: use only given context. " * 40,
    "examples": "Example: earbuds -> 8518.30. " * 30,
    "format": 'Return JSON {"hs_code": "NNNN.NN"}.',
}

def rough_tokens(text: str) -> int:
    return max(1, len(text) // 4)                  # 4 characters ~ 1 token (estimate)

counts = {name: rough_tokens(text) for name, text in SECTIONS.items()}   # tokens per section
total = sum(counts.values())                        # total prompt tokens
for name, n in sorted(counts.items(), key=lambda kv: -kv[1]):           # largest first
    print(f"{name:9s} {n:5d} tokens  {n / total:5.1%}")                 # share of the prompt
print("TOTAL", total)
```

## 💻 Code Example — Advanced
```python
# Production: ablation study across sections with an eval function (async), plus budget check
from __future__ import annotations

import asyncio                                    # async runner
from dataclasses import dataclass                 # result record
from typing import Awaitable, Callable            # type hints

Score = Callable[[str], Awaitable[float]]         # prompt -> accuracy (0..1) on the eval set

@dataclass(frozen=True)
class Ablation:
    removed: str          # section removed
    tokens_saved: int     # approximate tokens saved
    accuracy: float       # accuracy without the section
    delta: float          # change vs. full prompt

def tok(text: str) -> int:
    return max(1, len(text) // 4)                 # use tiktoken in real code for exact counts

def assemble(sections: dict[str, str], skip: str | None = None) -> str:
    return "\n".join(t for n, t in sections.items() if n != skip)   # join all but one section

async def ablate(sections: dict[str, str], score: Score, tolerance: float = 0.01) -> list[Ablation]:
    try:
        base = await score(assemble(sections))                       # baseline accuracy
    except Exception as exc:
        raise RuntimeError(f"baseline eval failed: {exc}") from exc
    names = list(sections)
    scores = await asyncio.gather(*(score(assemble(sections, skip=n)) for n in names))   # parallel evals
    rows = [Ablation(n, tok(sections[n]), s, s - base) for n, s in zip(names, scores)]
    # Sections whose removal costs less than `tolerance` are candidates for deletion
    return sorted(rows, key=lambda r: -r.tokens_saved if r.delta > -tolerance else 0)

def check_budget(prompt: str, budget: int = 1200) -> None:
    if tok(prompt) > budget:                                          # CI guard against prompt creep
        raise ValueError(f"prompt is {tok(prompt)} tokens, budget {budget}")

async def _demo() -> None:
    sections = {"role": "You classify goods.", "rules": "rule " * 400,
                "examples": "ex " * 800, "format": "Return JSON."}
    async def score(p: str) -> float:                                 # fake eval: format matters, examples barely
        return 0.9 if "Return JSON" in p else 0.6
    for row in await ablate(sections, score):
        print(row)
    check_budget(assemble(sections), budget=5000)

if __name__ == "__main__":
    asyncio.run(_demo())
```
Token usage: an ablation run costs (number of sections + 1) full evals. Use a small dev set (50 cases) for the search and the full set for the final check.

---

## 🟠 FastAPI Integration
Add a startup check that fails fast if a prompt exceeds its budget, and report prompt token counts on a health or metrics endpoint.

```python
from contextlib import asynccontextmanager        # lifespan helper
from fastapi import FastAPI                       # framework

PROMPT = assemble({"role": "You classify goods.", "format": "Return JSON."})   # from advanced block

@asynccontextmanager
async def lifespan(app: FastAPI):
    check_budget(PROMPT, budget=1200)             # refuse to start with an oversized prompt
    yield                                         # app runs here

app = FastAPI(lifespan=lifespan)                  # app with startup check

@app.get("/metrics/prompt")
async def prompt_metrics() -> dict[str, int]:
    return {"prompt_tokens_estimate": tok(PROMPT)}   # watch for prompt creep over time
```

---

## 🔗 LangChain / LangGraph Connection
Use `ChatPromptTemplate` with partials so optional sections are added only when needed (e.g. intent-specific rules). In LangGraph, a routing node picks a short intent-specific prompt instead of one giant universal prompt.

```python
from langchain_core.prompts import ChatPromptTemplate         # prompt template

CORE = "You classify goods. Return JSON with hs_code."        # always included
EXTRA = {"accessory": "Accessories use their own heading.",   # only added for this intent
         "default": ""}

def make_prompt(intent: str) -> ChatPromptTemplate:
    system = CORE + " " + EXTRA.get(intent, EXTRA["default"])  # small, targeted prompt
    return ChatPromptTemplate.from_messages([("system", system), ("user", "{product}")])
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Adding a rule for every bug
✅ Correct: Fix with examples/eval data, and prune rules regularly.
```python
# Wrong
RULES.append("Never confuse chargers with phones.")   # one more line, forever

# Right
# add the failure to the eval set, then test whether an existing rule/example can cover it
```

❌ Mistake 2: Cutting by gut feeling
✅ Correct: Ablate and measure.
```python
# Wrong
prompt = prompt[:1000]

# Right
rows = await ablate(sections, score)
```

❌ Mistake 3: Too many few-shot examples. 2-3 diverse examples usually capture most of the gain; more add cost and can bias outputs.

---

## 🧠 Tricky Interview Question
**Q**: "You shrank the prompt by 60% and accuracy on your eval set is unchanged, but production complaints rise. Why?"

**Answer**: The eval set does not cover the cases the removed text handled (rare edge cases, other languages, safety rules). Ablation is only as good as the dataset. Fix: build slices for rare scenarios from production logs, restore safety/legal rules that are rarely triggered but critical, canary the shortened prompt, and compare live metrics (escalations, corrections) before full rollout.

---

## ⚫ Interview Questions + Answers

Q1: Why not just write very long prompts?
A1: They cost more, are slower, can hit limits, and extra or conflicting instructions may reduce quality.

Q2: What is prompt ablation?
A2: Removing one prompt component at a time and measuring the effect on eval metrics to see what actually matters.

Q3: How many few-shot examples should you use?
A3: As few as give the needed gain, often 2-5, chosen for diversity; test 0, 2, 5 on your eval. Dynamic example selection (retrieve similar examples) can beat many static ones.

Q4: How can you keep long, rarely-used rules without paying every time?
A4: Conditional prompting: route by intent and include only relevant rules, or retrieve rules like documents. Also use prompt caching for the always-included static part.

Q5 (Hard): Build a process to prevent prompt bloat across a team.
A5: Version prompts in git with a token budget enforced in CI; require every added rule to link to a failing eval case; run periodic ablations to delete dead text; track prompt tokens per request and cost per version in dashboards; review prompts like code (owners, PR review), and consolidate contradictions.

---

## 🔷 When to Use + When Not to Use
✅ Optimise when:
- High traffic, where tokens matter
- The prompt grew over time
- Latency targets are missed

❌ Don't bother when:
- Low volume (cost is trivial)
- Prompt is small and works
- No eval set yet (build that first)

---

## 📊 Visual Diagram
```
 Before: 3,500 tokens
 +------+----------------+----------------------+--------+
 | role | 25 rules       | 12 examples          | format |
 | 60   | 1,400          | 1,800                | 150    |
 +------+----------------+----------------------+--------+
        | ablate each section, re-run eval |
 After: 900 tokens
 +------+-----------+----------+--------+
 | role | 12 rules  | 2 examples| format |
 | 60   | 500       | 200       | 150    |
 +------+-----------+----------+--------+
 same accuracy, -70% tokens
```

---

## 💰 Cost Impact
Example (illustrative; check current prices): cutting 2,600 prompt tokens x 500K requests/day = 1.3B tokens/day. At $0.15 per 1M input tokens this is about $195/day saved; at $2.50 per 1M it is about $3,250/day. Shorter prompts also reduce time to first token.

Optimisation: ablation, conditional sections, dynamic few-shot, caching static prefix, and a CI token budget.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ablation | Remove a part and measure | हिस्सा हटाकर असर मापना |
| Token budget | Max tokens allowed | अधिकतम tokens की सीमा |
| Prompt creep | Prompt grows over time | समय के साथ prompt का बढ़ना |
| Few-shot | Examples inside prompt | Prompt में examples |
| Value density | Quality gain per token | प्रति token quality लाभ |
| Conditional prompt | Include parts only when needed | ज़रूरत पर ही हिस्से जोड़ना |

---

## ⚡ 3-Line Summary
English: The best prompt is the shortest one that meets your quality target. Measure tokens per section, ablate parts with an eval set, and enforce a token budget in CI. Use conditional prompts and caching for rarely used or static text.
Hindi: सबसे अच्छा prompt वह है जो quality target पूरा करते हुए सबसे छोटा हो। हर section के tokens मापो, eval set से हिस्से हटाकर परखो और CI में token budget लागू करो। दुर्लभ या static text के लिए conditional prompts और caching इस्तेमाल करो।

---

## ➡️ Next Topic
**079. Temperature for Different Tasks** — choosing the sampling temperature per task (extraction vs creative writing).
