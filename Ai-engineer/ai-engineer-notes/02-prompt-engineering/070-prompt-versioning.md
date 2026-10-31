---

# 070. Prompt Versioning
# हिंदी में: Prompt Versioning — Prompts का version control

---

## 🔵 Simple Definition (English)
Prompt versioning means storing every prompt change with a version id, author, date and eval score, so you can compare versions, roll back and audit. Prompts are treated like code or configuration, not like text scattered in the codebase.

## 🔵 सरल परिभाषा (Hindi)
Prompt versioning में हर prompt बदलाव को version id, author, date और eval score के साथ store करते हैं, ताकि versions की तुलना, rollback और audit हो सके। Prompts को code या configuration की तरह माना जाता है, codebase में बिखरे text की तरह नहीं।

---

## 🔴 Problem it Solves
A teammate edits one line of the tariff prompt on Friday. On Monday accuracy has dropped and nobody knows which change caused it, or what the old prompt was. Prompts hard-coded in Python strings change silently with each deploy, and cannot be rolled back without a code release.

Versioning gives traceability: "answer X was produced by prompt `classify@v7`".

## 🔴 यह क्यों बना? (Hindi)
शुक्रवार को teammate tariff prompt की एक line बदलता है। सोमवार को accuracy गिरी हुई है और किसी को नहीं पता कौन सा बदलाव ज़िम्मेदार है, या पुराना prompt क्या था। Python strings में hard-coded prompts हर deploy के साथ चुपचाप बदलते हैं, और code release के बिना rollback नहीं होता। Versioning से traceability मिलती है: "जवाब X, prompt `classify@v7` से बना।"

---

## 🟢 How it Works — Step by Step

```
Step 1 → Move prompts out of code into files or a registry (name + version)
Step 2 → Every change creates a NEW immutable version (never edit in place)
Step 3 → Store metadata: author, date, change note, model, params, eval score
Step 4 → Code loads a prompt by name + version (or an alias like "production")
Step 5 → Log prompt name@version with every LLM call
Step 6 → Test the new version on the eval set; compare with the current one
Step 7 → Promote by moving the alias; roll back by moving it back
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Prompts को code से बाहर files/registry में रखो (name + version)
Step 2 → हर बदलाव एक NEW immutable version बनाए (in place edit नहीं)
Step 3 → Metadata रखो: author, date, change note, model, params, eval score
Step 4 → Code name + version (या alias जैसे "production") से prompt load करे
Step 5 → हर LLM call के साथ prompt name@version log करो
Step 6 → नए version को eval set पर test करो; मौजूदा से तुलना करो
Step 7 → Alias आगे सरकाकर promote करो; वापस सरकाकर rollback
```

---

## 🟡 Real World Example
**Tariff Classification System**: Prompt `classify` has versions v1 to v7. v6 is `production`, v7 is `candidate` with a new accessories rule. A canary sends 5% of traffic to v7. Eval says v7 = 89% vs v6 = 84%, and live correction rate is lower, so the alias `production` moves to v7. When a customs officer disputes an old result, the log shows `classify@v5` was used.

**Amazon-style**: Product-description generator with separate prompt versions per marketplace and language.

## 🟡 Real Example Hindi mein
**Tariff System**: Prompt `classify` के versions v1 से v7। v6 `production` है, v7 `candidate` है जिसमें accessories का नया rule है। Canary 5% traffic v7 को भेजता है। Eval में v7 = 89% बनाम v6 = 84%, live correction rate भी कम, इसलिए alias `production` v7 पर चला जाता है। कोई officer पुराने result पर सवाल उठाए तो log दिखाता है कि `classify@v5` इस्तेमाल हुआ था।

**Amazon-style**: हर marketplace और भाषा के लिए अलग prompt versions के साथ product-description generator।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny in-memory prompt registry with versions and aliases (offline)
from dataclasses import dataclass  # simple immutable records

@dataclass(frozen=True)            # frozen = cannot be edited after creation
class PromptVersion:
    name: str                      # prompt name, e.g. "classify"
    version: int                   # 1, 2, 3 ...
    text: str                      # the prompt template
    note: str                      # why it changed

REGISTRY: dict[tuple[str, int], PromptVersion] = {}   # (name, version) -> prompt
ALIASES: dict[tuple[str, str], int] = {}              # (name, alias) -> version

def add(name: str, text: str, note: str) -> PromptVersion:
    existing = [v for (n, v) in REGISTRY if n == name]   # versions already stored
    version = max(existing, default=0) + 1               # next version number
    pv = PromptVersion(name, version, text, note)        # build the record
    REGISTRY[(name, version)] = pv                       # store it
    return pv

def get(name: str, ref: str | int) -> PromptVersion:
    version = ALIASES[(name, ref)] if isinstance(ref, str) else ref   # resolve alias
    return REGISTRY[(name, version)]                                  # fetch version

