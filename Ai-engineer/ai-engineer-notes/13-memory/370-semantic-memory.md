---

# 370. Semantic Memory
# हिंदी में: Semantic Memory (Facts की Memory)

---

## 🔵 Simple Definition (English)
Semantic memory stores stable facts and knowledge — "the user imports cotton t-shirts", "company VAT id is X", "HS 6109 = knitted T-shirts". Unlike episodic memory, it is not tied to one event. It is usually kept as a profile (key-value / JSON) or as a set of short fact statements.

## 🔵 सरल परिभाषा (Hindi)
Semantic memory स्थायी facts और knowledge store करती है — "user cotton t-shirts import करता है", "कंपनी का VAT id X है", "HS 6109 = knitted T-shirts"। Episodic से अलग, यह किसी एक घटना से बँधी नहीं होती। आम तौर पर profile (key-value / JSON) या छोटे fact statements के रूप में रखी जाती है।

---

## 🔴 Problem it Solves
- Asking "what do you import?" every session is annoying.
- Re-reading 50 old chats to find one fact is wasteful.
- Facts must be compact, deduplicated and updateable (e.g. user moved city).

## 🔴 यह क्यों बना? (Hindi)
- हर session में "आप क्या import करते हैं?" पूछना परेशान करता है।
- एक fact के लिए 50 पुरानी chats पढ़ना बेकार है।
- Facts छोटे, deduplicated और update होने लायक चाहिए (जैसे user शहर बदले)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → After a turn, an EXTRACTOR (cheap LLM or rules) pulls candidate facts from the text
Step 2 → Normalise: {"subject": "user", "key": "origin_country", "value": "Bangladesh"}
Step 3 → Compare with existing facts: new -> add, same -> skip, changed -> update (keep history)
Step 4 → Store in profile table / doc store (optionally embed for search)
Step 5 → At prompt time load the profile (small) or top-k relevant facts
Step 6 → Inject as "Known facts" block
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Turn के बाद EXTRACTOR (सस्ता LLM या rules) text से facts निकालता है
Step 2 → Normalise: {"subject": "user", "key": "origin_country", "value": "Bangladesh"}
Step 3 → मौजूदा facts से तुलना: नया -> add, वही -> skip, बदला -> update
Step 4 → Profile table / doc store में रखो (चाहें तो search के लिए embed)
Step 5 → Prompt के समय profile या top-k relevant facts load करो
Step 6 → "Known facts" block बनाकर inject करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Profile of importer: `{"business": "garment importer", "origin_country": "Bangladesh", "currency": "INR", "iec": "0123456789"}`. Every classification answer uses these without asking again.
**Amazon AI**: "shoe size 9, prefers Nike" stored as facts.

## 🟡 Real Example Hindi mein
**Tariff System**: Importer profile: `{"business": "garment importer", "origin_country": "Bangladesh", "currency": "INR"}`। हर answer बिना दोबारा पूछे इन्हें इस्तेमाल करता है।
**Amazon AI**: "shoe size 9, Nike पसंद" facts की तरह store।

---

## 💻 Code Example — Basic
```python
# Pure Python (offline): a semantic profile with rule-based fact extraction
import re                                                            # regex for simple extraction

profile: dict[str, str] = {}                                         # semantic memory = key/value facts

PATTERNS: dict[str, str] = {                                         # fact key -> regex
    "origin_country": r"import(?:s)? from ([A-Z][a-z]+)",           # "I import from Bangladesh"
    "currency": r"in (INR|USD|EUR)",                                 # "show duty in INR"
}

def extract_facts(text: str) -> dict[str, str]:                      # find facts in one message
    found: dict[str, str] = {}                                       # collect matches
    for key, pattern in PATTERNS.items():                            # try every pattern
        match = re.search(pattern, text)                             # search in text
        if match:                                                    # got one
            found[key] = match.group(1)                              # store captured value
    return found                                                     # return facts

def update_profile(text: str) -> None:                               # write path
    for key, value in extract_facts(text).items():                   # each new fact
        if profile.get(key) != value:                                # only if new/changed
            print(f"update {key}: {profile.get(key)} -> {value}")    # visible change log
            profile[key] = value                                     # upsert

update_profile("I import from Bangladesh and want duty in INR")      # first message
update_profile("Actually I import from Vietnam")                     # fact changes
print(profile)                                                       # final facts
```

