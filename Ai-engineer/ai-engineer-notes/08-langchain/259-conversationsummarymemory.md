---

# 259. ConversationSummaryMemory
# हिंदी में: ConversationSummaryMemory (बातचीत का सारांश याद रखना)

---

## 🔵 Simple Definition (English)
`ConversationSummaryMemory` (legacy) keeps a **running summary** of the conversation instead of every message. After each turn, an LLM updates the summary ("new lines + old summary = new summary"). The prompt carries only the short summary, so long chats stay cheap.

## 🔵 सरल परिभाषा (Hindi)
`ConversationSummaryMemory` (legacy) हर message की जगह बातचीत का **चलता हुआ सारांश** रखती है। हर turn के बाद LLM summary अपडेट करता है ("नई lines + पुरानी summary = नई summary")। Prompt में सिर्फ़ छोटी summary जाती है, इसलिए लंबी chats सस्ती रहती हैं।

---

## 🔴 Problem it Solves
- Buffer memory grows with each turn and finally overflows the context window.
- Window memory forgets old but important facts ("my client is in Vietnam").
- Summary keeps the gist of the whole chat in a fixed small size.

## 🔴 यह क्यों बना? (Hindi)
- Buffer memory हर turn के साथ बढ़ती है और आख़िर में context window भर देती है।
- Window memory पुराने ज़रूरी facts भूल जाती है ("मेरा client Vietnam में है")।
- Summary पूरी chat का सार एक छोटे, तय size में रखती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → summary = "" at the start
Step 2 → Each turn: prompt = system + summary + new input
Step 3 → LLM answers
Step 4 → Memory calls a second LLM prompt: "Current summary + new lines → new summary"
Step 5 → Replace summary with the new one
Step 6 → Prompt size stays roughly constant
Step 7 → Trade-off: extra LLM call per turn, and details can be lost
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → शुरू में summary = ""
Step 2 → हर turn: prompt = system + summary + नया input
Step 3 → LLM जवाब देता है
Step 4 → Memory दूसरा LLM prompt चलाती है: "मौजूदा summary + नई lines → नई summary"
Step 5 → Summary को नई वाली से बदलो
Step 6 → Prompt का size लगभग स्थिर रहता है
Step 7 → Trade-off: हर turn एक extra LLM call, और details खो सकती हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: A 40-turn session with a broker covering 6 products. A summary like "Broker imports from Vietnam. Speaker = 8518.22 (20%). Headphones = 8518.30 (10%). Pending: cables." replaces 6000 tokens of transcript with ~60 tokens.
**Amazon AI**: a long support case summarised so an agent (or bot) can continue quickly.

## 🟡 Real Example Hindi mein
**Tariff System**: Broker के साथ 40 turns का session जिसमें 6 products हैं। "Broker Vietnam से import करता है। Speaker = 8518.22 (20%)। Headphones = 8518.30 (10%)। बाकी: cables।" जैसी summary 6000 tokens के transcript की जगह ~60 tokens में आ जाती है।
**Amazon AI**: लंबे support case की summary ताकि agent (या bot) जल्दी आगे बढ़े।

---

## 💻 Code Example — Basic
```python
# Basic: running-summary memory in pure Python with a fake summariser (runnable offline)
from typing import List

def fake_summarise(old_summary: str, new_lines: List[str]) -> str:
    """Stand-in for an LLM call: keeps only lines that contain a number or HS code."""
    kept = [ln for ln in new_lines if any(ch.isdigit() for ch in ln)]   # "important" lines
    pieces = ([old_summary] if old_summary else []) + kept
    return " ".join(pieces)

class SummaryMemory:
    def __init__(self) -> None:
        self.summary: str = ""                      # the only thing we keep

    def save(self, human: str, ai: str) -> None:
        # Update the summary with the new exchange
        self.summary = fake_summarise(self.summary, [f"H: {human}", f"A: {ai}"])

if __name__ == "__main__":
    mem = SummaryMemory()
    mem.save("Hello!", "Hi, how can I help?")                     # no numbers: nothing kept
    mem.save("HS code for speaker?", "A: HS 8518.22, duty 20%")   # numbers: kept
    print("summary:", mem.summary)
    print("summary chars:", len(mem.summary))
    # Real class (legacy): ConversationSummaryMemory(llm=llm)
```

