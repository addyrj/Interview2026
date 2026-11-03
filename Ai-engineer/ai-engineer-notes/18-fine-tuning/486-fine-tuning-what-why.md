---

# 486. Fine Tuning — What + Why
# हिंदी में: Fine Tuning — क्या और क्यों

---

## 🔵 Simple Definition (English)
Fine tuning means taking an already trained LLM and training it a little more on your own examples. The model's weights change, so it learns your style, format or task. After fine tuning, you need shorter prompts to get the behaviour you want.

## 🔵 सरल परिभाषा (Hindi)
Fine tuning का मतलब है पहले से trained LLM को आपके अपने examples पर थोड़ा और train करना। इससे model के weights बदल जाते हैं और वह आपका style, format या task सीख लेता है। Fine tuning के बाद छोटे prompt से भी वही behaviour मिल जाता है।

---

## 🔴 Problem it Solves
A base model is general. It does not know your output format, your company tone or your label set. Prompt engineering can fix some of this, but long prompts with 20 few-shot examples cost tokens on every call and still give inconsistent output. Fine tuning moves that knowledge from the prompt into the weights, so every call is cheaper and more consistent.

## 🔴 यह क्यों बना? (Hindi)
Base model general होता है। उसे आपका output format, company tone या label set नहीं पता होता। Prompt engineering कुछ हद तक मदद करती है, लेकिन 20 few-shot examples वाला लंबा prompt हर call पर tokens खर्च करता है और output फिर भी inconsistent रहता है। Fine tuning यह knowledge prompt से निकालकर weights में डाल देती है, इसलिए हर call सस्ती और consistent होती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick a pre-trained base model (e.g. gpt-4o-mini or Llama 3 8B)
Step 2 → Collect 50-1000+ high quality (input, ideal output) examples
Step 3 → Convert them to the training format (JSONL chat messages)
Step 4 → Run training: model sees examples, loss is computed, weights updated
Step 5 → Training runs for a few epochs (passes over the data)
Step 6 → You get a new model id (the fine tuned model)
Step 7 → Evaluate on held-out examples, then deploy and call it like any model
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक pre-trained base model चुनो (जैसे gpt-4o-mini या Llama 3 8B)
Step 2 → 50-1000+ अच्छे (input, ideal output) examples इकट्ठा करो
Step 3 → उन्हें training format (JSONL chat messages) में बदलो
Step 4 → Training चलाओ: model examples देखता है, loss निकलता है, weights update होते हैं
Step 5 → Training कुछ epochs (data पर कई passes) चलती है
Step 6 → आपको एक नया model id मिलता है (fine tuned model)
Step 7 → Held-out examples पर evaluate करो, फिर किसी भी model की तरह call करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The base model returns HS codes in free text: "I think it is around 8517". We need strict JSON like `{"hs_code": "8517.13", "confidence": "high"}`. We fine tune on 800 past classified products (description to JSON). Now the prompt is just "Classify: <description>" (about 30 tokens instead of 600), and the output format is correct nearly every time.

**Zomato-style**: Tag a restaurant review as `food`, `delivery`, `price` or `service`. A small fine tuned model beats a big prompted model on this narrow task at a fraction of the cost.

## 🟡 Real Example Hindi mein
**Tariff System**: Base model HS code free text में देता है: "मुझे लगता है 8517 के आसपास"। हमें strict JSON चाहिए `{"hs_code": "8517.13", "confidence": "high"}`। हम 800 पुराने classified products (description से JSON) पर fine tune करते हैं। अब prompt सिर्फ "Classify: <description>" है (600 की जगह लगभग 30 tokens) और output format लगभग हर बार सही आता है।

**Zomato-style**: Review को `food`, `delivery`, `price` या `service` tag करना। इस narrow task पर छोटा fine tuned model बड़े prompted model से कम cost में बेहतर चलता है।

---

## 💻 Code Example — Basic
```python
# Basic: show the idea of "prompt tokens saved" with pure Python (no API needed)
from typing import Dict, List  # type hints for clarity


def rough_tokens(text: str) -> int:
    """Very rough token estimate: about 4 characters per token (illustrative only)."""
    return max(1, len(text) // 4)  # never return 0


# A long prompt with few-shot examples, needed for the BASE model
few_shot_prompt: str = (
    "You classify products into HS codes. Reply ONLY as JSON.\n"
    "Example: 'iPhone 15' -> {\"hs_code\": \"8517.13\"}\n"
    "Example: 'Cotton T-shirt' -> {\"hs_code\": \"6109.10\"}\n"
    "Example: 'Laptop 14 inch' -> {\"hs_code\": \"8471.30\"}\n"
    "Now classify: Bluetooth headphones"
)

# A short prompt for the FINE TUNED model (behaviour lives in the weights)
tuned_prompt: str = "Classify: Bluetooth headphones"

# Compare the two prompts
base_tokens: int = rough_tokens(few_shot_prompt)  # tokens for base model prompt
tuned_tokens: int = rough_tokens(tuned_prompt)  # tokens for tuned model prompt
saving: float = 1 - tuned_tokens / base_tokens  # fraction of tokens saved

results: Dict[str, float] = {"base": base_tokens, "tuned": tuned_tokens, "saving": saving}
print(results)  # show the numbers
print(f"Prompt tokens saved per call: {saving:.0%}")  # human readable
```

