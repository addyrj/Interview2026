---

# 060. Role Prompting
# हिंदी में: Role Prompting

---

## 🔵 Simple Definition (English)
Role prompting tells the model to act as a specific persona ("You are a senior customs classification officer"). The role sets vocabulary, depth, tone and priorities. It helps style and focus, but it does not add knowledge the model does not have.

## 🔵 सरल परिभाषा (Hindi)
Role prompting में model को एक खास persona की तरह काम करने को कहा जाता है ("तुम एक senior customs classification officer हो")। Role से शब्दावली, गहराई, tone और priorities तय होती हैं। यह style और focus में मदद करता है, पर ऐसा knowledge नहीं जोड़ता जो model के पास नहीं है।

---

## 🔴 Problem it Solves
- Default answers are generic and may be at the wrong level (too simple or too technical).
- Different audiences need different voices: customs officer, new trader, auditor.
- A role gives the model a consistent point of view and checklist.

## 🔴 यह क्यों बना? (Hindi)
- Default जवाब generic होते हैं और गलत level के हो सकते हैं (बहुत आसान या बहुत technical)।
- अलग audiences को अलग आवाज़ चाहिए: customs officer, नया trader, auditor।
- Role model को एक स्थिर दृष्टिकोण और checklist देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose a role that matches the task and audience (expert, reviewer, teacher)
Step 2 → State experience level and domain: "senior customs officer, 15 years, India"
Step 3 → Add the audience: "explaining to a first-time importer"
Step 4 → Add responsibilities and checklist for that role
Step 5 → Add boundaries: what the role does not do
Step 6 → Add tone and format
Step 7 → Test role vs no-role on your test set; keep it only if it helps
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Task और audience से मेल खाता role चुनो (expert, reviewer, teacher)
Step 2 → Experience level और domain बताओ: "senior customs officer, 15 साल, भारत"
Step 3 → Audience जोड़ो: "पहली बार import करने वाले को समझाते हुए"
Step 4 → उस role की ज़िम्मेदारियाँ और checklist दो
Step 5 → सीमाएँ बताओ: role क्या नहीं करता
Step 6 → Tone और format दो
Step 7 → Role के साथ और बिना test set पर test करो; मदद करे तभी रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Three roles over the same data. (1) "Customs classifier": returns code and legal reasoning citing General Rules of Interpretation. (2) "Trade advisor for a first-time importer": explains in plain words what the code means for duty and paperwork. (3) "Skeptical auditor": challenges the classification and lists risks. The auditor role found 12% more wrong classifications when used as a second pass.

**Zomato-style**: "You are a friendly support agent for a food-delivery app" versus "You are a refund fraud analyst" give different behaviours on the same complaint.

## 🟡 Real Example Hindi mein
**Tariff System**: एक ही data पर तीन roles। (1) "Customs classifier": General Rules of Interpretation का हवाला देकर code और legal reasoning देता है। (2) "पहली बार import करने वाले का trade advisor": आसान शब्दों में बताता है कि code का duty और paperwork पर क्या असर है। (3) "शक्की auditor": classification को चुनौती देता है और जोखिम गिनाता है। दूसरे pass के रूप में auditor role ने 12% और गलत classifications पकड़ीं।

**Zomato-style**: "तुम food-delivery app के friendly support agent हो" बनाम "तुम refund fraud analyst हो" एक ही शिकायत पर अलग behaviour देते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: role templates + prompt builder (pure Python, runs offline)

ROLES: dict[str, str] = {  # role name -> persona text
    "classifier": ("You are a senior customs classification officer with 15 years of experience. "
                   "Cite the relevant General Rule of Interpretation."),
    "advisor": ("You are a friendly trade advisor explaining to a first-time importer. "
                "Use plain words, no jargon."),
    "auditor": ("You are a skeptical customs auditor. Look for misclassification risks "
                "and list them as bullets."),
}

def build_messages(role: str, task: str) -> list[dict[str, str]]:
    if role not in ROLES:  # protect against typos
        raise ValueError(f"Unknown role: {role}. Choose from {list(ROLES)}")
    return [
        {"role": "system", "content": ROLES[role]},  # persona goes in the system message
        {"role": "user", "content": task},  # task goes in the user message
    ]

for r in ROLES:  # show the same task with three roles
    msgs = build_messages(r, "Classify: Bluetooth speaker with FM radio")
    print(f"[{r}] system prompt: {msgs[0]['content']}\n")
```

## 💻 Code Example — Advanced
```python
# Production-style: async two-pass pipeline (classifier role then auditor role)
import asyncio  # async runtime
import json  # parse JSON
from pydantic import BaseModel  # pydantic v2
from openai import AsyncOpenAI, APIError  # openai>=1

client = AsyncOpenAI(timeout=25.0)  # shared client

CLASSIFIER = ("You are a senior customs classification officer. Return JSON "
              '{"hs_code": string, "reason": string}.')
AUDITOR = ("You are a skeptical customs auditor. Given a product and a proposed HS code, "
           'return JSON {"agree": boolean, "risks": [string]}. Do not invent legal text.')

class Review(BaseModel):
    hs_code: str  # proposed code
    reason: str  # reasoning from classifier
    agree: bool  # auditor verdict
    risks: list[str]  # auditor concerns

async def chat_json(system: str, user: str) -> dict:
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, max_tokens=250,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
        return json.loads(resp.choices[0].message.content or "{}")
    except (APIError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"role call failed: {exc}") from exc

