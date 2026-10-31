---

# 054. Chain of Thought (CoT)
# हिंदी में: Chain of Thought (CoT)

---

## 🔵 Simple Definition (English)
Chain of Thought prompting asks the model to reason step by step before giving the final answer ("Let's think step by step", or examples with reasoning). Writing intermediate steps improves accuracy on maths, logic and multi-step decisions. Note: some newer reasoning models think internally, so explicit CoT prompts help them less.

## 🔵 सरल परिभाषा (Hindi)
Chain of Thought prompting में model से कहा जाता है कि final answer से पहले step by step सोचे ("Let's think step by step", या reasoning वाले examples)। बीच के steps लिखने से maths, logic और multi-step decisions में accuracy बढ़ती है। ध्यान दें: कुछ नए reasoning models अंदर ही सोचते हैं, इसलिए उन पर explicit CoT कम मदद करता है।

---

## 🔴 Problem it Solves
- An LLM predicts the next token; jumping straight to a final answer for a multi-step problem often fails.
- Writing steps gives the model "scratch space": each step becomes context for the next.
- Steps also make errors visible to humans and to checkers.

## 🔴 यह क्यों बना? (Hindi)
- LLM अगला token predict करता है; multi-step problem में सीधे final answer पर कूदना अक्सर गलत होता है।
- Steps लिखने से model को "scratch space" मिलता है: हर step अगले का context बनता है।
- Steps से गलतियाँ इंसानों और checkers को दिख जाती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Ask for reasoning first, answer last ("Think step by step, then give FINAL: ...")
Step 2 → Give a structure: attributes -> rule matching -> candidate codes -> final choice
Step 3 → Model writes intermediate steps (these are output tokens)
Step 4 → Each step conditions the next tokens
Step 5 → Parse only the line after "FINAL:" for the machine-readable answer
Step 6 → Optionally log the reasoning for audit
Step 7 → Compare accuracy and cost with and without CoT
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → पहले reasoning, आखिर में answer माँगो ("Think step by step, then give FINAL: ...")
Step 2 → Structure दो: attributes -> rule matching -> candidate codes -> final choice
Step 3 → Model बीच के steps लिखता है (ये output tokens हैं)
Step 4 → हर step अगले tokens को प्रभावित करता है
Step 5 → Machine-readable answer के लिए सिर्फ़ "FINAL:" के बाद वाली line parse करो
Step 6 → चाहो तो reasoning को audit के लिए log करो
Step 7 → CoT के साथ और बिना accuracy और cost compare करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: "Smart watch with cellular calling" can be an HS 8517 (communication apparatus) or 9102 (wrist watches). With a plain prompt the model picks 9102 half the time. With CoT: "1) List functions. 2) Identify the principal function per HS Note rules. 3) Pick the heading. 4) FINAL: code" accuracy rises from 68% to 87%, and the reasoning is stored so an officer can verify the logic.

**Amazon-style**: Calculating delivery fee with discounts, taxes and coupons step by step.

## 🟡 Real Example Hindi mein
**Tariff System**: "Cellular calling वाली smart watch" HS 8517 (communication apparatus) या 9102 (wrist watches) हो सकती है। साधारण prompt में model आधी बार 9102 चुनता है। CoT के साथ: "1) Functions list करो। 2) HS Note rules से principal function पहचानो। 3) Heading चुनो। 4) FINAL: code" accuracy 68% से 87% हो गई, और reasoning save होने से officer logic verify कर सकता है।

**Amazon-style**: Discounts, taxes और coupons के साथ delivery fee step by step निकालना।

---

