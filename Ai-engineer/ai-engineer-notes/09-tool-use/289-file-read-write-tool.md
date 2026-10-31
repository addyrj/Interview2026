---

# 289. File Read/Write Tool
# हिंदी में: File Read/Write Tool (LLM के लिए सुरक्षित file access)

---

## 🔵 Simple Definition (English)
A file tool lets an LLM read or write files through functions such as `read_file(path)` and `write_file(path, content)`. Your code restricts access to one sandbox folder, limits sizes and file types, and returns text back to the model.

## 🔵 सरल परिभाषा (Hindi)
File tool से LLM `read_file(path)` और `write_file(path, content)` जैसे functions से files पढ़ और लिख सकता है। आपका code access एक sandbox folder तक सीमित रखता है, size और file type की limit लगाता है और text वापस model को देता है।

---

## 🔴 Problem it Solves
Agents need to read uploaded tariff PDFs/CSVs and save reports. A naive tool that accepts any path allows path traversal (`../../etc/passwd`, `~/.ssh/id_rsa`), overwriting code, or reading a 2 GB file into the prompt. Prompt injection inside a document could then ask the agent to exfiltrate secrets.

## 🔴 यह क्यों बना? (Hindi)
Agents को uploaded tariff CSV/PDF पढ़नी होती हैं और reports save करनी होती हैं। कोई भी path मान लेने वाला tool path traversal (`../../etc/passwd`), code overwrite और 2 GB file prompt में पढ़ने जैसे खतरे देता है। Document के अंदर छुपा prompt injection secrets चुरा सकता है। इसलिए **sandboxed file tool** चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose a sandbox root, e.g. /srv/agent_workspace
Step 2 → LLM calls read_file(path="reports/jan.csv")
Step 3 → Code resolves the real path and checks it is INSIDE the sandbox
Step 4 → Check extension allowlist (.txt .csv .json .md) and size limit
Step 5 → Read (truncate to N characters) or write atomically
Step 6 → Return text/status JSON as role="tool"
Step 7 → Tokens = file content returned (big!) -> truncate or summarise
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Sandbox root चुनो, जैसे /srv/agent_workspace
Step 2 → LLM call करता है read_file(path="reports/jan.csv")
Step 3 → Code real path निकालकर check करता है कि sandbox के अंदर है
Step 4 → Extension allowlist (.txt .csv .json .md) और size limit check
Step 5 → पढ़ो (N characters तक truncate) या atomic write करो
Step 6 → Text/status JSON role="tool" में लौटाओ
Step 7 → Tokens = file content (बड़ा!) -> truncate या summarise करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Importers upload `shipment_items.csv`. The agent calls `read_file("uploads/shipment_items.csv")` (first 200 lines), classifies each item, then `write_file("outputs/classified.csv", ...)` so the user can download the result.

**Amazon AI**: Seller assistant reads a product-feed file and writes a corrected feed, never touching other sellers' folders.

## 🟡 Real Example Hindi mein
**Tariff System**: Importer `shipment_items.csv` upload करता है। Agent `read_file` से पहली 200 lines पढ़ता है, हर item classify करता है, फिर `write_file("outputs/classified.csv", ...)` से result save करता है।

**Amazon AI**: Seller assistant product-feed पढ़कर corrected feed लिखता है, दूसरे sellers के folders को कभी नहीं छूता।

---

## 💻 Code Example — Basic
```python
# Sandboxed file tool (stdlib only, runs offline)
import json
import tempfile
from pathlib import Path                    # modern path handling

SANDBOX = Path(tempfile.mkdtemp(prefix="agent_ws_")).resolve()   # demo sandbox folder
ALLOWED_EXT = {".txt", ".csv", ".json", ".md"}                   # file type allowlist
MAX_READ_CHARS = 5_000                                           # cap what goes to the LLM

def _safe_path(rel: str) -> Path:
    """Resolve a relative path and make sure it stays inside SANDBOX."""
    target = (SANDBOX / rel).resolve()      # resolve() removes .. and follows symlinks
    if not target.is_relative_to(SANDBOX):  # Python 3.9+: block path traversal
        raise PermissionError("path escapes sandbox")
    if target.suffix.lower() not in ALLOWED_EXT:
        raise PermissionError(f"extension {target.suffix!r} not allowed")
    return target

def write_file(path: str, content: str) -> str:
    """Tool: write text to a file inside the sandbox."""
    try:
        target = _safe_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)   # create folders if needed
        target.write_text(content, encoding="utf-8")       # write as UTF-8
        return json.dumps({"ok": True, "bytes": len(content.encode())})
    except (PermissionError, OSError) as exc:
        return json.dumps({"ok": False, "error": str(exc)})

def read_file(path: str) -> str:
    """Tool: read text from a file inside the sandbox (truncated)."""
    try:
        text = _safe_path(path).read_text(encoding="utf-8")
        truncated = len(text) > MAX_READ_CHARS
        return json.dumps({"ok": True, "content": text[:MAX_READ_CHARS], "truncated": truncated})
    except FileNotFoundError:
        return json.dumps({"ok": False, "error": "file not found"})
    except (PermissionError, UnicodeDecodeError, OSError) as exc:
        return json.dumps({"ok": False, "error": str(exc)})

print(write_file("outputs/result.csv", "item,hs\nphone,8517.12\n"))   # ok
print(read_file("outputs/result.csv"))                                # content
print(read_file("../../etc/passwd"))                                  # blocked
print(write_file("run.py", "print('hi')"))                            # extension blocked
```

