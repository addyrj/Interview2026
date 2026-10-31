---

# 051. What is Prompt Engineering
# हिंदी में: Prompt Engineering क्या है

---

## 🔵 Simple Definition (English)
Prompt engineering is the practice of designing the input text (instructions, context, examples, output format) so an LLM gives accurate, consistent and useful answers. It is testing and refining wording like you test code, not guessing.

## 🔵 सरल परिभाषा (Hindi)
Prompt engineering यानी LLM के input text (instructions, context, examples, output format) को ऐसे design करना कि जवाब सही, consistent और काम का आए। यह code की तरह test और refine करने की प्रक्रिया है, अंदाज़ा लगाना नहीं।

---

## 🔴 Problem it Solves
- LLMs do not "know" what you want; vague prompts give vague, inconsistent answers.
- Retraining or fine-tuning a model is slow and costly; a better prompt is the cheapest first fix.
- Output must follow a format that code can parse.

## 🔴 यह क्यों बना? (Hindi)
- LLM को पता नहीं होता आप क्या चाहते हैं; अस्पष्ट prompt से अस्पष्ट और अलग-अलग जवाब मिलते हैं।
- Model retrain/fine-tune करना धीमा और महँगा है; बेहतर prompt सबसे सस्ता पहला उपाय है।
- Output ऐसे format में चाहिए जिसे code parse कर सके।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define the task and what a "good" answer looks like
Step 2 → Write a first prompt: role, task, context, constraints, output format
Step 3 → Add examples if the task is subtle (few-shot)
Step 4 → Run on a test set of real inputs (not just one)
Step 5 → Read failures, find the pattern (missing rule? ambiguous word?)
Step 6 → Change ONE thing, re-run, compare scores
Step 7 → Version the prompt and keep the test set in CI
Step 8 → If the prompt cannot fix it, consider RAG, tools or fine-tuning
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Task और "अच्छा जवाब" कैसा होगा, यह तय करो
Step 2 → पहला prompt लिखो: role, task, context, constraints, output format
Step 3 → Task सूक्ष्म हो तो examples जोड़ो (few-shot)
Step 4 → असली inputs के test set पर चलाओ (सिर्फ़ एक पर नहीं)
Step 5 → Failures पढ़ो, pattern ढूँढो (कोई rule छूटा? कोई शब्द अस्पष्ट?)
Step 6 → एक बार में एक चीज़ बदलो, फिर चलाओ, scores compare करो
Step 7 → Prompt को version करो और test set CI में रखो
Step 8 → Prompt से न बने तो RAG, tools या fine-tuning सोचो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Version 1 prompt: "What is the HS code for this product?" gave long essays and wrong chapters. Version 2: "You are a customs classifier. Given the product description, return JSON {hs_code, reason}. Use only the 6-digit international level. If unsure, set hs_code to null." Accuracy rose from 62% to 84% and output became machine-readable, with no model change at all.

**Zomato-style**: "Summarise reviews" became "Summarise these reviews in 3 bullets: food, delivery, price. Max 15 words each."

## 🟡 Real Example Hindi mein
**Tariff System**: Version 1 prompt: "इस product का HS code क्या है?" लंबे essays और गलत chapters देता था। Version 2: "तुम एक customs classifier हो। Product description से JSON {hs_code, reason} दो। सिर्फ़ 6-digit international level इस्तेमाल करो। पक्का न हो तो hs_code को null रखो।" Accuracy 62% से 84% हुई और output machine-readable हो गया, model बदले बिना।

**Zomato-style**: "Reviews का summary दो" को बदला: "इन reviews का 3 bullets में summary दो: खाना, delivery, price। हर bullet अधिकतम 15 शब्द।"

---