## 💻 Code Example — Basic
```python
# Basic: build a CoT prompt and parse only the FINAL line (mock model, runs offline)
import re  # regular expressions

def cot_prompt(product: str) -> str:
    return (
        "You are a customs classifier.\n"  # role
        "Think step by step:\n"  # ask for reasoning
        "1) List the product's functions.\n"  # step 1
        "2) Decide the principal function.\n"  # step 2
        "3) Choose the HS heading.\n"  # step 3
        "End with a last line exactly like: FINAL: <4-digit heading>\n"  # parsable end
        f"Product: {product}"  # input
    )

def mock_llm(prompt: str) -> str:
    # Fake model output with reasoning and a final line
    return ("1) Functions: tells time, makes calls, tracks health.\n"
            "2) Principal function: communication.\n"
            "3) Heading for telephone apparatus.\n"
            "FINAL: 8517")

def extract_final(text: str) -> str | None:
    m = re.search(r"FINAL:\s*(\d{4})\s*$", text.strip(), re.MULTILINE)  # find last line
    return m.group(1) if m else None  # None if the model broke the format

out = mock_llm(cot_prompt("Smart watch with cellular calling"))
print(out)  # full reasoning (keep for audit)
print("Answer:", extract_final(out))  # only the final answer for code
```

## 💻 Code Example — Advanced
```python
# Production-style: async CoT with parsing, format-repair retry and token tracking
import asyncio  # async runtime
import re  # parse FINAL line
from dataclasses import dataclass  # result object
from openai import AsyncOpenAI, APIError  # openai>=1

client = AsyncOpenAI(timeout=30.0)  # shared client

SYSTEM = (
    "You are a customs classifier. Reason step by step in at most 5 short lines: "
    "functions, principal function, candidate headings, choice. "
    "Then write a last line: FINAL: <4-digit HS heading>."
)
FINAL_RE = re.compile(r"FINAL:\s*(\d{4})\s*$", re.MULTILINE)  # compiled once

@dataclass
class CotResult:
    heading: str | None  # parsed answer
    reasoning: str  # full text for audit
    tokens: int  # total tokens used

async def classify_cot(product: str, retries: int = 1) -> CotResult:
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": product}]
    total = 0  # token counter
    for attempt in range(retries + 1):
        try:
            resp = await client.chat.completions.create(
                model="gpt-4o-mini", temperature=0, max_tokens=250, messages=messages)
        except APIError as exc:
            return CotResult(None, f"API error: {exc}", total)
        text = resp.choices[0].message.content or ""
        total += resp.usage.total_tokens  # add tokens
        m = FINAL_RE.search(text.strip())  # try to parse
        if m:
            return CotResult(m.group(1), text, total)
        messages += [{"role": "assistant", "content": text},  # ask for format repair
                     {"role": "user", "content": "End with 'FINAL: <4 digits>' only."}]
    return CotResult(None, text, total)  # give up: caller routes to review

# print(asyncio.run(classify_cot("Smart watch with cellular calling")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel, Field  # validation

app = FastAPI()  # app

class Q(BaseModel):
    product: str = Field(min_length=3, max_length=500)  # product description
    include_reasoning: bool = False  # hide reasoning by default

@app.post("/classify-cot")
async def classify_route(q: Q) -> dict:
    r = await classify_cot(q.product)  # run CoT classification
    if r.heading is None:
        raise HTTPException(status_code=422, detail="Could not classify; send to review")
    body = {"heading": r.heading, "tokens": r.tokens}
    if q.include_reasoning:  # reasoning is optional output (audit or debugging)
        body["reasoning"] = r.reasoning
    return body
```

---

## 🔗 LangChain / LangGraph Connection
In LCEL: `prompt | llm | parser` where parser is a custom function that extracts the FINAL line. In LangGraph you can split CoT into separate nodes (analyse -> decide -> verify) for better control, or use structured output with a `reasoning` field first and `answer` second.

```python
from pydantic import BaseModel, Field  # schema
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_openai import ChatOpenAI  # model

class Decision(BaseModel):
    reasoning: str = Field(description="Short step-by-step reasoning")  # generated FIRST
    heading: str = Field(description="4-digit HS heading")  # generated after reasoning

prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the product. Fill reasoning before heading."), ("human", "{product}")])
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Decision)
# print(chain.invoke({"product": "Smart watch with cellular calling"}))
```
Field order matters: put `reasoning` before `answer` so the model reasons before it commits.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Asking for the answer first, then the explanation
✅ Correct: Reasoning first, final answer last.

