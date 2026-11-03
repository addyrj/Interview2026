---

# 595. Build Prompt Manager
# हिंदी में: Prompt Manager बनाना

---

## 🔵 Simple Definition (English)
A prompt manager stores prompts as named, versioned templates. You render them with validated variables, activate a version, and roll back if a new prompt performs worse.

## 🔵 सरल परिभाषा (Hindi)
Prompt manager prompts को named, versioned templates की तरह store करता है। Variables validate करके render करता है, version activate करता है और नया prompt खराब निकले तो rollback करता है।

---

## 🔴 Problem it Solves
Prompts hard-coded in code get edited casually, with no history. A small wording change can break accuracy and nobody knows which version was live during an incident. Missing template variables silently produce broken prompts.

## 🔴 यह क्यों बना? (Hindi)
Code में hard-coded prompts बिना history के बदल दिए जाते हैं। छोटा wording change accuracy तोड़ सकता है और पता नहीं चलता incident के समय कौन सा version live था। Variable छूटने पर prompt चुपचाप टूट जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → register(name, template): new content -> new version number + SHA hash
Step 2 → Identical content is not duplicated
Step 3 → One version per name is "active"
Step 4 → render(name, **vars): check missing and extra variables
Step 5 → Return (text, "name@vN:sha") so logs can show the prompt version
Step 6 → rollback(name, version): flip the active pointer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → register: नया content -> नया version number + SHA hash
Step 2 → वही content दोबारा नहीं बनता
Step 3 → हर name का एक version "active" रहता है
Step 4 → render: missing और extra variables check होते हैं
Step 5 → (text, "name@vN:sha") return होता है ताकि logs में version दिखे
Step 6 → rollback: active pointer बदल दो
```

---

## 🟡 Real World Example
**Tariff Classification System**: prompt v1 says "Give the HS code for: {product}". v2 adds "You are a customs expert, give code + reason". The team evaluates v2 on a test set, ships it, sees reason-quality drop for textiles, and rolls back to v1 in one call. Every classification log has `classify@v1:edd84831` so audits can reproduce results.

**Zomato-style**: different prompt versions per city or language, A/B tested.

## 🟡 Real Example Hindi mein
**Tariff System**: v1 में सिर्फ HS code माँगा गया, v2 में "customs expert बनो, code + reason दो"। Test set पर v2 चला, textiles में quality गिरी, तो एक call में v1 पर rollback। हर log में `classify@v1:edd84831` होता है ताकि audit में result दोबारा बन सके।

**Zomato**: city/language के हिसाब से अलग prompt versions, A/B test।

---

## 💻 Code Example — Basic
```python
# Minimal template with validation using only the standard library
import string


TEMPLATE: str = "Give the HS code for: {product}"       # a named prompt


def render(template: str, **kwargs: str) -> str:
    """Fill variables; fail loudly if one is missing."""
    needed = {f for _, f, _, _ in string.Formatter().parse(template) if f}  # names in template
    missing = needed - kwargs.keys()                     # variables not supplied
    if missing:
        raise ValueError(f"missing: {sorted(missing)}")  # fail early, not silently
    return template.format(**kwargs)                     # safe to format now


print(render(TEMPLATE, product="LED bulb"))              # Give the HS code for: LED bulb
```

## 💻 Code Example — Advanced
Full file: `main.py` (frozen dataclass `PromptVersion`, `PromptManager`). Observed output:
```
classify@v2:a2841b4d -> You are a customs expert. Give HS code + reason for: LED bulb
classify@v1:edd84831
error: missing variables: ['product']
```
```python
# Excerpt from main.py
def register(self, name: str, template: str, activate: bool = True) -> PromptVersion:
    versions = self._store.setdefault(name, [])          # list of versions per name
    if versions and versions[-1].template == template:   # no change -> no new version
        return versions[-1]
    pv = PromptVersion(name, len(versions) + 1, template,
                       hashlib.sha256(template.encode()).hexdigest()[:8])  # content hash
    versions.append(pv)                                  # append-only history
    if activate:
        self._active[name] = pv.version                  # new version goes live
    return pv
