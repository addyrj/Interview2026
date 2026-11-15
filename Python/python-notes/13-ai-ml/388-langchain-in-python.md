---

# 388. LangChain in Python
# हिंदी में: Python में LangChain (LLM apps जोड़ने का framework)

---

## 🔵 Simple Definition (English)
LangChain is a framework that connects LLMs to prompts, output parsers, tools, and data. Its core idea is LCEL (LangChain Expression Language): small pieces called Runnables are joined with the `|` pipe, for example `prompt | llm | parser`, and every piece shares `invoke`, `batch`, and `stream`.

## 🔵 सरल परिभाषा (Hindi)
LangChain एक framework है जो LLMs को prompts, output parsers, tools और data से जोड़ता है। इसका मुख्य विचार LCEL (LangChain Expression Language) है: Runnables नाम के छोटे हिस्से `|` pipe से जुड़ते हैं, जैसे `prompt | llm | parser`, और हर हिस्से में `invoke`, `batch` और `stream` एक जैसे होते हैं।

---

## 🔴 Problem it Solves
Every LLM app repeats the same steps: fill a prompt template, call a model, parse the text into structured data, retry on failure, call tools, and swap providers. Writing this by hand for each provider creates glue code that is hard to change. LangChain gives standard interfaces (chat models, prompts, parsers, tools), so you can replace Claude with another model by changing one line.

## 🔴 यह क्यों बना? (Hindi)
हर LLM app वही steps दोहराता है: prompt template भरना, model call करना, text को structured data में parse करना, fail होने पर retry, tools call करना, और provider बदलना। हर provider के लिए यह हाथ से लिखने पर glue code बन जाता है जिसे बदलना मुश्किल है। LangChain standard interfaces (chat models, prompts, parsers, tools) देता है, इसलिए Claude की जगह दूसरा model एक line बदलकर लगाया जा सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Prompt template: ChatPromptTemplate.from_messages([("system", ...), ("human", "{question}")])
Step 2 → Chat model: a provider class (e.g. ChatAnthropic from langchain-anthropic)
Step 3 → Output parser: StrOutputParser (text) or PydanticOutputParser (typed object)
Step 4 → Compose with the pipe:  chain = prompt | llm | parser   (a RunnableSequence)
Step 5 → Run: chain.invoke({...}) | chain.batch([...]) | chain.stream({...}) | await chain.ainvoke({...})
Step 6 → Add reliability: chain.with_fallbacks([...]), .with_retry()
Step 7 → Tools: @tool turns a Python function into a tool with a JSON schema the model can call

dict --> prompt --> messages --> llm --> AIMessage --> parser --> str / Pydantic object
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Prompt template: ChatPromptTemplate.from_messages([("system", ...), ("human", "{question}")])
Step 2 → Chat model: provider की class (जैसे langchain-anthropic का ChatAnthropic)
Step 3 → Output parser: StrOutputParser (text) या PydanticOutputParser (typed object)
Step 4 → Pipe से जोड़ें:  chain = prompt | llm | parser   (एक RunnableSequence)
Step 5 → चलाएं: chain.invoke({...}) | chain.batch([...]) | chain.stream({...}) | await chain.ainvoke({...})
Step 6 → Reliability जोड़ें: chain.with_fallbacks([...]), .with_retry()
Step 7 → Tools: @tool एक Python function को JSON schema वाले tool में बदलता है जिसे model call कर सकता है
```

---

## 🟡 Real World Example
A support platform classifies incoming tickets: the chain takes the ticket text, asks the model for JSON `{category, priority}`, and parses it into a Pydantic object that routes the ticket. If the primary model returns bad JSON, a fallback chain runs. A RAG chatbot adds a retriever step before the prompt. A FastAPI endpoint runs the chain asynchronously.

## 🟡 Real Example Hindi mein
Support platform आने वाले tickets classify करता है: chain ticket का text लेती है, model से JSON `{category, priority}` मांगती है, और उसे Pydantic object में parse करती है जो ticket को route करता है। अगर primary model गलत JSON दे, तो fallback chain चलती है। RAG chatbot prompt से पहले retriever step जोड़ता है। FastAPI endpoint chain को async चलाता है।

---

## 💻 Code Example — Basic
```python
# Basic LCEL with a fake chat model so it runs offline (langchain-core 1.x)
# In production replace FakeListChatModel with e.g. ChatAnthropic(model="claude-opus-5-5")
from langchain_core.prompts import ChatPromptTemplate                  # prompt templates
from langchain_core.output_parsers import StrOutputParser              # model output -> str
from langchain_core.language_models.fake_chat_models import FakeListChatModel   # test double
from langchain_core.runnables import RunnableLambda                    # wrap a plain function

prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(        # build the prompt
    [("system", "You are a {role}."), ("human", "{question}")]         # {role}, {question} are variables
)
llm = FakeListChatModel(responses=["Use an index.", "Second answer"]) # returns these replies in a cycle
chain = prompt | llm | StrOutputParser()                               # pipe = LCEL composition
print(type(chain).__name__)                                            # it is a RunnableSequence
print(chain.invoke({"role": "DBA", "question": "Why is my query slow?"}))   # run once
print(prompt.invoke({"role": "DBA", "question": "q"}).to_messages()[0].content)   # see the filled prompt
print(chain.batch([{"role": "a", "question": "1"}]))                   # run a list of inputs
print([c for c in chain.stream({"role": "a", "question": "x"})][:3])   # stream pieces (the fake streams per character)
upper = RunnableLambda(lambda s: s.upper())                            # any function can join the chain
print((chain | upper).invoke({"role": "a", "question": "x"}))          # chain + post-processing

# Output:
# RunnableSequence
# Use an index.
# You are a DBA.
# ['Second answer']
# ['U', 's', 'e']
# SECOND ANSWER
# (the fake model cycles through its responses, so batch/stream/upper get different replies)
```

## 💻 Code Example — Advanced
```python
# Production style: typed output, fallback chain, and a tool (runs offline with fake models)
from __future__ import annotations                                     # modern hints
from pydantic import BaseModel, Field                                  # output schema
from langchain_core.exceptions import OutputParserException            # parse failure type
from langchain_core.language_models.fake_chat_models import FakeListChatModel   # fake model
from langchain_core.output_parsers import PydanticOutputParser         # JSON -> Pydantic
from langchain_core.prompts import ChatPromptTemplate                  # prompts
from langchain_core.runnables import Runnable                          # base type for chains
from langchain_core.tools import tool                                  # tool decorator


class Ticket(BaseModel):                                               # the typed result we want
    category: str = Field(description="billing, tech or other")       # description goes into the prompt
    priority: int = Field(ge=1, le=5)                                  # validated 1..5


parser: PydanticOutputParser = PydanticOutputParser(pydantic_object=Ticket)   # parser from schema
prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages([        # prompt with format rules
    ("system", "Classify the ticket. {format_instructions}"),
    ("human", "{text}"),
]).partial(format_instructions=parser.get_format_instructions())      # pre-fill one variable


def build_chain(llm: Runnable) -> Runnable:                            # factory: easy to swap models
    return prompt | llm | parser                                       # prompt -> model -> typed object


good = FakeListChatModel(responses=['{"category": "billing", "priority": 2}'])   # valid JSON reply
bad = FakeListChatModel(responses=["not json at all"])                 # broken reply
t: Ticket = build_chain(good).invoke({"text": "I was charged twice"})  # typed result
print(t, type(t).__name__)                                             # Ticket object, not a string
safe = build_chain(bad).with_fallbacks([build_chain(good)])            # if the first chain raises, try the next
print(safe.invoke({"text": "x"}))                                      # fallback rescued it
try:                                                                   # without fallback
    build_chain(bad).invoke({"text": "x"})                             # parser cannot read the reply
except OutputParserException as e:                                     # catch parse errors
    print("parse error:", type(e).__name__)                            # error name


@tool                                                                  # function -> tool with schema
def order_status(order_id: int) -> str:
    """Return the status of an order."""                               # docstring = tool description for the model
    return f"order {order_id}: shipped"                                # pretend DB lookup