## 💻 Code Example — Basic
```python
# Basic: build a structured prompt from parts (pure Python, runs offline)

def build_prompt(role: str, task: str, context: str, rules: list[str], output_format: str) -> str:
    rule_text = "\n".join(f"- {r}" for r in rules)  # bullet list of rules
    return (  # join all parts in a clear order
        f"Role: {role}\n"  # who the model should act as
        f"Task: {task}\n"  # what to do
        f"Context: {context}\n"  # input data
        f"Rules:\n{rule_text}\n"  # constraints
        f"Output format: {output_format}"  # exact shape of the answer
    )

prompt = build_prompt(
    role="Customs classification expert",
    task="Give the 6-digit HS code for the product.",
    context="Wireless earbuds with charging case",
    rules=["Use only the international 6-digit level", "If unsure return null"],
    output_format='JSON: {"hs_code": string|null, "reason": string}',
)
print(prompt)  # see the assembled prompt
print("Approx tokens:", len(prompt) // 4)  # rough estimate: 1 token ~ 4 characters
```

## 💻 Code Example — Advanced
```python
# Production-style: versioned prompt templates + A/B comparison on a test set
import asyncio  # async runtime
import json  # parse JSON answers
from dataclasses import dataclass  # prompt container
from openai import AsyncOpenAI, APIError  # openai>=1

client = AsyncOpenAI()  # shared client

@dataclass(frozen=True)
class PromptVersion:
    name: str  # for example "v1"
    system: str  # system instruction text

V1 = PromptVersion("v1", "What is the HS code?")  # weak prompt
V2 = PromptVersion(
    "v2",
    "You are a customs classifier. Return ONLY JSON: {\"hs_code\": string|null}. "
    "Use 6-digit international level. If unsure, null.",
)

TEST_SET: list[tuple[str, str]] = [  # (input, expected HS code)
    ("wireless earbuds", "851830"),
    ("cotton t-shirt for men", "610910"),
]

async def run_one(pv: PromptVersion, text: str) -> str | None:
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, max_tokens=60,
            messages=[{"role": "system", "content": pv.system},
                      {"role": "user", "content": text}])
        raw = resp.choices[0].message.content or ""
        return json.loads(raw).get("hs_code")  # works only for JSON prompts
    except (json.JSONDecodeError, AttributeError):  # prompt returned prose
        return None
    except APIError:  # API failure counts as a miss
        return None

async def score(pv: PromptVersion) -> float:
    answers = await asyncio.gather(*(run_one(pv, t) for t, _ in TEST_SET))  # parallel
    hits = sum(a == exp for a, (_, exp) in zip(answers, TEST_SET))  # correct count
    return hits / len(TEST_SET)  # accuracy

async def main() -> None:
    for pv in (V1, V2):  # compare versions on the same data
        print(pv.name, await score(pv))

# asyncio.run(main())  # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
Keep prompts in code or files with a version string and return the version in the response, so you can connect any bad answer to the prompt that produced it.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # validation
from openai import APIError  # error type

app = FastAPI()  # app
PROMPTS = {"v1": V1, "v2": V2}  # registry from advanced example

class Q(BaseModel):
    text: str  # product text
    prompt_version: str = "v2"  # choose version (for A/B tests)

@app.post("/classify")
async def classify(q: Q) -> dict:
    pv = PROMPTS.get(q.prompt_version)  # look up
    if pv is None:
        raise HTTPException(status_code=422, detail="Unknown prompt version")
    try:
        code = await run_one(pv, q.text)  # call LLM
    except APIError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return {"hs_code": code, "prompt_version": pv.name}  # return version for traceability
```

---

## 🔗 LangChain / LangGraph Connection
`ChatPromptTemplate` turns prompts into reusable templates with variables; `MessagesPlaceholder` inserts history; prompts can be pulled from LangSmith Hub and versioned. In LangGraph each node usually has its own prompt.

