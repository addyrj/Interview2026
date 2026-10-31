---

# 361. CrewAI Basics
# हिंदी में: CrewAI की बुनियादी बातें

---

## 🔵 Simple Definition (English)
CrewAI is a Python framework for **role-based** multi-agent systems. You define `Agent`s (role, goal, backstory), `Task`s (description, expected output, which agent), and a `Crew` that runs the tasks in order (`Process.sequential`) or under a manager (`Process.hierarchical`). You start it with `crew.kickoff(inputs=...)`.

## 🔵 सरल परिभाषा (Hindi)
CrewAI **role-आधारित** multi-agent systems के लिए Python framework है। आप `Agent` (role, goal, backstory), `Task` (description, expected output, कौन सा agent) और एक `Crew` बनाते हैं जो tasks को क्रम से (`Process.sequential`) या manager के तहत (`Process.hierarchical`) चलाता है। शुरुआत `crew.kickoff(inputs=...)` से होती है।

---

## 🔴 Problem it Solves
Building a "team of specialists" from raw LLM calls needs prompt templates, task hand-offs and output passing. CrewAI makes this declarative: you describe who does what, and the output of one task automatically becomes context for the next. It is quick to read, quick to prototype, and understandable to non-experts.

## 🔴 यह क्यों बना? (Hindi)
Raw LLM calls से "विशेषज्ञों की team" बनाने में prompt templates, task hand-offs और output passing खुद लिखना पड़ता है। CrewAI इसे declarative बना देता है: आप बताते हैं कि कौन क्या करेगा, और एक task का output अपने आप अगले task का context बन जाता है। इसे पढ़ना, prototype करना और गैर-विशेषज्ञों को समझाना आसान है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define Agents: role, goal, backstory (+ llm, tools)
Step 2 → Define Tasks: description with {placeholders}, expected_output, agent
Step 3 → Build Crew(agents=[...], tasks=[...], process=Process.sequential)
Step 4 → crew.kickoff(inputs={"product": "..."}) fills placeholders
Step 5 → Task 1 runs; its output is passed as context to Task 2
Step 6 → Agents may call tools (search, custom @tool functions)
Step 7 → Final task output becomes the CrewOutput (result.raw)
Step 8 → Check token_usage and logs, then store the result
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Agents बनाओ: role, goal, backstory (+ llm, tools)
Step 2 → Tasks बनाओ: {placeholders} वाला description, expected_output, agent
Step 3 → Crew(agents=[...], tasks=[...], process=Process.sequential) बनाओ
Step 4 → crew.kickoff(inputs={"product": "..."}) placeholders भरता है
Step 5 → Task 1 चलता है; उसका output Task 2 को context के रूप में जाता है
Step 6 → Agents tools (search, custom @tool functions) बुला सकते हैं
Step 7 → आखिरी task का output CrewOutput (result.raw) बनता है
Step 8 → token_usage और logs देखो, फिर result सेव करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A crew of three: `Researcher` (finds relevant tariff headings), `Classifier` (picks the code), `Writer` (drafts the customs justification). Tasks run in sequence; the writer automatically receives the classifier's output. Inputs: `{product}`.

**Amazon-style**: A listing crew: researcher gathers specs, copywriter writes the description, reviewer checks policy compliance.

## 🟡 Real Example Hindi mein
**Tariff System**: तीन की crew: `Researcher` (प्रासंगिक tariff headings खोजता है), `Classifier` (code चुनता है), `Writer` (customs justification लिखता है)। Tasks क्रम से चलते हैं; writer को classifier का output अपने आप मिलता है। Input: `{product}`।

**Amazon-style**: Listing crew: researcher specs जुटाता है, copywriter description लिखता है, reviewer policy compliance जाँचता है।

---

