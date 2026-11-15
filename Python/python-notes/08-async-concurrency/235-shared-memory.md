---

# 235. Shared Memory
# हिंदी में: Shared Memory — Processes के बीच एक ही memory block

---

## 🔵 Simple Definition (English)
Shared memory is a block of RAM that several processes can read and write at the same time, with no copying. Python offers `multiprocessing.Value` and `Array` for simple C types, and `multiprocessing.shared_memory.SharedMemory` (3.8+) for raw bytes you can view as numpy arrays, structs or memoryviews.

## 🔵 सरल परिभाषा (Hindi)
Shared memory RAM का एक block है जिसे कई processes एक ही समय में बिना copy किए पढ़-लिख सकते हैं। Python में सरल C types के लिए `multiprocessing.Value` और `Array` हैं, और raw bytes के लिए `multiprocessing.shared_memory.SharedMemory` (3.8+) है, जिसे आप numpy array, struct या memoryview की तरह इस्तेमाल कर सकते हैं।

---

## 🔴 Problem it Solves
Queues and pipes copy data by pickling it. For a 500 MB image batch or a big numpy matrix, copying to each of 8 workers costs time and 8x memory. Shared memory lets every worker look at the same bytes: zero copy, near-instant "send", and one copy of the data in RAM.

## 🔴 यह क्यों बना? (Hindi)
Queue और pipe data को pickle करके copy करते हैं। 500 MB की image batch या बड़े numpy matrix को 8 workers में copy करने में समय और 8 गुना memory लगती है। Shared memory में हर worker उन्हीं bytes को देखता है: zero copy, "भेजना" लगभग तुरंत, और RAM में data की सिर्फ एक copy।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Creator calls SharedMemory(create=True, size=N): OS reserves N bytes
         and gives the block a NAME (e.g. "psm_8f3a1c")
Step 2 → Creator writes into shm.buf (a memoryview over the block)
Step 3 → Other processes call SharedMemory(name="psm_8f3a1c") to attach
Step 4 → All see the same bytes. Python does NOT lock anything for you
Step 5 → Each process calls close() when done (detach from its own view)
Step 6 → Exactly ONE process calls unlink() to free the block, else it leaks

Value("i", 0)     -> one shared C int  (has a built-in lock: .get_lock())
Array("d", [..])  -> shared C array of doubles
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Creator SharedMemory(create=True, size=N) बुलाता है: OS N bytes reserve
         करता है और block को एक NAME देता है (जैसे "psm_8f3a1c")
Step 2 → Creator shm.buf (block पर memoryview) में लिखता है
Step 3 → दूसरे processes SharedMemory(name="psm_8f3a1c") से attach होते हैं
Step 4 → सब वही bytes देखते हैं। Python आपके लिए कोई lock नहीं लगाता
Step 5 → काम खत्म होने पर हर process close() करता है (अपना view हटाता है)
Step 6 → ठीक एक process unlink() करता है block free करने के लिए, वरना leak होता है
```

---

## 🟡 Real World Example
An AI inference service loads a 2 GB embedding matrix once into shared memory; eight worker processes do similarity search on it without eight copies (saves 14 GB of RAM). A video-analytics product writes decoded frames into a shared ring buffer and detector processes read them. A game server shares a read-only world map between simulation workers. A counter of "requests handled" shared by workers uses `Value`.

## 🟡 Real Example Hindi mein
AI inference service 2 GB का embedding matrix एक बार shared memory में load करती है; आठ worker processes उस पर similarity search करते हैं, आठ copies के बिना (14 GB RAM बचती है)। Video-analytics product decoded frames को shared ring buffer में लिखता है और detector processes उन्हें पढ़ते हैं। Game server read-only world map को simulation workers में share करता है। Workers का "handled requests" counter `Value` से share होता है।

---

## 💻 Code Example — Basic
```python
# Basic: Value, Array and shared_memory
from multiprocessing import Process, Value, Array, shared_memory   # shared tools


def bump(counter, arr) -> None:                             # child function
    for _ in range(1000):                                   # many increments
        with counter.get_lock():                            # lock makes += safe
            counter.value += 1                              # shared int
    arr[0] = 99                                             # write into shared array


if __name__ == "__main__":
    counter = Value("i", 0)                                 # shared C int, starts at 0
    arr = Array("d", [1.0, 2.0, 3.0])                       # shared array of doubles
    ps = [Process(target=bump, args=(counter, arr)) for _ in range(4)]   # 4 children
    for p in ps: p.start()                                  # start all
    for p in ps: p.join()                                   # wait all
    print(counter.value, arr[:])                            # 4000 [99.0, 2.0, 3.0]

    shm = shared_memory.SharedMemory(create=True, size=8)   # raw 8-byte block with a name
    shm.buf[0:3] = bytes([1, 2, 3])                         # write bytes
    other = shared_memory.SharedMemory(name=shm.name)       # attach by name (like another process)
    print(bytes(other.buf[0:3]))                            # b'\x01\x02\x03'
    other.close()                                           # detach
    shm.close()                                             # detach creator
    shm.unlink()                                            # free the block (do this ONCE)