```python
# Wrong: "Give the code, then explain."   # explanation is just a justification of a guess
# Right: "Reason step by step, then end with FINAL: <code>"
```

❌ Mistake 2: Showing raw reasoning to end users or trusting it blindly
✅ Correct: Treat reasoning as a helpful trace, not proof; parse the final field, verify with rules.

```python
# Wrong: return model_text_to_customer
# Right: return parsed["heading"]; store reasoning internally for audit
```

---

## 🧠 Tricky Interview Question
**Q**: "CoT improved accuracy but your latency and cost doubled. Also, a reviewer says the reasoning sometimes does not match the final answer. What now?"

**Answer**: CoT adds output tokens (cost and time). Limit it ("at most 5 short lines"), use CoT only for hard or low-confidence cases (route easy ones with zero-shot), or use a reasoning model that does it internally. Mismatched reasoning is "unfaithful reasoning": the written steps are not always the true cause of the answer. So do not use it as a legal explanation; verify the final answer against rules/tools, and use self-consistency or a checker for critical decisions.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is Chain of Thought prompting?
A1: Asking the model to write its reasoning steps before the final answer.

Q2: [Easy] Which tasks benefit most?
A2: Maths, logic, multi-step rules, planning, and ambiguous classification needing rule application.

Q3: [Medium] Zero-shot CoT vs few-shot CoT?
A3: Zero-shot CoT only adds a cue like "think step by step". Few-shot CoT includes example problems with worked reasoning. Few-shot is usually stronger but costs more tokens.

Q4: [Medium] What are the downsides?
A4: More output tokens (cost, latency), reasoning can be wrong or unfaithful, and longer outputs are harder to parse. Little gain on simple tasks.

Q5: [Hard] How does CoT relate to reasoning models like o-series?
A5: Reasoning models are trained to generate internal thinking tokens before answering, which is built-in CoT (billed as output tokens). Prompting them with long step-by-step instructions is often unnecessary; give a clear goal and constraints and let them think. For standard chat models, explicit CoT still helps.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multi-step reasoning, maths, rule application
- You need an audit trail

❌ Avoid when:
- Simple extraction or sentiment
- Tight latency/cost budgets or when using built-in reasoning models

---

## 📊 Visual Diagram
```
 Direct:   Question ───────────────────────────────► Answer (often wrong)

 CoT:      Question ─► Step 1 ─► Step 2 ─► Step 3 ─► FINAL answer
                        (each step becomes context for the next)
```

---

## 💰 Cost Impact
- CoT adds output tokens (often 100-300 per call). Output tokens are the pricey ones.
- Example (illustrative `gpt-4o-mini`, $0.60/1M output): +200 tokens x 100,000 calls = 20M tokens = about $12/day extra; on a large model with $10/1M output it is about $200/day.
- Optimise: limit steps ("max 5 short lines"), use CoT only on hard cases, cap `max_tokens`, or distil into a fine-tuned model.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CoT | Step-by-step reasoning prompt | कदम-दर-कदम सोचने वाला prompt |
| Reasoning trace | Written intermediate steps | बीच के steps का लिखित रूप |
| FINAL line | Parsable answer line | Parse होने वाली अंतिम line |
| Unfaithful reasoning | Steps not matching true cause | Steps असली कारण से मेल न खाएँ |
| Reasoning model | Model with internal thinking | अंदर सोचने वाला model |
| Scratch space | Room to work out steps | हल निकालने की जगह |

---

## ⚡ 3-Line Summary
English: CoT makes the model reason in steps before answering, improving multi-step accuracy. It costs extra output tokens and the reasoning may not be faithful. Use it for hard cases and parse only the final line.
Hindi: CoT model को जवाब से पहले steps में सोचने को कहता है, जिससे multi-step accuracy बढ़ती है। इसमें extra output tokens लगते हैं और reasoning हमेशा faithful नहीं होती। कठिन cases में इस्तेमाल करो और सिर्फ़ final line parse करो।

---

## ➡️ Next Topic
**055. Tree of Thought (ToT)** — explore several reasoning paths and pick the best one.
