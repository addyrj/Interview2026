---

# 024. Temperature + Top-p + Top-k
# हिंदी में: Temperature + Top-p + Top-k (Sampling Controls)

---

## 🔵 Simple Definition (English)
These are sampling settings that decide how the model picks the next token. **Temperature** makes the choice more or less random. **Top-p** (nucleus) keeps only the smallest set of tokens whose probabilities add up to p. **Top-k** keeps only the k most likely tokens.

## 🔵 सरल परिभाषा (Hindi)
ये sampling settings तय करती हैं कि model अगला token कैसे चुने। **Temperature** चुनाव को कम या ज़्यादा random बनाता है। **Top-p** (nucleus) सिर्फ़ उतने सबसे likely tokens रखता है जिनकी probability का जोड़ p हो। **Top-k** सिर्फ़ k सबसे likely tokens रखता है।

---

## 🔴 Problem it Solves
At each step the model produces a probability for every token in its vocabulary. Always picking the top one (greedy) gives dull, repetitive text and can get stuck in loops. Picking purely at random gives nonsense. Sampling controls let you balance: strict and repeatable for classification, creative for marketing copy.

## 🔴 यह क्यों बना? (Hindi)
हर step पर model पूरी vocabulary के हर token की probability बनाता है। हमेशा सबसे ऊपर वाला चुनो (greedy) तो text फीका और repetitive होता है। पूरी तरह random चुनो तो बकवास। Sampling controls से balance मिलता है: classification के लिए strict और repeatable, marketing copy के लिए creative।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Model outputs raw scores (logits) for every token
Step 2 → Temperature T: divide logits by T  (T<1 sharper, T>1 flatter)
Step 3 → Softmax turns scores into probabilities
Step 4 → Top-k: keep only the k highest-probability tokens
Step 5 → Top-p: keep the smallest set whose cumulative probability >= p
Step 6 → Re-normalise the remaining probabilities
Step 7 → Randomly sample one token from what is left
Step 8 → Repeat for the next token
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Model हर token के लिए raw scores (logits) देता है
Step 2 → Temperature T: logits को T से divide करो (T<1 तेज़/focused, T>1 सपाट/random)
Step 3 → Softmax से scores probabilities बनते हैं
Step 4 → Top-k: सिर्फ़ k सबसे ज़्यादा probability वाले tokens रखो
Step 5 → Top-p: वो सबसे छोटा set रखो जिसकी cumulative probability >= p
Step 6 → बचे हुए tokens की probabilities दोबारा normalise करो
Step 7 → बचे हुए में से एक token random sample करो
Step 8 → अगले token के लिए दोहराओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: Assigning an HS code must be repeatable. Same product, same code, every time. Use `temperature=0` (or very low). For drafting a customer-friendly explanation of why the code applies, `temperature=0.7` gives more natural wording.

**Amazon-style AI**: Product-title suggestions use temperature around 0.9 to get varied options, while the category tagger uses 0.

## 🟡 Real Example Hindi mein
**Tariff System**: HS code तय करना repeatable होना चाहिए। Same product, हर बार same code। इसलिए `temperature=0` (या बहुत कम)। Customer के लिए आसान explanation लिखने में `temperature=0.7` से wording ज़्यादा natural आती है।

**Amazon-style AI**: Product title suggestions में temperature लगभग 0.9 ताकि variety मिले, जबकि category tagger में 0।

---

## 💻 Code Example — Basic
```python
# Pure Python: see how temperature changes probabilities (no API key needed)
import math                                   # for exp
from typing import List                       # type hints

def softmax(logits: List[float], temperature: float = 1.0) -> List[float]:
    # Guard against divide by zero (temperature 0 means greedy)
    t = max(temperature, 1e-6)
    # Divide every score by temperature
    scaled = [x / t for x in logits]
    # Subtract max for numeric stability
    m = max(scaled)
    # Exponentiate each score
    exps = [math.exp(x - m) for x in scaled]
    # Normalise so they add to 1
    total = sum(exps)
    return [e / total for e in exps]

def top_p_filter(probs: List[float], p: float) -> List[int]:
    # Sort token indexes by probability, highest first
    order = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)
    kept: List[int] = []                      # indexes we keep
    cum = 0.0                                 # running probability total
    for i in order:                           # walk from most to least likely
        kept.append(i)                        # keep this token
        cum += probs[i]                       # add its probability
        if cum >= p:                          # enough mass collected
            break                             # stop
    return kept

tokens = ["8517", "8471", "8528", "9999"]     # candidate HS-code heading tokens
logits = [3.0, 2.0, 1.0, 0.1]                 # fake model scores

for t in (0.2, 1.0, 2.0):                     # low, normal, high temperature
    probs = softmax(logits, t)                # probabilities at this temperature
    print(f"T={t}: " + ", ".join(f"{tok}={p:.2f}" for tok, p in zip(tokens, probs)))

probs = softmax(logits, 1.0)                  # normal temperature
print("top_p=0.9 keeps:", [tokens[i] for i in top_p_filter(probs, 0.9)])
print("top_k=2 keeps:", tokens[:2])           # top-k is just the first k after sorting
```