# Output:
# 4000 [99.0, 2.0, 3.0]
# b'\x01\x02\x03'
```

## 💻 Code Example — Advanced
```python
# Production style: share a big array via SharedMemory with cleanup (no numpy needed)
from multiprocessing import Process, Queue, shared_memory   # tools
from multiprocessing.shared_memory import SharedMemory      # type
import struct                                               # pack numbers into bytes

N = 1000                                                    # number of doubles


def child(name: str, start: int, end: int, out: "Queue[float]") -> None:
    shm: SharedMemory = SharedMemory(name=name)             # attach to the existing block
    try:                                                    # always close in finally
        vals = struct.unpack_from(f"{end - start}d", shm.buf, start * 8)   # read my slice from the block
        out.put(sum(vals))                                  # send partial sum back
    finally:
        shm.close()                                         # detach (does NOT delete)


def main() -> None:
    shm: SharedMemory = SharedMemory(create=True, size=N * 8)   # 8 bytes per double
    try:                                                    # make sure unlink runs
        struct.pack_into(f"{N}d", shm.buf, 0, *[float(i) for i in range(N)])   # fill 0..999
        out: "Queue[float]" = Queue()                       # results queue
        ps = [Process(target=child, args=(shm.name, i * 250, (i + 1) * 250, out)) for i in range(4)]
        for p in ps: p.start()                              # 4 workers read 4 slices
        total: float = sum(out.get(timeout=10) for _ in ps)   # combine partial sums
        for p in ps: p.join()                               # wait
        print("total:", total)                              # 499500.0
    finally:
        shm.close()                                         # detach
        shm.unlink()                                        # delete the block, avoids leak


if __name__ == "__main__":
    main()

# Output (verified on Python 3.13):
# total: 499500.0
```
With numpy the same idea is one line: `np.ndarray((N,), dtype=np.float64, buffer=shm.buf)` gives an array view without copying (numpy not run here).

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript / Node.js |
|---------|--------|---------------------|
| Shared raw memory | `SharedMemory`, `Value`, `Array` | `SharedArrayBuffer` |
| Typed view | `memoryview` / numpy | `Int32Array`, `Float64Array` |
| Atomic ops | `Value.get_lock()` | `Atomics.add`, `Atomics.wait` |
| Between | processes | worker threads |
| Cleanup | `close()` + `unlink()` | garbage collected |

```python
# Python way — shared counter with a lock
from multiprocessing import Value                       # shared int

counter = Value("i", 0)                                  # create
with counter.get_lock():                                 # protect the read-modify-write
    counter.value += 1                                   # safe increment
print(counter.value)                                     # 1
```
```javascript
// JavaScript way — SharedArrayBuffer + Atomics
const sab = new SharedArrayBuffer(4);                    // 4 shared bytes
const view = new Int32Array(sab);                        // typed view
Atomics.add(view, 0, 1);                                 // atomic increment, no lock object needed
console.log(Atomics.load(view, 0));                      // 1
```

Key difference: JS uses it between worker threads and gives you `Atomics`; Python shares between processes and you must use locks yourself. Python also needs manual `unlink()` because the block lives in the OS, not in garbage collection.

---

## 🟠 FastAPI Connection
In an ML API, a startup script loads the model weights or a big lookup table into shared memory once, and each uvicorn worker process attaches by name instead of loading its own copy. Run on 3.13: a reader process attached by name sees the bytes written by the parent.

```python
# FastAPI example — workers attach to a table created by a loader
from multiprocessing import shared_memory                 # shared block
from fastapi import FastAPI                               # FastAPI

app: FastAPI = FastAPI()                                  # create app
SHM_NAME: str = "prices_table"                            # agreed name between loader and workers


@app.get("/price/{idx}")                                  # GET /price/3
def price(idx: int) -> dict[str, int]:
    shm = shared_memory.SharedMemory(name=SHM_NAME)       # attach (loader created it earlier)
    try:                                                  # always close our view
        return {"price": shm.buf[idx]}                    # read one byte from shared memory
    finally:
        shm.close()                                       # detach, never unlink here
```
(Pattern only; the loader process owns `create=True` and calls `unlink()` at shutdown. The attach-by-name mechanic was verified separately with a parent and a child process, which read back the text `hello`.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `unlink()` (memory leak) or calling it from every process
✅ Correct: every process `close()`s; only the owner `unlink()`s once

```python
from multiprocessing import shared_memory
shm = shared_memory.SharedMemory(create=True, size=16)
# Wrong — only close(): the block stays in the OS until reboot / resource tracker cleans it
shm.close()
# Right — owner also unlinks
shm2 = shared_memory.SharedMemory(create=True, size=16)
shm2.close(); shm2.unlink()
shm.unlink()      # (cleaning the first one so this example leaves nothing behind)
```

❌ Mistake 2: `counter.value += 1` without a lock
✅ Correct: `with counter.get_lock(): counter.value += 1` (the `+=` is read, add, write: three steps, so two processes can overwrite each other)

```python
# Wrong — updates get lost, final value is below 4000 on a busy machine
# counter.value += 1
# Right
# with counter.get_lock(): counter.value += 1
```

❌ Mistake 3: Keeping a `memoryview` / numpy view alive and then closing
✅ Correct: delete views before `shm.close()`, otherwise `BufferError: cannot close exported pointers exist`

```python
# Wrong order
# view = shm.buf[:4]; shm.close()      # BufferError
# Right
# view = shm.buf[:4]; ...; view.release(); shm.close()
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from multiprocessing import Process, Value
total = 0
def child(v) -> None:
    global total
    total = 5
    v.value = 5
