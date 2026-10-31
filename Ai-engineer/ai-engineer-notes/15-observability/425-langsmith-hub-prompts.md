---

# 425. LangSmith Hub (Prompts)
# हिंदी में: LangSmith Hub (Prompts)

---

## 🔵 Simple Definition (English)
LangSmith Hub (the Prompt Hub / Prompt Canvas area) is a place to store, version and share prompts outside your code. Each prompt has a name, commit history and tags (like `prod`). Your app pulls a prompt by name with `client.pull_prompt("name")`, so changing a prompt needs no redeploy.

## 🔵 सरल परिभाषा (Hindi)
LangSmith Hub (Prompt Hub) prompts को code से बाहर store, version और share करने की जगह है। हर prompt का नाम, commit history और tags (जैसे `prod`) होते हैं। App `client.pull_prompt("name")` से prompt खींचता है, इसलिए prompt बदलने के लिए redeploy नहीं चाहिए।

---

## 🔴 Problem it Solves
- Prompts hard-coded in Python need a code review and deployment for every wording change.
- No history: nobody knows which prompt version produced yesterday's bad answers.
- Non-engineers (domain experts) cannot edit prompts safely.

## 🔴 यह क्यों बना? (Hindi)
- Python में hard-code prompts बदलने के लिए हर बार code review और deployment चाहिए।
- History नहीं: पता नहीं कल के खराब answers किस prompt version से बने।
- Non-engineers (domain experts) prompts सुरक्षित रूप से edit नहीं कर सकते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a ChatPromptTemplate in code or the Hub UI
Step 2 → Push: client.push_prompt("tariff-classifier", object=prompt)
Step 3 → Each push creates a commit hash; you can add tags (staging, prod)
Step 4 → App pulls: client.pull_prompt("tariff-classifier:prod")
Step 5 → Returned object is a LangChain prompt → pipe into model
Step 6 → Test new commit in Playground / evaluate() on a dataset
Step 7 → Move tag "prod" to the winning commit → app picks it up (cache TTL)
Step 8 → Roll back by moving the tag to the previous commit
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Code या Hub UI में ChatPromptTemplate लिखो
Step 2 → Push: client.push_prompt("tariff-classifier", object=prompt)
Step 3 → हर push एक commit hash बनाता है; tags (staging, prod) जोड़ सकते हैं
Step 4 → App pull करता है: client.pull_prompt("tariff-classifier:prod")
Step 5 → मिला object LangChain prompt है → model से pipe करो
Step 6 → नया commit Playground / evaluate() से dataset पर test करो
Step 7 → जीतने वाले commit पर tag "prod" ले जाओ → app उसे उठा लेता है (cache TTL के बाद)
Step 8 → Rollback के लिए tag को पिछले commit पर वापस ले जाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: The customs expert edits the prompt "Always check chapter and section notes before choosing a heading" in the Hub. A new commit `a1b2c3d` is created. An evaluation on `tariff-golden` shows +4 points. The engineer moves tag `prod` to that commit; within 5 minutes (cache TTL) all pods use it, with no deployment. Next week a regression is found; the tag moves back in 10 seconds.

**Zomato AI**: Marketing edits the tone of the offers prompt weekly; engineering keeps the structure and variables stable.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs expert Hub में prompt बदलता है: "Heading चुनने से पहले हमेशा chapter और section notes देखो"। नया commit `a1b2c3d` बनता है। `tariff-golden` पर evaluation में +4 points दिखते हैं। Engineer tag `prod` उस commit पर ले जाता है; 5 मिनट (cache TTL) में सभी pods नया prompt इस्तेमाल करते हैं, बिना deployment। अगले हफ़्ते regression मिले तो tag 10 सेकंड में वापस।

**Zomato AI**: Marketing हर हफ़्ते offers prompt का tone बदलती है; engineering structure और variables स्थिर रखती है।

---