add("classify", "Give the HS code for {product}.", "initial")
add("classify", "Give the HS code for {product}. Accessories use their own heading.", "accessories rule")
ALIASES[("classify", "production")] = 1                  # production points to v1
print(get("classify", "production").note)                # initial
ALIASES[("classify", "production")] = 2                  # promote v2
print(get("classify", "production").note)                # accessories rule
ALIASES[("classify", "production")] = 1                  # instant rollback
print(get("classify", "production").version)             # 1
```

## 💻 Code Example — Advanced
```python
# Production: file-based registry (YAML-like JSON files), content hash, canary routing, logging
from __future__ import annotations

import asyncio                                   # async demo
import hashlib                                   # content hash for integrity
import json                                      # metadata files
import logging                                   # structured logs
import random                                    # canary sampling
from dataclasses import dataclass                # records
from pathlib import Path                         # file paths
from typing import Awaitable, Callable           # type hints

log = logging.getLogger("prompts")               # module logger
LLM = Callable[[str], Awaitable[str]]            # prompt -> reply

@dataclass(frozen=True)
class Prompt:
    name: str                                    # prompt name
    version: int                                 # version number
    text: str                                    # template text
    sha: str                                     # short content hash

    @property
    def ref(self) -> str:
        return f"{self.name}@v{self.version}"    # label to log with each call

class PromptStore:
    """Layout: root/<name>/v1.txt, v2.txt ... and root/<name>/aliases.json"""
    def __init__(self, root: Path) -> None:
        self.root = root                         # base directory

    def load(self, name: str, ref: str | int) -> Prompt:
        folder = self.root / name                # folder for this prompt
        try:
            if isinstance(ref, str):             # alias such as "production"
                aliases = json.loads((folder / "aliases.json").read_text(encoding="utf-8"))
                version = int(aliases[ref])      # resolve alias to a number
            else:
                version = ref
            text = (folder / f"v{version}.txt").read_text(encoding="utf-8")
        except (FileNotFoundError, KeyError, ValueError) as exc:    # missing file / alias
            raise LookupError(f"prompt {name}:{ref} not found") from exc
        sha = hashlib.sha256(text.encode()).hexdigest()[:8]         # integrity fingerprint
        return Prompt(name, version, text, sha)

async def run(store: PromptStore, llm: LLM, name: str, product: str,
              canary: int | None = None, canary_pct: float = 0.05) -> tuple[str, str]:
    use_canary = canary is not None and random.random() < canary_pct   # small % of traffic
    prompt = store.load(name, canary if use_canary else "production")  # pick version
    reply = await llm(prompt.text.format(product=product))             # call model
    log.info("llm_call prompt=%s sha=%s", prompt.ref, prompt.sha)      # traceability
    return reply, prompt.ref                                           # return which version ran

async def _demo() -> None:
    import tempfile
    root = Path(tempfile.mkdtemp())                      # temp registry
    (root / "classify").mkdir()
    (root / "classify" / "v1.txt").write_text("HS code for {product}?", encoding="utf-8")
    (root / "classify" / "v2.txt").write_text("HS code for {product}? Accessories differ.", encoding="utf-8")
    (root / "classify" / "aliases.json").write_text(json.dumps({"production": 1}), encoding="utf-8")
    async def llm(p: str) -> str:
        return "8518.30"
    print(await run(PromptStore(root), llm, "classify", "earbuds", canary=2, canary_pct=0.0))

if __name__ == "__main__":
    asyncio.run(_demo())
```
Token usage: versioning itself costs no tokens. Version metadata should include token counts of the prompt so you can see cost change per version.

---

## 🟠 FastAPI Integration
Load the production alias at request time (or cache it with a short TTL) so promotion and rollback need no redeploy. Return the prompt ref in a response header for debugging.

```python
from fastapi import FastAPI, HTTPException, Response   # framework pieces
from pathlib import Path                               # file paths
from pydantic import BaseModel                         # models
from openai import AsyncOpenAI                         # openai>=1

app = FastAPI()                                        # app
client = AsyncOpenAI()                                 # client
store = PromptStore(Path("prompts"))                   # from the advanced block

class Q(BaseModel):
    product: str                                       # input

async def openai_llm(p: str) -> str:
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, max_tokens=50,
        messages=[{"role": "user", "content": p}])
    return r.choices[0].message.content or ""

@app.post("/classify")
async def classify(q: Q, response: Response) -> dict[str, str]:
    try:
        reply, ref = await run(store, openai_llm, "classify", q.product, canary=None)
    except LookupError as exc:                         # prompt/alias missing
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    response.headers["X-Prompt-Version"] = ref         # trace which prompt answered
    return {"hs_code": reply}
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith's Prompt Hub stores and versions prompts (`hub.pull("name:tag")`), and `langchain_core.prompts.ChatPromptTemplate` can be built from the loaded text. In LangGraph put the prompt ref into the graph state or run metadata so every trace shows which version ran.

