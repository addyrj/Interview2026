---

# 061. Instruction Following
# हिंदी में: Instruction Following

---

## 🔵 Simple Definition (English)
Instruction following is how well an LLM does exactly what the prompt asks: all constraints, in the right format, without extra or missing parts. Chat models are trained (instruction tuning, RLHF) for it, but it weakens with long, conflicting, multi-constraint or ambiguous prompts. Good prompting and verification make it dependable.

## 🔵 सरल परिभाषा (Hindi)
Instruction following यानी LLM prompt में माँगा गया काम कितनी ठीक तरह करता है: सारी constraints, सही format में, बिना extra या कम हिस्सों के। Chat models इसके लिए trained होते हैं (instruction tuning, RLHF), पर लंबे, विरोधाभासी, कई-constraint वाले या अस्पष्ट prompts में यह कमज़ोर पड़ता है। अच्छा prompting और verification इसे भरोसेमंद बनाते हैं।

---

## 🔴 Problem it Solves
- Models skip constraints (word limits, forbidden words), add chatty preambles, or mix up formats.
- Downstream code expects exact behaviour; a 95% follow rate still means failures at scale.
- You need to know whether a prompt or model is reliable enough.

## 🔴 यह क्यों बना? (Hindi)
- Models constraints छोड़ देते हैं (word limit, मना किए शब्द), बेकार भूमिका जोड़ते हैं या formats मिला देते हैं।
- Downstream code को ठीक-ठीक behaviour चाहिए; 95% follow rate भी scale पर failures है।
- जानना ज़रूरी है कि prompt या model पर्याप्त भरोसेमंद है या नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write instructions as a numbered list of atomic, testable constraints
Step 2 → Keep one task per prompt (split multi-task prompts into steps)
Step 3 → Put the hard constraints in the system prompt, the task in the user message
Step 4 → Specify the exact output format and what to do when a constraint cannot be met
Step 5 → Remove conflicts (brief vs detailed) and ambiguous words (short, soon)
Step 6 → Verify in code: length, JSON validity, forbidden words, required fields
Step 7 → On violation: retry once with the specific error, else fallback
Step 8 → Measure the follow rate on a test set; improve prompt or use a stronger model
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Instructions को numbered, atomic, testable constraints की list में लिखो
Step 2 → एक prompt में एक task (multi-task prompts को steps में तोड़ो)
Step 3 → कठोर constraints system prompt में, task user message में
Step 4 → ठीक-ठीक output format और constraint पूरी न हो सके तब क्या करना है, बताओ
Step 5 → विरोधाभास (brief बनाम detailed) और अस्पष्ट शब्द (short, soon) हटाओ
Step 6 → Code में verify करो: length, JSON validity, मना किए शब्द, ज़रूरी fields
Step 7 → उल्लंघन पर: specific error के साथ एक retry, नहीं तो fallback
Step 8 → Test set पर follow rate नापो; prompt सुधारो या stronger model लो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The explanation for each classification must: (1) be at most 40 words, (2) mention the General Rule used, (3) not mention competitor brands, (4) be in English. A single prompt failed on 18% of items (usually word limit). Fixes: numbered constraints, a code-side checker, and one repair retry ("Your answer has 52 words; rewrite in at most 40"). Violations dropped below 2%.

**Zomato-style**: Notification text must be under 90 characters, include the restaurant name and no emojis; validate in code before sending.

## 🟡 Real Example Hindi mein
**Tariff System**: हर classification की explanation में: (1) अधिकतम 40 शब्द, (2) इस्तेमाल हुए General Rule का ज़िक्र, (3) competitor brands का नाम नहीं, (4) English में। एक ही prompt 18% items पर fail हुआ (ज़्यादातर word limit)। सुधार: numbered constraints, code-side checker और एक repair retry ("तुम्हारे जवाब में 52 शब्द हैं; अधिकतम 40 में दोबारा लिखो")। Violations 2% से नीचे आ गए।

**Zomato-style**: Notification text 90 characters से कम, restaurant का नाम शामिल, कोई emoji नहीं; भेजने से पहले code में validate करो।

---

