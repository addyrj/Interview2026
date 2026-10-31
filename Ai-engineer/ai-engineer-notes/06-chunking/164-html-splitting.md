---

# 164. HTML Splitting
# हिंदी में: HTML Splitting (HTML को structure के हिसाब से बाँटना)

---

## 🔵 Simple Definition (English)
HTML splitting means cutting a web page into chunks by its tags (`<h1>`, `<h2>`, `<table>`, `<li>`) instead of by raw character count. Each chunk keeps its heading path (for example "Chapter 85 > Heading 8517") as metadata. The tags tell us where a topic starts and ends, so we should use them.

## 🔵 सरल परिभाषा (Hindi)
HTML splitting में web page को raw character count से नहीं, बल्कि tags (`<h1>`, `<h2>`, `<table>`) के हिसाब से chunks में बाँटा जाता है। हर chunk के साथ उसका heading path (जैसे "Chapter 85 > Heading 8517") metadata में रहता है। Tags बताते हैं कि topic कहाँ शुरू और कहाँ खत्म होता है।

---

## 🔴 Problem it Solves
- A plain character splitter sees `<div class="x"><p>Duty 10%</p>...` as text. It can cut in the middle of a tag or a table row.
- Tags and CSS classes waste tokens and pollute embeddings.
- The heading above a paragraph (for example "Exemptions") is lost, so the chunk "10% duty" has no context.
- Tables break: header row ends up in one chunk, data rows in another.

## 🔴 यह क्यों बना? (Hindi)
- Plain splitter HTML को text समझता है और tag या table row के बीच में काट देता है।
- Tags और CSS classes tokens बर्बाद करते हैं और embedding खराब करते हैं।
- Paragraph के ऊपर वाला heading खो जाता है, तो "10% duty" chunk का कोई context नहीं बचता।
- Table टूट जाती है: header एक chunk में, rows दूसरे में।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Fetch HTML (customs website, e-commerce page, help centre)
Step 2 → Parse with a real parser (BeautifulSoup / html.parser) - never regex
Step 3 → Remove noise: <script>, <style>, <nav>, <footer>, ads
Step 4 → Walk the tree; every <h1>/<h2>/<h3> starts a NEW section
Step 5 → Keep tables whole (convert to markdown/text rows with header repeated)
Step 6 → If a section is still bigger than chunk_size, sub-split it recursively
Step 7 → Attach metadata: {"h1": ..., "h2": ..., "source_url": ...}
Step 8 → Embed chunk text (heading path + body) and store with metadata
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → HTML लाओ (customs site, e-commerce page)
Step 2 → असली parser से parse करो (regex कभी नहीं)
Step 3 → Noise हटाओ: script, style, nav, footer
Step 4 → हर <h1>/<h2>/<h3> एक नया section शुरू करता है
Step 5 → Tables को पूरा रखो (header हर row के साथ)
Step 6 → Section अभी भी बड़ा है तो recursive split करो
Step 7 → Metadata जोड़ो: h1, h2, source_url
Step 8 → Embed करो और metadata के साथ store करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The customs authority publishes the tariff schedule as HTML. Each `<h2>` is a heading like "8517 - Telephone sets" and below it is a `<table>` of sub-codes with duty rates. HTML splitting gives one chunk per heading with the table kept whole and metadata `{"chapter": "85", "heading": "8517"}`. A query "duty on smartphones" can then filter by chapter 85.

**Zomato / Amazon style**: A restaurant page has `<h2>Menu</h2>`, `<h2>Reviews</h2>`, `<h2>Offers</h2>`. Splitting by `<h2>` lets the AI answer "any offers today?" using only the Offers chunk, not the reviews.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs authority tariff schedule HTML में publish करती है। हर `<h2>` एक heading है ("8517 - Telephone sets") और उसके नीचे `<table>` में sub-codes और duty rates हैं। HTML splitting हर heading का एक chunk बनाती है, table पूरी रहती है, और metadata में chapter/heading रहता है।

**Zomato**: Restaurant page में Menu, Reviews, Offers sections हैं। `<h2>` पर split करने से "आज कोई offer है?" का जवाब सिर्फ Offers chunk से मिलता है।

---

