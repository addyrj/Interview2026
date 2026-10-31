---

# 254. StrOutputParser
# हिंदी में: StrOutputParser (Message से सीधा String)

---

## 🔵 Simple Definition (English)
`StrOutputParser` takes the model's `AIMessage` and returns just its text as a plain Python `str`. It is the simplest parser and the most used one: `prompt | llm | StrOutputParser()`. It also supports **streaming**: text pieces come out as the model generates them.

## 🔵 सरल परिभाषा (Hindi)
`StrOutputParser` model के `AIMessage` से सिर्फ़ text निकालकर plain Python `str` लौटाता है। यह सबसे simple और सबसे ज़्यादा इस्तेमाल होने वाला parser है: `prompt | llm | StrOutputParser()`। यह **streaming** भी support करता है: model जैसे-जैसे text बनाता है, टुकड़े बाहर आते हैं।

---

## 🔴 Problem it Solves
Chat models return an `AIMessage` object with `content`, `response_metadata`, `usage_metadata`... Most code only wants the text. Writing `.content` everywhere is easy to forget, and in a chain the next step (another prompt, a `RunnableLambda`, a template) expects a string, not a message. `.content` can also be a list of blocks (multimodal / Anthropic) — a parser handles that consistently.

## 🔴 यह क्यों बना? (Hindi)
Chat model `AIMessage` object लौटाता है जिसमें `content`, `response_metadata`, `usage_metadata` आदि होते हैं। ज़्यादातर code को सिर्फ़ text चाहिए। हर जगह `.content` लिखना भूलना आसान है, और chain में अगला step (दूसरा prompt, lambda) string चाहता है, message नहीं। `.content` कभी blocks की list भी हो सकता है — parser इसे एक जैसा संभालता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → llm returns AIMessage(content="Heading 8507", usage_metadata=...)
Step 2 → StrOutputParser.invoke(message) reads the text of the message
Step 3 → Returns plain str: "Heading 8507"
Step 4 → In streaming: llm yields AIMessageChunk pieces
Step 5 → Parser maps every chunk to its text piece -> chain.stream() yields strings
Step 6 → Next step in chain (or your API) works with str
Step 7 → NOTE: metadata (token usage) is dropped here -> read it BEFORE the parser if you need cost tracking
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → llm AIMessage(content="Heading 8507", usage_metadata=...) लौटाता है
Step 2 → StrOutputParser.invoke(message) message का text पढ़ता है
Step 3 → Plain str लौटता है: "Heading 8507"
Step 4 → Streaming में: llm AIMessageChunk टुकड़े देता है
Step 5 → Parser हर chunk को उसके text में बदलता है -> chain.stream() strings देती है
Step 6 → Chain का अगला step (या API) str के साथ काम करता है
Step 7 → ध्यान दो: metadata (token usage) यहाँ गिर जाता है -> cost चाहिए तो parser से पहले पढ़ो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A "explain this classification in plain language" endpoint returns a paragraph. The chain `prompt | llm | StrOutputParser()` gives a string that is streamed to the officer's browser. A second chain takes that string as input to a translation prompt (English → Hindi) — possible only because the first step output a `str`.

**Zomato AI**: Chatbot reply text streamed to the mobile app token by token.

## 🟡 Real Example Hindi mein
**Tariff System**: "इस classification को आसान भाषा में समझाओ" endpoint एक paragraph लौटाता है। `prompt | llm | StrOutputParser()` एक string देता है जो officer के browser में stream होती है। दूसरी chain उस string को translation prompt (English → Hindi) में लेती है — यह तभी संभव है क्योंकि पहला step `str` देता है।

**Zomato AI**: Chatbot का reply text app में token-by-token stream होता है।

---

