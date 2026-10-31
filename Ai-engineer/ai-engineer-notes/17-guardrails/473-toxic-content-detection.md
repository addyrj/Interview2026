---

# 473. Toxic Content Detection
# हिंदी में: Toxic Content की पहचान

---

## 🔵 Simple Definition (English)
Toxic content detection finds harmful language in user input or model output: hate, harassment, threats, sexual content, self-harm and violence. It scores text per category and the app decides to allow, warn, rewrite or block. Tools: the OpenAI moderation endpoint, Perspective-style classifiers, Llama Guard, and Guardrails Hub validators.

## 🔵 सरल परिभाषा (Hindi)
Toxic content detection user input या model output में हानिकारक भाषा खोजता है: नफरत, उत्पीड़न, धमकी, यौन सामग्री, self-harm और हिंसा। यह text को category के हिसाब से score करता है और app तय करता है कि allow, warn, rewrite या block करना है। Tools: OpenAI moderation endpoint, Perspective जैसे classifiers, Llama Guard और Guardrails Hub validators।

---

## 🔴 Problem it Solves
A public bot that repeats abuse or generates it harms users and your brand. Users can also provoke the model. Detection lets you refuse politely, protect staff who read logs, and meet platform and legal rules.

## 🔴 यह क्यों बना? (Hindi)
Public bot जो गाली दोहराए या बनाए, users और आपके brand दोनों को नुकसान पहुँचाता है। Users model को उकसा भी सकते हैं। Detection से आप विनम्रता से मना कर सकते हैं, logs पढ़ने वाले staff की रक्षा कर सकते हैं और platform व कानूनी नियम पूरे कर सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Take text (user input and/or model output)
Step 2 → Fast layer: blocklist / regex for obvious slurs (incl. Hindi and Hinglish)
Step 3 → Classifier: moderation API or local model returns category scores
Step 4 → Apply thresholds per category (self-harm stricter than mild profanity)
Step 5 → Action: allow | warn | rewrite | block | escalate (self-harm -> helpline text)
Step 6 → Log category and score, not the toxic text (to protect reviewers)
Step 7 → Review false positives weekly and tune thresholds
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Text लो (user input और/या model output)
Step 2 → तेज़ layer: साफ गालियों के लिए blocklist / regex (Hindi और Hinglish सहित)
Step 3 → Classifier: moderation API या local model category scores देता है
Step 4 → हर category का अलग threshold (self-harm सख्त, हल्की profanity ढीली)
Step 5 → Action: allow | warn | rewrite | block | escalate (self-harm -> helpline संदेश)
Step 6 → Category और score log करो, toxic text नहीं (reviewers की सुरक्षा)
Step 7 → हर हफ्ते false positives देखकर thresholds tune करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A frustrated importer types abusive words at the bot after a customs delay. The input guard detects harassment (score 0.92), the bot replies calmly: "I understand the delay is frustrating. Let me help with your shipment details", and the conversation is tagged for the support team. Product descriptions like "knife set" or "shot glasses" must not be flagged as violence, which is why context-aware classifiers beat plain keyword lists.

**Zomato AI**: Delivery partner reviews are screened for abuse before the summary is generated.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs देरी के बाद नाराज़ importer bot को गालियाँ लिखता है। Input guard harassment पकड़ता है (score 0.92), bot शांति से जवाब देता है: "मैं समझता हूँ देरी परेशान करती है। आइए आपके shipment की details देखें", और बातचीत support team के लिए tag होती है। "knife set" या "shot glasses" जैसे product descriptions को हिंसा नहीं माना जाना चाहिए, इसीलिए context समझने वाले classifiers सिर्फ keyword lists से बेहतर हैं।

**Zomato AI**: Delivery partner reviews को summary बनने से पहले abuse के लिए screen किया जाता है।

---