## 💻 Code Example — Advanced
```python
# Async LLM-based fact extraction + upsert with history and validation
import asyncio                                                       # async runtime
import json                                                          # parse LLM output
from dataclasses import dataclass, field                             # data classes
from typing import Awaitable, Callable                               # callable typing

LLMFn = Callable[[str], Awaitable[str]]                              # prompt -> text


@dataclass
class Fact:                                                          # one semantic fact
    key: str                                                         # e.g. origin_country
    value: str                                                       # e.g. Vietnam
    history: list[str] = field(default_factory=list)                 # old values (audit)


EXTRACT_PROMPT = (                                                   # keep prompt short = cheap
    "Extract stable user facts from the message as JSON object "
    'like {"origin_country": "..."}; return {} if none.\nMessage: '
)
ALLOWED_KEYS = {"origin_country", "currency", "business", "product"}  # whitelist prevents junk


class SemanticMemory:                                                # per-user fact store
    def __init__(self, llm: LLMFn) -> None:
        self.llm = llm                                               # extractor model
        self.users: dict[str, dict[str, Fact]] = {}                  # user -> key -> Fact

    async def ingest(self, user_id: str, message: str) -> list[str]: # extract + upsert
        try:
            raw = await self.llm(EXTRACT_PROMPT + message)           # ask the model
            data = json.loads(raw)                                   # parse JSON
            if not isinstance(data, dict):                           # shape check
                return []
        except (json.JSONDecodeError, Exception):                    # bad output must not crash chat
            return []
        changes: list[str] = []                                      # what changed
        facts = self.users.setdefault(user_id, {})                   # user's facts
        for key, value in data.items():                              # each candidate
            if key not in ALLOWED_KEYS or not isinstance(value, str) or not value.strip():
                continue                                             # validate
            old = facts.get(key)                                     # existing fact
            if old is None:                                          # new fact
                facts[key] = Fact(key, value.strip())
                changes.append(f"add {key}")
            elif old.value != value.strip():                         # changed fact
                old.history.append(old.value)                        # keep audit trail
                old.value = value.strip()                            # update value
                changes.append(f"update {key}")
        return changes                                               # for logging

    def block(self, user_id: str) -> str:                            # prompt text
        facts = self.users.get(user_id, {})
        return "KNOWN FACTS:\n" + "\n".join(f"- {f.key}: {f.value}" for f in facts.values()) if facts else ""


async def fake_llm(prompt: str) -> str:                              # offline extractor
    return '{"origin_country": "Vietnam"}' if "Vietnam" in prompt else "{}"


async def main() -> None:
    mem = SemanticMemory(fake_llm)
    print(await mem.ingest("u1", "I import from Vietnam"))           # ['add origin_country']
    print(mem.block("u1"))                                           # prompt block

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Run extraction **after** responding (background task) so users do not wait for the extractor LLM; expose `GET /profile/{user_id}` so users can see and correct what you remember (trust + GDPR).

```python
# FastAPI: chat uses facts; extraction runs in background; profile endpoints for transparency
from fastapi import FastAPI, BackgroundTasks          # framework

app = FastAPI()                                       # app
sem = SemanticMemory(fake_llm)                        # singleton

@app.post("/chat")
async def chat(user_id: str, message: str, bg: BackgroundTasks) -> dict[str, str]:
    facts = sem.block(user_id)                        # load facts (cheap, no LLM)
    answer = f"(answer using {facts or 'no facts'})"  # real LLM call goes here
    bg.add_task(sem.ingest, user_id, message)         # extract AFTER reply
    return {"answer": answer}

@app.get("/profile/{user_id}")
async def profile(user_id: str) -> dict[str, str]:
    return {k: f.value for k, f in sem.users.get(user_id, {}).items()}   # show what we remember

@app.delete("/profile/{user_id}")
async def forget(user_id: str) -> dict[str, str]:
    sem.users.pop(user_id, None)                      # right to be forgotten
    return {"status": "deleted"}
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph docs call this "profile" or "collection" semantic memory stored in a `Store`. For extraction use `llm.with_structured_output(PydanticModel)` so the facts come back typed. LangMem and mem0 automate this.

