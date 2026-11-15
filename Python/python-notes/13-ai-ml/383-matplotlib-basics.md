---

# 383. Matplotlib Basics
# हिंदी में: Matplotlib की बुनियादी बातें (Python में charts बनाना)

---

## 🔵 Simple Definition (English)
Matplotlib is the core Python library for drawing charts: line, bar, scatter, histogram and more. You create a `Figure` (the canvas) and one or more `Axes` (the actual plots), draw on the axes, then show or save the image.

## 🔵 सरल परिभाषा (Hindi)
Matplotlib Python की मुख्य library है charts बनाने के लिए: line, bar, scatter, histogram आदि। आप एक `Figure` (canvas) और एक या ज्यादा `Axes` (असली plots) बनाते हैं, axes पर draw करते हैं, फिर image दिखाते या save करते हैं।

---

## 🔴 Problem it Solves
Numbers in a table hide trends. A chart shows a spike, a drop or a comparison in a second. Before Matplotlib, Python had no standard way to plot; people exported data to Excel. Matplotlib gives full control over every element of a figure from code, so reports can be generated automatically.

## 🔴 यह क्यों बना? (Hindi)
Table के numbers में trend छिपा रहता है। Chart एक सेकंड में spike, गिरावट या तुलना दिखा देता है। Matplotlib से पहले Python में plot का कोई standard तरीका नहीं था; लोग data Excel में ले जाते थे। Matplotlib code से figure के हर हिस्से पर पूरा control देता है, इसलिए reports अपने आप बन सकती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → fig, ax = plt.subplots()      creates a Figure and an Axes (object-oriented API)
Step 2 → ax.plot / ax.bar / ax.scatter draws data on that Axes
Step 3 → ax.set_title / set_xlabel / set_ylabel / legend  add labels
Step 4 → fig.savefig("chart.png")      renders to a file (or plt.show() for a window)
Step 5 → plt.close(fig)                frees memory (figures stay alive until closed)
Step 6 → On servers, use the non-GUI backend "Agg" (no window needed)

Figure ──contains──> Axes ──contains──> lines, bars, text, ticks
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → fig, ax = plt.subplots()      Figure और Axes बनाता है (object-oriented API)
Step 2 → ax.plot / ax.bar / ax.scatter उस Axes पर data draw करता है
Step 3 → ax.set_title / set_xlabel / set_ylabel / legend  labels जोड़ते हैं
Step 4 → fig.savefig("chart.png")      file में render करता है (या plt.show() से window)
Step 5 → plt.close(fig)                memory खाली करता है (figure close होने तक जिंदा रहता है)
Step 6 → Servers पर non-GUI backend "Agg" इस्तेमाल करें (window की जरूरत नहीं)
```

---

## 🟡 Real World Example
A Razorpay-style daily report job draws a line chart of transactions per hour and emails the PNG. A FastAPI endpoint `/chart.png` renders revenue by city on demand. A data scientist plots a model's training loss per epoch. A Swiggy ops dashboard exports delivery-time histograms.

## 🟡 Real Example Hindi mein
Razorpay जैसी daily report job हर घंटे के transactions का line chart बनाती है और PNG email करती है। FastAPI endpoint `/chart.png` मांग पर शहर के हिसाब से revenue render करता है। Data scientist model का training loss हर epoch पर plot करता है। Swiggy का ops dashboard delivery-time के histograms export करता है।

---

## 💻 Code Example — Basic
```python
# Basic matplotlib (3.11), headless-safe
import os                                             # for path checks
import matplotlib                                     # to select the backend
matplotlib.use("Agg")                                 # no GUI window, render to files
import matplotlib.pyplot as plt                       # pyplot interface
import numpy as np                                    # numbers for the scatter

OUT: str = "/tmp/mpl_demo"                            # change to any folder you like
os.makedirs(OUT, exist_ok=True)                       # create folder if missing
x: list[int] = [1, 2, 3, 4]                           # days
y: list[int] = [10, 20, 15, 30]                       # sales
fig, ax = plt.subplots()                              # one figure, one axes
ax.plot(x, y, marker="o", label="sales")              # line with dots
ax.set_title("Daily sales")                           # title
ax.set_xlabel("Day")                                  # x label
ax.set_ylabel("Rupees")                               # y label
ax.legend()                                           # show the label box
print(type(fig).__name__, type(ax).__name__)          # what we got
fig.savefig(f"{OUT}/line.png", dpi=100)               # write PNG file
print(os.path.exists(f"{OUT}/line.png"))              # file created?
plt.close(fig)                                        # free the memory
print(plt.get_fignums())                              # no open figures left
fig, axes = plt.subplots(1, 2, figsize=(8, 3))        # one row, two charts
print(axes.shape, fig.get_size_inches().tolist())     # array of 2 axes, size in inches
axes[0].bar(["Delhi", "Pune"], [300, 200])            # bar chart on the left
axes[1].scatter(np.arange(5), np.arange(5) ** 2)      # scatter on the right
plt.close(fig)                                        # close again
print(matplotlib.get_backend())                       # which backend is active