## 💻 Code Example — Advanced
```python
# Production style: decide between "prompt only" and "fine tune" using a simple cost model
import asyncio  # async version
from dataclasses import dataclass  # tidy config object
from typing import Optional  # optional values


@dataclass
class Scenario:
    """Inputs for the break-even calculation (all prices are illustrative)."""

    calls_per_month: int  # how many API calls per month
    base_prompt_tokens: int  # prompt tokens with few-shot examples
    tuned_prompt_tokens: int  # prompt tokens after fine tuning
    output_tokens: int  # output tokens per call
    input_price_per_m: float  # $ per 1M input tokens (illustrative)
    output_price_per_m: float  # $ per 1M output tokens (illustrative)
    training_cost: float  # one time training cost in $ (illustrative)


def monthly_cost(prompt_tokens: int, s: Scenario) -> float:
    """Cost of one month at a given prompt size."""
    if s.calls_per_month < 0:  # guard against bad input
        raise ValueError("calls_per_month must be >= 0")
    per_call = (  # cost of one call
        prompt_tokens * s.input_price_per_m / 1_000_000
        + s.output_tokens * s.output_price_per_m / 1_000_000
    )
    return per_call * s.calls_per_month  # scale by volume


def break_even_months(s: Scenario) -> Optional[float]:
    """Months needed for fine tuning savings to repay training cost."""
    saving = monthly_cost(s.base_prompt_tokens, s) - monthly_cost(s.tuned_prompt_tokens, s)
    if saving <= 0:  # no saving means never pays back
        return None
    return s.training_cost / saving  # months to break even


async def analyse(s: Scenario) -> dict:
    """Async wrapper so it can be awaited inside an API route."""
    await asyncio.sleep(0)  # yield control (real code may call a pricing service)
    return {
        "base_monthly": round(monthly_cost(s.base_prompt_tokens, s), 2),
        "tuned_monthly": round(monthly_cost(s.tuned_prompt_tokens, s), 2),
        "break_even_months": break_even_months(s),
    }


if __name__ == "__main__":
    sc = Scenario(1_000_000, 600, 30, 40, 0.30, 1.20, 25.0)  # illustrative numbers
    print(asyncio.run(analyse(sc)))  # run the async function
```

---

## 🟠 FastAPI Integration
Fine tuning itself is an offline job. FastAPI comes in when you serve the tuned model: the route just uses the fine tuned model id from config.

```python
import os  # read env variables
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel  # request schema
from openai import AsyncOpenAI  # async OpenAI client

app = FastAPI()  # create app
client = AsyncOpenAI()  # reads OPENAI_API_KEY from env
# Fine tuned model id looks like ft:gpt-4o-mini-2024-07-18:org::abc123 (placeholder)
TUNED_MODEL: str = os.getenv("TARIFF_MODEL", "gpt-4o-mini")  # fall back to base


class ClassifyRequest(BaseModel):
    description: str  # product description


@app.post("/classify")
async def classify(req: ClassifyRequest) -> dict:
    """Classify a product using the fine tuned model with a SHORT prompt."""
    try:
        resp = await client.chat.completions.create(
            model=TUNED_MODEL,  # tuned model id
            messages=[{"role": "user", "content": f"Classify: {req.description}"}],
            max_tokens=60,  # output is small JSON
        )
    except Exception as exc:  # API errors
        raise HTTPException(status_code=502, detail=str(exc))
    return {
        "result": resp.choices[0].message.content,  # model answer
        "prompt_tokens": resp.usage.prompt_tokens,  # tokens used (cost tracking)
    }
```

---

## 🔗 LangChain / LangGraph Connection
A fine tuned model is used in LangChain exactly like any other chat model. Only the `model` name changes. In LangGraph, you can use the cheap tuned model for the classify node and a bigger model for the reasoning node.

