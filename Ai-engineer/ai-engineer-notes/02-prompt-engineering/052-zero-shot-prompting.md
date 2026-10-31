---

# 052. Zero-Shot Prompting
# हिंदी में: Zero-Shot Prompting

---

## 🔵 Simple Definition (English)
Zero-shot prompting means asking the model to do a task with only instructions and no worked examples. The model relies on what it learned in pre-training and instruction tuning. It is the fastest and cheapest prompting style.

## 🔵 सरल परिभाषा (Hindi)
Zero-shot prompting में आप model को सिर्फ़ instructions देते हैं, कोई solved example नहीं। Model अपनी pre-training और instruction tuning से काम करता है। यह सबसे तेज़ और सस्ता prompting style है।

---

## 🔴 Problem it Solves
- You may have no labelled examples yet.
- Examples cost tokens on every call.
- Many common tasks (summarise, translate, sentiment, simple classify) are already well understood by modern models.

## 🔴 यह क्यों बना? (Hindi)
- शायद आपके पास अभी labelled examples नहीं हैं।
- Examples हर call में tokens खर्च करते हैं।
- कई आम tasks (summary, translate, sentiment, simple classification) modern models पहले से अच्छी तरह समझते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a clear instruction (task + labels/allowed values)
Step 2 → State the output format precisely
Step 3 → Add input between delimiters
Step 4 → Set temperature 0 for classification
Step 5 → Run on a test set and measure accuracy
Step 6 → If accuracy is below target, add rules/definitions first
Step 7 → If still low, move to few-shot (next topic) or CoT
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → साफ़ instruction लिखो (task + allowed labels/values)
Step 2 → Output format ठीक-ठीक बताओ
Step 3 → Input को delimiters के बीच रखो
Step 4 → Classification के लिए temperature 0 रखो
Step 5 → Test set पर चलाकर accuracy measure करो
Step 6 → Accuracy कम हो तो पहले rules/definitions जोड़ो
Step 7 → फिर भी कम हो तो few-shot (अगला topic) या CoT लो
```

---

## 🟡 Real World Example
**Tariff Classification System**: First step: decide whether an invoice line is a physical good, a service or a fee, so services skip HS classification. Zero-shot: "Classify the line as GOOD, SERVICE or FEE. Reply with one word." Works at 96% with no examples, costing about 60 input tokens per call.

**Zomato-style**: Tag a review as POSITIVE / NEGATIVE / NEUTRAL with a one-line zero-shot prompt.

## 🟡 Real Example Hindi mein
**Tariff System**: पहला step: invoice line physical good है, service है या fee, ताकि services को HS classification से निकाल दें। Zero-shot: "Line को GOOD, SERVICE या FEE में classify करो। सिर्फ़ एक शब्द में जवाब दो।" बिना examples के 96% सही, लगभग 60 input tokens प्रति call।

**Zomato-style**: Review को एक-line zero-shot prompt से POSITIVE / NEGATIVE / NEUTRAL tag करना।

---

## 💻 Code Example — Basic
```python
# Basic: zero-shot prompt builder + label validation (mock model, runs offline)

LABELS = ["GOOD", "SERVICE", "FEE"]  # allowed answers

def zero_shot_prompt(line: str) -> str:
    return (  # no examples, only instruction + format
        f"Classify the invoice line as one of: {', '.join(LABELS)}.\n"  # task and labels
        "Reply with exactly one word.\n"  # output format
        f"Invoice line: <<{line}>>"  # input in delimiters
    )

def mock_model(prompt: str) -> str:
    # Tiny fake model: keyword rules instead of a real LLM
    text = prompt.split("<<")[-1].lower()  # look only at the invoice line, not the instruction
    if "freight" in text or "consulting" in text:
        return "SERVICE"
    if "fee" in text:
        return "FEE"
    return "GOOD"

def classify(line: str) -> str:
    answer = mock_model(zero_shot_prompt(line)).strip().upper()  # get answer
    return answer if answer in LABELS else "UNKNOWN"  # guard against bad output

for item in ["Wireless earbuds x100", "Freight charges", "Handling fee"]:
    print(item, "->", classify(item))  # show results
```

## 💻 Code Example — Advanced
```python
# Production-style: async zero-shot classifier with label validation and retries
import asyncio  # async runtime
from typing import Literal, get_args  # exact label types
from openai import AsyncOpenAI, APIError, RateLimitError  # openai>=1

Label = Literal["GOOD", "SERVICE", "FEE"]  # allowed labels
LABELS: tuple[str, ...] = get_args(Label)  # tuple of label strings

client = AsyncOpenAI(timeout=15.0)  # shared client

SYSTEM = (
    "You classify invoice lines. Allowed labels: GOOD, SERVICE, FEE. "
    "GOOD = physical item. SERVICE = work or transport. FEE = tax, handling, admin charge. "
    "Reply with exactly one label and nothing else."
)

async def classify_line(line: str) -> Label | Literal["UNKNOWN"]:
    for attempt in range(3):  # retry transient errors
        try:
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,  # deterministic
                max_tokens=3,  # label is tiny: cap output cost
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": f"<<{line}>>"}])
            text = (resp.choices[0].message.content or "").strip().upper()
            return text if text in LABELS else "UNKNOWN"  # type: ignore[return-value]
        except RateLimitError:
            await asyncio.sleep(2 ** attempt)  # backoff
        except APIError:
            return "UNKNOWN"  # fail soft; caller sends to review
    return "UNKNOWN"

