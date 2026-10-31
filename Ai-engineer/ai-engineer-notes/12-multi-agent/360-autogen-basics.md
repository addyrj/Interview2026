---

# 360. AutoGen Basics
# हिंदी में: AutoGen की बुनियादी बातें

---

## 🔵 Simple Definition (English)
AutoGen is Microsoft's open-source framework for building multi-agent systems where agents **solve tasks by talking to each other** in a team. You create agents (`AssistantAgent`), put them in a team (for example `RoundRobinGroupChat`), set a termination condition, and call `team.run(task=...)`. This note uses the modern AutoGen 0.4+ API (`autogen_agentchat`).

## 🔵 सरल परिभाषा (Hindi)
AutoGen Microsoft का open-source framework है जिसमें agents एक team में **आपस में बात करके task हल करते हैं**। आप agents (`AssistantAgent`) बनाते हैं, उन्हें team (जैसे `RoundRobinGroupChat`) में रखते हैं, termination condition तय करते हैं और `team.run(task=...)` बुलाते हैं। यह note आधुनिक AutoGen 0.4+ API (`autogen_agentchat`) इस्तेमाल करता है।

---

## 🔴 Problem it Solves
Wiring multiple LLM agents by hand means writing turn-taking logic, message routing, stopping rules and tool calls yourself. AutoGen gives ready teams (round-robin, selector, swarm), async-first messaging, termination conditions, tool support and code-execution agents, so you focus on roles and prompts.

## 🔴 यह क्यों बना? (Hindi)
कई LLM agents को हाथ से जोड़ने का मतलब है turn-taking logic, message routing, रुकने के नियम और tool calls खुद लिखना। AutoGen तैयार teams (round-robin, selector, swarm), async-first messaging, termination conditions, tool support और code-execution agents देता है ताकि आप roles और prompts पर ध्यान दें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a model client (OpenAIChatCompletionClient)
Step 2 → Create agents with name, system_message, model_client (+ tools)
Step 3 → Choose a team type: RoundRobinGroupChat / SelectorGroupChat
Step 4 → Define termination: TextMentionTermination | MaxMessageTermination
Step 5 → await team.run(task="...") starts the conversation
Step 6 → Agents speak in turn; each message is broadcast to the team
Step 7 → Termination condition fires -> TaskResult returned
Step 8 → Read result.messages; inspect token usage and stop reason
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Model client बनाओ (OpenAIChatCompletionClient)
Step 2 → नाम, system_message, model_client (+ tools) के साथ agents बनाओ
Step 3 → Team का प्रकार चुनो: RoundRobinGroupChat / SelectorGroupChat
Step 4 → Termination तय करो: TextMentionTermination | MaxMessageTermination
Step 5 → await team.run(task="...") बातचीत शुरू करता है
Step 6 → Agents बारी-बारी बोलते हैं; हर message पूरी team को जाता है
Step 7 → Termination शर्त पूरी -> TaskResult लौटता है
Step 8 → result.messages पढ़ो; token usage और stop reason देखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Two agents in a round-robin team: `classifier` proposes an HS code with reasoning; `reviewer` checks it against rules and either replies `APPROVE` or lists problems. `TextMentionTermination("APPROVE")` stops the chat, and `MaxMessageTermination(8)` prevents endless loops. This is the Critic + Generator pattern with a few lines of AutoGen.

**Swiggy/Zomato-style**: A support team where a `triage` agent and a `refund` agent chat until the ticket is resolved.

## 🟡 Real Example Hindi mein
**Tariff System**: Round-robin team में दो agents: `classifier` तर्क के साथ HS code सुझाता है; `reviewer` उसे नियमों से जाँचता है और या तो `APPROVE` लिखता है या समस्याएँ बताता है। `TextMentionTermination("APPROVE")` बातचीत रोकती है और `MaxMessageTermination(8)` अनंत loop रोकती है। यह Critic + Generator pattern है जो AutoGen में कुछ lines में बन जाता है।

**Swiggy/Zomato-style**: Support team जिसमें `triage` और `refund` agents ticket हल होने तक बात करते हैं।

---