## 💻 Code Example — Advanced
```python
# Production: task-based sampling presets with sync + async calls and error handling
import asyncio                                           # async runner
import logging                                           # logging
from dataclasses import dataclass                        # simple config object
from typing import Optional                              # optional type

from openai import AsyncOpenAI, OpenAI, OpenAIError      # SDK v1 clients + base error

logger = logging.getLogger(__name__)                     # module logger


@dataclass(frozen=True)
class Sampling:
    temperature: float                                   # randomness
    top_p: float = 1.0                                   # nucleus mass


# OpenAI guidance: change temperature OR top_p, not both
PRESETS = {
    "classify": Sampling(temperature=0.0),               # deterministic labels
    "explain": Sampling(temperature=0.7),                # natural wording
    "brainstorm": Sampling(temperature=1.0),             # varied ideas
}


def ask(prompt: str, preset: str = "classify", model: str = "gpt-4o-mini") -> Optional[str]:
    cfg = PRESETS[preset]                                # pick settings
    client = OpenAI()                                    # needs OPENAI_API_KEY
    try:
        r = client.chat.completions.create(
            model=model,                                 # model name
            messages=[{"role": "user", "content": prompt}],  # one user turn
            temperature=cfg.temperature,                 # randomness
            max_tokens=200,                              # cap output cost
            seed=42,                                     # best-effort reproducibility
        )
        return r.choices[0].message.content              # answer text
    except OpenAIError as exc:                           # any SDK error
        logger.error("LLM call failed: %s", exc)         # log it
        return None                                      # caller handles None


async def aask(prompt: str, preset: str = "classify", model: str = "gpt-4o-mini") -> Optional[str]:
    cfg = PRESETS[preset]                                # same presets
    client = AsyncOpenAI()                               # async client
    try:
        r = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=cfg.temperature,
            max_tokens=200,
        )
        return r.choices[0].message.content
    except OpenAIError as exc:
        logger.error("Async LLM call failed: %s", exc)
        return None


if __name__ == "__main__":
    print(asyncio.run(aask("HS heading for a smartphone? Answer with 4 digits.")))
```

---

## 🟠 FastAPI Integration
Let the endpoint choose the preset from the task, not from the user. This keeps classification deterministic.

```python
from fastapi import FastAPI, HTTPException      # framework + errors
from pydantic import BaseModel, Field           # pydantic v2 models
from openai import AsyncOpenAI, OpenAIError     # async client + base error

app = FastAPI()                                 # create app
client = AsyncOpenAI()                          # shared client


class ClassifyIn(BaseModel):
    product: str = Field(min_length=2)          # product description


class ExplainIn(BaseModel):
    product: str
    hs_code: str


async def run(prompt: str, temperature: float) -> str:
    try:
        r = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,            # task-specific
            max_tokens=250,
        )
        return r.choices[0].message.content or ""
    except OpenAIError as exc:                  # map SDK errors to HTTP
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/classify")
async def classify(body: ClassifyIn) -> dict:
    code = await run(f"Give only the HS code for: {body.product}", temperature=0.0)
    return {"hs_code": code.strip()}


@app.post("/explain")
async def explain(body: ExplainIn) -> dict:
    text = await run(f"Explain simply why {body.product} is {body.hs_code}", temperature=0.7)
    return {"explanation": text}
```

---

## 🔗 LangChain / LangGraph Connection
In LangChain, set `temperature` on the model object. Use different model objects for different graph nodes. Anthropic and Gemini also accept top-k; OpenAI does not expose top-k.