if __name__ == "__main__":
    v = Value("i", 0)
    p = Process(target=child, args=(v,)); p.start(); p.join()
    print(total, v.value)
```
Answer: `0 5` (verified on 3.13). The child changed its OWN copy of the global `total`; processes have separate memory, so the parent still sees `0`. `Value` lives in shared memory, so the parent sees `5`. This is the one-line explanation of why shared memory exists. (With `fork` the child starts with a copy of memory, with `spawn` it re-imports the module; either way the global is not shared.)

---

## ⚫ Interview Questions + Answers

Q1: How is `SharedMemory` different from sending data through a Queue?
A1: A Queue pickles and copies the data for each receiver. `SharedMemory` maps the same bytes into every process: no copy, no pickling. It is much faster for large data, but you must handle locking and cleanup yourself.

Q2: Why do we need a lock with `Value`?
A2: `counter.value += 1` is not atomic: read, add, write. Two processes can read the same old value and both write old+1, losing one update. `Value(..., lock=True)` (default) gives `get_lock()` which you wrap around the update.

Q3: `close()` vs `unlink()`?
A3: `close()` detaches the calling process from the block; every user must call it. `unlink()` asks the OS to delete the block once nobody needs it; call it once, from the owner. After unlink, existing attachments still work until closed, but new attaches by name fail. On POSIX, Python's resource tracker may warn about leaked blocks if you forget.

Q4: Can you share a Python list or dict with shared memory?
A4: Not directly: only raw bytes and C types. `multiprocessing.shared_memory.ShareableList` shares a fixed-size list of simple values (int, float, str, bytes, bool, None). For arbitrary objects use `multiprocessing.Manager()` (slower, goes through a server process).

Q5: Does a shared numpy array need a lock?
A5: If workers write to different slices, no. If two workers write the same element, or read while another writes it, yes: you need your own `Lock`, or design work so each worker owns its slice.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Large read-mostly data (arrays, images, model weights) is used by many processes
- You want to avoid pickling and an N-times memory cost
- Simple shared counters or flags (`Value`, `Array`)
- Each worker writes to its own slice of one big buffer

❌ Avoid when:
- Data is small; a Queue is simpler
- You need to share arbitrary Python objects; use `Manager` or a database
- You cannot guarantee cleanup (crashing scripts can leave blocks behind)
- The processes live on different machines; use Redis or a network protocol

---

## 📊 Visual Diagram
```
        process A              process B              process C
        +--------+             +--------+             +--------+
        | own    |             | own    |             | own    |
        | memory |             | memory |             | memory |
        +---+----+             +---+----+             +---+----+
            |  shm.buf               | shm.buf              | shm.buf
            +-----------+------------+----------------------+
                        v
              +----------------------+
              |  shared block "psm_x" |   <- one copy of the bytes in RAM
              |  [ 0 1 2 3 4 5 ... ]  |
              +----------------------+

 lifecycle:  create -> attach -> use -> close (each) -> unlink (once)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Shared memory | One RAM block mapped into many processes | कई processes में map हुआ एक RAM block |
| `SharedMemory` | Named raw-bytes block (3.8+) | नाम वाला raw bytes block |
| `Value` / `Array` | Shared C int / array with a lock | Lock वाला shared C int / array |
| `unlink()` | Delete the block from the OS | Block को OS से हटाना |
| Zero copy | Use data without duplicating it | बिना duplicate किए data इस्तेमाल करना |
| Race condition | Wrong result from unsynchronised access | बिना तालमेल के access से गलत result |

---

## ⚡ 3-Line Summary
English: Shared memory maps one block of RAM into several processes so big data is used without copying. Use `Value` / `Array` for simple numbers and `SharedMemory` for raw bytes or numpy buffers. You own the locking, and you must `close()` everywhere and `unlink()` exactly once.
Hindi: Shared memory RAM का एक block कई processes में map करती है ताकि बड़ा data बिना copy के इस्तेमाल हो। सरल numbers के लिए `Value` / `Array` और raw bytes या numpy buffers के लिए `SharedMemory` लें। Locking आपकी ज़िम्मेदारी है, और हर जगह `close()` तथा ठीक एक बार `unlink()` करना ज़रूरी है।

---

## ➡️ Next Topic
**236. multiprocessing vs threading** — a head-to-head comparison: GIL, memory, startup cost, communication and a simple rule for choosing between them.
