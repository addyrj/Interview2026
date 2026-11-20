---

# 99. Built-in Tools (SerperDevTool, FileReadTool, WebsiteSearchTool, CodeInterpreterTool etc.)
# हिंदी में: CrewAI के बने-बनाए Tools (Search, File, Website, Code)
# Framework: CrewAI
# Already Known: No

---

> Verified against crewai 1.15.41 and crewai-tools 1.15.41 (Python 3.13.3, fastapi 0.163.1). Both code samples were run offline: the LLM is a scripted stand-in (`fake.py`, listing at the end of this note), so no API key was needed. NOT run: real LLM calls (need an LLM key), `SerperDevTool` network search (needs `SERPER_API_KEY`), `WebsiteSearchTool` (needs an embedding key and a live website). Token counts are not shown because the scripted LLM reports none.

---

## 🔵 Simple Definition (2-3 lines)
The `crewai-tools` package ships ready-made tools you can hand to an agent: search the web (`SerperDevTool`), read a file (`FileReadTool`), list a folder (`DirectoryReadTool`), search inside a website (`WebsiteSearchTool`), and many more. You import, construct, and put them in `tools=[...]`; you write no tool code.

## 🔵 सरल परिभाषा (Hindi)
`crewai-tools` package में पहले से बने tools मिलते हैं जो आप agent को दे सकते हैं: web search (`SerperDevTool`), file पढ़ना (`FileReadTool`), folder की list (`DirectoryReadTool`), किसी website के अंदर search (`WebsiteSearchTool`) और बहुत से और। आप बस import करते हैं, object बनाते हैं और `tools=[...]` में डालते हैं; tool का code खुद नहीं लिखना पड़ता।

---

## 🔴 Problem it Solves
An LLM alone cannot read your rate sheet, browse the web, or run code. Writing and testing a tool for every common need (HTTP, schema, error handling, argument validation) is repeated work, and each hand-written tool is another place for bugs. Built-in tools give a tested starting point.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ LLM आपकी rate sheet नहीं पढ़ सकता, web browse नहीं कर सकता और code नहीं चला सकता। हर आम ज़रूरत (HTTP, schema, error handling, argument validation) के लिए खुद tool लिखना बार-बार का काम है और हर हाथ से लिखा tool bug की नई जगह है। Built-in tools एक जाँचा-परखा शुरुआती बिंदु देते हैं।

---

## 🟢 How it Works

```
pip install crewai-tools
Step 1 → tool = FileReadTool(file_path="rates.txt")      (construct, maybe with config / API key in env)
Step 2 → Agent(tools=[tool, ...])                         (tool name + description + args schema go into the prompt)
Step 3 → LLM writes:  Action: <tool name>  Action Input: {json}
Step 4 → CrewAI validates args against args_schema, runs tool._run(...)
Step 5 → tool output is appended to the conversation as an Observation
Step 6 → LLM continues until it writes Final Answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
pip install crewai-tools
Step 1 → tool बनाओ: FileReadTool(file_path="rates.txt")   (ज़रूरत हो तो config / API key env में)
Step 2 → Agent(tools=[tool, ...]) में दो            (tool का नाम + description + args schema prompt में जाता है)
Step 3 → LLM लिखता है:  Action: <tool नाम>  Action Input: {json}
Step 4 → CrewAI args को args_schema से validate करके tool._run(...) चलाता है
Step 5 → tool का output Observation बनकर बातचीत में जुड़ता है
Step 6 → LLM तब तक चलता है जब तक Final Answer न लिख दे
```

