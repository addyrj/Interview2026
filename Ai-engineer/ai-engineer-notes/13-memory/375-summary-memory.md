---

# 375. Summary Memory
# हिंदी में: Summary Memory

---

## 🔵 Simple Definition (English)
Summary memory compresses older conversation into a **short running summary** using an LLM, and keeps only recent messages in full. The prompt becomes: system prompt + summary of the past + last few messages. It remembers the gist without paying for every old token.

## 🔵 सरल परिभाषा (Hindi)
Summary memory पुरानी बातचीत को LLM की मदद से एक **छोटे चलते सारांश** में बदल देती है और सिर्फ हाल के messages पूरे रखती है। Prompt बनता है: system prompt + अतीत का सारांश + आखिरी कुछ messages। यह हर पुराने token का खर्च किए बिना मुख्य बात याद रखती है।

---

## 🔴 Problem it Solves
Sliding windows forget old facts completely; full history is too expensive and may exceed the context. Users expect the assistant to remember decisions made earlier ("we agreed to ship via sea"). Summary memory keeps the important points in a compact form.

## 🔴 यह क्यों बना? (Hindi)
Sliding window पुरानी बातें पूरी तरह भूल जाती है; पूरी history महँगी है और context से बाहर जा सकती है। Users चाहते हैं कि assistant पहले लिए फैसले याद रखे ("हमने sea से भेजना तय किया था")। Summary memory ज़रूरी बिंदुओं को संक्षिप्त रूप में सहेजती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Keep a buffer of recent messages (raw) and a string "summary"
Step 2 → After each turn, check buffer size (tokens or message count)
Step 3 → If over the limit, take the oldest messages out of the buffer
Step 4 → Ask an LLM: "Update the summary with these messages" (summary + old msgs)
Step 5 → Replace the summary with the new, short version
Step 6 → Next prompt = system + summary + recent raw messages
Step 7 → Keep the summary under a size cap (re-compress if it grows)
Step 8 → Store summary per session in a database
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हाल के raw messages का buffer और एक "summary" string रखो
Step 2 → हर turn के बाद buffer का आकार जाँचो (tokens या messages)
Step 3 → सीमा पार हो तो सबसे पुराने messages buffer से निकालो
Step 4 → LLM से कहो: "इन messages के साथ summary अपडेट करो" (summary + पुराने msgs)
Step 5 → Summary को नए, छोटे version से बदल दो
Step 6 → अगला prompt = system + summary + हाल के raw messages
Step 7 → Summary पर आकार सीमा रखो (बढ़े तो दोबारा compress करो)
Step 8 → Summary को हर session के लिए database में रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A 60-message conversation with an importer: product is a LED driver, origin Vietnam, shipping by sea, the user rejected HS 8504 and wants a drawback report. The summary stores: "Product: LED driver (VN origin, sea). Rejected: HS 8504. Wants: drawback report. Open: confirm voltage." The next question "what did we decide about shipping?" is answered from the summary at a fraction of the cost.

**Amazon-style**: A support bot summarises a long troubleshooting chat so a human agent can take over instantly.

## 🟡 Real Example Hindi mein
**Tariff System**: Importer के साथ 60 messages की बातचीत: product LED driver, origin Vietnam, sea से shipping, user ने HS 8504 अस्वीकार किया और drawback report चाहता है। Summary में रहता है: "Product: LED driver (VN origin, sea). Rejected: HS 8504. Wants: drawback report. Open: voltage confirm करना।" अगला सवाल "shipping के बारे में हमने क्या तय किया?" summary से बहुत कम cost में जवाब पाता है।

**Amazon-style**: Support bot लंबी troubleshooting chat का सारांश बनाता है ताकि human agent तुरंत कमान सँभाल सके।

---

## 💻 Code Example — Basic
```python
# Summary memory with a mock summariser (runs offline)
Message = dict[str, str]  # {"role": ..., "content": ...}

def mock_summarise(summary: str, old: list[Message]) -> str:
    # A real version calls an LLM: "Update this summary with the new messages"
    facts = "; ".join(m["content"][:25] for m in old)  # crude compression for the demo
    return (summary + " | " + facts).strip(" |")

class SummaryMemory:
    def __init__(self, keep_last: int = 4) -> None:
        self.keep_last = keep_last        # how many raw messages stay
        self.summary = ""                 # compressed past
        self.buffer: list[Message] = []   # recent raw messages

    def add(self, role: str, content: str) -> None:
        self.buffer.append({"role": role, "content": content})
        if len(self.buffer) > self.keep_last:                  # buffer too large?
            old = self.buffer[: -self.keep_last]               # oldest part
            self.buffer = self.buffer[-self.keep_last:]        # keep newest
            self.summary = mock_summarise(self.summary, old)   # fold old into summary

    def prompt(self, system: str) -> list[Message]:
        msgs: list[Message] = [{"role": "system", "content": system}]
        if self.summary:
            msgs.append({"role": "system", "content": f"Conversation summary: {self.summary}"})
        return msgs + self.buffer

if __name__ == "__main__":
    mem = SummaryMemory(keep_last=2)
    for i in range(1, 6):
        mem.add("user" if i % 2 else "assistant", f"message number {i}")
    for m in mem.prompt("You are a tariff bot."):
        print(m)
```