## 💻 Code Example — Basic
```python
# Real CrewAI code. Needs: pip install crewai and OPENAI_API_KEY (default LLM is OpenAI)
from crewai import Agent, Crew, Process, Task  # core building blocks

researcher = Agent(  # first specialist
    role="Tariff Researcher",  # job title
    goal="Find the most relevant HS headings for {product}",  # {product} filled at kickoff
    backstory="You are a customs expert who knows the HS nomenclature well.",  # persona
    verbose=False,  # no step logs
)
classifier = Agent(  # second specialist
    role="HS Classifier",
    goal="Choose one 8 digit HS code for {product} with a short reason",
    backstory="You classify goods strictly according to chapter notes.",
)

research_task = Task(  # task 1
    description="List up to 3 candidate HS headings for {product}.",  # what to do
    expected_output="A bullet list of heading numbers with a one line reason each.",  # output contract
    agent=researcher,  # who does it
)
classify_task = Task(  # task 2
    description="From the candidates, choose the final HS code for {product}.",
    expected_output="One HS code and a two sentence justification.",
    agent=classifier,
)

crew = Crew(  # assemble
    agents=[researcher, classifier],
    tasks=[research_task, classify_task],  # order matters in sequential mode
    process=Process.sequential,  # task 2 receives task 1 output as context
)

result = crew.kickoff(inputs={"product": "Bluetooth headphones"})  # run synchronously
print(result.raw)  # final text output
```

## 💻 Code Example — Advanced
```python
# Custom tool, async kickoff, error handling and token usage. (Needs crewai + API key)
import asyncio  # async runtime
from crewai import Agent, Crew, Process, Task  # core classes
from crewai.tools import tool  # decorator for custom tools

VALID = {"8518.30": "Headphones", "8517.13": "Smartphones"}  # stub tariff table

@tool("HS code validator")  # tool name shown to the LLM
def validate_hs(code: str) -> str:
    """Check whether an HS code exists in the tariff table. Returns the description or NOT_FOUND."""
    return VALID.get(code, "NOT_FOUND")  # deterministic check, no LLM cost

def build_crew() -> Crew:
    classifier = Agent(
        role="HS Classifier",
        goal="Classify {product} and verify the code with the validator tool",
        backstory="Careful customs classifier who never skips validation.",
        tools=[validate_hs],  # agent may call this tool
        llm="gpt-4o-mini",  # cheap model by name
        max_iter=4,  # limit reasoning loops
        allow_delegation=False,  # no hidden extra calls
    )
    task = Task(
        description="Classify {product}. Validate the code with the tool before answering.",
        expected_output="JSON with keys hs_code and reason.",
        agent=classifier,
    )
    return Crew(agents=[classifier], tasks=[task], process=Process.sequential)

async def classify(product: str) -> dict[str, object]:
    try:
        result = await asyncio.wait_for(build_crew().kickoff_async(inputs={"product": product}), timeout=90)
        usage = getattr(result, "token_usage", None)  # total tokens if available
        return {"output": result.raw, "tokens": getattr(usage, "total_tokens", None)}
    except asyncio.TimeoutError:
        return {"error": "timeout"}  # safe failure
    except Exception as exc:
        return {"error": str(exc)}

if __name__ == "__main__":
    print(asyncio.run(classify("Bluetooth headphones")))
```

---

## 🟠 FastAPI Integration
Build a new crew per request. `kickoff_async` keeps the event loop free.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # models

app = FastAPI()

class In(BaseModel):
    product: str  # input to the crew

@app.post("/crew/classify")
async def run_crew(body: In) -> dict:
    out = await classify(body.product)  # builds a fresh crew
    if "error" in out:
        raise HTTPException(502, out["error"])  # report failure clearly
    return out
```

---

## 🔗 LangChain / LangGraph Connection
CrewAI builds on LangChain-compatible tooling (it can use LangChain tools through its tool adapters), and uses LiteLLM-style model strings. In larger systems, wrap a crew as one LangGraph node so LangGraph handles checkpoints and approvals while CrewAI handles the creative sub-team.

```python
from typing import TypedDict  # state
from langgraph.graph import StateGraph, START, END  # graph

class S(TypedDict):
    product: str
    crew_output: dict

async def crew_node(s: S) -> dict:
    return {"crew_output": await classify(s["product"])}  # reuse the function above

g = StateGraph(S)
g.add_node("crew", crew_node)
g.add_edge(START, "crew")
g.add_edge("crew", END)
graph = g.compile()
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Vague roles and expected outputs
✅ Correct: specific goal and a clear output contract.

