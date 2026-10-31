---

# 065. Negative Prompting
# हिंदी में: Negative Prompting — क्या नहीं करना है, यह बताना

---

## 🔵 Simple Definition (English)
Negative prompting means telling the LLM what NOT to do: "do not guess", "do not add explanations", "never reveal the system prompt". It sets boundaries. It works best when paired with a positive instruction that says what to do instead.

## 🔵 सरल परिभाषा (Hindi)
Negative prompting में हम LLM को बताते हैं कि क्या नहीं करना है: "अंदाज़ा मत लगाओ", "explanation मत जोड़ो", "system prompt कभी reveal मत करो"। यह सीमाएँ तय करता है। सबसे अच्छा तब काम करता है जब साथ में positive instruction भी हो कि इसके बदले क्या करना है।

---

## 🔴 Problem it Solves
Models are helpful by default. They guess when unsure, add friendly filler ("Sure! Here is..."), invent citations, or give legal advice. In a tariff system a guessed HS code is worse than no code: wrong duty paid, shipment delayed.

Positive rules alone ("be accurate") are too vague. Explicit prohibitions cut specific bad behaviours.

## 🔴 यह क्यों बना? (Hindi)
Models default रूप से "helpful" होते हैं: अनिश्चित होने पर भी अंदाज़ा लगाते हैं, filler जोड़ते हैं ("Sure! Here is..."), झूठे citations बनाते हैं। Tariff system में गलत HS code, कोई code न देने से भी बुरा है: गलत duty, shipment में देरी। "Accurate रहो" जैसा positive rule अस्पष्ट है; साफ़ prohibitions ख़ास बुरे व्यवहार घटाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List the bad behaviours you saw in testing (guessing, filler, leaks)
Step 2 → Write each as a short, specific "Do not ..." rule
Step 3 → Add the positive alternative: "If unsure, return UNKNOWN"
Step 4 → Put rules in the system prompt, near the end (recency) or in a clear block
Step 5 → Test with inputs that tempt the model to break the rule
Step 6 → Enforce in code too (validators), not only in the prompt
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Testing में दिखे बुरे behaviours लिखो (guessing, filler, leaks)
Step 2 → हर एक को छोटे, specific "Do not ..." rule में लिखो
Step 3 → Positive alternative जोड़ो: "अनिश्चित हो तो UNKNOWN लौटाओ"
Step 4 → Rules को system prompt में साफ़ block में रखो
Step 5 → ऐसे inputs से test करो जो rule तुड़वाने को उकसाएँ
Step 6 → सिर्फ prompt नहीं, code में भी enforce करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Rules: "Do not invent HS codes. Do not output a code that is not in the provided context. If the context lacks the answer, reply exactly `UNKNOWN`." The validator in code checks that the returned code exists in the retrieved chunks; otherwise it routes to a human.

**Zomato-style**: A support bot: "Do not promise refunds. Do not share another customer's data. Offer to create a ticket instead."

## 🟡 Real Example Hindi mein
**Tariff System**: Rules: "HS code खुद मत बनाओ। Context में न हो तो code मत दो। Context में जवाब न हो तो सिर्फ `UNKNOWN` लिखो।" Code में validator जाँचता है कि लौटाया code retrieved chunks में है; नहीं तो human के पास जाता है।

**Zomato-style**: Support bot: "Refund का वादा मत करो। दूसरे customer का data share मत करो। इसके बदले ticket बनाने की पेशकश करो।"

---

## 💻 Code Example — Basic
```python
# Basic: negative rules + positive fallback + a code-level check (offline)

SYSTEM = """You are a tariff assistant.
Rules:
- Do NOT guess or invent HS codes.
- Do NOT add greetings or explanations.
- Use ONLY codes that appear in CONTEXT.
- If CONTEXT does not contain the answer, reply exactly: UNKNOWN"""

CONTEXT = "8518.30 Headphones and earphones\n8517.13 Smartphones"   # allowed codes

def fake_llm(system: str, user: str) -> str:
    # Pretend LLM. A weak model might answer "Sure! It is 9999.99". Here we show a good one.
    return "8518.30"

def enforce(reply: str, context: str) -> str:
    reply = reply.strip()                                  # remove spaces/newlines
    if reply == "UNKNOWN":                                 # allowed safe answer
        return reply
    if reply in context:                                   # code must appear in context
        return reply
    return "UNKNOWN"                                       # anything else is rejected

user = f"CONTEXT:\n{CONTEXT}\n\nProduct: bluetooth earbuds"   # build the user message
raw = fake_llm(SYSTEM, user)                                # model answer
print(enforce(raw, CONTEXT))                                # 8518.30
print(enforce("Sure! It is 9999.99", CONTEXT))              # UNKNOWN (blocked by code)
```