```python
from langchain_openai import ChatOpenAI          # OpenAI wrapper
from langchain_core.prompts import ChatPromptTemplate  # prompt template

classifier = ChatOpenAI(model="gpt-4o-mini", temperature=0)      # strict node
writer = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)        # creative node

prompt = ChatPromptTemplate.from_template("HS code for {product}? Reply with digits only.")
chain = prompt | classifier                      # LCEL pipe
# print(chain.invoke({"product": "power bank"}).content)

# LangGraph idea: node "classify" uses `classifier`, node "explain" uses `writer`.
# Each node owns its own sampling settings, so one graph mixes both behaviours.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: High temperature for classification or JSON output
✅ Correct: Use 0 for deterministic tasks.

```python
# Wrong — same product may get different codes on different calls
client.chat.completions.create(model="gpt-4o-mini", messages=m, temperature=1.2)
# Right — stable labels
client.chat.completions.create(model="gpt-4o-mini", messages=m, temperature=0)
```

❌ Mistake 2: Tuning temperature and top_p together
✅ Correct: Change one, leave the other at default. They interact and results are hard to reason about.

❌ Mistake 3: Assuming temperature=0 is 100 percent deterministic
✅ Correct: It is close, but GPU floating point and model updates can still change outputs. Use `seed` for best effort and validate outputs with a schema.

---

## 🧠 Tricky Interview Question

**Q**: "You set temperature=0 for your tariff classifier, yet the same input sometimes gives different codes. Why?"

**Answer**: Temperature 0 means greedy choice, but it is not a guarantee. Reasons: (1) near-tied logits can flip due to floating-point differences across GPUs and batch sizes, (2) the provider may update the model behind an alias, (3) a mixture-of-experts routing can vary. Mitigations: pin a dated model snapshot, pass `seed`, keep prompts identical, constrain output (enum or structured output), cache results by input hash, and run an evaluation set to catch drift.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does temperature do?
A1: It scales the logits before softmax. Low values make the distribution sharp (predictable); high values flatten it (more random).

Q2: [Easy] What temperature for a code or data-extraction task?
A2: 0 or very low, because you want consistent and correct output, not creativity.

Q3: [Medium] Difference between top-p and top-k?
A3: Top-k keeps a fixed number of tokens. Top-p keeps a variable number: the smallest set whose cumulative probability reaches p. Top-p adapts: few tokens when the model is confident, more when unsure.

Q4: [Medium] Which providers support top-k?
A4: Anthropic (`top_k`), Gemini (`top_k` in generation config), and Ollama/local models do. The OpenAI Chat Completions API does not expose top-k.

Q5: [Hard] Explain why high temperature increases hallucination risk.
A5: Flattening the distribution gives low-probability (often wrong) tokens a real chance to be sampled. One wrong early token then shapes everything after it because generation is autoregressive. So factual and structured tasks need low temperature plus grounding (RAG) and validation.

---

## 🔷 When to Use + When Not to Use
✅ Low temperature (0 to 0.3) when:
- Classification, extraction, SQL or JSON generation
- Reproducibility and testing matter

✅ Higher temperature (0.7 to 1.0) when:
- Creative writing, brainstorming, varied suggestions

❌ Avoid when:
- Tuning both temperature and top-p together
- Using a high value on factual question answering

---

## 📊 Visual Diagram
```
Next-token probabilities for: "HS code of phone is 85__"

Low T (0.2)            T = 1.0               High T (2.0)
 ██████████ 0.97        ██████ 0.66           ████ 0.45
 █ 0.02                 ██ 0.24               ███ 0.30
 . 0.01                 █ 0.09                ██ 0.17
                        . 0.01                █ 0.08
 (almost always         (balanced)            (more surprises)
  the top token)

Top-k=2 : keep the first 2 bars only
Top-p=0.9 : keep bars until cumulative >= 0.9
```

---

## 💰 Cost Impact
- Sampling settings do not change the price per token, but they change tokens used. High temperature can produce rambling, longer answers, and more retries when output validation fails.
- Low temperature gives stable outputs, so you can cache by input hash and avoid repeat calls.
- Always set `max_tokens` to cap output cost. Illustrative: 200 output tokens at $0.60 per 1M is $0.00012 per call; uncapped 1,000-token ramble is five times that.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Temperature | Randomness control | Randomness का control |
| Top-p (nucleus) | Keep tokens until cumulative p | p तक cumulative वाले tokens |
| Top-k | Keep k best tokens | सबसे अच्छे k tokens |
| Greedy decoding | Always pick the top token | हमेशा सबसे ऊपर वाला token |
| Logits | Raw model scores | Model के raw scores |
| Softmax | Scores to probabilities | Scores से probabilities |
| Seed | Fixed randomness start | Randomness का fixed starting point |

---

## ⚡ 3-Line Summary
English: Temperature, top-p, and top-k control how the model samples the next token. Use 0 for classification and extraction, and 0.7 to 1.0 for creative text. Tune only one of temperature or top-p, and never assume zero means perfectly deterministic.
Hindi: Temperature, top-p और top-k तय करते हैं कि model अगला token कैसे चुने। Classification और extraction के लिए 0, creative text के लिए 0.7 से 1.0। Temperature या top-p में से सिर्फ़ एक tune करो, और 0 को पूरी तरह deterministic मत मानो।

---

## ➡️ Next Topic
**025. OpenAI API — Complete Guide** — setup, key concepts, and every main endpoint in one place.