**What we confirmed in the installed package (crewai-tools 1.15.41):**
- Importable at top level: `SerperDevTool`, `FileReadTool`, `DirectoryReadTool`, `WebsiteSearchTool`, `ScrapeWebsiteTool`, `PDFSearchTool`, `CSVSearchTool`, `JSONSearchTool`, `TXTSearchTool`, `DirectorySearchTool`, `RagTool`, `TavilySearchTool`, `BraveSearchTool`, `EXASearchTool`, `FileWriterTool`, `NL2SQLTool`, `MCPServerAdapter` and many more (run `import crewai_tools; print(crewai_tools.__all__)` to see the full list for your version).
- **`CodeInterpreterTool` is NOT exported by crewai-tools 1.15.41.** Older tutorials import it; in this version the sandboxed code-execution tools are `E2BPythonTool`, `DaytonaPythonTool`, and the AWS Bedrock code-interpreter toolkit (`crewai_tools.aws.bedrock.code_interpreter`). We did not run any of them (E2B/Daytona need accounts and API keys). Check the docs of your own version before copying an old import.
- Real tool names the LLM sees: `FileReadTool` -> `Read a file's content`, `DirectoryReadTool` -> `List files in directory`, `SerperDevTool` -> `Search the internet with Serper`.
- `FileReadTool(file_path="rates.txt")` pre-binds a default file, so the agent can call it with empty input.
- `SerperDevTool()` constructs fine without a key, but `.run(search_query=...)` raised `KeyError: 'SERPER_API_KEY'` in our test. Handle that at start-up, not mid-run.

**Hindi नोट:** `CodeInterpreterTool` पुराने tutorials में मिलता है, पर इस version (1.15.41) में top-level पर export नहीं है। Code चलाने के लिए E2B / Daytona / Bedrock वाले tools हैं, पर इन्हें हमने चलाकर नहीं देखा (account + API key चाहिए)। अपने version के docs ज़रूर जाँचें।

---

## 🟡 Real World Example
**Tariff Agent.** A customs broker asks "what is the duty for HS 8471?". The agent has `FileReadTool` bound to the company's `rates.txt`, `DirectoryReadTool` to see which rate sheets exist, and (if `SERPER_API_KEY` is set) `SerperDevTool` to check a recent government notification. Local file first, web only when needed.

**Research Agent:** `SerperDevTool` finds pages, `ScrapeWebsiteTool` reads one, `WebsiteSearchTool` answers questions over one site.

## 🟡 Real Example Hindi mein
**Tariff Agent.** Customs broker पूछता है "HS 8471 की duty क्या है?" Agent के पास कंपनी की `rates.txt` से बंधा `FileReadTool` है, कौन-सी rate sheets मौजूद हैं यह देखने के लिए `DirectoryReadTool` है, और अगर `SERPER_API_KEY` सेट है तो सरकारी notification देखने के लिए `SerperDevTool`। पहले local file, ज़रूरत हो तब ही web।

**Research Agent:** `SerperDevTool` pages खोजता है, `ScrapeWebsiteTool` एक page पढ़ता है, `WebsiteSearchTool` एक site के ऊपर सवालों के जवाब देता है।

---

## 💻 Code Example — Basic
Runs offline (needs `fake.py` from the listing at the end of this note, and a `rates.txt` file containing `HS 8471 laptops 0%`).