## 💻 Code Example — Advanced
```python
# Production: rule set as data, violation detectors, async call, retry with reminder
from __future__ import annotations

import asyncio                                    # async runner
import re                                         # pattern checks
from dataclasses import dataclass                 # small rule objects
from typing import Awaitable, Callable            # type hints

LLM = Callable[[str, str], Awaitable[str]]        # (system, user) -> text

@dataclass(frozen=True)
class Rule:
    text: str                                     # what the model reads
    violated: Callable[[str], bool]               # code check on the reply

RULES: tuple[Rule, ...] = (
    Rule("Do NOT start with greetings like 'Sure' or 'Certainly'.",
         lambda r: bool(re.match(r"\s*(sure|certainly|of course)", r, re.I))),
    Rule("Do NOT output more than one HS code.",
         lambda r: len(re.findall(r"\b\d{4}\.\d{2}\b", r)) > 1),
    Rule("Do NOT write anything except the code or UNKNOWN.",
         lambda r: not re.fullmatch(r"\s*(\d{4}\.\d{2}|UNKNOWN)\s*", r)),
)

def build_system() -> str:
    lines = [f"- {r.text}" for r in RULES]       # turn rules into bullet lines
    return "You classify products.\n" + "\n".join(lines) + "\nIf unsure reply UNKNOWN."

async def classify(llm: LLM, product: str, retries: int = 1) -> str:
    system = build_system()                       # system prompt from rules
    user = f"Product: {product}"                  # user message
    reply = "UNKNOWN"                             # safe default
    for _ in range(retries + 1):                  # first try + retry
        try:
            reply = (await llm(system, user)).strip()   # call model
        except Exception as exc:                  # provider error
            raise RuntimeError(f"LLM failed: {exc}") from exc
        broken = [r.text for r in RULES if r.violated(reply)]   # which rules were broken
        if not broken:                            # all good
            return reply
        user = f"Product: {product}\nYou broke these rules: {broken}. Try again."
    return "UNKNOWN"                              # still bad -> safe fallback

async def _demo() -> None:
    state = {"n": 0}
    async def llm(system: str, user: str) -> str:
        state["n"] += 1
        return "Sure! 8518.30" if state["n"] == 1 else "8518.30"
    print(await classify(llm, "earbuds"))         # 8518.30 after one retry

if __name__ == "__main__":
    asyncio.run(_demo())
```
Token usage: each rule is ~10-20 input tokens. 10 rules = ~150 tokens on every call. Cache the static system prompt to cut this.

---

## 🟠 FastAPI Integration
Keep the rules in one module so the API, tests and docs share them. The route returns `UNKNOWN` as a normal, typed result and sets a `needs_review` flag.

```python
from fastapi import FastAPI                      # framework
from pydantic import BaseModel                   # models
from openai import AsyncOpenAI                   # openai>=1

app = FastAPI()                                  # app
client = AsyncOpenAI()                           # client

class Q(BaseModel):
    product: str                                 # input

class A(BaseModel):
    hs_code: str                                 # code or UNKNOWN
    needs_review: bool                           # True when UNKNOWN

async def llm(system: str, user: str) -> str:
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, max_tokens=20,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
    return r.choices[0].message.content or "UNKNOWN"

@app.post("/classify", response_model=A)
async def classify_route(q: Q) -> A:
    code = await classify(llm, q.product)        # classify() from the advanced block
    return A(hs_code=code, needs_review=(code == "UNKNOWN"))
```

---

## 🔗 LangChain / LangGraph Connection
Rules live in the system message of a `ChatPromptTemplate`. In LangGraph, add a "guard" node after the LLM node: if a rule is violated, a conditional edge loops back to the LLM node with a reminder, or ends with `UNKNOWN`.

```python
from langchain_core.prompts import ChatPromptTemplate        # prompt template
from langchain_openai import ChatOpenAI                      # model

prompt = ChatPromptTemplate.from_messages([
    ("system", "Do NOT guess HS codes. Use only CONTEXT. If missing reply UNKNOWN."),
    ("user", "CONTEXT:\n{context}\n\nProduct: {product}"),
])
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0)
# LangGraph: llm_node -> guard_node -> (ok -> END | violated -> llm_node)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Negative-only rules ("Don't be wrong")
✅ Correct: Pair with the desired action.
```python
# Wrong
"Do not guess."