## 💻 Code Example — Advanced
```python
# Rolling summary memory built with modern building blocks (async, typed, error handling)
import asyncio

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

summarise_prompt = ChatPromptTemplate.from_template(
    "Current summary:\n{summary}\n\nNew lines:\n{lines}\n\n"
    "Write an updated summary in under 80 words. Keep facts, numbers, HS codes, and open tasks."
)
summariser = summarise_prompt | llm.bind(max_tokens=150) | StrOutputParser()

answer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a tariff assistant. Conversation so far (summary): {summary}"),
    ("human", "{input}"),
])
answerer = answer_prompt | llm.bind(max_tokens=300) | StrOutputParser()

class RollingSummaryChat:
    def __init__(self, keep_last: int = 2) -> None:
        self.summary: str = "(none)"
        self.recent: list[BaseMessage] = []        # last few raw messages (not yet summarised)
        self.keep_last = keep_last

    async def ask(self, text: str) -> str:
        try:
            reply = await answerer.ainvoke({"summary": self.summary, "input": text})
        except Exception as exc:                   # network / rate limit / auth
            return f"Error: {type(exc).__name__}"
        self.recent += [HumanMessage(text), AIMessage(reply)]
        if len(self.recent) > self.keep_last * 2:  # fold older messages into the summary
            old, self.recent = self.recent[:-self.keep_last * 2], self.recent[-self.keep_last * 2:]
            lines = "\n".join(f"{m.type}: {m.content}" for m in old)
            try:
                self.summary = await summariser.ainvoke({"summary": self.summary, "lines": lines})
            except Exception:
                self.recent = old + self.recent    # keep raw messages if summarising fails
        return reply

async def demo() -> None:
    chat = RollingSummaryChat()
    for q in ["I import from Vietnam", "HS code for speakers?", "And headphones?", "Duty on the first one?"]:
        print(await chat.ask(q))
    print("SUMMARY:", chat.summary)

if __name__ == "__main__":
    asyncio.run(demo())   # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
Store the summary string (and last messages) per session in Redis. Summarise in a background task so the user gets the answer first.

```python
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

app = FastAPI()
chats: dict[str, RollingSummaryChat] = {}    # use Redis in production