## 💻 Code Example — Basic
```python
# Basic HTML splitter using only the Python standard library
from html.parser import HTMLParser  # built-in HTML parser, no install needed

HTML = """
<html><body>
<script>var x = 1;</script>
<h1>Chapter 85</h1>
<h2>8517 Telephone sets</h2>
<p>Smartphones attract 10 percent basic duty.</p>
<h2>8518 Microphones</h2>
<p>Microphones attract 7.5 percent basic duty.</p>
</body></html>
"""  # sample tariff page


class SectionSplitter(HTMLParser):  # subclass the parser to collect sections
    HEADINGS = {"h1", "h2", "h3"}  # tags that start a new section

    def __init__(self) -> None:  # constructor
        super().__init__()  # init the base parser
        self.sections: list[dict] = []  # finished sections
        self._current: dict | None = None  # section being built
        self._in_heading: bool = False  # are we inside a heading tag?
        self._skip: bool = False  # are we inside script/style?

    def handle_starttag(self, tag: str, attrs: list) -> None:  # on <tag>
        if tag in ("script", "style"):  # noise tags
            self._skip = True  # start skipping text
        elif tag in self.HEADINGS:  # a heading begins
            self._current = {"heading": "", "body": []}  # open new section
            self.sections.append(self._current)  # register it
            self._in_heading = True  # next text is the heading

    def handle_endtag(self, tag: str) -> None:  # on </tag>
        if tag in ("script", "style"):  # noise ended
            self._skip = False  # stop skipping
        elif tag in self.HEADINGS:  # heading ended
            self._in_heading = False  # body text follows

    def handle_data(self, data: str) -> None:  # on text
        text = data.strip()  # trim whitespace
        if not text or self._skip or self._current is None:  # ignore empty/noise
            return  # nothing to do
        if self._in_heading:  # heading text
            self._current["heading"] += text  # append to heading
        else:  # body text
            self._current["body"].append(text)  # append to body


parser = SectionSplitter()  # create the parser
parser.feed(HTML)  # parse the page
for sec in parser.sections:  # show every chunk
    print(sec["heading"], "->", " ".join(sec["body"]))  # heading and body
# Expected: 3 sections (Chapter 85 has an empty body, then 8517, 8518)
```

## 💻 Code Example — Advanced
```python
# Production: heading-path metadata, table-safe, size fallback, async wrapper
from __future__ import annotations  # allow modern type hints everywhere

import asyncio  # for the async version
import logging  # for error logging
from dataclasses import dataclass, field  # light data containers
from html.parser import HTMLParser  # stdlib parser

logger = logging.getLogger(__name__)  # module logger


@dataclass
class HtmlChunk:  # one output chunk
    text: str  # chunk text
    metadata: dict[str, str] = field(default_factory=dict)  # heading path etc.


class _Walker(HTMLParser):  # collects (heading_level, heading, text) blocks
    def __init__(self) -> None:  # constructor
        super().__init__()  # init base
        self.blocks: list[tuple[int, str, list[str]]] = []  # parsed blocks
        self._skip = 0  # depth of skipped tags
        self._heading_level = 0  # 0 means not in heading
        self._buf: list[str] = []  # text buffer
        self._in_td = False  # inside a table cell
        self._row: list[str] = []  # cells of the current row

    def handle_starttag(self, tag: str, attrs: list) -> None:  # open tag
        if tag in {"script", "style", "nav", "footer"}:  # noise
            self._skip += 1  # go deeper into noise
        elif tag in {"h1", "h2", "h3"}:  # heading start
            self._heading_level = int(tag[1])  # remember level
            self._buf = []  # clear buffer
        elif tag in {"td", "th"}:  # table cell
            self._in_td = True  # mark inside cell
            self._buf = []  # fresh buffer

    def handle_endtag(self, tag: str) -> None:  # close tag
        if tag in {"script", "style", "nav", "footer"}:  # leaving noise
            self._skip = max(0, self._skip - 1)  # go up
        elif tag in {"h1", "h2", "h3"}:  # heading end
            title = " ".join(self._buf).strip()  # heading text
            self.blocks.append((self._heading_level, title, []))  # new block
            self._heading_level = 0  # leave heading
        elif tag in {"td", "th"}:  # cell end
            self._row.append(" ".join(self._buf).strip())  # save cell
            self._in_td = False  # leave cell
        elif tag == "tr" and self._row and self.blocks:  # row end
            self.blocks[-1][2].append(" | ".join(self._row))  # keep row whole
            self._row = []  # reset row

    def handle_data(self, data: str) -> None:  # text node
        text = data.strip()  # trim
        if not text or self._skip:  # skip empty/noise
            return  # done
        if self._heading_level or self._in_td:  # heading/cell text
            self._buf.append(text)  # buffer it
        elif self.blocks:  # paragraph text
            self.blocks[-1][2].append(text)  # add to latest block


def split_html(html: str, source: str, max_chars: int = 1200) -> list[HtmlChunk]:
    """Split HTML by headings, keep heading path, sub-split oversize blocks."""
    if not html.strip():  # validate input
        raise ValueError("html is empty")  # fail loudly
    walker = _Walker()  # create walker
    try:  # parsing can fail on broken markup
        walker.feed(html)  # parse
    except Exception as exc:  # broad catch to log context
        logger.exception("HTML parse failed for %s", source)  # log
        raise RuntimeError(f"cannot parse {source}") from exc  # re-raise
    path: dict[int, str] = {}  # current heading per level
    chunks: list[HtmlChunk] = []  # output list
    for level, title, lines in walker.blocks:  # each section
        path[level] = title  # update this level
        for deeper in [k for k in path if k > level]:  # drop deeper headings
            del path[deeper]  # they are stale now
        crumb = " > ".join(path[k] for k in sorted(path))  # "H1 > H2"
        body = "\n".join(lines)  # section body
        # sub-split by lines only (never inside a table row)
        piece, size = [], 0  # running piece
        for line in body.splitlines() or [""]:  # iterate lines
            if size + len(line) > max_chars and piece:  # too big
                chunks.append(HtmlChunk(f"{crumb}\n" + "\n".join(piece),
                                        {"path": crumb, "source": source}))  # emit
                piece, size = [], 0  # reset
            piece.append(line)  # add line
            size += len(line)  # track size
        chunks.append(HtmlChunk(f"{crumb}\n" + "\n".join(piece),
                                {"path": crumb, "source": source}))  # last piece
    return chunks  # done


async def split_html_async(html: str, source: str) -> list[HtmlChunk]:
    """Async wrapper: parsing is CPU-bound, so run it in a worker thread."""
    return await asyncio.to_thread(split_html, html, source)  # non-blocking


if __name__ == "__main__":  # demo
    page = ("<h1>Chapter 85</h1><h2>8517 Phones</h2>"
            "<table><tr><th>Code</th><th>Duty</th></tr>"
            "<tr><td>85171300</td><td>10%</td></tr></table>")  # tiny page
    for c in asyncio.run(split_html_async(page, "demo")):  # run async
        print(c.metadata, repr(c.text))  # show chunk
```