## 💻 Code Example — Basic
```python
# Basic: StrOutputParser, streaming and chaining (offline, no API key)
import asyncio                                                         # to run the async example
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # scripted fake LLM
from langchain_core.output_parsers import StrOutputParser              # message -> str
from langchain_core.prompts import ChatPromptTemplate                  # prompt

prompt = ChatPromptTemplate.from_messages([("human", "Explain HS code for {product}")])  # simple prompt
parser = StrOutputParser()                                             # create parser

# 1) Without parser we get a message object
llm = FakeListChatModel(responses=["Power banks fall under heading 8507."])
msg = (prompt | llm).invoke({"product": "power bank"})                 # AIMessage
print(type(msg).__name__)                                              # AIMessage

# 2) With parser we get a str
llm = FakeListChatModel(responses=["Power banks fall under heading 8507."])
text = (prompt | llm | parser).invoke({"product": "power bank"})
print(isinstance(text, str), "|", text)                                # True | Power banks ... (a str subclass)

# 3) Streaming: chunks arrive as strings
llm = FakeListChatModel(responses=["Heading 8507"])
chunks = list((prompt | llm | parser).stream({"product": "x"}))        # list of small strings
print(len(chunks) > 1, "".join(chunks))                                # True Heading 8507

# 4) Async
async def main() -> None:
    llm2 = FakeListChatModel(responses=["async answer"])               # fresh fake
    print(await (prompt | llm2 | parser).ainvoke({"product": "x"}))    # await the chain

asyncio.run(main())                                                    # run the coroutine

# 5) Chaining two LLM calls: first output (str) becomes the second input
step1 = prompt | FakeListChatModel(responses=["English explanation"]) | parser
step2 = ChatPromptTemplate.from_template("Translate to Hindi: {text}") | FakeListChatModel(responses=["हिंदी अनुवाद"]) | parser
print((step1 | (lambda s: {"text": s}) | step2).invoke({"product": "x"}))  # lambda adapts str -> dict
```

## 💻 Code Example — Advanced
```python
# Production: keep token usage while returning a string, plus streaming + error handling
import logging                                                         # logging
from collections.abc import AsyncIterator                              # async generator type
from typing import Any                                                 # typing
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel

logger = logging.getLogger("tariff.str")                               # logger


def with_usage(llm: BaseChatModel, prompt: ChatPromptTemplate):
    """Return a chain that outputs {'text': str, 'usage': dict}. StrOutputParser would drop usage."""
    def split(msg: AIMessage) -> dict[str, Any]:                       # convert message to dict
        return {"text": StrOutputParser().invoke(msg), "usage": msg.usage_metadata or {}}
    return prompt | llm | RunnableLambda(split)                        # keep both pieces


async def stream_text(llm: BaseChatModel, question: str) -> AsyncIterator[str]:
    """Async generator of text pieces for streaming APIs."""
    chain = ChatPromptTemplate.from_messages([("human", "{q}")]) | llm | StrOutputParser()
    try:
        async for piece in chain.astream({"q": question}):             # each piece is a str
            yield piece                                                # forward to the client
    except Exception:                                                  # provider dropped the stream
        logger.exception("stream failed")                              # log it
        yield "\n[error: response interrupted]"                        # tell the client politely
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI                                   # FastAPI
from fastapi.responses import StreamingResponse                        # streaming response
from pydantic import BaseModel, Field                                  # schema

app = FastAPI()                                                        # app


class Q(BaseModel):                                                    # request model
    question: str = Field(min_length=3, max_length=1000)


def get_llm():
    raise NotImplementedError                                          # shared model


@app.post("/explain/stream")                                           # SSE-like text stream
async def explain_stream(q: Q, llm=Depends(get_llm)) -> StreamingResponse:
    # stream_text is the async generator from the advanced block
    return StreamingResponse(stream_text(llm, q.question), media_type="text/plain")
```

---

## 🔗 LangChain / LangGraph Connection
```python
# Every LCEL chain that ends in plain text ends with StrOutputParser:
chain = prompt | llm | StrOutputParser()

# RAG: the final answer string
rag = {"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()

# LangGraph: a node usually stores the string in state: return {"answer": chain.invoke(state)}
# For messages-based graphs you often keep the AIMessage instead (so tool calls survive) -- do NOT parse there.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Parsing away the message in an agent/tool-calling flow
```python
# Wrong — tool_calls live on the AIMessage; the parser throws them away:
chain = prompt | llm_with_tools | StrOutputParser()

# Correct — keep the AIMessage and inspect msg.tool_calls:
msg = (prompt | llm_with_tools).invoke(inputs)
```

❌ Mistake 2: Using `.content` and assuming it is a str
```python
# Wrong — may be a list of content blocks:
text = msg.content.upper()