async def classify_and_audit(product: str) -> Review:
    first = await chat_json(CLASSIFIER, product)  # pass 1: classifier role
    second = await chat_json(  # pass 2: auditor role challenges the answer
        AUDITOR, f"Product: {product}\nProposed code: {first.get('hs_code')}\nReason: {first.get('reason')}")
    return Review(hs_code=str(first.get("hs_code", "")), reason=str(first.get("reason", "")),
                  agree=bool(second.get("agree", False)), risks=list(second.get("risks", [])))

# print(asyncio.run(classify_and_audit("Bluetooth speaker with FM radio")))
```

---

## 🟠 FastAPI Integration
Let the client choose a role from an allow-list (enum), never free text that goes into the system prompt.

```python
from enum import Enum  # allowed values
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # validation

app = FastAPI()  # app

class RoleName(str, Enum):
    classifier = "classifier"
    advisor = "advisor"
    auditor = "auditor"

class Q(BaseModel):
    task: str  # user task
    role: RoleName = RoleName.classifier  # validated by FastAPI

@app.post("/ask-as")
async def ask_as(q: Q) -> dict:
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0.2, max_tokens=250,
            messages=build_messages(q.role.value, q.task))  # from basic example
    except APIError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return {"role": q.role, "answer": resp.choices[0].message.content}
```

---

## 🔗 LangChain / LangGraph Connection
In LangGraph, a multi-agent graph is role prompting at scale: each node is an agent with its own role (researcher, classifier, auditor), and edges decide who speaks next. In LangChain, the role is the system message in the template and can be a template variable.

```python
from langchain_core.prompts import ChatPromptTemplate  # template
from langchain_openai import ChatOpenAI  # model

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are {role_description}"),  # role as a variable
    ("human", "{task}"),
])
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0.2)  # LCEL
# chain.invoke({"role_description": "a skeptical customs auditor. List risks as bullets.",
#               "task": "HS 8518.22 for a Bluetooth speaker with FM radio"})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Believing the role adds knowledge
✅ Correct: Combine the role with retrieved facts and tools.

```python
# Wrong: "You are the world's best customs lawyer. Give the exact current duty."  # may hallucinate
# Right: role + tool call for the duty table / retrieved legal notes
```

❌ Mistake 2: Vague or inflated roles
✅ Correct: Specific role, audience and task.

```python
# Wrong: "You are a genius AI expert."
# Right: "You are a customs classification officer explaining to a first-time importer."
```

---

## 🧠 Tricky Interview Question
**Q**: "Does telling the model 'You are an expert' improve accuracy?"

**Answer**: Evidence is mixed. Roles reliably change style, depth and focus, and can help in open-ended or domain-flavoured tasks, but they give small or no gains on factual accuracy and reasoning for modern models. Do not assume; test with and without the role on your test set. Better accuracy levers: clear task instructions, examples, retrieval, tools, and verification. Role prompting is still very useful for tone, audience and multi-agent specialisation.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is role prompting?
A1: Assigning the model a persona or job so it answers in that voice and focus.

Q2: [Easy] Where is the role usually placed?
A2: In the system message, so it applies for the whole conversation.

Q3: [Medium] Why use different roles in one pipeline?
A3: Different roles give different perspectives: a generator proposes, a critic/auditor challenges, a writer explains. This catches errors a single pass misses.

Q4: [Medium] What are the risks?
A4: Over-confidence in an "expert" tone, role drift in long chats, and prompt injection if users can edit the role text. Keep roles server-side.

Q5: [Hard] How would you evaluate whether a role helps?
A5: A/B test prompt variants (no role, simple role, detailed role) on a labelled set, measuring accuracy, format validity, tone ratings and cost; check statistical significance and look at failure categories. Keep roles that show measurable gains on your metric.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Audience and tone matter
- Multi-agent or reviewer patterns

❌ Avoid when:
- Using the role as a substitute for facts or tools
- The task is mechanical and the role adds tokens only

---

## 📊 Visual Diagram
```
 same input: "Classify Bluetooth speaker with FM radio"
     |
     +--> [classifier role] --> code + legal reasoning
     |
     +--> [advisor role]    --> plain-language explanation
     |
     +--> [auditor role]    --> risks and challenges
```

---

## 💰 Cost Impact
- A role line is cheap (20-60 tokens) but multi-role pipelines multiply calls: classifier + auditor = 2 calls, so about 2x tokens.
- Example (illustrative `gpt-4o-mini`): 2 calls x 500 tokens x 100,000 items = 100M tokens = about $15-30/day depending on output share.
- Optimise: run the auditor only when classifier confidence is low or value is high, keep roles short, use a small model for the critic where tests allow, and cache.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Role prompting | Assign a persona | Persona देना |
| Persona | Character/voice for the model | Model की भूमिका/आवाज़ |
| Audience | Who reads the answer | जवाब किसके लिए है |
| Critic/auditor | Role that challenges output | जवाब को चुनौती देने वाला role |
| Multi-agent | Several role-based agents | कई role वाले agents |
| Role drift | Model leaves the role over time | Role से भटकना |

---

## ⚡ 3-Line Summary
English: Role prompting sets persona, audience and focus, mostly improving style and structure. It does not add facts, so pair it with tools or retrieval. Test whether the role really helps.
Hindi: Role prompting persona, audience और focus तय करता है, ज़्यादातर style और structure सुधारता है। यह facts नहीं जोड़ता, इसलिए tools या retrieval के साथ मिलाओ। Test करो कि role सच में मदद करता है या नहीं।

---

## ➡️ Next Topic
**061. Instruction Following** — how to write instructions the model actually obeys, and how to measure it.