print(order_status.name, order_status.args)                            # name + JSON schema of args
print(order_status.invoke({"order_id": 42}))                           # call the tool directly
print(prompt.input_variables)                                          # only 'text' is left to supply

# Output:
# category='billing' priority=2 Ticket
# category='billing' priority=2
# parse error: OutputParserException
# order_status {'order_id': {'title': 'Order Id', 'type': 'integer'}}
# order 42: shipped
# ['text']
```
Version note: verified with `langchain-core` 1.7.7 on Python 3.13. Provider packages (`langchain-anthropic`, `langchain-openai`) and real model calls were NOT run here (need API keys). LangChain changes quickly: older tutorials using `LLMChain`, `ConversationChain` or `from langchain.chat_models import ...` are legacy; use LCEL and the `langchain-<provider>` packages.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Package | `langchain`, `langchain-core` | `langchain`, `@langchain/core` |
| Compose | `prompt \| llm \| parser` | `prompt.pipe(llm).pipe(parser)` |
| Run | `chain.invoke(...)` | `await chain.invoke(...)` |
| Tools | `@tool` decorator | `tool(fn, {schema})` with Zod |
| Typed output | Pydantic | Zod |

```python
# Python way
chain = prompt | llm | StrOutputParser()                   # pipe operator
print(chain.invoke({"question": "hi"}))                    # sync call
```
```javascript
// JavaScript way
const chain = prompt.pipe(llm).pipe(new StringOutputParser());   // .pipe() chaining
console.log(await chain.invoke({ question: "hi" }));             // always async
```

Key difference: Python overloads the `|` operator (the `__or__` magic method) for a compact syntax; JavaScript has no operator overloading, so it uses `.pipe()`. Concepts and class names are almost identical.

---

## 🟠 FastAPI Connection
Build the chain once at startup and call `await chain.ainvoke(...)` inside `async def` endpoints so the event loop is not blocked. Use the Pydantic output model as `response_model`. Use `chain.astream(...)` with `StreamingResponse` for token streaming. Verified below with the fake model and TestClient.

```python
# FastAPI example — POST /classify (verified: {'category': 'billing', 'priority': 2})
from fastapi import FastAPI                                        # FastAPI
from pydantic import BaseModel                                     # request model

app: FastAPI = FastAPI()                                           # create app
CHAIN = build_chain(good)                                          # build ONCE; use ChatAnthropic in production


class In(BaseModel):                                               # request body
    text: str                                                      # ticket text


@app.post("/classify", response_model=Ticket)                      # response validated as Ticket
async def classify(i: In) -> Ticket:                               # async endpoint
    return await CHAIN.ainvoke({"text": i.text})                   # non-blocking chain call
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using legacy APIs (`LLMChain`, `initialize_agent`) from old tutorials
✅ Correct: use LCEL (`prompt | llm | parser`) and current `langchain-<provider>` packages

```python
# Wrong (legacy): chain = LLMChain(llm=llm, prompt=prompt)
# Right
# chain = prompt | llm | StrOutputParser()
```

❌ Mistake 2: Passing a missing variable to the chain
✅ Correct: provide exactly the template variables (check `prompt.input_variables`)

```python
# prompt.input_variables -> ['question', 'role']
# Wrong: chain.invoke({"question": "hi"})            # missing 'role' -> error
# Right: chain.invoke({"role": "DBA", "question": "hi"})
```

❌ Mistake 3: Trusting that the model always returns valid JSON
✅ Correct: parse with a Pydantic parser (or `with_structured_output`) and add `with_fallbacks` / `with_retry`

```python
# Wrong: json.loads(chain.invoke(...))    # crashes on "Sure! Here is the JSON: ..."
# Right: chain = prompt | llm | parser ; safe = chain.with_fallbacks([backup_chain])
```

❌ Mistake 4: Building the model/chain inside every request
✅ Correct: build it once at startup, reuse it