```python
from langchain_openai import ChatOpenAI  # LangChain OpenAI wrapper
from langchain_core.prompts import ChatPromptTemplate  # prompt template

# Use the fine tuned model id (placeholder, replace with your own)
llm = ChatOpenAI(model="ft:gpt-4o-mini-2024-07-18:my-org::abc123", temperature=0)
prompt = ChatPromptTemplate.from_messages([("user", "Classify: {desc}")])  # short prompt
chain = prompt | llm  # LCEL chain
# result = await chain.ainvoke({"desc": "Bluetooth headphones"})  # needs API key
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Fine tuning to teach the model new facts
✅ Correct: Use RAG for facts, fine tuning for behaviour and format.

```python
# Wrong: train on tariff rate tables hoping the model memorises them
# Right: retrieve current rates with RAG, fine tune only the output style
```

❌ Mistake 2: Fine tuning before trying a good prompt
✅ Correct: Try prompt engineering and few-shot first, fine tune only if still not enough.

```python
# Wrong: jump to fine tuning on day 1 with 20 messy examples
# Right: build an eval set, measure the prompt baseline, then decide
```

---

## 🧠 Tricky Interview Question
**Q**: "A manager says: fine tune GPT on our 10,000 policy PDFs so it knows our policies. Good idea?"

**Answer**: Usually no. Fine tuning is poor at injecting factual knowledge, it can still hallucinate, and policies change so you would retrain again and again. Use RAG for the knowledge. Fine tune only if you also need a special tone, a strict format or a narrow classification skill. Often the best answer is RAG plus a small fine tune for style.

---

## ⚫ Interview Questions + Answers

Q1: What is fine tuning? (Easy)
A1: Further training a pre-trained model on task specific examples so its weights adapt to your task, style or format.

Q2: Does fine tuning change the model weights? (Easy)
A2: Yes in full fine tuning. With LoRA/QLoRA only small adapter weights are trained, and the base weights stay frozen.

Q3: Why does fine tuning reduce cost? (Medium)
A3: Behaviour moves from the prompt into weights, so you drop long instructions and few-shot examples. Fewer input tokens per call, and often a smaller model can replace a bigger one.

Q4: Fine tuning vs prompt engineering? (Medium)
A4: Prompting is fast, free to iterate and needs no data. Fine tuning needs data and training but gives consistency, lower per-call cost and shorter prompts. Start with prompting.

Q5: What risks come with fine tuning? (Hard)
A5: Overfitting on small data, catastrophic forgetting of general skills, bad labels being learned as truth, model version lock-in (when the base model is retired you must retrain), and no live knowledge updates. Mitigate with a held-out eval set, fewer epochs, clean data and a retraining pipeline.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a strict output format or consistent tone
- A narrow task has many labelled examples
- Long few-shot prompts make calls expensive
- You want a small cheap model to match a big one on one task

❌ Avoid when:
- You need fresh or private facts (use RAG)
- You have fewer than a few dozen good examples
- Prompting already meets your quality bar

---

## 📊 Visual Diagram
```
Base model (general)          Your examples (JSONL)
        │                              │
        └──────────────┬───────────────┘
                       ▼
              Training (update weights)
                       │
                       ▼
        Fine tuned model (specialised)
                       │
   short prompt ──────►│──────► consistent JSON output
```

---

## 💰 Cost Impact
- Training is a one time cost, billed by training tokens x epochs (prices are illustrative, check the provider page).
- Tuned models usually cost more per token than the base model, but prompts are much shorter.
- Token usage example: 600 prompt tokens down to 30 means about 95 percent fewer input tokens on every call.
- Optimise: start with the smallest base model, use few epochs, reuse the tuned model for many tasks, and track break-even months.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fine tuning | Extra training on your data | अपने data पर अतिरिक्त training |
| Base model | Pre-trained general model | शुरुआती general model |
| Weights | Learned numbers inside the model | Model के अंदर सीखे हुए numbers |
| Epoch | One full pass over training data | Data पर एक पूरा pass |
| Few-shot | Examples placed inside the prompt | Prompt में दिए examples |
| Overfitting | Memorises training data, fails on new | Training data रट लेना |

---

## ⚡ 3-Line Summary
English: Fine tuning trains a pre-trained model further on your examples so it learns style, format and narrow tasks.
It makes prompts shorter and output consistent, but it is not the right tool for adding fresh facts.
Try prompting and RAG first, fine tune when you have good data and a clear gap.
Hindi: Fine tuning pre-trained model को आपके examples पर और train करती है ताकि वह style, format और narrow task सीखे।
इससे prompt छोटे और output consistent होता है, लेकिन नए facts डालने के लिए यह सही tool नहीं है।
पहले prompting और RAG आज़माओ, अच्छा data और साफ gap हो तब fine tune करो।

---

## ➡️ Next Topic
**487. Fine Tuning vs RAG** — the most common interview comparison: when knowledge belongs in weights and when in retrieval.