class In(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
async def chat(body: In) -> dict[str, str]:
    c = chats.setdefault(body.session_id, RollingSummaryChat())
    reply = await c.ask(body.message)       # includes summarising when needed
    return {"answer": reply, "summary": c.summary}
```

---

## 🔗 LangChain / LangGraph Connection
Legacy: `ConversationSummaryMemory(llm=llm)` and `ConversationSummaryBufferMemory(llm=llm, max_token_limit=500)` (summary for old turns, raw for recent). Modern LangGraph: add a `summary` field to the state and a node that summarises when `len(messages)` is large, then removes old messages with `RemoveMessage`. LangMem and LangGraph docs describe this pattern.

```python
from langchain_core.messages import RemoveMessage

def summarize_node(state: dict) -> dict:
    msgs = state["messages"]
    if len(msgs) <= 6:
        return {}                                              # nothing to do
    text = "\n".join(f"{m.type}: {m.content}" for m in msgs[:-2])
    summary = llm.invoke(f"Summarise briefly:\n{text}").content
    return {"summary": summary,
            "messages": [RemoveMessage(id=m.id) for m in msgs[:-2]]}   # drop old messages
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Letting the summary grow forever.
✅ Correct: Ask for a maximum length ("under 80 words") and set `max_tokens`.

```python
# Wrong
prompt = "Summarise the chat."
# Right
prompt = "Update the summary in under 80 words. Keep numbers and HS codes."
```

❌ Mistake 2: Summarising away exact values (HS codes, amounts).
✅ Correct: Tell the summariser to keep identifiers and numbers.

❌ Mistake 3: Summarising on the critical path with no failure handling.
✅ Correct: Keep the raw messages if summarising fails; summarise in the background.

---

## 🧠 Tricky Interview Question
**Q**: "Your summary-memory bot sometimes states things the user never said. Why?"

**Answer**: Summaries are LLM-generated, so errors compound: a hallucinated detail gets into the summary, then future summaries keep and amplify it ("telephone game"). Mitigation: temperature 0, strict prompt ("only facts stated; do not infer"), keep last N raw messages beside the summary (SummaryBuffer pattern), store critical facts structurally (a JSON of entities), and periodically verify against the raw log.

---

## ⚫ Interview Questions + Answers

Q1: What does ConversationSummaryMemory store?
A1: One string: a running summary of the conversation produced by an LLM.

Q2: Why use it instead of buffer memory?
A2: Constant, small prompt size for long chats, so lower cost and no context overflow.

Q3: What is ConversationSummaryBufferMemory?
A3: A hybrid: keeps recent messages raw up to `max_token_limit`, and summarises older ones. Good balance of detail and size.

Q4: What are the drawbacks?
A4: Extra LLM call (cost, latency) each time, possible loss or distortion of details, and error compounding.

Q5: Design memory for a 200-turn support chat with legal exactness for amounts.
A5: Hybrid: last 6 raw messages, rolling summary for narrative, and a structured fact store (order id, amounts, HS codes) updated by extraction with validation. Prompt includes facts + summary + recent messages. Keep the full raw log in a database for audit, and summarise asynchronously.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Long conversations
- Gist matters more than exact wording
- Token cost is a concern

❌ Avoid when:
- Exact quotes or numbers are essential (without structured facts)
- Very short chats (buffer is cheaper)
- Latency is critical (extra LLM call)

---

## 📊 Visual Diagram
```
 old summary ─┐
              ├─► [Summariser LLM] ─► new summary ──┐
 new lines  ──┘                                     │
                                                    ▼
 Next turn prompt = system + SUMMARY (short) + new input ──► LLM

 Turn:       1     10     50     200
 Buffer:    ▂     ▃▃     ▅▅▅▅   ███████ (overflow)
 Summary:   ▂     ▂▂     ▂▂▂    ▂▂▂     (flat)
```

---

## 💰 Cost Impact
- Each turn adds a summarising call: ~summary (100 tokens) + new lines (200) in, ~80 out, about 380 tokens. With gpt-4o-mini this is roughly $0.0001 per turn.
- Savings: after 30 turns, buffer sends ~4500 history tokens per call; summary sends ~100.
- Optimise: summarise every N turns instead of every turn, use a small cheap model, cap summary tokens, run in the background, and store key facts structurally.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Summary memory | Running LLM-written summary | चलती हुई सारांश memory |
| SummaryBuffer | Summary of old + raw recent messages | पुराने की summary + हाल के raw messages |
| max_token_limit | Size limit before summarising | Summarise करने से पहले की token सीमा |
| Error compounding | Mistakes carried forward in summaries | Summary में गलतियों का आगे बढ़ना |
| RemoveMessage | LangGraph way to delete messages | LangGraph में message हटाने का तरीका |

---

## ⚡ 3-Line Summary
English: Summary memory keeps a short, LLM-updated summary instead of the full transcript. It keeps long-chat cost flat, but adds an LLM call and may distort details. Combine with recent raw messages and structured facts for accuracy.
Hindi: Summary memory पूरे transcript की जगह LLM से अपडेट होने वाली छोटी summary रखती है। लंबी chat की cost स्थिर रहती है, पर एक extra LLM call लगती है और details बिगड़ सकती हैं। सटीकता के लिए हाल के raw messages और structured facts साथ रखो।

---

## ➡️ Next Topic
**260. Chains — Legacy**: LLMChain, SequentialChain and why LCEL replaced them.