```python
# Wrong: @app.post("/x") def x(): chain = build_chain(ChatAnthropic(...)); ...   # new client each call
# Right: CHAIN = build_chain(ChatAnthropic(model="claude-opus-5-5")) at module level
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from langchain_core.prompts import ChatPromptTemplate
p = ChatPromptTemplate.from_messages([("system", "Rules: {rules}"), ("human", "{text}")])
print(sorted(p.input_variables))
p2 = p.partial(rules="be brief")
print(p2.input_variables)
print(p2.invoke({"text": "hello"}).to_messages()[0].content)
```
Answer: `['rules', 'text']`, then `['text']`, then `Rules: be brief`. `partial()` returns a NEW prompt with one variable pre-filled, so only `text` is still required. The original `p` is not changed (templates are immutable-style). This is how `format_instructions` is attached in the advanced example.

---

## ⚫ Interview Questions + Answers

Q1: What is a Runnable and what is LCEL?
A1: A Runnable is any component with `invoke`, `batch`, `stream` (and async versions). LCEL composes Runnables with `|` into a `RunnableSequence` (or `RunnableParallel` with a dict), so streaming, batching and async work for the whole chain automatically.

Q2: How do you get structured output?
A2: Two ways: a `PydanticOutputParser` that adds format instructions to the prompt and parses the text, or the chat model's `with_structured_output(Schema)`, which uses the provider's native tool/JSON features and is usually more reliable.

Q3: How does LangChain call tools?
A3: Define tools with `@tool` (name, docstring and type hints become the schema). Bind them with `llm.bind_tools([...])`. The model returns `tool_calls` in the AIMessage; you execute them and send `ToolMessage` results back, or let an agent framework (LangGraph / `create_agent`) run the loop.

Q4: LangChain vs calling the provider SDK directly?
A4: SDK direct is simpler, fewer dependencies, and exposes new features first. LangChain helps when you need provider swapping, shared abstractions (retrievers, parsers, tracing with LangSmith), or complex chains. For a single prompt and model, the plain SDK is often enough.

Q5: How do you make a chain production-ready?
A5: Build once, use async (`ainvoke`/`astream`), add timeouts and `with_retry` / `with_fallbacks`, validate outputs with Pydantic, log with tracing, and keep API keys in environment variables.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need RAG, multi-step chains, or tool-using agents with reusable parts
- You want to swap model providers easily
- You want built-in tracing/evals integrations

❌ Avoid when:
- One simple prompt-in, text-out call: use the provider SDK
- You need the newest provider-specific features immediately
- You want minimal dependencies and a small attack surface

---

## 📊 Visual Diagram
```
 {"role":"DBA","question":"..."}
          │
          ▼
 ┌──────────────┐   ┌──────────┐   ┌───────────────┐
 │ ChatPrompt   │──>│ ChatModel│──>│ OutputParser  │──> Ticket(category, priority)
 │ Template     │   │ (Claude) │   │ (Pydantic)    │
 └──────────────┘   └──────────┘   └───────────────┘
        prompt     |     llm      |     parser        = RunnableSequence
        .invoke  .batch  .stream  .ainvoke  .astream  (all come for free)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Runnable | Component with invoke/batch/stream | invoke/batch/stream वाला component |
| LCEL | Pipe syntax to compose Runnables | Runnables जोड़ने की pipe syntax |
| Prompt template | Text with `{variables}` | `{variables}` वाला text |
| Output parser | Turns model text into data | Model text को data में बदलना |
| Tool | Function the model can call | Model जो function call कर सके |
| Fallback | Backup chain if first fails | पहली fail हो तो बैकअप chain |

---

## ⚡ 3-Line Summary
English: LangChain composes prompts, chat models, parsers and tools into chains with the `|` operator (LCEL), and every chain supports invoke, batch, stream and async. Use Pydantic parsers and fallbacks for reliable output. Prefer the plain provider SDK when your app is just one simple call.
Hindi: LangChain prompts, chat models, parsers और tools को `|` operator (LCEL) से chains में जोड़ता है, और हर chain में invoke, batch, stream और async मिलता है। भरोसेमंद output के लिए Pydantic parsers और fallbacks इस्तेमाल करें। अगर app सिर्फ एक सरल call है तो सीधे provider SDK बेहतर है।

---

## ➡️ Next Topic
**389. LlamaIndex Basics** — load documents, build a vector index and query your own data (RAG) with LlamaIndex.