async def classify_many(lines: list[str]) -> list[str]:
    sem = asyncio.Semaphore(8)  # limit concurrency
    async def guarded(x: str) -> str:
        async with sem:
            return await classify_line(x)
    return list(await asyncio.gather(*(guarded(l) for l in lines)))

# print(asyncio.run(classify_many(["Wireless earbuds x100", "Freight charges"])))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel, Field  # validation

app = FastAPI()  # app

class Lines(BaseModel):
    lines: list[str] = Field(min_length=1, max_length=100)  # bounded batch size

@app.post("/line-type")
async def line_type(body: Lines) -> dict:
    labels = await classify_many(body.lines)  # parallel zero-shot calls
    return {"results": [{"line": l, "label": lab} for l, lab in zip(body.lines, labels)],
            "needs_review": [l for l, lab in zip(body.lines, labels) if lab == "UNKNOWN"]}
```

---

## 🔗 LangChain / LangGraph Connection
A zero-shot chain is just prompt | model | parser. `with_structured_output` with a `Literal` field enforces the label set. In LangGraph this is a typical first "router" node.

```python
from typing import Literal  # label type
from pydantic import BaseModel  # schema
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_openai import ChatOpenAI  # model

class LineType(BaseModel):
    label: Literal["GOOD", "SERVICE", "FEE"]  # enforced by structured output

prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the invoice line."), ("human", "{line}")])
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(LineType)
# print(chain.invoke({"line": "Freight charges"}))  # LineType(label='SERVICE')
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not defining labels
✅ Correct: Name each label and explain edge cases.

```python
# Wrong: "Classify this line."
# Right: "Labels: GOOD (physical item), SERVICE (work/transport), FEE (tax/admin). One word."
```

❌ Mistake 2: Using free text then string matching
✅ Correct: Constrain output and validate.

```python
# Wrong: if "service" in answer.lower(): ...   # matches "not a service"
# Right: answer in {"GOOD","SERVICE","FEE"} else UNKNOWN
```

---

## 🧠 Tricky Interview Question
**Q**: "Zero-shot gives 70% on your task; adding 5 examples gives 90%. Should you always add the examples?"

**Answer**: Not automatically. Examples add tokens to every call (cost and latency). Compare gains vs cost: if 100,000 calls/day x 300 extra tokens is real money, consider cheaper options: better definitions, a few shortest examples, dynamic few-shot (retrieve only relevant examples), prompt caching for static examples, or fine-tuning a small model. Decide with numbers.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is zero-shot prompting?
A1: Giving instructions with no examples, relying on the model's existing knowledge.

Q2: [Easy] Give a good zero-shot task.
A2: Sentiment analysis, language detection, simple summarisation, translation.

Q3: [Medium] How can you improve zero-shot without examples?
A3: Clearer label definitions, rules for edge cases, strict output format, role/context, delimiters around input, and lower temperature.

Q4: [Medium] When does zero-shot fail?
A4: When labels are subjective or domain-specific, the format is unusual, or the task needs multi-step reasoning. Then use few-shot or CoT.

Q5: [Hard] How do you decide between zero-shot, few-shot and fine-tuning?
A5: Start zero-shot (cheapest). If accuracy is short, add definitions, then few-shot. If volume is huge and the same examples are always needed, or latency/cost matters, fine-tune a smaller model. Always compare on a held-out test set with cost per correct answer.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Common tasks and quick prototypes
- Tokens/latency matter
- No labelled examples yet

❌ Avoid when:
- Custom label meanings or house style
- Hard reasoning that needs steps

---

## 📊 Visual Diagram
```
 Instruction + Input  ──────────►  LLM  ──────────►  Answer
 (no examples)

 Compare:
 Zero-shot : [instruction][input]                    (smallest)
 Few-shot  : [instruction][ex1][ex2][ex3][input]     (more tokens)
```

---

## 💰 Cost Impact
- Cheapest prompting style: only instruction + input tokens (often 50-300 tokens).
- For tiny outputs (one label), set `max_tokens=3` so output cost is nearly zero.
- Example (illustrative `gpt-4o-mini`, $0.15/1M input): 100,000 calls x 100 tokens = 10M tokens = about $1.50/day.
- Optimise: short system prompt, label-only outputs, cache repeated inputs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Zero-shot | No examples | बिना examples |
| Label | Allowed output category | Output की category |
| Delimiter | Marker around input | Input के चारों ओर निशान |
| Instruction tuning | Training to follow instructions | Instructions मानना सिखाना |
| Temperature 0 | Least random output | सबसे कम randomness |
| UNKNOWN fallback | Safe default label | सुरक्षित default label |

---

## ⚡ 3-Line Summary
English: Zero-shot means instructions only, no examples. It is cheap, fast and good for common tasks. Improve it with clear labels and format before adding examples.
Hindi: Zero-shot यानी सिर्फ़ instructions, examples नहीं। यह सस्ता, तेज़ और आम tasks के लिए अच्छा है। Examples जोड़ने से पहले साफ़ labels और format से सुधारो।

---

## ➡️ Next Topic
**053. Few-Shot Prompting** — add examples to teach the model your exact pattern.