```python
# Structured fact extraction with LangChain (pydantic v2 schema)
from pydantic import BaseModel, Field                      # schema
from langchain_openai import ChatOpenAI                    # model

class UserFacts(BaseModel):                                # what we want back
    origin_country: str | None = Field(None, description="Country user imports from")
    currency: str | None = Field(None, description="Preferred currency code")

extractor = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(UserFacts)
# facts = extractor.invoke("I import from Vietnam, show INR")   # -> UserFacts(...)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Storing facts as free text that duplicates
✅ Correct: store keyed, normalised facts and upsert.

```python
# Wrong: facts.append("user imports from Bangladesh"); facts.append("user imports from Vietnam")
# Right: facts["origin_country"] = "Vietnam"   # one truth, old value kept in history
```

❌ Mistake 2: Trusting the extractor blindly
✅ Correct: whitelist keys, validate types, keep confidence/source.

```python
# Wrong: profile.update(json.loads(llm_output))     # prompt injection can add any key
# Right: only keys in ALLOWED_KEYS, str values, length limits
```

---

## 🧠 Tricky Interview Question
**Q**: "User said 'I import from Bangladesh' in January and 'we moved sourcing to Vietnam' in June. The bot still says Bangladesh. Why and how to fix?"

**Answer**: Appending facts without conflict resolution leaves both; retrieval returns the older, stronger-embedded one. Fix: keyed upsert (latest wins), store `updated_at` and history, extract with an LLM that sees the existing fact ("update or add?"), and prefer recent facts when ranking. For ambiguity ask the user to confirm.

---

## ⚫ Interview Questions + Answers

Q1: What is semantic memory?
A1: Stable facts and general knowledge, independent of one event.

Q2: Give two storage formats.
A2: Profile (JSON/key-value, small, always loaded) and collection of fact statements with embeddings (large, searched by relevance).

Q3: How do you extract facts reliably?
A3: Structured output with a pydantic schema, low temperature, key whitelist, validation, and tests on labelled messages.

Q4: How do you handle contradicting facts?
A4: Upsert by key, keep history and timestamps, prefer latest, or ask the user to confirm when confidence is low.

Q5: Profile vs collection: when each?
A5: Profile for few well-known attributes (cheap, deterministic, easy to show/edit). Collection for open-ended facts that grow without bound; needs retrieval, dedupe and consolidation jobs; riskier for stale/duplicate data.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Personalisation (preferences, business details)
- Reducing repeated questions
- Compact always-on context

❌ Avoid when:
- Facts change every minute (use live tools/DB instead)
- Sensitive data without consent
- You cannot validate extractor output

---

## 📊 Visual Diagram
```
 message ─▶ [Extractor] ─▶ candidate facts ─▶ validate ─▶ upsert ─▶ Profile/Fact store
                                                                       │
 next prompt:  "KNOWN FACTS: origin=Vietnam, currency=INR" ◀───────────┘
```

---

## 💰 Cost Impact
- Extraction costs one small LLM call per message (~150 tokens in, ~30 out on gpt-4o-mini: well under $0.0001). Run it only on messages that look informative or batch every N turns.
- Benefit: a 10-fact profile is ~80 tokens vs thousands of history tokens.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fact | Stable piece of knowledge | स्थायी जानकारी |
| Profile | Key-value summary of user | User का key-value सार |
| Upsert | Insert or update | नया डालो या बदलो |
| Extractor | Pulls facts from text | Text से facts निकालने वाला |
| Whitelist | Allowed keys only | केवल अनुमत keys |

---

## ⚡ 3-Line Summary
English: Semantic memory keeps stable facts, usually as a small profile. Extract with structured output, validate, and upsert so latest truth wins. Let users view and delete their data.
Hindi: Semantic memory स्थायी facts रखती है, अक्सर छोटी profile के रूप में। Structured output से extract करो, validate करो और upsert करो ताकि नवीनतम सच रहे। User को अपना data देखने और delete करने दो।

---

## ➡️ Next Topic
**371. Procedural Memory** — remembering *how* to behave: rules, instructions and learned skills.
