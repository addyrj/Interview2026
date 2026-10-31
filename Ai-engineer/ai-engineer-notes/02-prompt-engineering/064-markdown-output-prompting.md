---

# 064. Markdown Output Prompting
# हिंदी में: Markdown Output Prompting — इंसानों के लिए सुंदर जवाब

---

## 🔵 Simple Definition (English)
Markdown Output Prompting tells the LLM to format its answer with Markdown: headings, bullet lists, tables, bold text and code blocks. The text then renders nicely in chat UIs, docs and emails. It is for human readers, not for machine parsing.

## 🔵 सरल परिभाषा (Hindi)
Markdown Output Prompting में हम LLM से कहते हैं कि जवाब Markdown में दे: headings, bullet lists, tables, bold और code blocks। Chat UI, docs और emails में यह अच्छा दिखता है। यह इंसानों के पढ़ने के लिए है, machine parsing के लिए नहीं।

---

## 🔴 Problem it Solves
A plain paragraph with 12 facts is hard to scan. Raw LLM output often has random formatting: sometimes bullets, sometimes walls of text. Different answers look different, and UIs cannot style them consistently.

Markdown prompting gives a predictable, readable layout that front-end renderers (React Markdown, marked, etc.) can show well.

## 🔴 यह क्यों बना? (Hindi)
12 facts वाला लंबा paragraph scan करना मुश्किल है। LLM का default formatting कभी bullets, कभी text की दीवार होता है। हर जवाब अलग दिखता है और UI उन्हें एक जैसा style नहीं कर पाता। Markdown prompting predictable और पढ़ने लायक layout देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide the layout (sections, table columns, length)
Step 2 → Tell the model the exact Markdown elements allowed
Step 3 → Give a small template or example of the layout
Step 4 → Call the model (temperature 0.2-0.5)
Step 5 → Get Markdown text
Step 6 → Sanitize (remove raw HTML / scripts) before rendering
Step 7 → Render in UI (react-markdown, marked, mdx)
Step 8 → (Optional) lint: check headings and table shape with code
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Layout तय करो (sections, table columns, length)
Step 2 → Model को बताओ कौन से Markdown elements allowed हैं
Step 3 → छोटा template या example दो
Step 4 → Model call करो (temperature 0.2-0.5)
Step 5 → Markdown text मिलता है
Step 6 → Render से पहले raw HTML / scripts हटाओ (sanitize)
Step 7 → UI में render करो
Step 8 → (Optional) code से headings और table shape check करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs officer asks "Explain why this item is 8518.30". The prompt asks for Markdown with sections `## Classification`, `## Reasoning` (bullets) and `## Duty Rates` (a table with Country, Rate). The web UI renders this as a clean report the officer can copy into a case file.

**Amazon-style**: A product comparison assistant returns a Markdown table: Feature, Product A, Product B.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs officer पूछता है "यह item 8518.30 क्यों है?" Prompt Markdown माँगता है: `## Classification`, `## Reasoning` (bullets) और `## Duty Rates` (Country, Rate table)। Web UI इसे साफ़ report की तरह दिखाता है जिसे officer case file में copy कर सकता है।

**Amazon-style**: Product comparison assistant Markdown table देता है: Feature, Product A, Product B।

---

## 💻 Code Example — Basic
```python
# Basic: ask for Markdown, then check the layout with plain Python (offline)
import re  # regular expressions for simple checks

SYSTEM = """You write tariff reports in Markdown.
Use exactly these sections, in this order:
## Classification
## Reasoning   (3 bullet points)
## Duty Rates  (a table with columns: Country | Rate)
No HTML. No text outside the sections."""

def fake_llm(system: str, user: str) -> str:
    # Pretend LLM reply that follows the template
    return (
        "## Classification\n8518.30 - Headphones and earphones\n\n"
        "## Reasoning\n- Worn on the ear\n- Converts electrical signal to sound\n- Wireless does not change heading\n\n"
        "## Duty Rates\n| Country | Rate |\n|---|---|\n| US | 0% |\n| IN | 20% |\n"
    )

def check_layout(md: str) -> list[str]:
    problems: list[str] = []                                  # collect problems found
    for heading in ("## Classification", "## Reasoning", "## Duty Rates"):
        if heading not in md:                                  # required heading missing?
            problems.append(f"missing {heading}")
    bullets = re.findall(r"^- .+", md, flags=re.MULTILINE)     # lines starting with "- "
    if len(bullets) != 3:                                      # we asked for exactly 3
        problems.append(f"expected 3 bullets, got {len(bullets)}")
    if "<script" in md.lower():                                # basic safety check
        problems.append("contains script tag")
    return problems                                            # empty list = good

reply = fake_llm(SYSTEM, "Explain 8518.30 for wireless earbuds")  # get Markdown
print(reply)                                                   # show the report
print("Problems:", check_layout(reply))                        # Problems: []
```