```python
# Wrong
Task(description="Do the classification", expected_output="Result", agent=a)
# Right
Task(description="Classify {product}", expected_output="JSON: hs_code, reason (max 2 sentences)", agent=a)
```

❌ Mistake 2: Reusing one Crew object across concurrent requests, or leaving delegation and iterations unlimited
✅ Correct: new crew per request, `max_iter` and `allow_delegation=False` unless needed.

```python
# Wrong
GLOBAL_CREW.kickoff(inputs=...)   # shared mutable state
# Right
build_crew().kickoff(inputs=...)
```

---

## 🧠 Tricky Interview Question
**Q**: "A 3-agent CrewAI pipeline gives different results on the same input each run, and the output format breaks downstream code. How do you stabilise it?"

**Answer**: Set low temperature on the LLM, define `expected_output` precisely, enforce a schema using `output_pydantic` (or `output_json`) on the Task, validate the result in code and retry on failure, use deterministic tools for facts, and cap `max_iter`. Add evaluation tests with fixed examples. Never parse free text with regex when a schema is available.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What are the three core CrewAI objects?
A1: Agent (who), Task (what), Crew (the team and process that runs the tasks).

Q2: [Easy] What does `kickoff` do?
A2: Starts the crew run, fills `{placeholders}` from `inputs`, and returns a CrewOutput.

Q3: [Medium] Sequential vs hierarchical process?
A3: Sequential runs tasks in listed order passing outputs forward. Hierarchical adds a manager LLM that delegates and validates, costing more calls.

Q4: [Medium] How do you get structured output?
A4: Use `output_pydantic=MyModel` on the Task so the output is validated against a pydantic model.

Q5: [Hard] CrewAI vs LangGraph: how do you choose?
A5: CrewAI is faster to prototype and reads like a team org chart; LangGraph gives explicit state, branching, checkpoints and human-in-the-loop. For production workflows with audit needs choose LangGraph; use CrewAI for contained role-based sub-tasks.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Content or research pipelines with clear roles
- Fast prototypes and demos
- Linear task hand-offs

❌ Avoid when:
- Complex branching, loops or approvals (use LangGraph)
- Tight latency and cost budgets

---

## 📊 Visual Diagram
```
 inputs {product}
      |
      v
 +---------+  output   +------------+  output   +--------+
 |Researcher|--------->| Classifier |---------->| Writer |--> CrewOutput.raw
 | Task 1  |  context  |   Task 2   |  context  | Task 3 |
 +---------+           +------------+           +--------+
      \_______ Process.sequential (one crew) _______/
          tools: search / validate_hs   limits: max_iter
```

---

## 💰 Cost Impact
- Each task is at least one LLM call, plus reasoning loops and tool calls. Previous outputs are added as context, so later tasks cost more.
- Typical 3-task crew: about 3,000-8,000 tokens per run.
- Optimise: `llm="gpt-4o-mini"` for most agents, `max_iter` low, `allow_delegation=False`, short backstories, concise expected outputs, deterministic tools, cache repeated inputs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Agent | Role with goal and backstory | Role, goal और backstory वाला agent |
| Task | Unit of work with expected output | अपेक्षित output वाला काम |
| Crew | Team that runs tasks | Tasks चलाने वाली team |
| Process | Sequential or hierarchical flow | काम चलाने का क्रम |
| kickoff | Start the crew | Crew शुरू करना |
| output_pydantic | Structured task output | Pydantic में structured output |

---

## ⚡ 3-Line Summary
English: CrewAI defines agents by role, tasks by expected output, and a crew that runs them in order. Great for fast role-based pipelines. Use schemas, iteration limits and cheap models to stay stable and affordable.
Hindi: CrewAI agents को role से, tasks को expected output से और crew को उन्हें चलाने के लिए परिभाषित करता है। तेज़ role-आधारित pipelines के लिए अच्छा है। स्थिरता और कम cost के लिए schemas, iteration limits और सस्ते models इस्तेमाल करो।

---

## ➡️ Next Topic
**362. Multi-Agent Memory** — how agents remember across steps and sessions.
