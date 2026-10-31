---

# 053. Few-Shot Prompting
# हिंदी में: Few-Shot Prompting

---

## 🔵 Simple Definition (English)
Few-shot prompting puts a small number of input-output examples (usually 2-8) inside the prompt so the model copies the pattern, labels, style or format. The model learns "in context" at inference time; no training happens.

## 🔵 सरल परिभाषा (Hindi)
Few-shot prompting में prompt के अंदर कुछ (आमतौर पर 2-8) input-output examples रखे जाते हैं ताकि model वही pattern, labels, style या format दोहराए। Model inference के समय "in-context" सीखता है; कोई training नहीं होती।

---

## 🔴 Problem it Solves
- Instructions alone cannot describe subtle rules, house style or unusual formats.
- Labels like "borderline" or "high risk" mean different things for different companies.
- Fine-tuning for a small pattern is overkill.

## 🔴 यह क्यों बना? (Hindi)
- सिर्फ़ instructions से सूक्ष्म rules, house style या अनोखे formats समझाना मुश्किल है।
- "borderline" या "high risk" जैसे labels का मतलब हर company में अलग होता है।
- छोटे pattern के लिए fine-tuning ज़रूरत से ज़्यादा है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect real examples, including tricky edge cases
Step 2 → Pick 3-6 diverse examples (cover every label, avoid all being the same)
Step 3 → Format them identically: Input -> Output
Step 4 → Place them after the instruction and before the real input
Step 5 → Balance labels and vary order (models copy the last/majority label)
Step 6 → Test with and without examples; keep only those that help
Step 7 → For many examples, retrieve the most similar ones dynamically (dynamic few-shot)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → असली examples जमा करो, tricky edge cases सहित
Step 2 → 3-6 विविध examples चुनो (हर label कवर करो, सब एक जैसे न हों)
Step 3 → सबको एक ही format में लिखो: Input -> Output
Step 4 → Instruction के बाद और असली input से पहले रखो
Step 5 → Labels balance करो और order बदलो (model आखिरी/बहुमत label की नकल करता है)
Step 6 → Examples के साथ और बिना test करो; सिर्फ़ मददगार रखो
Step 7 → बहुत examples हों तो सबसे similar वाले dynamic रूप से retrieve करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Product descriptions in invoices are messy: "TWS BT 5.3 earphones w/ case blk". A prompt with 4 examples (messy text -> clean product name + HS chapter) raises accuracy from 74% to 91%. For a new customer with their own wording, we retrieve the 4 most similar past corrected invoices as examples (dynamic few-shot).

**Amazon-style**: Product title normalisation with examples of "ugly seller title -> clean title" in the brand's style.

## 🟡 Real Example Hindi mein
**Tariff System**: Invoice में product descriptions गंदे होते हैं: "TWS BT 5.3 earphones w/ case blk"। 4 examples (गंदा text -> साफ़ product name + HS chapter) वाला prompt accuracy 74% से 91% कर देता है। नए customer के अपने wording के लिए हम पुराने सुधारे हुए invoices में से 4 सबसे similar examples retrieve करते हैं (dynamic few-shot)।

**Amazon-style**: Product title normalisation जिसमें "गंदा seller title -> साफ़ title" के examples brand के style में होते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: build a few-shot prompt string (pure Python, runs offline)

EXAMPLES: list[tuple[str, str]] = [  # (messy input, clean output)
    ("TWS BT 5.3 earphones w/ case blk", "wireless earbuds | 85"),
    ("men cotton tee shirt L navy", "cotton t-shirt | 61"),
    ("basmati rice 5kg bag", "rice | 10"),
]

def few_shot_prompt(query: str, examples: list[tuple[str, str]]) -> str:
    lines = ["Convert messy invoice text to 'clean name | HS chapter'."]  # instruction
    for text, label in examples:  # add each example in the same format
        lines.append(f"Input: {text}\nOutput: {label}")
    lines.append(f"Input: {query}\nOutput:")  # real query, leave Output empty
    return "\n\n".join(lines)  # separate blocks with blank lines

prompt = few_shot_prompt("usb-c cable 2m braided", EXAMPLES)
print(prompt)  # inspect
print("Approx tokens:", len(prompt) // 4)  # rough cost estimate
```

## 💻 Code Example — Advanced
```python
# Production-style: dynamic few-shot with similarity selection, as proper chat messages
import asyncio  # async runtime
from difflib import SequenceMatcher  # simple similarity (use embeddings in production)
from openai import AsyncOpenAI, APIError  # openai>=1

client = AsyncOpenAI(timeout=15.0)  # shared client

BANK: list[tuple[str, str]] = [  # example bank (usually in a database)
    ("TWS BT 5.3 earphones w/ case blk", "wireless earbuds | 85"),
    ("men cotton tee shirt L navy", "cotton t-shirt | 61"),
    ("basmati rice 5kg bag", "rice | 10"),
    ("leather laptop sleeve 15in", "laptop sleeve | 42"),
    ("usb a to c cable 1m", "usb cable | 85"),
]

def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()  # 0..1 string similarity

def pick_examples(query: str, k: int = 3) -> list[tuple[str, str]]:
    ranked = sorted(BANK, key=lambda ex: similar(query, ex[0]), reverse=True)  # best first
    return ranked[:k]  # top-k most similar

def build_messages(query: str) -> list[dict[str, str]]:
    msgs: list[dict[str, str]] = [{"role": "system",
        "content": "Convert messy invoice text to 'clean name | HS chapter'. Output only that."}]
    for text, label in pick_examples(query):  # examples as user/assistant turns
        msgs.append({"role": "user", "content": text})
        msgs.append({"role": "assistant", "content": label})
    msgs.append({"role": "user", "content": query})  # real query last
    return msgs

async def normalise(query: str) -> str:
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, max_tokens=30,
            messages=build_messages(query))
        return (resp.choices[0].message.content or "").strip()
    except APIError as exc:
        return f"ERROR: {exc.__class__.__name__}"  # fail soft