## 💻 Code Example — Advanced
```python
# Production style: async generation, layout lint, HTML sanitizing, one repair retry
from __future__ import annotations

import asyncio                                   # async demo runner
import re                                        # regex helpers
from typing import Awaitable, Callable           # type hints

LLM = Callable[[str, str], Awaitable[str]]       # (system, user) -> reply text

REQUIRED = ("## Classification", "## Reasoning", "## Duty Rates")   # headings we demand
TAG_RE = re.compile(r"<[^>]+>")                  # crude HTML tag matcher

def strip_html(md: str) -> str:
    """Remove raw HTML tags. For real apps also sanitize in the renderer."""
    return TAG_RE.sub("", md)                    # delete anything like <b> or <script>

def lint(md: str) -> list[str]:
    """Return a list of layout problems (empty means OK)."""
    issues = [f"missing {h}" for h in REQUIRED if h not in md]     # missing headings
    if "| Country | Rate |" not in md:                              # table header check
        issues.append("duty table header missing")
    return issues

async def generate_report(llm: LLM, question: str, retries: int = 1) -> str:
    system = ("Write the answer in Markdown with sections: "
              + ", ".join(REQUIRED) + ". Use a table '| Country | Rate |' under Duty Rates. No HTML.")
    prompt = question                                              # first user message
    for _ in range(retries + 1):                                   # allow one repair
        try:
            md = strip_html(await llm(system, prompt))             # call + clean
        except Exception as exc:                                   # network/API failure
            raise RuntimeError(f"LLM call failed: {exc}") from exc
        issues = lint(md)                                          # check the layout
        if not issues:                                             # good report
            return md
        prompt = f"{question}\nFix these layout problems: {issues}"   # ask for a repair
    return md                                                      # return best effort

async def _demo() -> None:
    async def llm(system: str, user: str) -> str:
        if "Fix" not in user:                                      # first try is bad
            return "Here you go: 8518.30"
        return ("## Classification\n8518.30\n\n## Reasoning\n- ear worn\n\n"
                "## Duty Rates\n| Country | Rate |\n|---|---|\n| US | 0% |")
    print(await generate_report(llm, "Explain 8518.30"))

if __name__ == "__main__":
    asyncio.run(_demo())
```
Token usage: Markdown symbols (`##`, `|`, `-`) add ~10-20% more output tokens than plain text; tables cost the most. A repair retry doubles the request cost.

---

## 🟠 FastAPI Integration
Return Markdown as `text/markdown` or inside JSON `{ "markdown": "..." }`. Streaming Markdown with Server-Sent Events gives a typing effect in the UI.

```python
from fastapi import FastAPI                       # web framework
from fastapi.responses import StreamingResponse   # for streaming tokens
from openai import AsyncOpenAI                    # openai>=1 async client
from pydantic import BaseModel                    # request model

app = FastAPI()                                   # create app
client = AsyncOpenAI()                            # key from env

class Ask(BaseModel):
    question: str                                 # user question

SYSTEM = "Answer in Markdown: ## Answer, ## Why (bullets). No HTML."   # style rules

@app.post("/report")
async def report(body: Ask) -> StreamingResponse:
    async def gen():                              # async generator of text chunks
        stream = await client.chat.completions.create(
            model="gpt-4o-mini", stream=True, temperature=0.3, max_tokens=500,
            messages=[{"role": "system", "content": SYSTEM},
                      {"role": "user", "content": body.question}],
        )
        async for chunk in stream:                # each chunk has a small delta
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content   # send text to the client
    return StreamingResponse(gen(), media_type="text/markdown")
```

---

## 🔗 LangChain / LangGraph Connection
`StrOutputParser` returns the Markdown string. Put the style rules in a system message in a `ChatPromptTemplate`. In LangGraph, a final "writer" node often turns structured state (JSON from earlier nodes) into a Markdown report.

```python
from langchain_core.prompts import ChatPromptTemplate   # prompt template
from langchain_core.output_parsers import StrOutputParser  # returns plain string
from langchain_openai import ChatOpenAI                 # chat model

prompt = ChatPromptTemplate.from_messages([
    ("system", "Write a Markdown report with ## Classification and ## Reasoning. No HTML."),
    ("user", "Facts: {facts}"),                        # facts come from earlier steps
])
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0.3) | StrOutputParser()
# md = await chain.ainvoke({"facts": "hs=8518.30, conf=0.93"})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using Markdown when code must parse the output
✅ Correct: Use JSON for machines, Markdown for humans. Do both: JSON for data, then render Markdown from it.
```python
# Wrong: regex over a Markdown table to read the HS code
code = re.search(r"\| (\d{4}\.\d{2})", md).group(1)