```python
# Basic: give a CrewAI agent built-in tools (FileReadTool + DirectoryReadTool). Runs offline.
# verified against crewai 1.15.41 + crewai-tools 1.15.41; real LLM: not run - needs OPENAI_API_KEY (or another provider)
import os                                                          # env switches
os.environ["OTEL_SDK_DISABLED"] = "true"                           # keep telemetry quiet in the demo
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"                    # same, CrewAI-side
from crewai import Agent, Task, Crew                               # core CrewAI objects
from crewai_tools import FileReadTool, DirectoryReadTool          # built-in tools (no API key needed)
from fake import ScriptedLLM                                       # scripted offline LLM (listing at end of note)

reader = FileReadTool(file_path="rates.txt")                       # pre-bind one file: agent only passes nothing
lister = DirectoryReadTool(directory=".")                          # list files below this directory
print("tool names:", reader.name, "|", lister.name)               # these exact names go in the prompt

llm = ScriptedLLM(model="fake", replies=[                          # reply 1: ask for the tool (ReAct text format)
    'Thought: read the tariff sheet.\nAction: Read a file\'s content\nAction Input: {}',
    'Thought: got it.\nFinal Answer: HS 8471 laptops carry 0% duty.',   # reply 2: final answer
])
analyst = Agent(                                                   # one Tariff Agent
    role="Tariff Analyst", goal="Answer duty questions from the rates file",
    backstory="Senior customs analyst", tools=[reader, lister], llm=llm, verbose=False)
task = Task(description="What is the duty for HS 8471?", expected_output="One sentence", agent=analyst)
result = Crew(agents=[analyst], tasks=[task], verbose=False).kickoff()   # run the crew
print(result.raw)                                                  # HS 8471 laptops carry 0% duty.
print("tool output reached the prompt:", "HS 8471 laptops 0%" in " ".join(llm.seen))   # True
```

Output we got: `tool names: Read a file's content | List files in directory`, `HS 8471 laptops carry 0% duty.`, `tool output reached the prompt: True`.

## 💻 Code Example — Advanced
FastAPI endpoint, async crew (`kickoff_async`), tool list built from the environment (web search only if the key exists), bounded loop (`max_iter`), errors turned into HTTP 502.

```python
# Advanced: FastAPI + async crew + built-in tools chosen by env, with error handling.
# verified against crewai 1.15.41, crewai-tools 1.15.41, fastapi 0.163.1 (TestClient).
# Real search (SerperDevTool) and real LLM: not run - need SERPER_API_KEY and an LLM key.
import os                                                          # env access
os.environ["OTEL_SDK_DISABLED"] = "true"                           # quiet telemetry
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
from typing import Any                                             # type hints
from fastapi import FastAPI, HTTPException                         # web layer
from pydantic import BaseModel                                     # request/response models
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool                                  # common base of every tool
from crewai_tools import FileReadTool, SerperDevTool              # built-in tools
from fake import ScriptedLLM                                       # offline LLM stand-in

class AskIn(BaseModel):                                            # request body
    question: str

class AskOut(BaseModel):                                           # response body
    answer: str
    tools_used: list[str]

def build_tools() -> list[BaseTool]:
    tools: list[BaseTool] = [FileReadTool(file_path="rates.txt")]  # always-on local tool
    if os.getenv("SERPER_API_KEY"):                                # web search only when the key exists
        tools.append(SerperDevTool(n_results=3))                   # n_results is a real constructor field
    return tools                                                   # missing key => no web tool (not a crash)

def build_llm() -> ScriptedLLM:                                    # swap for LLM(model=...) in production
    return ScriptedLLM(model="fake", replies=[
        'Thought: read file.\nAction: Read a file\'s content\nAction Input: {}',
        'Thought: done.\nFinal Answer: 8471 laptops: 0% duty.'])

app = FastAPI()

@app.post("/ask", response_model=AskOut)
async def ask(body: AskIn) -> AskOut:
    tools = build_tools()                                          # fresh tool list per request
    agent = Agent(role="Tariff Analyst", goal="Answer duty questions", backstory="Customs expert",
                  tools=tools, llm=build_llm(), verbose=False, max_iter=5)   # max_iter bounds the loop (cost guard)
    task = Task(description=body.question, expected_output="One sentence", agent=agent)
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    try:
        out: Any = await crew.kickoff_async()                      # async entry point; does not block the event loop
    except Exception as e:                                         # tool/LLM failures become a clean 502
        raise HTTPException(status_code=502, detail=f"{type(e).__name__}: {e}")
    return AskOut(answer=out.raw, tools_used=[t.name for t in tools])

if __name__ == "__main__":
    from fastapi.testclient import TestClient
    print(TestClient(app).post("/ask", json={"question": "Duty for HS 8471?"}).json())
    try:
        SerperDevTool().run(search_query="x")                      # no key set -> KeyError (we saw this)
    except KeyError as e:
        print("Serper without key raises KeyError:", e)
```

