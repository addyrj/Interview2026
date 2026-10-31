---

# 347. Agent Types + Roles
# हिंदी में: Agent के प्रकार + Roles

---

## 🔵 Simple Definition (English)
An agent type is a standard job an agent can do: router, researcher, executor, planner, critic, validator, writer. A role is the written contract for that job: goal, allowed tools, input format and output format. Clear roles make agents predictable.

## 🔵 सरल परिभाषा (Hindi)
Agent type एक standard काम है जो agent कर सकता है: router, researcher, executor, planner, critic, validator, writer। Role उस काम का लिखित contract है: goal, allowed tools, input format और output format। Clear roles से agents predictable बनते हैं।

---

## 🔴 Problem it Solves
- Agents with vague roles ("be helpful") overlap, repeat work and argue.
- Without defined output formats, the next agent cannot parse the previous result.
- Giving every agent every tool is both a safety risk and a quality risk.
- Teams cannot test an agent when nobody knows what it should do.

## 🔴 यह क्यों बना? (Hindi)
- Vague roles ("helpful बनो") वाले agents overlap करते हैं, काम दोहराते हैं और टकराते हैं।
- Output format तय न हो तो अगला agent पिछला result parse नहीं कर पाता।
- हर agent को हर tool देना safety और quality दोनों के लिए खतरा है।
- जब पता ही न हो agent को क्या करना है, तो उसे test नहीं कर सकते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List the sub-tasks in the workflow
Step 2 → Map each sub-task to a type (router, researcher, executor, critic ...)
Step 3 → Write a role spec: goal, tools, input schema, output schema, limits
Step 4 → Turn the spec into a system prompt + a Pydantic output model
Step 5 → Give the agent only the tools in its spec
Step 6 → Test each agent alone with fixed examples
Step 7 → Connect agents through typed outputs
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Workflow के sub-tasks की list बनाओ
Step 2 → हर sub-task को type से map करो (router, researcher, executor, critic ...)
Step 3 → Role spec लिखो: goal, tools, input schema, output schema, limits
Step 4 → Spec को system prompt + Pydantic output model में बदलो
Step 5 → Agent को सिर्फ spec वाले tools दो
Step 6 → हर agent को fixed examples से अलग से test करो
Step 7 → Typed outputs से agents को जोड़ो
```

---

## 🟡 Real World Example
**Tariff Classification System** roles:
- Router: decides if the query is a new classification, a duty-rate lookup or a dispute.
- Researcher: searches HS code database and past rulings (tool: vector search).
- Classifier (executor): picks the final 8-digit code.
- Critic/Validator: checks the code against chapter notes and flags doubt.
- Writer: produces the importer-friendly explanation.

**Zomato**: router (food vs grocery), searcher, ranker, support agent. **Amazon**: order agent, returns agent, recommendation agent.

## 🟡 Real Example Hindi mein
**Tariff System** roles: Router (नई classification, duty-rate lookup या dispute), Researcher (HS database और पुराने rulings search), Classifier (final 8-digit code), Validator (chapter notes से check), Writer (importer के लिए explanation)।

**Zomato**: router, searcher, ranker, support agent। **Amazon**: order agent, returns agent, recommendation agent।

---

## 💻 Code Example — Basic
```python
# Role specs as plain data, so every agent has a clear contract
from dataclasses import dataclass  # lightweight typed container


@dataclass(frozen=True)  # frozen: a role should not change at runtime
class Role:
    name: str  # role name
    goal: str  # one-sentence goal
    tools: tuple[str, ...]  # tools this role may use
    output: str  # expected output format


ROLES: dict[str, Role] = {  # registry of all roles
    "router": Role("router", "Pick the next specialist", (), "one word: research|classify"),
    "researcher": Role("researcher", "Find HS candidates", ("vector_search",), "list of codes"),
    "critic": Role("critic", "Find problems in an answer", (), "OK or a list of issues"),
}


def build_prompt(role: Role) -> str:  # turn a role into a system prompt
    tools = ", ".join(role.tools) or "none"  # readable tool list
    return f"You are the {role.name}. Goal: {role.goal}. Tools: {tools}. Reply as: {role.output}."


for r in ROLES.values():  # print every prompt
    print(build_prompt(r))  # shows the generated prompt
```

## 💻 Code Example — Advanced
```python
# Typed roles with enforced tool permissions and structured output (pydantic v2)
import asyncio  # async runtime
from typing import Awaitable, Callable  # type hints
from pydantic import BaseModel, Field, ValidationError  # validation

ToolFn = Callable[[str], Awaitable[str]]  # async tool signature


class RoleSpec(BaseModel):
    name: str  # role name
    goal: str  # goal
    allowed_tools: list[str] = Field(default_factory=list)  # permission list


class AgentOutput(BaseModel):
    role: str  # who answered
    content: str  # answer text
    confidence: float = Field(ge=0.0, le=1.0)  # must be between 0 and 1


async def vector_search(q: str) -> str:  # sample tool
    await asyncio.sleep(0.01)  # fake latency
    return f"results for {q}"  # fake result


TOOLS: dict[str, ToolFn] = {"vector_search": vector_search}  # tool registry


class RoleAgent:
    def __init__(self, spec: RoleSpec) -> None:
        self.spec = spec  # keep the spec

    async def call_tool(self, tool: str, arg: str) -> str:
        if tool not in self.spec.allowed_tools:  # enforce permission
            raise PermissionError(f"{self.spec.name} cannot use {tool}")
        return await TOOLS[tool](arg)  # run the allowed tool

    async def run(self, task: str) -> AgentOutput:
        raw = {"role": self.spec.name, "content": f"done: {task}", "confidence": 0.8}
        try:  # validate the model output shape
            return AgentOutput(**raw)
        except ValidationError as exc:  # bad output from the LLM
            raise ValueError(f"invalid output: {exc}") from exc