## 💻 Code Example — Basic
```python
# Basic toxicity check with a tiny blocklist + thresholds - pure Python, runs directly
import re  # regex

# Small demo lexicon with weights (real systems use a trained classifier)
LEXICON: dict[str, float] = {"idiot": 0.6, "stupid": 0.5, "kill you": 0.95, "hate you": 0.7}
THRESHOLDS: dict[str, float] = {"block": 0.85, "warn": 0.5}  # tune on labelled data


def score(text: str) -> float:
    t = re.sub(r"\s+", " ", text.lower())  # normalise spaces
    hits = [w for term, w in LEXICON.items() if term in t]  # matched terms
    return max(hits, default=0.0)  # highest score wins


def decide(text: str) -> str:
    s = score(text)
    if s >= THRESHOLDS["block"]:
        return "block"
    if s >= THRESHOLDS["warn"]:
        return "warn"
    return "allow"


for t in ["HS code for knife set?", "you are stupid", "I will kill you"]:
    print(t, "->", decide(t))
```

## 💻 Code Example — Advanced
```python
# Production: async moderation with OpenAI moderation endpoint + fallback + category thresholds
import asyncio  # async runtime
import logging  # logs
import os  # env
from dataclasses import dataclass  # result type

log = logging.getLogger("toxicity")

# Per-category thresholds: stricter for the dangerous ones
THRESHOLDS: dict[str, float] = {"harassment": 0.7, "hate": 0.5, "violence": 0.7, "self_harm": 0.3, "sexual": 0.6}


@dataclass
class ToxicityResult:
    action: str  # allow | block | escalate
    categories: dict[str, float]  # score per category


def local_fallback(text: str) -> dict[str, float]:
    bad = any(w in text.lower() for w in ("kill you", "hate you"))  # minimal backup rules
    return {"harassment": 0.9 if bad else 0.0}


async def moderate(text: str) -> ToxicityResult:
    scores: dict[str, float]
    if os.getenv("OPENAI_API_KEY"):
        try:
            from openai import AsyncOpenAI  # openai>=1

            client = AsyncOpenAI()
            r = await asyncio.wait_for(
                client.moderations.create(model="omni-moderation-latest", input=text), timeout=5
            )
            raw = r.results[0].category_scores.model_dump()  # e.g. {"harassment": 0.01, ...}
            scores = {k.replace("/", "_").replace("-", "_"): float(v or 0.0) for k, v in raw.items()}
        except Exception as exc:  # network, quota, timeout
            log.warning("moderation API failed (%s); using fallback", exc)
            scores = local_fallback(text)
    else:
        scores = local_fallback(text)  # offline mode
    flagged = {c: s for c, s in scores.items() if s >= THRESHOLDS.get(c, 0.8)}
    if "self_harm" in flagged:
        return ToxicityResult("escalate", scores)  # show support resources, notify human
    return ToxicityResult("block" if flagged else "allow", scores)


if __name__ == "__main__":
    for msg in ["HS code for a knife set", "I hate you and will kill you"]:
        print(msg, "->", asyncio.run(moderate(msg)).action)
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # models

app = FastAPI()


class Msg(BaseModel):
    text: str  # user message


@app.post("/chat")
async def chat(body: Msg) -> dict[str, str]:
    verdict = await moderate(body.text)  # screen input
    if verdict.action == "escalate":
        return {"reply": "You are not alone. Please contact a local helpline or someone you trust."}
    if verdict.action == "block":
        raise HTTPException(status_code=400, detail="Message violates our usage policy")
    reply = "HS code guidance goes here"  # LLM call
    out = await moderate(reply)  # screen output too
    return {"reply": reply if out.action == "allow" else "I cannot provide that response."}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has a moderation chain/tool for OpenAI moderation in the older API (`OpenAIModerationChain` in `langchain` classic). In modern LCEL/LangGraph, the simplest approach is a `RunnableLambda` or a graph node that calls `moderate` before and after the LLM node, with a conditional edge to a refusal node.

```python
from langchain_core.runnables import RunnableLambda  # wrapper


async def moderated(text: str) -> str:
    v = await moderate(text)
    if v.action != "allow":
        raise ValueError("moderation blocked")  # stops the chain
    return text