## 💻 Code Example — Advanced
```python
# Production: async file IO, atomic writes, size limits, CSV preview, tool loop
import asyncio, csv, io, json, os, tempfile
from pathlib import Path
from typing import Any
from openai import AsyncOpenAI

client = AsyncOpenAI()
SANDBOX = Path(os.environ.get("AGENT_WORKSPACE", "./workspace")).resolve()
SANDBOX.mkdir(parents=True, exist_ok=True)
MAX_FILE_BYTES = 1_000_000                       # refuse files > 1 MB
ALLOWED_EXT = {".txt", ".csv", ".json", ".md"}

def safe_path(rel: str) -> Path:
    """Path guard, same idea as the basic example."""
    p = (SANDBOX / rel).resolve()
    if not p.is_relative_to(SANDBOX) or p.suffix.lower() not in ALLOWED_EXT:
        raise PermissionError("path or extension not allowed")
    return p

def _read_sync(rel: str, max_chars: int) -> dict[str, Any]:
    p = safe_path(rel)
    if p.stat().st_size > MAX_FILE_BYTES:         # check size BEFORE reading
        raise PermissionError("file too large")
    text = p.read_text(encoding="utf-8")
    return {"content": text[:max_chars], "truncated": len(text) > max_chars}

def _write_sync(rel: str, content: str) -> dict[str, Any]:
    p = safe_path(rel)
    if len(content.encode()) > MAX_FILE_BYTES:
        raise PermissionError("content too large")
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=p.parent)      # write to temp file first
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(content)
    os.replace(tmp, p)                            # atomic rename: no half-written files
    return {"bytes": len(content.encode())}

async def read_file(path: str, max_chars: int = 4000) -> dict[str, Any]:
    """Async wrapper: blocking IO runs in a thread."""
    try:
        return {"ok": True, **await asyncio.to_thread(_read_sync, path, max_chars)}
    except FileNotFoundError:
        return {"ok": False, "error": "file not found"}
    except (PermissionError, UnicodeDecodeError, OSError) as exc:
        return {"ok": False, "error": str(exc)}

async def write_file(path: str, content: str) -> dict[str, Any]:
    try:
        return {"ok": True, **await asyncio.to_thread(_write_sync, path, content)}
    except (PermissionError, OSError) as exc:
        return {"ok": False, "error": str(exc)}

def csv_preview(text: str, rows: int = 5) -> str:
    """Send only the header and a few rows instead of the whole CSV (saves tokens)."""
    reader = csv.reader(io.StringIO(text))
    return "\n".join(",".join(r) for _, r in zip(range(rows + 1), reader))

TOOLS: list[dict[str, Any]] = [
    {"type": "function", "function": {
        "name": "read_file", "description": "Read a text file from the workspace.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "write_file", "description": "Write a text file in the workspace (overwrites).",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
]
DISPATCH = {"read_file": read_file, "write_file": write_file}   # name -> function

async def run_agent(task: str) -> str:
    messages: list[dict[str, Any]] = [{"role": "user", "content": task}]
    for _ in range(5):                            # cap rounds
        resp = await client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=TOOLS)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content or ""
        messages.append(msg)
        for c in msg.tool_calls:
            fn = DISPATCH.get(c.function.name)
            try:
                out = await fn(**json.loads(c.function.arguments)) if fn else {"ok": False, "error": "unknown tool"}
            except (TypeError, json.JSONDecodeError) as exc:
                out = {"ok": False, "error": f"bad arguments: {exc}"}
            messages.append({"role": "tool", "tool_call_id": c.id, "content": json.dumps(out)})
    return "Stopped after 5 rounds."
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, UploadFile, HTTPException
from pathlib import Path

app = FastAPI()

@app.post("/upload")
async def upload(file: UploadFile) -> dict:
    """Save an upload into the sandbox, then the agent can read it."""
    name = Path(file.filename or "upload.csv").name          # strip any directory parts
    data = await file.read()
    if len(data) > 1_000_000:
        raise HTTPException(status_code=413, detail="file too large")
    result = await write_file(f"uploads/{name}", data.decode("utf-8", errors="replace"))
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"saved_as": f"uploads/{name}"}

@app.post("/agent/classify-file")
async def classify(filename: str) -> dict:
    return {"result": await run_agent(f"Read uploads/{Path(filename).name} and classify items.")}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_community.agent_toolkits import FileManagementToolkit   # ready-made file tools

toolkit = FileManagementToolkit(
    root_dir=str(SANDBOX),                                  # sandbox root
    selected_tools=["read_file", "write_file", "list_directory"],
)
file_tools = toolkit.get_tools()                            # list of BaseTool
# agent = create_react_agent(llm, file_tools)
```
`FileManagementToolkit` confines paths to `root_dir`. Still add size limits and an extension allowlist yourself, or wrap with a custom `@tool`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Joining paths without resolving
✅ Correct: `resolve()` then check `is_relative_to`.