```
Async note: rendering is pure CPU and instant, so no async is needed; only the storage (database) layer would be async in production.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from main import PromptManager                           # our module

app = FastAPI()
pm = PromptManager()
pm.register("classify", "You are a customs expert. HS code for: {product}")


@app.post("/classify")
async def classify(product: str) -> dict:
    try:
        text, tag = pm.render("classify", product=product)   # tag = version id
    except (KeyError, ValueError) as e:                      # unknown prompt or bad vars
        raise HTTPException(status_code=500, detail=str(e))
    # response = await llm.ainvoke(text)  # real LLM call goes here
    return {"prompt_tag": tag, "prompt": text}


@app.post("/admin/prompts/{name}/rollback/{version}")
async def rollback(name: str, version: int) -> dict:
    try:
        pm.rollback(name, version)                           # flip active version
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"active": version}
```

---

## 🔗 LangChain / LangGraph Connection
`ChatPromptTemplate` is LangChain's template object; you can build it from a managed version.

```python
from langchain_core.prompts import ChatPromptTemplate

template_text = "You are a customs expert. HS code for: {product}"   # from manager
prompt = ChatPromptTemplate.from_messages([("system", "Be concise."),
                                           ("human", template_text)])
print(prompt.invoke({"product": "LED bulb"}).to_messages())          # rendered messages
```
LangSmith Hub also versions prompts. In LangGraph, pass the version tag in node metadata so traces show it.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Editing a prompt in place.
✅ Correct: register a new version; old ones stay immutable.

```python
# Wrong
PROMPT = PROMPT.replace("brief", "detailed")   # history lost
# Right
pm.register("classify", new_text)              # v3 created, v2 still available
```

❌ Mistake 2: Using `str.format` on user-supplied templates. Curly-brace attribute access like `{x.__class__}` can leak data; only allow templates written by your team, or use a sandboxed engine.
✅ Correct: templates from trusted storage; user input only as values.

❌ Mistake 3: Not logging the version with each LLM call.

---

## 🧠 Tricky Interview Question
**Q**: "After a prompt change accuracy dropped, but your tests passed. Why?"

**Answer**: Tests were likely too few or not representative, or they checked format rather than quality. Prompt changes can shift behaviour on rare categories. Fix: maintain an evaluation set per prompt, run it in CI for every new version, canary the new version on a slice of traffic, log the version tag, and keep one-click rollback.

---

## ⚫ Interview Questions + Answers

Q1: Why version prompts?
A1: To reproduce past behaviour, compare versions, and roll back safely.

Q2: Why a content hash?
A2: It identifies exact content; two environments can verify they run the same prompt.

Q3: Where should prompts live?
A3: Files in git (reviewed) or a database/registry with audit trail; not scattered string literals.

Q4: How do you A/B test prompts?
A4: Hash the user ID to a bucket, serve version A or B, log tag + outcome, compare on the eval metric.

Q5 (Hard): How do you deploy prompt changes without redeploying code, safely?
A5: Store versions in a registry; services fetch the active version with short caching; promotion goes through eval gates and canary percentage; rollback just moves the pointer; every call logs the version tag.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple prompts, several people editing, production audit needs

❌ Avoid when:
- A single throwaway script

---

## 📊 Visual Diagram
```
 register("classify", t1) ─► v1 ┐
 register("classify", t2) ─► v2 ├─ history (immutable)
                                │
              active ─────────► v2      rollback(1) ─► active = v1
                                │
 render(**vars) ─ validate ─► (text, "classify@v2:sha") ─► LLM + log
```

---

## 💰 Cost Impact
The manager is free to run, but prompt length is paid on every call: a 900-token system prompt at 1M calls/month is 900M input tokens. Version tracking lets you measure token count per version, compare cost vs quality, and ship shorter prompts. Also place the static part first so provider prompt caching can discount it (prices illustrative, check provider).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Template | Prompt with placeholders | Placeholders वाला prompt |
| Version | Numbered immutable copy | नंबर वाली अपरिवर्तनीय copy |
| Rollback | Return to older version | पुराने version पर वापस |
| Hash | Fingerprint of content | Content की पहचान |
| Canary | Small-traffic test | थोड़े traffic पर test |

---

## ⚡ 3-Line Summary
English: Treat prompts like code: versioned, validated, logged. Render with checks for missing and extra variables. Keep rollback one call away.
Hindi: Prompts को code की तरह treat करो: versioned, validated, logged। Missing/extra variables check करो। Rollback एक call दूर रखो।

---

## ➡️ Next Topic
**596. Build Fine Tuning Dataset** — when prompting is not enough, build clean training data.