mod_step = RunnableLambda(moderated)  # supports ainvoke
# chain = mod_step | prompt | llm | StrOutputParser() | mod_step
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Keyword-only filters
✅ Correct: Use a classifier plus context; keywords flag "Scunthorpe"-type innocent words and miss creative spellings.

```python
# Wrong
if "shot" in text: block()
# Right
scores = await moderate(text)
```

❌ Mistake 2: Same threshold for every category and language
✅ Correct: Per-category thresholds, tested on Hindi and Hinglish data.

```python
# Wrong
if max(scores.values()) > 0.5: block()
# Right
flagged = {c: s for c, s in scores.items() if s >= THRESHOLDS[c]}
```

---

## 🧠 Tricky Interview Question
**Q**: "Your toxicity filter blocks 8% of legitimate Hindi-English mixed (Hinglish) messages. Why, and how do you fix it?"

**Answer**: Most classifiers are trained mainly on English; slang and code-mixed words can look like slurs, and transliterated Hindi may be mis-scored. Build a labelled Hinglish test set, measure false positives per category, add a multilingual or fine-tuned model, use allowlists for domain terms, and send borderline scores to a "warn/review" path instead of a hard block.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is toxic content detection?
A1: Automatically finding harmful language such as hate, harassment, threats and self-harm.

Q2: [Easy] Where do you apply it?
A2: On user input and on model output.

Q3: [Medium] Why per-category thresholds?
A3: Risks differ. Self-harm needs high recall (low threshold, human support), while mild profanity may only need a warning.

Q4: [Medium] Precision vs recall here?
A4: High recall catches more harm but blocks good users; high precision avoids false blocks but misses some harm. Choose by category risk.

Q5: [Hard] How do you moderate a streaming response?
A5: Check sentence by sentence before releasing, keep a lightweight rolling check on partial text, and on a violation stop the stream and replace with a safe message. For low-risk apps, moderate asynchronously and retract if flagged.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Public-facing chat or user-generated content
- Staff read conversation logs

❌ Avoid heavy moderation when:
- Closed internal tools with vetted users (keep a light check)
- It would block valid domain terms (tune with allowlists)

---

## 📊 Visual Diagram
```
text ─► blocklist (fast) ─► classifier (scores per category)
                                     │
        harassment 0.9  hate 0.1  self_harm 0.0 ...
                                     │ thresholds per category
          ┌──────────┬───────────────┼──────────────┐
        allow      warn/rewrite     block        escalate (self-harm)
```

---

## 💰 Cost Impact
The OpenAI moderation endpoint is currently free to use, so the cost is mainly latency (~100-300 ms) and engineering time. An LLM-based safety judge such as a 300-token gpt-4o-mini check costs about $0.00005 per message, roughly $50 per 1M messages. Optimise: run blocklists first, moderate input and output in parallel with the main call when safe, skip output checks for cached verified answers, and sample low-risk traffic.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Toxicity | Harmful/abusive language | हानिकारक/अपमानजनक भाषा |
| Moderation | Reviewing content safety | सामग्री की सुरक्षा जाँच |
| Threshold | Score cut-off | सीमा-मान |
| False positive | Good text blocked | सही text का block होना |
| Hinglish | Hindi in English letters | अंग्रेज़ी अक्षरों में हिंदी |
| Escalate | Send to human/support | इंसान/support को भेजना |

---

## ⚡ 3-Line Summary
English: Toxic content detection scores input and output by category and applies per-category actions. Combine a fast blocklist with a classifier and test on Hindi and Hinglish. Tune thresholds with real labelled data.
Hindi: Toxic content detection input और output को category के हिसाब से score करता है और हर category की अलग कार्रवाई करता है। तेज़ blocklist और classifier मिलाओ और Hindi व Hinglish पर test करो। Thresholds असली labelled data से tune करो।

---

## ➡️ Next Topic
**474. Bias Detection** - the next safety concern: unfair or skewed model behaviour across groups.