---

## 🟠 FastAPI Integration
Expose the splitter as an ingestion endpoint. The crawler (or an admin UI) posts HTML; the API returns chunks that a background job embeds. Parsing runs in a thread so the event loop stays free.

```python
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel, Field  # request validation (pydantic v2)

app = FastAPI()  # create app


class IngestRequest(BaseModel):  # request body
    html: str = Field(min_length=1, max_length=2_000_000)  # cap size
    source: str  # url or file name


@app.post("/ingest/html")  # route
async def ingest_html(req: IngestRequest) -> dict:  # async handler
    try:  # guard parsing
        chunks = await split_html_async(req.html, req.source)  # split off-loop
    except ValueError as exc:  # bad input
        raise HTTPException(status_code=422, detail=str(exc))  # client error
    except RuntimeError as exc:  # parser failure
        raise HTTPException(status_code=400, detail=str(exc))  # bad markup
    return {"count": len(chunks),  # number of chunks
            "chunks": [{"text": c.text, "metadata": c.metadata} for c in chunks]}  # payload
```

---

## 🔗 LangChain / LangGraph Connection
`langchain-text-splitters` ships `HTMLHeaderTextSplitter` (splits on header tags, writes header names to metadata) and `HTMLSectionSplitter`. Chain it with `RecursiveCharacterTextSplitter` to cap size.

```python
from langchain_text_splitters import HTMLHeaderTextSplitter, RecursiveCharacterTextSplitter  # splitters

headers = [("h1", "chapter"), ("h2", "heading")]  # tag -> metadata key
html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers)  # header-aware
docs = html_splitter.split_text("<h1>Ch 85</h1><h2>8517</h2><p>Duty 10%</p>")  # Documents
final = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80).split_documents(docs)  # size cap
# In LangGraph: make this a "chunk" node between a "fetch_html" node and an "embed" node.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Parsing HTML with regex or stripping tags blindly
✅ Correct: Use a real parser and keep the heading structure.

```python
import re  # regex module

# Wrong - removes tags but also destroys headings and table structure
flat = re.sub(r"<[^>]+>", " ", "<h2>8517</h2><td>10%</td>")  # "  8517   10%  "