# Output:
# Figure Axes
# True
# []
# (2,) [8.0, 3.0]
# Agg
```

## 💻 Code Example — Advanced
```python
# Production style: render a chart to PNG bytes in memory, thread-safe (no pyplot global state)
from __future__ import annotations                    # modern hints
import io                                             # in-memory buffer
import matplotlib                                     # backend selection
matplotlib.use("Agg")                                 # headless backend
from matplotlib.figure import Figure                  # Figure class, no global state


def revenue_chart(labels: list[str], values: list[float], title: str = "Revenue by city") -> bytes:
    """Return a PNG (as bytes) bar chart."""
    if len(labels) != len(values):                    # validate input
        raise ValueError("labels and values must have the same length")
    fig: Figure = Figure(figsize=(6, 4), dpi=100)     # a figure NOT registered in pyplot
    ax = fig.subplots()                               # a single axes
    bars = ax.bar(labels, values, color="#4c72b0")    # draw the bars
    ax.bar_label(bars, fmt="%.0f")                    # write the value above each bar
    ax.set_title(title)                               # chart title
    ax.set_ylabel("Rupees")                           # y axis label
    ax.grid(axis="y", alpha=0.3)                      # light horizontal grid
    buf: io.BytesIO = io.BytesIO()                    # memory file
    fig.savefig(buf, format="png", bbox_inches="tight")   # render into memory
    return buf.getvalue()                             # raw PNG bytes


png: bytes = revenue_chart(["Delhi", "Mumbai", "Pune"], [300, 420, 250])   # make chart
print(png[:8] == b"\x89PNG\r\n\x1a\n", len(png) > 1000)   # valid PNG header, non-trivial size
try:                                                  # error handling demo
    revenue_chart(["a"], [1, 2])                      # lengths differ
except ValueError as e:                               # catch it
    print("Error:", e)                                # clear message

# Output:
# True True
# Error: labels and values must have the same length
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (Matplotlib) | JavaScript |
|---------|---------------------|-----------|
| Library | matplotlib | Chart.js, D3, Recharts |
| Where it runs | Server / notebook, outputs images | Browser, draws on canvas/SVG |
| Output | PNG, SVG, PDF files | live interactive DOM element |
| Style | imperative calls on `ax` | declarative config object |

```python
# Python way
import matplotlib
matplotlib.use("Agg")                                      # headless
import matplotlib.pyplot as plt                            # pyplot
fig, ax = plt.subplots()                                   # figure + axes
ax.bar(["a", "b"], [3, 5])                                 # draw
fig.savefig("/tmp/x.png")                                  # file output
```
```javascript
// JavaScript way (Chart.js)
new Chart(document.getElementById("c"), {                  // canvas element
  type: "bar",                                             // chart type
  data: { labels: ["a", "b"], datasets: [{ data: [3, 5] }] }   // data as config
});
```

Key difference: Chart.js describes a chart as a config object and draws live in the browser. Matplotlib makes a static image on the server by calling methods on `Axes` objects. For interactive web charts, send JSON to a JS library; use Matplotlib for reports, emails and notebooks.

---

## 🟠 FastAPI Connection
A FastAPI endpoint can return a chart as an image. Use the `Figure` class directly (not `pyplot`) because `pyplot` keeps global state that is not thread-safe, and FastAPI runs sync endpoints in a thread pool. Return `Response(content=png, media_type="image/png")`.

```python
# FastAPI example — GET /chart.png (verified with TestClient: 200 image/png)
from fastapi import FastAPI, Response                      # FastAPI + raw response
# from charts import revenue_chart                         # the function from the Advanced example

app: FastAPI = FastAPI()                                   # create app


@app.get("/chart.png")                                     # image endpoint
def chart() -> Response:                                   # sync def: CPU-bound drawing
    png: bytes = revenue_chart(["a", "b"], [1.0, 2.0])     # render in memory
    return Response(content=png, media_type="image/png")   # browser shows the image

# Test result: status 200, content-type image/png
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Never closing figures (memory leak in long-running servers)
✅ Correct: `plt.close(fig)`, or use the `Figure` class which is not tracked

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
# Wrong
for _ in range(3): plt.figure()                       # 3 figures stay alive
print(len(plt.get_fignums()))                         # 3
# Right
plt.close("all")                                      # free everything
print(len(plt.get_fignums()))                         # 0
```