# Correct:
text = StrOutputParser().invoke(msg)
```

❌ Mistake 3: Losing token usage for cost tracking
```python
# Wrong — usage_metadata is not on a str:
result = (prompt | llm | StrOutputParser()).invoke(x)
print(result.usage_metadata)     # AttributeError

# Correct — use a callback / with_usage() from the advanced block, or read the AIMessage first.
```

---

## 🧠 Tricky Interview Question

**Q**: "You added `StrOutputParser` and your streaming endpoint no longer shows token usage in logs. Why, and how do you get both?"

**Answer**: `StrOutputParser` converts each `AIMessageChunk` into text, so the chunk objects that carry `usage_metadata` (usually only in the final chunk) are discarded. Options: attach a callback handler (`on_llm_end` receives the full `LLMResult` including usage), use `astream_events` to observe the model events while the user sees parsed text, or stream the raw model output and accumulate chunks (`AIMessageChunk` supports `+`), parsing yourself. Callbacks are the cleanest for logging without changing the chain.

---

## ⚫ Interview Questions + Answers

Q1: What does StrOutputParser do? (Easy)
A1: Converts an `AIMessage` (or chunk) into a plain `str` containing its text.

Q2: Why not just use `.content`? (Easy)
A2: In a chain you cannot call `.content` between runnables; the parser does it as a Runnable step, and also handles content that is a list of blocks. It keeps chains declarative.

Q3: Does it support streaming? (Medium)
A3: Yes. `chain.stream()` / `astream()` yield string pieces as soon as the model produces them (transform support), so the first token reaches the user quickly.

Q4: When should you not use it? (Medium)
A4: When you need tool calls, usage metadata, response metadata or structured data from the message. Then keep the AIMessage, or use a structured parser.

Q5: How does a multi-step chain pass data between prompts? (Hard)
A5: Output of step 1 is a `str`; the next prompt needs a dict like `{"text": ...}`. Insert a `RunnableLambda(lambda s: {"text": s})` or a `RunnableParallel`/dict map such as `{"text": step1, "original": RunnablePassthrough()}`. LCEL coerces dicts into RunnableParallel automatically.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Final answer is free text
- Next step expects a string
- Streaming text to a UI

❌ Avoid when:
- You need tool calls (agents)
- You need token usage/metadata from the same chain output
- You need JSON or typed output (use JsonOutputParser / structured output)

---

## 📊 Visual Diagram
```
 prompt ──► ChatModel ──► AIMessage(content="Heading 8507",
                                    usage_metadata={...},
                                    tool_calls=[...])
                               │
                       StrOutputParser
                               ▼
                       "Heading 8507"        <- only text survives
                       (usage, tool_calls dropped)

 streaming:  chunk("Head") chunk("ing ") chunk("8507")  ──►  "Head" "ing " "8507"
```

---

## 💰 Cost Impact
The parser itself is free (no tokens). Its effect on cost is indirect: it hides `usage_metadata`, so teams that forget to log usage before the parser cannot see where tokens go. Example: 100K calls/day × 800 input + 200 output tokens on gpt-4o-mini = $12 + $12 = $24/day — invisible if not tracked.

Optimise: log usage via callbacks (topic 264), limit `max_tokens` so long answers do not surprise you, and prefer streaming for perceived speed (it does not change token cost).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| StrOutputParser | Message to string | Message से string |
| AIMessage | Model reply object | Model का जवाब object |
| Chunk | Piece of streamed reply | Stream का एक टुकड़ा |
| Content blocks | List form of message content | Content के blocks की list |
| `usage_metadata` | Token counts on message | Message पर token गिनती |
| Callback | Hook to observe runs | Run देखने का hook |

---

## ⚡ 3-Line Summary
English: StrOutputParser turns an AIMessage into a plain string and streams text pieces. Use it for free-text answers and to chain prompts. It discards tool calls and usage metadata, so track those separately.
Hindi: StrOutputParser AIMessage को plain string में बदलता है और text के टुकड़े stream करता है। Free-text जवाबों और prompts जोड़ने के लिए इस्तेमाल करो। यह tool calls और usage metadata हटा देता है, इन्हें अलग से track करो।

---

## ➡️ Next Topic
**255. PydanticOutputParser** — parse AND validate the reply into a typed pydantic model.