# Right - parse, keep heading as metadata, keep rows whole
chunks = split_html("<h1>Ch</h1><h2>8517</h2><table><tr><td>10%</td></tr></table>", "x")  # structured
```

❌ Mistake 2: Splitting a table across chunks
✅ Correct: Treat a table as one unit (or repeat the header row in every sub-chunk).

❌ Mistake 3: Forgetting to drop nav/footer/cookie banners, so every chunk matches "Accept cookies".
✅ Correct: Remove boilerplate before splitting.

---

## 🧠 Tricky Interview Question
**Q**: "Your HTML splitter gives perfect chunks in testing, but retrieval quality drops after a site redesign. Nothing in your code changed. Why, and how do you make it robust?"

**Answer**: The redesign changed tags (headings became `<div class="title">`), so the splitter found no `<h2>` and produced one giant section, then the size fallback cut it blindly. Make it robust by (1) detecting "no headings found" and alerting, (2) supporting CSS-selector-based heading rules per site, (3) adding a regression test with saved HTML snapshots, (4) monitoring average chunk size and chunks-per-page as health metrics.

---

## ⚫ Interview Questions + Answers

Q1: Why not split HTML with a plain character splitter?
A1: It can cut inside tags or tables, wastes tokens on markup, and loses the heading context. Structure-aware splitting keeps each topic together.

Q2: What metadata should an HTML chunk carry?
A2: Heading path (h1 > h2), source URL, page title, crawl date, and optionally the CSS section id. This enables filtering and citations.

Q3: How do you handle tables?
A3: Keep a table as one unit if it fits; otherwise split by rows and repeat the header row in each chunk, or convert rows to sentences ("HS 85171300: duty 10%").

Q4: `HTMLHeaderTextSplitter` vs `RecursiveCharacterTextSplitter` - when use which?
A4: Header splitter follows document structure and adds header metadata but does not enforce a size limit. Recursive splitter enforces size but ignores structure. Use header splitter first, then recursive to cap size.

Q5: (Hard) How would you ingest 1 million changing HTML pages cheaply?
A5: Hash each page's cleaned text; re-chunk and re-embed only if the hash changed. Store chunk ids as `hash(source + heading path + chunk text)` so unchanged chunks are never re-embedded. Run parsing in worker processes, batch embedding calls, and delete vectors of removed pages.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Source is web pages, help-centre articles, HTML exports of tariffs or manuals
- Headings carry meaning (sections, chapters)
- Tables must stay intact

❌ Avoid when:
- Source is a scanned PDF image (no HTML exists)
- HTML is a JavaScript-rendered shell (render first, then split)
- Content is a flat text with no structure (use recursive splitter)

---

## 📊 Visual Diagram
```
<h1>Chapter 85</h1>
   <h2>8517 Phones</h2>   ──►  Chunk A  {path: "Chapter 85 > 8517"}
      <p>...</p>                 text + table rows (kept whole)
      <table>...</table>
   <h2>8518 Microphones</h2> ──► Chunk B  {path: "Chapter 85 > 8518"}
      <p>...</p>
 
 noise (<script> <nav> <footer>) ──► dropped before splitting
```

---

## 💰 Cost Impact
- Removing tags and boilerplate typically cuts embedding tokens by 30-60% versus embedding raw HTML.
- Heading path adds about 5-15 tokens per chunk but raises retrieval accuracy (fewer re-asks, fewer retries).
- Re-embed only changed pages (content hash) - saves most of the ongoing embedding cost.
- Example: 100K pages x 800 tokens = 80M tokens; at $0.02 per 1M tokens (small embedding model) = about $1.60 per full crawl. Raw HTML at 3x tokens would be about $4.80.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DOM | Tree form of an HTML page | HTML का tree structure |
| Heading path | Chain of parent headings | Parent headings की श्रृंखला |
| Boilerplate | Nav, footer, ads | बेकार repeated content |
| Section chunk | Chunk = one heading section | एक heading का chunk |
| HTMLHeaderTextSplitter | LangChain header splitter | Header आधारित splitter |
| Content hash | Fingerprint of text | Text का fingerprint |

---

## ⚡ 3-Line Summary
English: HTML splitting cuts pages by heading tags, not by character count. It keeps tables whole and stores the heading path as metadata. Remove boilerplate first and sub-split only oversize sections.
Hindi: HTML splitting page को heading tags से काटती है, character count से नहीं। Tables पूरी रहती हैं और heading path metadata में जाता है। पहले boilerplate हटाओ, फिर सिर्फ बड़े sections को sub-split करो।

---

## ➡️ Next Topic
**165. PDF Chunking** - PDFs have no tags, so layout, pages and scanned text need different tricks.