## 💻 Code Example — Basic
```python
# Basic: a local "prompt registry" with commits and tags — the idea behind Hub (offline)
import hashlib                                                # commit hash
from dataclasses import dataclass, field                      # structures

@dataclass
class PromptRegistry:
    commits: dict[str, str] = field(default_factory=dict)     # hash -> template text
    tags: dict[str, str] = field(default_factory=dict)        # tag -> hash

    def push(self, template: str, tag: str | None = None) -> str:
        h = hashlib.sha1(template.encode()).hexdigest()[:7]   # content-based commit id
        self.commits[h] = template                            # store the version
        if tag:
            self.tags[tag] = h                                # move tag to this commit
        return h

    def pull(self, ref: str) -> str:
        h = self.tags.get(ref, ref)                           # accept a tag or a hash
        if h not in self.commits:
            raise KeyError(f"unknown prompt ref: {ref}")      # clear error
        return self.commits[h]

reg = PromptRegistry()
v1 = reg.push("Classify {product} into an HS code.", tag="prod")
v2 = reg.push("Check chapter notes, then classify {product} into an HS code.", tag="staging")
print(reg.pull("prod").format(product="power bank"))          # v1 text
reg.tags["prod"] = v2                                         # promote staging -> prod
print(reg.pull("prod").format(product="power bank"))          # v2 text (no redeploy!)
```

## 💻 Code Example — Advanced
```python
# Real Hub usage: push, pull by tag, TTL cache, fallback to local prompt, async-safe
# pip install langsmith langchain-core
import asyncio                                                # async wrapper
import logging                                                # logs
import time                                                   # TTL cache
from langchain_core.prompts import ChatPromptTemplate         # prompt type
from langsmith import Client                                  # SDK

log = logging.getLogger("hub")                                # logger

FALLBACK = ChatPromptTemplate.from_messages([                 # safe local default
    ("system", "You are a customs tariff expert. Return only the HS code."),
    ("human", "Product: {product}"),
])

_cache: dict[str, tuple[float, ChatPromptTemplate]] = {}      # ref -> (time, prompt)
TTL_SECONDS = 300                                             # refresh every 5 minutes

def push_prompt(name: str, prompt: ChatPromptTemplate) -> str:
    client = Client()                                         # needs LANGSMITH_API_KEY
    return client.push_prompt(name, object=prompt, description="Tariff classifier prompt")  # returns URL

def pull_prompt_sync(ref: str) -> ChatPromptTemplate:
    now = time.time()                                         # current time
    hit = _cache.get(ref)                                     # cached copy?
    if hit and now - hit[0] < TTL_SECONDS:
        return hit[1]                                         # fresh enough
    try:
        prompt = Client().pull_prompt(ref)                    # e.g. "tariff-classifier:prod"
        _cache[ref] = (now, prompt)                           # update cache
        return prompt
    except Exception as exc:                                  # network/auth/not found
        log.warning("hub pull failed (%s); using %s", type(exc).__name__, "cache" if hit else "fallback")
        return hit[1] if hit else FALLBACK                    # stale cache beats nothing

async def get_prompt(ref: str = "tariff-classifier:prod") -> ChatPromptTemplate:
    return await asyncio.to_thread(pull_prompt_sync, ref)     # keep event loop responsive

if __name__ == "__main__":
    p = asyncio.run(get_prompt())                             # falls back offline
    print(p.format_messages(product="power bank"))
```

---

## 🟠 FastAPI Integration
Load the prompt per request through the cached helper, so editing the `prod` tag in Hub changes behaviour without redeploying. Return the prompt ref used, so incidents can be traced to a prompt version.

```python
from fastapi import FastAPI                                   # framework
from langchain_openai import ChatOpenAI                       # model

app = FastAPI()                                               # app
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)          # shared model object

@app.get("/classify")
async def classify(product: str, ref: str = "tariff-classifier:prod") -> dict[str, str]:
    prompt = await get_prompt(ref)                            # cached Hub prompt (or fallback)
    chain = prompt | llm                                      # LCEL composition
    msg = await chain.ainvoke({"product": product})           # async call
    return {"hs_code": str(msg.content), "prompt_ref": ref}   # expose which prompt was used
```

---

## 🔗 LangChain / LangGraph Connection
`pull_prompt` returns a normal LangChain prompt (`ChatPromptTemplate`), so `prompt | model | parser` works unchanged. In LangGraph, pull the prompt inside a node (or at graph construction time) and log its ref in node metadata. `langchain.hub.pull` is an older alias; prefer `Client().pull_prompt`.