## 💻 Code Example — Basic
```python
# Basic: check constraints in code (pure Python, runs offline)
import re  # pattern checks

def check_constraints(text: str, max_words: int = 40, banned: tuple[str, ...] = ("samsung", "apple")) -> list[str]:
    problems: list[str] = []  # collected violations
    words = len(text.split())  # word count
    if words > max_words:  # length rule
        problems.append(f"too long: {words} words (max {max_words})")
    if not re.search(r"general rule\s*\d", text, re.I):  # must cite a rule
        problems.append("missing 'General Rule <number>' citation")
    low = text.lower()  # case-insensitive checks
    for b in banned:  # banned words rule
        if b in low:
            problems.append(f"contains banned word: {b}")
    return problems  # empty list = all constraints satisfied

good = "Classified under heading 8518 by General Rule 1 because the principal function is sound reproduction."
bad = "This Apple speaker is wonderful and has many fine features that buyers love very much " * 3
print("good:", check_constraints(good))  # []
print("bad :", check_constraints(bad))  # list of problems
```

## 💻 Code Example — Advanced
```python
# Production-style: generate -> verify -> targeted repair retry (async), with pydantic
import asyncio  # async runtime
import re  # checks
from openai import AsyncOpenAI, APIError  # openai>=1

client = AsyncOpenAI(timeout=20.0)  # shared client

SYSTEM = (
    "Write a classification explanation. Constraints:\n"
    "1. At most 40 words.\n"
    "2. Cite the rule as 'General Rule <number>'.\n"
    "3. Do not mention brand names.\n"
    "4. English only.\n"
    "Return only the explanation text."
)

def violations(text: str) -> list[str]:
    v: list[str] = []  # list of violations
    n = len(text.split())
    if n > 40:
        v.append(f"it has {n} words, the maximum is 40")
    if not re.search(r"General Rule\s*\d", text):
        v.append("it does not cite 'General Rule <number>'")
    if re.search(r"\b(apple|samsung|sony)\b", text, re.I):
        v.append("it mentions a brand name")
    return v

async def explain(product: str, code: str, max_repairs: int = 2) -> tuple[str, list[str]]:
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"Product: {product}\nHS code: {code}"}]
    text, v = "", ["not generated"]
    for _ in range(max_repairs + 1):  # first try + repairs
        try:
            resp = await client.chat.completions.create(
                model="gpt-4o-mini", temperature=0.2, max_tokens=120, messages=messages)
        except APIError as exc:
            return f"ERROR: {exc.__class__.__name__}", ["api error"]
        text = (resp.choices[0].message.content or "").strip()
        v = violations(text)  # verify in code
        if not v:
            return text, []  # all constraints satisfied
        messages += [{"role": "assistant", "content": text},  # targeted repair instruction
                     {"role": "user", "content": "Rewrite fixing: " + "; ".join(v)}]
    return text, v  # still violating: caller flags for review

# print(asyncio.run(explain("Bluetooth speaker with FM radio", "8518.22")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # validation

app = FastAPI()  # app

class Q(BaseModel):
    product: str  # product text
    hs_code: str  # code to explain

@app.post("/explain")
async def explain_route(q: Q) -> dict:
    text, v = await explain(q.product, q.hs_code)  # generate + verify
    return {"explanation": text, "constraints_ok": not v, "violations": v}  # expose quality status
```

---

## 🔗 LangChain / LangGraph Connection
A verify-and-repair loop is a classic LangGraph pattern: `generate` node -> `validate` node -> conditional edge back to `generate` (with the error in state) or to END, with a retry counter. In LCEL, `PydanticOutputParser` or `with_structured_output` enforce structure and can be wrapped with `.with_retry()`.