# print(asyncio.run(normalise("usb-c cable 2m braided")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel, Field  # validation

app = FastAPI()  # app

class Q(BaseModel):
    text: str = Field(min_length=2, max_length=300)  # messy invoice text

class NewExample(BaseModel):
    text: str  # messy text
    label: str  # corrected output by a human

@app.post("/normalise")
async def normalise_route(q: Q) -> dict:
    return {"input": q.text, "output": await normalise(q.text)}  # dynamic few-shot call

@app.post("/examples")
async def add_example(ex: NewExample) -> dict:
    BANK.append((ex.text, ex.label))  # human corrections become future examples
    return {"bank_size": len(BANK)}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has `FewShotChatMessagePromptTemplate` and `SemanticSimilarityExampleSelector` (uses embeddings + a vector store to choose examples dynamically).

```python
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

examples = [  # static example list
    {"input": "TWS BT 5.3 earphones", "output": "wireless earbuds | 85"},
    {"input": "men cotton tee shirt", "output": "cotton t-shirt | 61"},
]
example_prompt = ChatPromptTemplate.from_messages([("human", "{input}"), ("ai", "{output}")])
few_shot = FewShotChatMessagePromptTemplate(example_prompt=example_prompt, examples=examples)
final = ChatPromptTemplate.from_messages([
    ("system", "Convert messy invoice text to 'clean name | HS chapter'."),
    few_shot,  # examples are inserted here
    ("human", "{input}"),
])
# chain = final | ChatOpenAI(model="gpt-4o-mini", temperature=0)
# For dynamic choice use SemanticSimilarityExampleSelector with an embeddings model + vector store.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Examples that all have the same label
✅ Correct: Cover every label and some edge cases.

```python
# Wrong: 5 examples, all "GOOD"  -> model says GOOD for everything
# Right: 2 GOOD, 2 SERVICE, 1 FEE, plus one tricky borderline case
```

❌ Mistake 2: Inconsistent example format
✅ Correct: Use one exact format.

```python
# Wrong: "Input: x => y" then "Q: x / A: y"
# Right: "Input: x\nOutput: y" for every example
```

---

## 🧠 Tricky Interview Question
**Q**: "You added 10 examples and accuracy dropped. Why?"

**Answer**: Possible causes: label imbalance or order bias (the model favours the last or most common label), examples that conflict with each other or with the instructions, noisy/incorrect example labels, overly similar examples that cause copying, or prompt length hurting attention for the actual input. Fix by auditing examples, balancing labels, shuffling order, and trying fewer, better examples; measure on a test set (not on the examples themselves).

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is few-shot prompting?
A1: Including a few input-output examples in the prompt to show the model the pattern.

Q2: [Easy] How many examples are usually enough?
A2: Often 3-8. More gives diminishing returns and costs tokens; test it.

Q3: [Medium] What is dynamic few-shot?
A3: Choosing examples per request by similarity (embeddings) from a larger bank, so each query gets the most relevant examples.

Q4: [Medium] What biases affect few-shot?
A4: Majority-label bias, recency bias (last example), and format copying. Balance and shuffle examples.

Q5: [Hard] Few-shot vs fine-tuning for 5M requests/month?
A5: Few-shot adds example tokens to every call (cost and latency), though prompt caching can reduce this for static examples. Fine-tuning a small model bakes the pattern in and shortens prompts, but needs a dataset, training and maintenance. Compare cost per correct answer; if the example set is stable and volume is high, fine-tuning often wins.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Custom labels, style or output format
- Messy real-world inputs

❌ Avoid when:
- Task is simple and zero-shot already works
- Prompt is near the context limit or cost is tight

---

## 📊 Visual Diagram
```
 [Instruction]
 [Example 1: input -> output]
 [Example 2: input -> output]
 [Example 3: input -> output]
 [Real input -> ?]
         |
         v
       LLM copies the pattern
         |
         v
   output in the same format
```

---

## 💰 Cost Impact
- Each example adds tokens to every call. 5 examples x 60 tokens = 300 extra input tokens. At 100,000 calls/day that is 30M extra tokens/day (about $4.50/day at $0.15/1M, much more on large models).
- Optimise: pick the fewest useful examples, dynamic selection (k=3), shorten examples, use provider prompt caching for static example blocks, or fine-tune.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Few-shot | Prompt with examples | Examples वाला prompt |
| In-context learning | Learning from prompt only | Prompt से सीखना |
| Dynamic few-shot | Choose examples per query | हर query के लिए examples चुनना |
| Recency bias | Favours last example | आखिरी example की तरफ झुकाव |
| Example bank | Stored examples | Examples का भंडार |
| Embedding | Vector of meaning | अर्थ का vector |

---

## ⚡ 3-Line Summary
English: Few-shot adds a few examples so the model copies your pattern. Use diverse, balanced, consistent examples and test the gain. Consider dynamic selection or fine-tuning for scale.
Hindi: Few-shot में कुछ examples जोड़े जाते हैं ताकि model आपका pattern दोहराए। Diverse, balanced और consistent examples लो और फ़ायदा test करो। Scale पर dynamic selection या fine-tuning सोचो।

---

## ➡️ Next Topic
**054. Chain of Thought (CoT)** — make the model reason step by step for harder problems.