❌ Mistake 2: `plt.show()` on a server or in CI (blocks or does nothing)
✅ Correct: use the `Agg` backend and `savefig`

```python
# Wrong: plt.show()            # needs a display
# Right: fig.savefig("chart.png")
```

❌ Mistake 3: Mixing the `plt.plot` state machine with `ax` objects
✅ Correct: pick the object-oriented style (`fig, ax = plt.subplots()`) and call methods on `ax`

```python
# Wrong — which axes does this draw on? Whichever is "current".
# plt.plot(x, y)
# Right
# fig, ax = plt.subplots(); ax.plot(x, y)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.plot([1, 2])
plt.plot([3, 4])
print(len(plt.gca().lines), len(plt.get_fignums()))
fig, ax = plt.subplots()
print(len(plt.get_fignums()))
```
Answer: `2 1`, then `2`. Without creating a figure, `plt.plot` makes one implicit figure and axes; the second call draws on the same current axes, so there are 2 lines and 1 figure. `plt.subplots()` creates a second figure, so there are now 2 open figures. This hidden "current figure" state is why the object-oriented API is safer.

---

## ⚫ Interview Questions + Answers

Q1: What are Figure and Axes?
A1: `Figure` is the whole canvas/window. `Axes` is one plot inside it (with x-axis, y-axis, title, data). A figure can have many axes; `plt.subplots(2, 2)` makes four.

Q2: `pyplot` API vs object-oriented API?
A2: `pyplot` (`plt.plot`) tracks a "current" figure and axes in global state, handy for notebooks. The object-oriented API (`ax.plot`) is explicit and recommended for scripts, functions, and servers.

Q3: How do you generate charts on a server without a display?
A3: Use the `Agg` backend (`matplotlib.use("Agg")`) and `savefig` to a file or `BytesIO`. Use the `Figure` class to avoid global state and close figures.

Q4: How do you plot a pandas DataFrame?
A4: `df.plot(kind="bar", ax=ax)` uses Matplotlib under the hood. Pass `ax` to control where it draws.

Q5: Why is Matplotlib not thread-safe?
A5: `pyplot` keeps global state (current figure). Concurrent requests can draw on each other's figures. Use independent `Figure` objects per request or a lock.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need static charts for reports, PDFs, emails, notebooks
- You need full control over every element
- You build ML plots (loss curves, confusion matrices)

❌ Avoid when:
- You need interactive web dashboards: use Plotly, Chart.js, or Recharts
- You want pretty statistical plots in few lines: use Seaborn (it sits on Matplotlib)
- You plot millions of points interactively: use a GPU or WebGL tool

---

## 📊 Visual Diagram
```
Figure (canvas, 8x3 inches)
┌──────────────────────────────────────────┐
│  Axes[0]  (bar)          Axes[1] (scatter)│
│  ┌─────────────┐         ┌─────────────┐ │
│  │ title       │         │ title       │ │
│  │  ▇  ▅       │         │        •    │ │
│  │ Delhi Pune  │         │     •       │ │
│  └─────────────┘         └─────────────┘ │
└──────────────────────────────────────────┘
fig.savefig("x.png")  ->  file
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Figure | The whole canvas | पूरा canvas |
| Axes | One plot area inside a figure | Figure के अंदर एक plot |
| Backend | The renderer (Agg = files only) | Render करने वाला इंजन |
| savefig | Write the chart to a file | Chart को file में लिखना |
| subplots | Make a grid of axes | Axes का grid बनाना |
| legend | Label box for series | Series के नाम का box |

---

## ⚡ 3-Line Summary
English: Matplotlib draws charts with a Figure holding Axes. Use the object-oriented style, the `Agg` backend on servers, and always close figures. For web APIs, render to `BytesIO` with the `Figure` class.
Hindi: Matplotlib में Figure के अंदर Axes पर charts बनते हैं। Object-oriented style, servers पर `Agg` backend इस्तेमाल करें और figures हमेशा close करें। Web APIs के लिए `Figure` class से `BytesIO` में render करें।

---

## ➡️ Next Topic
**384. Seaborn Basics** — statistical plots (histograms, box plots, heatmaps) in one line on top of Matplotlib and pandas.