```python
from langchain_core.output_parsers import StrOutputParser     # string output

# chain = (await get_prompt("tariff-classifier:prod")) | llm | StrOutputParser()
# answer = await chain.ainvoke({"product": "power bank"}, config={"metadata": {"prompt_ref": "tariff-classifier:prod"}})
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Pulling `latest` in production, so an unreviewed edit goes live instantly.
✅ Correct: pull a tag (`:prod`) or a commit hash, and promote deliberately after evaluation.

```python
# Wrong
Client().pull_prompt("tariff-classifier")          # latest commit
# Right
Client().pull_prompt("tariff-classifier:prod")     # controlled by tag
```

❌ Mistake 2: Pulling the prompt over the network on every request, with no fallback.
✅ Correct: cache with TTL and keep a local fallback.

```python
# Wrong
prompt = Client().pull_prompt(ref)   # adds 100-300 ms and fails if Hub is down
# Right
prompt = await get_prompt(ref)       # TTL cache + fallback
```

---

## 🧠 Tricky Interview Question
**Q**: "Prompts live in Hub and can be changed without deployment. What new risks does that create?"

**Answer**: Behaviour can change without code review, tests or release process. Risks: bad edit breaks JSON output format, variable names change (`{product}` removed) and crash chains, or Hub downtime breaks the app. Mitigation: tags for environments, mandatory evaluation before moving `prod`, schema/variable checks in CI, access control (who can move `prod`), TTL caching with a local fallback, logging of prompt ref/commit in every trace, and an easy rollback.

---

## ⚫ Interview Questions + Answers

Q1: What is the Prompt Hub used for? (Easy)
A1: Storing, versioning, sharing and pulling prompts separately from application code.

Q2: How do you load a prompt from Hub? (Easy)
A2: `Client().pull_prompt("owner/name:tag")` (or just `"name"`), which returns a LangChain prompt object.

Q3: Why use tags like `prod` and `staging`? (Medium)
A3: Tags are movable pointers to commits, so you can promote or roll back a prompt without changing code or hashes.

Q4: How do you test a prompt change safely? (Medium)
A4: Push as a new commit, run `evaluate()` on a dataset comparing with the current prod commit, check quality, tokens and format validity, then move the tag.

Q5: When would you keep prompts in code instead of a Hub? (Hard)
A5: When prompts are tightly coupled to code (structured output schemas, tool names), when compliance needs every change reviewed in git, when offline/air-gapped deployment is required, or when latency/availability risk of an external dependency is unacceptable. A hybrid works: prompts in git, synced to Hub on release for visibility and evaluation.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Domain experts edit prompts
- You iterate on prompts often and want history and rollback

❌ Avoid when:
- Strict change control requires git-only review
- Prompts are trivial and rarely change

---

## 📊 Visual Diagram
```
  Hub: "tariff-classifier"
   commit a1b2c3d (v1)  ◄── tag: staging-old
   commit e4f5a6b (v2)  ◄── tag: prod   ── moved here after eval ✔
   commit 9c8d7e6 (v3)  ◄── tag: staging
          │
   App pods:  pull_prompt("tariff-classifier:prod")  (cache 5 min)
          │
   prompt | llm | parser → answer   (trace logs prompt_ref)
```

---

## 💰 Cost Impact
- Hub itself does not use tokens, but prompt length directly sets input cost on every call. A 1,500-token system prompt at 100K requests/day on gpt-4o-mini is 150M tokens/day, about $22/day for the prompt alone.
- Optimise: A/B test shorter prompts via evaluation, move static examples into fewer shots, use provider prompt caching for the stable prefix, and track tokens per prompt commit in traces.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Prompt Hub | Store for versioned prompts | Versioned prompts का भंडार |
| Commit | One saved prompt version | Prompt का एक सहेजा version |
| Tag | Movable name for a commit | Commit का बदलने वाला नाम |
| Pull / Push | Download / upload prompt | Prompt लाना / भेजना |
| Rollback | Return to earlier version | पुराने version पर लौटना |
| TTL cache | Cache that expires after time | समय बाद खत्म होने वाला cache |

---

## ⚡ 3-Line Summary
English: The Hub stores prompts with commits and tags so they can be edited, evaluated and rolled back without redeploying code. Pull by tag, cache with a TTL and keep a local fallback. Always evaluate before moving the `prod` tag.
Hindi: Hub prompts को commits और tags के साथ रखता है ताकि बिना redeploy के edit, evaluate और rollback हो सके। Tag से pull करो, TTL के साथ cache करो और local fallback रखो। `prod` tag हिलाने से पहले हमेशा evaluate करो।

---

## ➡️ Next Topic
**426. LangSmith Monitoring** — dashboards and alerts to watch these traces and prompts in production.