```python
from typing import TypedDict  # state type
from langgraph.graph import StateGraph, END  # graph

class S(TypedDict):
    text: str  # latest draft
    problems: list[str]  # violations
    tries: int  # retry counter

def generate(s: S) -> dict:  # in real code: call the LLM with the problems in the prompt
    return {"text": s["text"] or "draft", "tries": s["tries"] + 1}

def validate(s: S) -> dict:  # reuse the violations() function
    return {"problems": violations(s["text"])}

def route(s: S) -> str:  # loop until valid or out of tries
    return END if not s["problems"] or s["tries"] >= 3 else "generate"

g = StateGraph(S)
g.add_node("generate", generate)
g.add_node("validate", validate)
g.set_entry_point("generate")
g.add_edge("generate", "validate")
g.add_conditional_edges("validate", route)
graph = g.compile()  # runnable
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Packing 10 instructions into one paragraph
✅ Correct: Numbered, atomic constraints.

```python
# Wrong: "Write a short professional explanation that cites rules, avoids brands, ..."
# Right: "1. Max 40 words. 2. Cite General Rule <n>. 3. No brand names."
```

❌ Mistake 2: Trusting the model to obey without checking
✅ Correct: Verify programmatically and repair.

```python
# Wrong: send(text)
# Right: if violations(text): repair(text) else: send(text)
```

---

## 🧠 Tricky Interview Question
**Q**: "The model follows each instruction alone, but when you give all 8 together it drops 2 or 3. Why and what do you do?"

**Answer**: Instruction-following degrades as constraint count and prompt length grow (limited attention, conflicts). Fixes: reduce to the essential constraints; group and order them; move hard format rules into structured outputs/JSON schema, and checkable rules into code validators; split into two steps (draft then edit/check with a focused prompt); use a stronger model for the final step; measure per-constraint pass rates to see which ones fail.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is instruction following?
A1: The ability of a model to do precisely what the prompt asks, including all constraints and the format.

Q2: [Easy] Name a simple way to improve it.
A2: Make instructions explicit and atomic (numbered list), and specify the exact output format.

Q3: [Medium] Why validate in code?
A3: Models are probabilistic; code can check length, schema and forbidden content deterministically and trigger a repair or fallback.

Q4: [Medium] What is a repair retry?
A4: Re-calling the model with its previous answer and the specific violations to fix, usually more effective than repeating the same prompt.

Q5: [Hard] How do you measure instruction following at scale?
A5: Build a test set with programmatically checkable constraints (like IFEval-style tests), compute per-constraint and per-prompt pass rates, track over time and per model/prompt version, review failures by category, and use LLM-as-judge only for constraints that cannot be checked by code (with calibration against human labels).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Outputs feed code or compliance workflows
- Many constraints (length, format, tone, forbidden content)

❌ Avoid when:
- Over-constraining creative tasks (too many rules reduce quality)

---

## 📊 Visual Diagram
```
 constraints (numbered) + task
            |
            v
          LLM  ----> draft
            |
            v
   code validator --pass--> deliver
            |
          fail
            v
   repair prompt (draft + exact violations) -> LLM -> validator
            |
   still failing after N tries -> flag for human review
```

---

## 💰 Cost Impact
- Repair retries cost extra tokens: each repair re-sends the prompt plus the draft. If 10% of items need one repair, cost rises about 10-15%.
- Better first-pass prompts (clear constraints, structured outputs) reduce repairs. Cap retries at 1-2.
- Example: 100,000 items x 600 tokens = 60M tokens; 10% repairs x 900 tokens = +9M tokens (about +15%).
- Optimise: simple code fixes (truncate whitespace) without calling the model, structured output for format, small model for the first pass.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Instruction following | Obeying prompt constraints | Prompt की शर्तें मानना |
| Constraint | A rule to satisfy | पूरी करने वाली शर्त |
| Validator | Code that checks output | Output जाँचने वाला code |
| Repair retry | Re-ask with specific errors | Errors बताकर दोबारा माँगना |
| IFEval | Benchmark for checkable instructions | जाँचे जा सकने वाले instructions का benchmark |
| Atomic instruction | One rule per line | एक line में एक नियम |

---

## ⚡ 3-Line Summary
English: Write numbered, atomic, non-conflicting instructions and specify the exact format. Verify output in code and repair with targeted feedback. Measure the follow rate on a test set.
Hindi: Numbered, atomic और बिना विरोधाभास वाले instructions लिखो और ठीक-ठीक format बताओ। Output को code में verify करो और specific feedback से repair करो। Test set पर follow rate नापो।

---

## ➡️ Next Topic
**062. Output Format Control** — getting JSON, tables and fixed structures reliably.