```python
from langchain_core.prompts import ChatPromptTemplate  # template class
from langchain_openai import ChatOpenAI  # model
from langchain_core.output_parsers import JsonOutputParser  # parse JSON output

prompt = ChatPromptTemplate.from_messages([  # system + human template
    ("system", "You are a customs classifier. Return JSON {{\"hs_code\": string|null}}."),
    ("human", "{product}"),
])
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | JsonOutputParser()  # LCEL
# print(chain.invoke({"product": "wireless earbuds"}))
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Vague instructions
✅ Correct: Be specific about task, audience, length and format.

```python
# Wrong: "Tell me about this product's code"
# Right: "Return the 6-digit HS code as JSON {hs_code}. No explanation."
```

❌ Mistake 2: Judging a prompt on one example
✅ Correct: Test on 30-100 varied inputs including edge cases.

```python
# Wrong: print(ask("earbuds"))   # looks good, ship it
# Right: accuracy = score(prompt, test_set)   # measured
```

---

## 🧠 Tricky Interview Question
**Q**: "Your improved prompt fixes 10 failing examples but accuracy overall drops. Why?"

**Answer**: Prompt changes have side effects (regressions). Fixing one pattern can break others, especially if you added a narrow rule or example that the model over-applies. This is why you evaluate on a full test set, not just the failures. Keep a regression set, change one thing at a time, and look at which new cases broke.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What are the main parts of a good prompt?
A1: Role, task, context, constraints/rules, examples (optional) and output format.

Q2: [Easy] Why use low temperature for extraction tasks?
A2: Lower randomness gives consistent, repeatable output, which is what extraction and classification need.

Q3: [Medium] Prompt engineering vs fine-tuning vs RAG?
A3: Prompting changes instructions (fast, cheap). RAG adds fresh or private knowledge into the prompt. Fine-tuning changes model behaviour/style using training data (slower, costlier). Start with prompting, add RAG for knowledge gaps, fine-tune for consistent style/format at scale.

Q4: [Medium] How do you make prompts testable?
A4: Store them as versioned templates, use a golden set with metrics (accuracy, format validity), run in CI, and compare versions before release.

Q5: [Hard] A prompt works on GPT-4o but fails on a smaller model. What do you do?
A5: Smaller models need clearer, simpler instructions, more examples, shorter prompts and stricter output format. Split a big task into steps, use structured outputs, and measure again. If still failing, use a larger model for that step only (routing).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need quick quality improvements with no training
- Output format and tone must be controlled

❌ Avoid when:
- The model lacks the knowledge (use RAG)
- The task needs exact deterministic logic (use code)

---

## 📊 Visual Diagram
```
 +----------------------------- PROMPT -----------------------------+
 | Role | Task | Context | Rules | Examples | Output format         |
 +-------------------------------+---------------------------------+
                                 |
                                 v
                               LLM
                                 |
                                 v
                 answer --> evaluate on test set
                                 |
                      fail --> change ONE thing --> repeat
```

---

## 💰 Cost Impact
- Every word in the prompt is billed as input tokens on every call. A 1,500-token prompt at 100,000 calls/day means 150M input tokens/day.
- Good prompts reduce output tokens (ask for brief JSON) and reduce retries and manual fixes.
- Optimise: remove filler, keep only useful examples, use provider prompt caching for static prefixes, test shorter prompts against your accuracy bar.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Prompt | Input instructions for LLM | LLM को दिए निर्देश |
| System prompt | Top-level rules | मुख्य नियम |
| Few-shot | Examples inside prompt | Prompt में examples |
| Temperature | Randomness setting | Randomness का स्तर |
| Golden set | Test inputs with answers | सही जवाबों वाला test set |
| Regression | New change breaks old case | नया बदलाव पुराना काम तोड़े |

---

## ⚡ 3-Line Summary
English: Prompt engineering is writing and testing instructions so LLM output is accurate and parseable. Be specific, give format and examples, and evaluate on a test set. Change one thing at a time.
Hindi: Prompt engineering यानी instructions लिखना और test करना ताकि LLM output सही और parse होने लायक हो। Specific रहो, format और examples दो, और test set पर evaluate करो। एक बार में एक चीज़ बदलो।

---

## ➡️ Next Topic
**052. Zero-Shot Prompting** — the simplest style: ask the task with no examples.