```python
from langchain_core.prompts import ChatPromptTemplate     # prompt template
from langchain_openai import ChatOpenAI                   # model

p = store.load("classify", "production")                  # load by alias
prompt = ChatPromptTemplate.from_template(p.text)         # build template from stored text
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0)
# result = await chain.ainvoke({"product": "earbuds"}, config={"metadata": {"prompt": p.ref}})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Editing a prompt in place
✅ Correct: Create a new immutable version.
```python
# Wrong: history lost
PROMPT = PROMPT.replace("guess", "avoid guessing")

# Right
add("classify", new_text, note="stop guessing")   # v3 created, v2 untouched
```

❌ Mistake 2: Not logging which version answered
✅ Correct: Log the ref with every call.
```python
# Wrong
reply = await llm(text)

# Right
reply = await llm(text)
log.info("prompt=%s", prompt.ref)
```

❌ Mistake 3: Versioning only the text, not the model and parameters. A new model with the same prompt behaves differently; store model, temperature and tools too.

---

## 🧠 Tricky Interview Question
**Q**: "You roll back the prompt to v5 but the bug stays. Why?"

**Answer**: The prompt is not the only thing that changed. Other versioned parts may differ: model snapshot, temperature, tool definitions, retrieval index, embedding model, post-processing code, or few-shot data. Version the whole "LLM configuration bundle" (prompt + model + params + retrieval settings) and log it per call. Also check that the cache or CDN is not serving old responses.

---

## ⚫ Interview Questions + Answers

Q1: Why version prompts?
A1: To track changes, compare quality, roll back quickly and audit which prompt produced which answer.

Q2: What should a prompt version record contain?
A2: Name, version, text, author, date, change note, model and parameters, eval score, and a content hash.

Q3: What is an alias like "production"?
A3: A movable pointer to a specific version. Promoting or rolling back means changing the pointer, with no redeploy.

Q4: Where can prompts be stored?
A4: Git files in the repo, a database or config service, or a prompt management tool (LangSmith Hub, Langfuse, etc.). Git is simple and reviewable; a registry allows runtime changes.

Q5 (Hard): Design a safe release process for prompt changes.
A5: Pull request with the new version and change note, automated eval on a fixed dataset (must beat the baseline and pass safety tests), review by a human, deploy as `candidate`, canary 5% of traffic with live metrics (accuracy proxies, latency, cost, escalation rate), promote the alias if healthy, keep the old version for instant rollback, and log the version on every call for audit.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Prompts affect production behaviour
- Several people edit prompts
- You need audit or compliance

❌ Avoid when:
- Throwaway prototypes (keep it simple)
- A one-off script with a single run

---

## 📊 Visual Diagram
```
 prompts/classify/
   v1.txt   v2.txt   v3.txt  ...  v7.txt
   aliases.json -> { "production": 6, "candidate": 7 }

 Request ---> load("classify","production") ---> v6 ---> LLM
        \--> 5% canary: load("classify", 7)   ---> v7 ---> LLM
                          |
                  log: classify@v6 / classify@v7
 Rollback = change "production" back to 5
```

---

## 💰 Cost Impact
- Versioning is free in tokens, but each version can change token count (longer prompt = higher cost on every call). Store `prompt_tokens` in metadata and compare versions.
- Canary and eval runs cost tokens; use a small dev set first.
- A bad version causes retries and wrong answers, which cost more than the registry.

Optimisation: track cost-per-request by prompt version in your logs, reject versions that raise cost without gaining quality, and pair with prompt caching by keeping the static prefix stable inside a version.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Version | A saved state of a prompt | Prompt की सहेजी हुई अवस्था |
| Immutable | Cannot be changed after saving | सहेजने के बाद बदला नहीं जा सकता |
| Alias | Movable name for a version | Version का बदला जा सकने वाला नाम |
| Rollback | Return to an older version | पुराने version पर लौटना |
| Canary | Small traffic test | थोड़े traffic पर परीक्षण |
| Audit trail | Record of what ran | क्या चला उसका रिकॉर्ड |

---

## ⚡ 3-Line Summary
English: Prompt versioning stores every prompt change as an immutable version with metadata and scores. Use aliases for promotion and rollback, and log the version with every call. Version the model and parameters too.
Hindi: Prompt versioning हर बदलाव को metadata और scores के साथ immutable version के रूप में रखती है। Promotion और rollback के लिए aliases इस्तेमाल करो और हर call के साथ version log करो। Model और parameters भी version करो।

---

## ➡️ Next Topic
**071. Prompt Testing Strategy** — how to build eval sets and automated tests that decide whether a new prompt version is better.