## 💻 Code Example — Basic
```python
# Real AutoGen 0.4+ code. Needs: pip install autogen-agentchat "autogen-ext[openai]" and OPENAI_API_KEY
import asyncio  # AutoGen is async-first
from autogen_agentchat.agents import AssistantAgent  # LLM-backed agent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination  # stop rules
from autogen_agentchat.teams import RoundRobinGroupChat  # agents speak in turn
from autogen_ext.models.openai import OpenAIChatCompletionClient  # model wrapper

async def main() -> None:
    model = OpenAIChatCompletionClient(model="gpt-4o-mini")  # reads OPENAI_API_KEY from env
    classifier = AssistantAgent(  # first agent
        name="classifier",  # unique name
        model_client=model,  # which LLM to use
        system_message="Propose an HS code for the product with a one line reason.",  # role
    )
    reviewer = AssistantAgent(  # second agent
        name="reviewer",
        model_client=model,
        system_message="Check the proposed HS code. If correct reply exactly APPROVE, else list the problem.",
    )
    stop = TextMentionTermination("APPROVE") | MaxMessageTermination(8)  # stop on APPROVE or 8 messages
    team = RoundRobinGroupChat([classifier, reviewer], termination_condition=stop)  # build the team
    result = await team.run(task="Wireless Bluetooth headphones")  # run the conversation
    for msg in result.messages:  # print the transcript
        print(f"{msg.source}: {getattr(msg, 'content', '')}")
    print("stop reason:", result.stop_reason)  # why it ended
    await model.close()  # release HTTP resources

if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 Code Example — Advanced
```python
# Production style: tools, error handling, streaming, token tracking. (Needs autogen + API key)
import asyncio  # async runtime
from autogen_agentchat.agents import AssistantAgent  # agent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination  # stop rules
from autogen_agentchat.teams import RoundRobinGroupChat  # team
from autogen_agentchat.ui import Console  # prints streamed messages
from autogen_ext.models.openai import OpenAIChatCompletionClient  # model client

VALID = {"8518.30": "Headphones", "8517.13": "Smartphones"}  # stub tariff table

async def lookup_hs(code: str) -> str:
    """Tool: check whether an HS code exists in the tariff table."""  # docstring becomes the tool description
    return VALID.get(code, "NOT_FOUND")  # plain async function = tool

async def classify(task: str, max_messages: int = 8) -> dict[str, object]:
    model = OpenAIChatCompletionClient(model="gpt-4o-mini")  # cheap model
    try:
        classifier = AssistantAgent("classifier", model_client=model, system_message="Propose an HS code.")
        reviewer = AssistantAgent(
            "reviewer",
            model_client=model,
            tools=[lookup_hs],  # reviewer can call the tool
            system_message="Verify the code with lookup_hs. Reply APPROVE only if found.",
        )
        team = RoundRobinGroupChat(
            [classifier, reviewer],
            termination_condition=TextMentionTermination("APPROVE") | MaxMessageTermination(max_messages),
        )
        result = await asyncio.wait_for(team.run(task=task), timeout=60)  # hard timeout
        usage = sum(  # sum token usage when present
            (m.models_usage.prompt_tokens + m.models_usage.completion_tokens)
            for m in result.messages
            if getattr(m, "models_usage", None)
        )
        return {"approved": "APPROVE" in str(result.stop_reason), "tokens": usage}
    except asyncio.TimeoutError:
        return {"approved": False, "error": "timeout"}  # fail safe
    except Exception as exc:  # network or API error
        return {"approved": False, "error": str(exc)}
    finally:
        await model.close()  # always clean up

if __name__ == "__main__":
    print(asyncio.run(classify("Bluetooth headphones")))
```

---

## 🟠 FastAPI Integration
Create a fresh team per request (teams hold state), run with a timeout, and return the transcript summary.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # models

app = FastAPI()

class ClassifyIn(BaseModel):
    product: str  # product description

@app.post("/autogen/classify")
async def classify_endpoint(body: ClassifyIn) -> dict:
    out = await classify(body.product)  # builds a new team inside; no shared state across requests
    if "error" in out:
        raise HTTPException(502, out["error"])  # map failures to HTTP errors
    return out
```

---

## 🔗 LangChain / LangGraph Connection
AutoGen and LangGraph solve similar problems differently. AutoGen is conversation-first (agents chat, the team decides who speaks). LangGraph is graph-first (you define nodes, edges and state explicitly). A team can be wrapped as one LangGraph node, or you can use LangChain tools inside AutoGen.