```python
# Wrong — "../../etc/passwd" escapes:
open(os.path.join(ROOT, user_path)).read()
# Right:
p = (ROOT / user_path).resolve()
if not p.is_relative_to(ROOT): raise PermissionError
```

❌ Mistake 2: Sending a whole large file to the LLM
✅ Correct: Truncate, preview or chunk.

```python
# Wrong — 3 MB CSV = ~1M tokens:
content = Path(p).read_text()
# Right:
content = Path(p).read_text()[:4000]
```

❌ Mistake 3: Non-atomic writes (crash leaves half a file). Write temp + `os.replace`.

---

## 🧠 Tricky Interview Question

**Q**: "You check `'..' not in path`, but an attacker still reads `/etc/passwd`. How?"

**Answer**: String checks are bypassable: absolute paths (`/etc/passwd` replaces the base in `Path(base) / "/etc/passwd"`), URL-encoded dots, and symlinks inside the sandbox pointing outside. Correct approach: `Path.resolve()` (follows symlinks, normalises) and verify `is_relative_to(sandbox)`, preferably also run the process with OS-level permissions (container, read-only mounts, separate user).

---

## ⚫ Interview Questions + Answers

Q1: Why sandbox file tools? (Easy)
A1: To prevent path traversal and unintended reads or writes of secrets or code, especially under prompt injection.

Q2: Why return truncated content? (Easy)
A2: Files can be huge; tokens cost money and context is limited. Return a preview or chunk and let the model ask for more.

Q3: How do you read big documents with an agent? (Medium)
A3: Provide `read_file(path, offset, limit)` or chunk and index into a vector store; return summaries or the relevant chunks instead of the full text.

Q4: Why atomic writes? (Medium)
A4: Write to a temp file, then `os.replace`. Readers never see partial content and crashes do not corrupt data.

Q5: How to make a file-writing agent safe in production? (Hard)
A5: Run in a container with a dedicated volume, no network, non-root user; allowlist extensions; size and count quotas; per-user directories; never allow executable types; virus-scan uploads; log every operation; optionally require approval for overwrites; treat file contents as untrusted input (indirect prompt injection).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Agent processes uploads (CSV, TXT, JSON)
- Agent must produce downloadable reports
- Workspace is isolated per user

❌ Avoid when:
- Data belongs in a DB or object store (S3) with proper access control
- You cannot sandbox the process
- Files are binary/huge (pre-process into text/chunks first)

---

## 📊 Visual Diagram
```
 LLM ─ read_file("uploads/a.csv") ─►  resolve() ─► inside sandbox? ──no──► error
                                         │ yes
                                         ▼
                              ext allowed? size ok? ──no──► error
                                         │ yes
                                         ▼
                                 read + truncate (4000 chars)
                                         │
 LLM ◄──────── JSON {content, truncated} ┘

 /srv/agent_workspace/   <- the ONLY world the agent can see
   ├─ uploads/
   └─ outputs/
```

---

## 💰 Cost Impact
File content is the dominant token cost: 1 KB of English text is about 250 tokens; a 100 KB CSV is about 25K tokens (about $0.004 per call input on gpt-4o-mini, re-sent each round). Hindi text costs 2-4x more tokens.

Optimize: truncate, send CSV headers and a few rows, chunk and retrieve (RAG), cache parsed content, ask the model to write code that processes the file (the file never enters the prompt), and set `max_tokens` on output.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Sandbox | Restricted folder/environment | सीमित सुरक्षित क्षेत्र |
| Path traversal | Using `..` to escape a folder | `..` से folder से बाहर जाना |
| Symlink | Shortcut file pointing elsewhere | दूसरी जगह इशारा करने वाली file |
| Atomic write | All-or-nothing write | पूरा या बिल्कुल नहीं |
| Truncation | Cutting content to a limit | Limit तक काटना |
| Indirect prompt injection | Malicious instructions inside a document | Document में छुपे निर्देश |

---

## ⚡ 3-Line Summary
English: File tools let agents read inputs and write outputs, but only inside a sandbox. Resolve paths, allowlist extensions, limit sizes and write atomically. File content is the biggest token cost, so truncate or chunk it.
Hindi: File tools से agent inputs पढ़ता और outputs लिखता है, पर सिर्फ़ sandbox में। Path resolve करो, extensions allowlist करो, size limit और atomic write लगाओ। File content सबसे बड़ा token cost है, इसलिए truncate या chunk करो।

---

## ➡️ Next Topic
**290. Tool Error Handling** — what to return when a tool fails so the LLM can recover instead of crashing.