Output we got: `{'answer': '8471 laptops: 0% duty.', 'tools_used': ["Read a file's content"]}` and `Serper without key raises KeyError: 'SERPER_API_KEY'`.

**`fake.py` (offline LLM used by every sample in this folder):**

```python
"""Scripted offline LLM for CrewAI (subclass of crewai.BaseLLM). verified crewai 1.15.41"""
from typing import Any
from crewai import BaseLLM

class ScriptedLLM(BaseLLM):
    replies: list[str] = []          # replies returned in order
    calls: int = 0                   # how many times call() ran
    seen: list[str] = []             # text of every prompt the LLM received
    def call(self, messages: Any, tools: Any = None, callbacks: Any = None,
             available_functions: Any = None, from_task: Any = None,
             from_agent: Any = None, response_model: Any = None) -> str:
        self.seen.append(str(messages))   # keep the prompt so we can inspect it
        r = self.replies[min(self.calls, len(self.replies) - 1)]
        self.calls += 1
        return r
    def supports_function_calling(self) -> bool:
        return False                 # force ReAct text format
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Ready-made tools | Few in core; many via `langchain-community` | Large `crewai-tools` catalogue (search, scrape, file, RAG, DB) | Hosted tools (web search, file search, code interpreter) run by OpenAI | Some extension tools (e.g. code executors) |
| Tool definition | LangChain `@tool` / `BaseTool` | `@tool` or `BaseTool` subclass | `@function_tool` | Python functions wrapped as tools |
| Needs extra keys | Per tool | Per tool (e.g. Serper) | OpenAI account for hosted tools | Per tool |
| Offline test | Fake chat model | Scripted `BaseLLM` (shown here) | Mock model | `ReplayChatCompletionClient` |

_CrewAI column verified in crewai-tools 1.15.41. The other columns are from general knowledge and were not installed or re-verified here; check their docs before quoting them in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake 1: Copying `from crewai_tools import CodeInterpreterTool` from an old blog post.
✅ Correct: Check `crewai_tools.__all__` for your installed version; in 1.15.41 use E2B / Daytona / Bedrock based tools for sandboxed code.

❌ Mistake 2: Constructing `SerperDevTool()` and assuming it works; the key error appears only at call time.
✅ Correct: Check `os.getenv("SERPER_API_KEY")` at start-up and only add the tool if present (as in the advanced sample).

❌ Mistake 3: Giving the agent every tool "just in case".
✅ Correct: Fewer tools = shorter prompt = fewer wrong tool choices = lower cost. Give each agent only what its role needs.

❌ Mistake 4: Letting a file tool read anywhere on disk in a web service.
✅ Correct: Bind it to one file (`file_path=`) or one directory, never accept a path from the user unchecked.

---

## 🧠 Tricky Interview Question
Your CrewAI agent keeps calling `SerperDevTool` three times with near-identical queries and the bill is high. What do you check?

**Answer:** (1) Tool descriptions: if two tools sound alike the model hesitates and retries; sharpen them. (2) `max_iter` on the agent caps the loop. (3) Per-tool `max_usage_count` (a real field on `BaseTool`) caps calls per tool instance; we saw the framework return a usage-limit failure once it is spent (note #100). (4) Tool result caching (`cache_function` on `BaseTool`) avoids paying for identical queries. (5) Put the cheapest tool first in the instructions ("check the rates file before searching the web"). (6) Lower `n_results` so each observation is shorter. (7) Log tool calls per task to see the real pattern before changing anything.

---

## ⚫ Interview Questions + Answers

**Q1:** What is `crewai-tools`?

**A1:** A separate package of ready-made tools (search, scrape, file, RAG over files/sites, DB, cloud) that you pass to `Agent(tools=[...])`.

**Q2:** How does the agent decide which tool to call?

**A2:** The tool's name, description and args schema are placed in the prompt; the LLM writes an action with JSON arguments, and CrewAI validates them and runs the tool.

**Q3:** Why does `FileReadTool(file_path=...)` matter in production?

**A3:** It pre-binds the file so the model cannot choose arbitrary paths, which is both safer and cheaper (no path in each call).

**Q4:** A built-in tool needs an API key and the key is missing at runtime. How do you design for it?

**A4:** Fail fast at start-up or build the tool list from the environment; catch exceptions around `kickoff_async` and return a clean error (we returned 502).

**Q5:** System design: an agent service where tenants can enable different tools.

**A5:** Build the tool list per request from tenant config (allow-list), create fresh agent/tool objects per request, keep secrets in a secret manager not in the prompt, cap `max_iter` and per-tool `max_usage_count`, log every tool call with tenant id, and never share one mutable tool object with per-tenant state across requests.

---

## 💰 Cost Impact
Each tool adds its description and schema to every LLM call in the loop (input tokens), and each observation (file text, search results) is added to later calls. Rough formula: tokens per run = sum over steps of (system prompt + tool schemas + history so far) + outputs. Tips: few tools per agent, small `n_results`, bind files narrowly, cap `max_iter`, cache repeated queries. Dollar amounts depend on the model's price list; use clearly labelled estimates ("approximate, from public pricing at time of writing - verify") and measure with your provider's usage fields in a real run. We did not measure tokens here.

---

## 🔷 When to Use
✅ Use when:
- The need is common (web search, read a file, scrape a page, RAG over a PDF/CSV)
- You want a quick, tested start before writing your own tool
- Prototype or internal tools

❌ Avoid when:
- You need strict security control over what the tool can touch (write a narrow custom tool, note #100)
- The built-in tool pulls heavy dependencies you do not want in production
- The tool changed between versions and you cannot pin the version

---

## 📊 Visual Diagram
```
 user question
      |
      v
  +---------+   Action: "Read a file's content"    +----------------+
  |  Agent  | -----------------------------------> | FileReadTool   | -> rates.txt
  |  (LLM)  | <----------------------------------- +----------------+
  |         |   Observation: "HS 8471 laptops 0%"
  |         |   Action: "Search the internet..."   +----------------+
  |         | -----------------------------------> | SerperDevTool  | -> web (needs key)
  +---------+ <----------------------------------- +----------------+
      |
      v
  Final Answer
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| crewai-tools | Package of ready-made tools | बने-बनाए tools का package |
| SerperDevTool | Google-style web search via Serper API | Serper API से web search |
| FileReadTool | Reads a text file | text file पढ़ने वाला tool |
| DirectoryReadTool | Lists files in a folder | folder की files की सूची |
| WebsiteSearchTool | RAG search inside a website | website के अंदर search |
| args_schema | Pydantic model of tool inputs | tool के inputs का schema |
| Observation | Tool output fed back to the LLM | tool का नतीजा LLM को वापस |

---

## ⚡ 3-Line Summary
English: crewai-tools gives you ready tools; construct them and pass them in `tools=[...]`.
Check the installed version's `__all__` (CodeInterpreterTool is gone in 1.15.41) and handle missing API keys at start-up.
Fewer, narrower tools mean lower cost and fewer wrong calls.

Hindi: crewai-tools बने-बनाए tools देता है; उन्हें बनाकर `tools=[...]` में दें।
अपने version का `__all__` जाँचें (1.15.41 में CodeInterpreterTool नहीं है) और API key की कमी start-up पर ही पकड़ें।
कम और सीमित tools मतलब कम cost और कम गलत calls।

---

## ➡️ Next Topic
**#100 Custom Tools in CrewAI** - when no built-in tool fits (your own tariff API, your DB), you write a tool with `@tool` or `BaseTool`, validate its inputs, and make it fail safely.

---