```python
# Wrap an AutoGen team as a single LangGraph node
from typing import TypedDict  # state
from langgraph.graph import StateGraph, START, END  # graph

class S(TypedDict):
    product: str
    result: dict

async def autogen_node(state: S) -> dict:
    return {"result": await classify(state["product"])}  # call the AutoGen team

g = StateGraph(S)
g.add_node("autogen_team", autogen_node)  # async node is supported
g.add_edge(START, "autogen_team")
g.add_edge("autogen_team", END)
graph = g.compile()
# use: await graph.ainvoke({"product": "headphones"})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No termination condition
✅ Correct: always combine a text trigger with a max-message cap.

```python
# Wrong: agents chat (and bill you) forever
team = RoundRobinGroupChat([a, b])
# Right
team = RoundRobinGroupChat([a, b], termination_condition=TextMentionTermination("APPROVE") | MaxMessageTermination(8))
```

❌ Mistake 2: Using old pyautogen (v0.2) examples with the new package
✅ Correct: check the version; v0.4+ uses `autogen_agentchat` and async `run`.

```python
# Wrong (old 0.2 style): user_proxy.initiate_chat(assistant, message="...")
# Right (0.4+): result = await team.run(task="...")
```

---

## 🧠 Tricky Interview Question
**Q**: "Your two-agent AutoGen team costs 10x a single call and sometimes loops. Why and how do you fix it?"

**Answer**: In group chats every agent sees the full growing transcript, so input tokens grow roughly quadratically with turns, and weak termination lets agents keep agreeing politely. Fixes: strict termination (`APPROVE` token + max messages), shorter system messages, cheaper models for reviewers, tools with deterministic checks, summarise long transcripts, and consider a graph (LangGraph) when the flow is fixed.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is AutoGen?
A1: Microsoft's framework for multi-agent LLM apps in which agents collaborate through conversation.

Q2: [Easy] What is a termination condition?
A2: A rule that ends the chat, such as a keyword like `APPROVE` or a maximum number of messages.

Q3: [Medium] RoundRobin vs Selector team?
A3: RoundRobin gives each agent a turn in fixed order. Selector uses an LLM to pick the next speaker based on the conversation.

Q4: [Medium] How do agents use tools in AutoGen 0.4+?
A4: Pass Python functions (sync or async, with type hints and docstrings) in `tools=[...]`; the agent calls them via function calling.

Q5: [Hard] AutoGen vs LangGraph for a regulated workflow?
A5: LangGraph gives explicit control, checkpoints, human interrupts and determinism, better for regulated flows. AutoGen suits exploratory, conversational collaboration and code-execution scenarios. Often use LangGraph as the outer workflow and AutoGen inside one node.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Open-ended collaboration (research, coding with execution)
- Quick prototypes of multi-agent chats
- You want built-in team types and code executors

❌ Avoid when:
- Flow is fixed and auditable (use a graph)
- Strict cost control, chatty teams are expensive

---

## 📊 Visual Diagram
```
  task --> +--------------------- RoundRobinGroupChat ---------------------+
           |   [classifier] --msg--> [reviewer] --msg--> [classifier] ...  |
           |        ^                    |  tool: lookup_hs                 |
           |        +---- shared transcript (everyone sees all) ----+      |
           +----------------------------------------------------------------+
                          stop on "APPROVE" or 8 messages
                                         |
                                    TaskResult
```

---

## 💰 Cost Impact
- Each turn re-sends the whole transcript. Turn n costs about n x average message size. 8 turns of 300 tokens each can total about 10,000 input tokens.
- Optimise: low max messages, concise system messages, cheap model for the reviewer, deterministic tools, summarising agents, run in LangGraph when order is fixed, log `models_usage` per message.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AssistantAgent | LLM-backed agent | LLM आधारित agent |
| Team | Group of agents that chat | बातचीत करने वाले agents का समूह |
| RoundRobinGroupChat | Fixed turn order | तय क्रम में बारी |
| Termination condition | When to stop | कब रुकना है |
| Model client | Wrapper for the LLM API | LLM API का wrapper |
| TaskResult | Output of team.run | team.run का नतीजा |

---

## ⚡ 3-Line Summary
English: AutoGen lets agents collaborate by chatting inside teams with termination rules. Use `AssistantAgent`, `RoundRobinGroupChat` and `team.run`. Watch cost: transcripts grow every turn.
Hindi: AutoGen में agents teams के अंदर बातचीत से सहयोग करते हैं और termination rules से रुकते हैं। `AssistantAgent`, `RoundRobinGroupChat` और `team.run` इस्तेमाल करो। Cost पर ध्यान रखो: हर turn पर transcript बढ़ता है।

---

## ➡️ Next Topic
**361. CrewAI Basics** — a role-based alternative where agents, tasks and a crew are defined declaratively.
