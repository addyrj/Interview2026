---

# Q220. Stream Large Data
# Category: Async Challenges
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Process a huge dataset without loading it all into memory. Use an async generator and a `ReadableStream` to read data chunk by chunk, count lines and sum numbers as they arrive.

```javascript
for await (const chunk of stream) process(chunk); // memory stays small
```

---

## 💡 Quick Concept (2 lines only)
Streams deliver data in small chunks; `for await...of` consumes them one at a time, so memory use stays constant no matter the total size.
हिंदी: Stream data को छोटे chunks में देता है, इसलिए पूरा data memory में लोड नहीं करना पड़ता।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: producer = async generator that yields chunks (fake large source)
// Step 2: wrap it in a ReadableStream (like fetch().body)
// Step 3: consume with for await, handling lines that span chunk borders

async function* produce(totalLines, chunkSize) {
  let text = '';                                      // build the full text lazily below
  for (let n = 1; n <= totalLines; n++) text += `${n}\n`; // one number per line
  for (let i = 0; i < text.length; i += chunkSize) {  // cut into fixed-size pieces
    await new Promise(r => setTimeout(r, 1));         // simulate network delay
    yield text.slice(i, i + chunkSize);               // chunk may cut a line in half!
  }
}

function toStream(asyncIterable) {
  const iterator = asyncIterable[Symbol.asyncIterator](); // get iterator
  return new ReadableStream({
    async pull(controller) {                          // called when consumer wants more
      const { value, done } = await iterator.next();  // next chunk
      if (done) controller.close();                   // no more data
      else controller.enqueue(value);                 // push chunk downstream
    }
  });
}

async function summarize(stream) {
  let leftover = '';                                  // partial line carried across chunks
  let lines = 0, sum = 0, chunks = 0;                 // running totals
  const handle = line => {                            // process one complete line
    if (line === '') return;                          // skip blanks
    lines++; sum += Number(line);                     // update totals
  };
  for await (const chunk of stream) {                 // consume incrementally
    chunks++;
    const parts = (leftover + chunk).split('\n');     // join leftover + split lines
    leftover = parts.pop();                           // last part may be incomplete
    parts.forEach(handle);                            // handle complete lines
  }
  handle(leftover);                                   // flush the final partial line
  return { lines, sum, chunks };
}

// ============================================
// TEST CASES
// ============================================

(async () => {
  const stream = toStream(produce(1000, 100));       // 1000 lines in 100-char chunks
  const result = await summarize(stream);
  console.log(result.lines, result.sum);              // Expected: 1000 500500
  console.log(result.chunks > 1);                     // Expected: true (streamed, not one blob)

  const small = await summarize(toStream(produce(5, 3)));
  console.log(small.lines, small.sum);                // Expected: 5 15
})();
```

---

## 🔍 Why This Works (3 lines max)
`pull` is called only when the consumer is ready, giving natural backpressure. Carrying `leftover` handles lines split across chunk boundaries, which is the classic streaming bug.
हिंदी: `leftover` अधूरी line को अगले chunk से जोड़ता है, और `pull` से backpressure अपने आप मिलता है।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Node streams: readline over any Readable (e.g. fs.createReadStream('big.txt'))
const readline = require('readline');
const { Readable } = require('stream');

async function countLines(readable) {
  const rl = readline.createInterface({ input: readable }); // splits lines for us
  let n = 0;
  for await (const line of rl) n++;                   // one line at a time
  return n;
}
// countLines(Readable.from(['a\nb\n', 'c\n'])).then(console.log); // 3
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: loads the entire file/response into memory
const data = await (await fetch(url)).text();

// ✅ Correct: stream the body
for await (const chunk of (await fetch(url)).body) { /* process chunk */ }
```

---

## 🎯 Interview Tip (1 line)
Mention backpressure, chunk boundaries, and use cases: large CSV/log processing, video, AI token streaming.

---

## 🔗 Related Questions
→ Q254 (async generator) | Q182 (infinite scroll logic) | Q285 (web workers) | Q219 (abort fetch)