async def main() -> None:
    researcher = RoleAgent(RoleSpec(name="researcher", goal="search", allowed_tools=["vector_search"]))
    critic = RoleAgent(RoleSpec(name="critic", goal="review"))
    print(await researcher.call_tool("vector_search", "t-shirt"))  # allowed
    try:
        await critic.call_tool("vector_search", "x")  # not allowed
    except PermissionError as exc:
        print("blocked:", exc)  # permission works


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Expose the role registry so the frontend or other services can see which agents exist, and route a request to one role.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app

ROLE_GOALS: dict[str, str] = {  # simple registry
    "researcher": "Find HS candidates",
    "critic": "Review answers",
}


class RunRequest(BaseModel):
    role: str  # which role to run
    task: str  # input


@app.get("/roles")
async def list_roles() -> dict[str, str]:
    return ROLE_GOALS  # show available roles


@app.post("/run")
async def run_role(req: RunRequest) -> dict[str, str]:
    if req.role not in ROLE_GOALS:  # unknown role
        raise HTTPException(status_code=404, detail="unknown role")
    return {"role": req.role, "result": f"{req.role} handled {req.task}"}
```

---

## 🔗 LangChain / LangGraph Connection
In LangChain a role is a `ChatPromptTemplate` with a system message plus a structured-output model. Each role becomes a runnable; LangGraph nodes call them.

```python
from langchain_core.prompts import ChatPromptTemplate  # prompt template
from pydantic import BaseModel  # output schema


class Verdict(BaseModel):
    ok: bool  # approved or not
    issues: list[str]  # list of problems


critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a customs critic. Find problems in the HS code answer."),
    ("human", "{answer}"),
])  # role = system prompt
# critic = critic_prompt | ChatOpenAI(model="gpt-4o-mini").with_structured_output(Verdict)
print(critic_prompt.format_messages(answer="6109.10")[0].content)  # check template
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: One "do everything" role.
✅ Correct: One job per agent.

```python
# Wrong
prompt = "You search, classify, validate and write the report."
# Right
prompts = {"search": "Only search.", "classify": "Only classify.", "validate": "Only validate."}
```

❌ Mistake 2: Free-text output between agents.
✅ Correct: Use a typed schema.

```python
# Wrong: next agent must guess
reply = "I think maybe 6109?"
# Right: parseable
reply_obj = {"code": "6109.10", "confidence": 0.82}
```

---

## 🧠 Tricky Interview Question
**Q**: "Your researcher and critic agents keep agreeing with each other even when the answer is wrong. Why?"

**Answer**: They share the same model, similar prompts and often the same context, so errors correlate (shared bias). Make the critic independent: give it different instructions (checklist of rules), different tools or data (chapter notes, deterministic validators), possibly a different model, and hide the researcher's reasoning so it checks the result, not the argument. Measure critic recall on a set of known-bad answers.

---

## ⚫ Interview Questions + Answers

Q1: Name common agent types.
A1: Router, planner, researcher, executor, writer, critic/validator, and supervisor/orchestrator.

Q2: What goes into a role spec?
A2: Goal, allowed tools, input and output schema, limits (max steps, tokens) and escalation rule.

Q3: Why restrict tools per agent?
A3: Better tool choice accuracy, smaller prompts, and safety (a writer agent should not be able to call a delete or payment tool).

Q4: How do you test a role?
A4: Unit-test it alone with a golden dataset and a mock for its tools, check output schema validity and measure accuracy per role.

Q5: How do you stop roles from overlapping in a large system?
A5: Write a responsibility matrix, make inputs/outputs disjoint, use a router with a clear decision rule, log which agent handled each request and review overlaps in traces, merging or sharpening roles where two agents often produce the same output.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The workflow has distinct skills
- You need permissions per step
- Several people own different agents

❌ Avoid when:
- The "roles" differ only by wording
- A single function call can do the step

---

## 📊 Visual Diagram
```
 Role spec ──► System prompt ──► Agent ──► Typed output
    │                              │
    └── allowed tools ─────────────┘

 Router ─► Researcher ─► Classifier ─► Critic ─► Writer
```

---

## 💰 Cost Impact
Small, focused role prompts (150-300 tokens) are cheaper than one 3,000-token mega prompt that is paid on every call. Use gpt-4o-mini for router/critic style roles; reserve a bigger model for the classifier. Structured outputs reduce retries and parsing failures, saving tokens.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Role | Contract for an agent's job | agent के काम का contract |
| Router | Chooses next agent | अगला agent चुनने वाला |
| Researcher | Finds information | जानकारी खोजने वाला |
| Critic | Checks quality | quality जाँचने वाला |
| Tool permission | Which tools are allowed | कौन से tools allowed हैं |
| Output schema | Fixed result structure | तय result structure |

---

## ⚡ 3-Line Summary
English: Agent types are standard jobs, and roles are written contracts for them. Give each agent one goal, few tools and a typed output. This makes the system testable, safe and cheaper.
Hindi: Agent types standard jobs हैं और roles उनके लिखित contracts। हर agent को एक goal, कम tools और typed output दो। इससे system testable, safe और सस्ता बनता है।

---

## ➡️ Next Topic
**348. Agent Communication** — how agents exchange messages, shared state versus direct messages, and message formats.