## 💻 Code Example — Advanced
```python
# Async summary memory: token threshold, summary size cap, error handling, usage tracking
import asyncio  # async runtime

Message = dict[str, str]

def tokens(text: str) -> int:
    return max(1, len(text) // 4)  # approximation; use tiktoken in production

async def llm_summarise(summary: str, old: list[Message]) -> tuple[str, int]:
    """Stand-in for a cheap LLM call. Returns (new_summary, tokens_used)."""
    await asyncio.sleep(0)
    text = summary + " " + " ".join(m["content"][:30] for m in old)
    return text[:400], tokens(text) + 120  # summary capped at 400 characters

class AsyncSummaryMemory:
    def __init__(self, max_buffer_tokens: int = 300, keep_last: int = 4) -> None:
        self.max_buffer_tokens, self.keep_last = max_buffer_tokens, keep_last
        self.summary, self.buffer = "", []            # type: str, list[Message]
        self.summary_tokens_spent = 0                 # cost tracking
        self._lock = asyncio.Lock()                   # one summarisation at a time

    async def add(self, role: str, content: str) -> None:
        async with self._lock:
            self.buffer.append({"role": role, "content": content})
            total = sum(tokens(m["content"]) for m in self.buffer)
            if total <= self.max_buffer_tokens or len(self.buffer) <= self.keep_last:
                return                                # nothing to compress yet
            old, self.buffer = self.buffer[: -self.keep_last], self.buffer[-self.keep_last:]
            try:
                self.summary, used = await llm_summarise(self.summary, old)
                self.summary_tokens_spent += used
            except Exception:
                self.buffer = old + self.buffer       # keep messages if summarising fails (retry later)

    def prompt(self, system: str) -> list[Message]:
        head: list[Message] = [{"role": "system", "content": system}]
        if self.summary:
            head.append({"role": "system", "content": f"Summary so far: {self.summary}"})
        return head + self.buffer

async def main() -> None:
    mem = AsyncSummaryMemory(max_buffer_tokens=60, keep_last=2)
    for i in range(8):
        await mem.add("user" if i % 2 == 0 else "assistant", f"turn {i} " + "detail " * 10)
    print("summary chars:", len(mem.summary), "| buffer:", len(mem.buffer), "| summariser tokens:", mem.summary_tokens_spent)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Update the summary in a background task so the user does not wait for summarisation.

```python
from fastapi import BackgroundTasks, FastAPI, HTTPException  # framework
from pydantic import BaseModel  # models
from openai import AsyncOpenAI  # async client

app = FastAPI()
client = AsyncOpenAI()
SESSIONS: dict[str, AsyncSummaryMemory] = {}  # Redis/Postgres in production