# Right: ask for JSON; build the Markdown yourself from typed data
md = f"## Classification\n{result.hs_code}"
```

❌ Mistake 2: Rendering model output as raw HTML
✅ Correct: Sanitize. A prompt-injected document can make the model emit `<script>` or markdown links with `javascript:`.
```python
# Wrong
html = markdown_to_html(md)            # then inject into the page as-is

# Right
html = sanitize(markdown_to_html(md))  # allow-list tags and URL schemes
```

❌ Mistake 3: No layout example, so every answer looks different. Add a short template.

---

## 🧠 Tricky Interview Question
**Q**: "Your chat UI shows broken tables for some answers. The prompt says 'use Markdown tables'. Why, and how do you fix it?"

**Answer**: Models sometimes write tables with missing separator rows, unescaped `|` in cells, or wrap the table in a code fence. Fixes: (1) give an exact table template in the prompt, (2) tell it to escape pipes or avoid them in cell text, (3) lint the reply (header row + separator row + equal column count), (4) auto-repair or retry, (5) for critical data return JSON and render the table in the front-end yourself.

---

## ⚫ Interview Questions + Answers

Q1: When do you ask for Markdown instead of JSON?
A1: When the reader is a human (chat UI, report, email). Use JSON when software consumes the output.

Q2: Name 4 Markdown elements useful in LLM answers.
A2: Headings (`##`), bullet lists, tables, and fenced code blocks (also bold for key terms).

Q3: How do you keep the formatting consistent across answers?
A3: Put the exact layout in the system prompt, add a short example, use low temperature, and lint the output.

Q4: Is Markdown output safe to render directly?
A4: No. Output can contain HTML, tracking images or `javascript:` links, especially after prompt injection. Sanitize with an allow-list renderer and avoid auto-loading remote images.

Q5 (Hard): How would you stream Markdown to a UI without flicker from half-finished tables or code fences?
A5: Buffer on the server or client at block boundaries (blank lines). Keep a state machine that knows when a fence or table is open, render completed blocks immediately, and show the open block as plain text until it closes. Use an incremental Markdown renderer (e.g. react-markdown with memoised blocks) so the DOM updates only for the changed block.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Output is read by people (reports, chat, docs)
- You need tables, lists or headings for scanning
- You show code samples

❌ Avoid when:
- Another program parses the output (use JSON)
- The UI is voice or plain SMS (symbols get read aloud or shown raw)
- Token cost is extremely tight (symbols add tokens)

---

## 📊 Visual Diagram
```
 System prompt: "Use ## sections, bullets, table"
                    |
                    v
              +-----------+
              |    LLM    |
              +-----------+
                    |
                    v
   ## Classification        raw Markdown text
   8518.30
   ## Duty Rates
   | Country | Rate |
                    |
        lint + strip HTML + sanitize
                    |
                    v
          Markdown renderer (UI)
                    |
                    v
            Pretty report for user
```

---

## 💰 Cost Impact
- Markdown symbols and table pipes add roughly 10-20% output tokens versus plain prose.
- Long templates in the system prompt add input tokens each call.

Optimisation: ask for concise sections ("max 3 bullets"), cap `max_tokens`, cache the fixed system prompt (prompt caching), use a cheaper model for formatting-only work, and avoid tables when a list is enough.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Markdown | Light text markup for formatting | Formatting के लिए हल्की markup भाषा |
| Template | Fixed layout shown in the prompt | Prompt में दिया fixed layout |
| Sanitize | Remove unsafe HTML/links | असुरक्षित HTML/links हटाना |
| Lint | Automatic layout check | Layout की automatic जाँच |
| Streaming | Sending output piece by piece | Output टुकड़ों में भेजना |
| Renderer | Turns Markdown into UI | Markdown को UI में बदलने वाला |

---

## ⚡ 3-Line Summary
English: Markdown prompting makes answers easy for humans to scan using headings, bullets and tables. Give an exact template, lint the reply, and sanitize before rendering. Use JSON when a program reads the output.
Hindi: Markdown prompting से जवाब headings, bullets और tables के साथ इंसानों के लिए आसान बनता है। Exact template दो, reply lint करो और render से पहले sanitize करो। Program को output पढ़ना हो तो JSON use करो।

---

## ➡️ Next Topic
**065. Negative Prompting** — telling the model what NOT to do (no guessing, no extra text) and why that needs careful wording.