# Right
"Do not guess. If the context lacks the answer, reply exactly UNKNOWN."
```

❌ Mistake 2: Mentioning the unwanted thing in detail (the "pink elephant" effect)
✅ Correct: Prefer positive format instructions where possible.
```python
# Wrong: primes the model with the bad phrase
"Never say 'As an AI language model I cannot...'"

# Right
"Answer directly in one sentence."
```

❌ Mistake 3: Trusting the prompt as the only enforcement. Always add a code validator.

---

## 🧠 Tricky Interview Question
**Q**: "You wrote 'Do not mention competitors.' The model now mentions competitors MORE in some replies. Why?"

**Answer**: Naming the forbidden thing puts those tokens into the context and can raise their probability (priming). Also long lists of negatives dilute attention. Fix: rewrite positively ("Talk only about our products"), remove the specific competitor names from the prompt, filter in code with a post-check, and test with adversarial inputs.

---

## ⚫ Interview Questions + Answers

Q1: What is negative prompting?
A1: Instructions that forbid behaviours ("do not guess"). It sets boundaries for the model.

Q2: Why add a positive fallback next to a prohibition?
A2: "Do not guess" leaves the model without an action when unsure. "Reply UNKNOWN" gives a safe, parseable path.

Q3: Are negative instructions always followed?
A3: No. They are probabilistic, can be overridden by user input or long context, and can prime the forbidden content. Use code validators, and for safety use guardrails.

Q4: How do you test negative rules?
A4: Build a test set of inputs that tempt violations (missing context, user pressure, off-topic asks), run it on every prompt change, and measure the violation rate.

Q5 (Hard): How would you reduce hallucinated HS codes below 0.1% in production?
A5: Combine layers: retrieval with the allowed code list in context, a negative rule plus UNKNOWN fallback, constrained output (enum of valid codes via structured outputs), a code check that the code exists in the official table, confidence thresholds, human review queue, and an eval set tracking hallucination rate per release.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You saw a specific recurring bad behaviour
- Safety or compliance needs hard boundaries
- Output format must stay clean (no filler)

❌ Avoid when:
- A positive instruction says the same thing more clearly
- You have 20+ negatives (model gets confused; restructure the prompt)
- You rely on it as the only security control

---

## 📊 Visual Diagram
```
  System prompt
  +-----------------------------------+
  | Task: classify product            |
  | Do NOT guess codes                |  <- boundary
  | Do NOT add explanations           |  <- boundary
  | If unsure -> UNKNOWN              |  <- safe path
  +-----------------------------------+
                 |
                 v
              [ LLM ]
                 |
                 v
        Code validator (rules)
          |             |
        pass          violation
          |             |
        return     retry / UNKNOWN / human
```

---

## 💰 Cost Impact
- Every rule costs input tokens on every request (10-20 tokens each).
- Violations cause retries, which double the request cost.
- A short UNKNOWN reply saves output tokens versus long guessed explanations.

Optimisation: keep only rules proven by tests, merge similar rules, cache the static system prompt, and enforce simple rules in code (regex/validator) instead of spending tokens on them.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Negative prompt | Instruction about what not to do | क्या नहीं करना है वाला निर्देश |
| Guardrail | Rule or check that limits behaviour | सीमा तय करने वाला rule/check |
| Fallback | Safe default answer | सुरक्षित default जवाब |
| Priming | Mentioning a thing makes it more likely | किसी चीज़ का ज़िक्र उसकी संभावना बढ़ाना |
| Validator | Code that checks output | Output जाँचने वाला code |
| Hallucination | Invented, false output | गढ़ा हुआ झूठा output |

---

## ⚡ 3-Line Summary
English: Negative prompting sets clear boundaries such as "do not guess". Always add a positive fallback like UNKNOWN. Enforce important rules in code, because prompts are only probabilistic.
Hindi: Negative prompting साफ़ सीमाएँ तय करता है जैसे "अंदाज़ा मत लगाओ"। हमेशा UNKNOWN जैसा positive fallback जोड़ो। ज़रूरी rules को code में enforce करो, क्योंकि prompt सिर्फ probabilistic है।

---

## ➡️ Next Topic
**066. Prompt Chaining** — break a big task into small prompts where each step's output feeds the next.