class ChatIn(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
async def chat(body: ChatIn, bg: BackgroundTasks) -> dict:
    mem = SESSIONS.setdefault(body.session_id, AsyncSummaryMemory())
    msgs = mem.prompt("You are a tariff assistant.") + [{"role": "user", "content": body.message}]
    try:
        resp = await client.chat.completions.create(model="gpt-4o-mini", messages=msgs, max_tokens=300)
    except Exception as exc:
        raise HTTPException(502, str(exc))
    answer = resp.choices[0].message.content or ""
    bg.add_task(mem.add, "user", body.message)      # summarise after the response is sent
    bg.add_task(mem.add, "assistant", answer)
    return {"answer": answer, "summary_chars": len(mem.summary)}
```

---

## 🔗 LangChain / LangGraph Connection
The old `ConversationSummaryMemory` is deprecated. The current approach is a LangGraph node that summarises messages in state (the `langmem` package also offers `SummarizationNode`).

```python
from langchain_core.messages import HumanMessage, RemoveMessage  # message types
from langchain_openai import ChatOpenAI  # llm
from langgraph.graph import MessagesState, StateGraph, START, END  # graph

llm = ChatOpenAI(model="gpt-4o-mini")

class State(MessagesState):
    summary: str  # extra field kept next to the messages

def call_model(state: State) -> dict:
    msgs = state["messages"]
    if state.get("summary"):
        msgs = [("system", f"Summary of earlier chat: {state['summary']}")] + msgs
    return {"messages": [llm.invoke(msgs)]}

def summarise(state: State) -> dict:
    old = state["messages"][:-2]                                   # everything except the last 2
    prompt = f"Current summary: {state.get('summary', '')}\nExtend it with these messages: {old}"
    new_summary = llm.invoke([HumanMessage(prompt)]).content
    return {"summary": new_summary, "messages": [RemoveMessage(id=m.id) for m in old]}  # delete old from state

def should_summarise(state: State) -> str:
    return "summarise" if len(state["messages"]) > 6 else "end"

g = StateGraph(State)
g.add_node("model", call_model)
g.add_node("summarise", summarise)
g.add_edge(START, "model")
g.add_conditional_edges("model", should_summarise, {"summarise": "summarise", "end": END})
g.add_edge("summarise", END)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Summarising on every single turn
✅ Correct: summarise only when the buffer exceeds a threshold.

```python
# Wrong: an LLM call per message doubles cost
summary = llm_summarise(summary, [new_msg])
# Right
if buffer_tokens > LIMIT:
    summary = llm_summarise(summary, old_messages)
```

❌ Mistake 2: Letting the summary drop exact values (codes, amounts, ids)
✅ Correct: tell the summariser to keep exact identifiers, or store them as structured facts.

```python
# Wrong prompt: "Summarise the chat."
# Right prompt: "Update the summary. Keep exact HS codes, numbers, names and decisions verbatim."
```

---

## 🧠 Tricky Interview Question
**Q**: "After a long conversation the assistant states a wrong HS code the user had actually rejected. What failed?"

**Answer**: Summarisation is lossy and may flip or omit negations ("rejected 8504" became "8504"). Mitigate with a structured summary (sections: decisions, rejected options, open questions), verbatim identifiers, a summarisation prompt that preserves negatives, storing hard facts in a separate structured store, and tests that check key facts survive summarisation.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is summary memory?
A1: A running LLM-written summary of older conversation, combined with recent raw messages.

Q2: [Easy] Why use it instead of a sliding window?
A2: It keeps the gist of old turns rather than forgetting them.

Q3: [Medium] What are the downsides?
A3: Extra LLM calls and cost, latency, and information loss or distortion in summaries.

Q4: [Medium] When should summarisation run?
A4: When the buffer passes a token threshold, ideally in the background after responding.

Q5: [Hard] How do you evaluate summary quality?
A5: Make a set of conversations with key facts; after summarising, ask questions about those facts and measure recall; check for contradictions and negation errors; compare cost and accuracy against full history and sliding window.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Long conversations where earlier decisions matter
- Support handoffs, planning sessions

❌ Avoid when:
- Short chats (a window is enough)
- Exact wording or numbers are required (use structured storage or retrieval)

---

## 📊 Visual Diagram
```
 Turns: m1 m2 m3 m4 m5 m6 m7 m8
        \________ old _______/ \_ recent _/
                 |                  |
        [LLM summariser]            |
                 v                  v
        "summary text"   +   m7, m8 (raw)

 Prompt = [system] + [summary] + [recent raw messages] + [new user message]
```

---

## 💰 Cost Impact
- Summarisation call: about 400-800 tokens in, 150-300 out each time the buffer overflows, cheaper on gpt-4o-mini (about $0.0002 per call).
- Saves tokens on every later turn: 5,000-token history becomes about 300-token summary + 600 recent.
- Optimise: summarise in batches, cheap model, summary size cap, run async in the background, cache the summary per session.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Summary memory | Compressed past conversation | पुरानी बातचीत का सारांश |
| Running summary | Summary updated over time | समय के साथ अपडेट होता सारांश |
| Lossy | Some detail is lost | कुछ जानकारी खो जाती है |
| Buffer | Recent raw messages | हाल के raw messages |
| Compression | Making text shorter | Text को छोटा करना |

---

## ⚡ 3-Line Summary
English: Summary memory compresses old turns into a short running summary and keeps recent turns raw. It remembers decisions at low token cost but is lossy and needs extra LLM calls. Preserve exact facts in structured form.
Hindi: Summary memory पुराने turns को छोटे सारांश में बदलती है और हाल के turns को raw रखती है। यह कम token cost में फैसले याद रखती है पर lossy है और अतिरिक्त LLM calls माँगती है। सटीक facts structured रूप में सुरक्षित रखो।

---

## ➡️ Next Topic
**376. Entity Memory** — remembering specific people, products and facts as structured entities instead of free text.
