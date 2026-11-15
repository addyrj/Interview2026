---

# 384. Seaborn Basics
# हिंदी में: Seaborn की बुनियादी बातें (सुंदर statistical charts)

---

## 🔵 Simple Definition (English)
Seaborn is a statistical plotting library built on top of Matplotlib. You give it a pandas DataFrame and column names, and it draws good-looking charts (bar, box, histogram, scatter, heatmap) in one line, aggregating the data for you.

## 🔵 सरल परिभाषा (Hindi)
Seaborn Matplotlib के ऊपर बनी statistical plotting library है। आप इसे pandas DataFrame और column names देते हैं, और यह एक line में सुंदर charts (bar, box, histogram, scatter, heatmap) बना देती है, data का aggregation भी खुद करती है।

---

## 🔴 Problem it Solves
Plain Matplotlib needs many lines for a grouped, colored, labelled chart, and you must aggregate the data yourself first. Default styles look dated. Seaborn understands DataFrames: `sns.barplot(data=df, x="city", y="amount")` groups, averages, adds confidence intervals, and applies a clean theme.

## 🔴 यह क्यों बना? (Hindi)
सादे Matplotlib में group किए हुए, रंगीन, labels वाले chart के लिए कई lines लिखनी पड़ती हैं, और data का aggregation पहले खुद करना पड़ता है। Default style पुराना लगता है। Seaborn DataFrames समझती है: `sns.barplot(data=df, x="city", y="amount")` group करता है, average निकालता है, confidence interval जोड़ता है और साफ theme लगाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Keep data in "tidy" (long) format: one row per observation, one column per variable
Step 2 → Call a plot function with data=df and column names: x=, y=, hue=
Step 3 → Seaborn groups/aggregates rows (mean + confidence interval by default)
Step 4 → It draws using Matplotlib and RETURNS a Matplotlib Axes (axes-level functions)
Step 5 → Figure-level functions (displot, relplot, catplot, pairplot) return a FacetGrid
Step 6 → You customize and save with the normal Matplotlib API: ax.set_title, fig.savefig

DataFrame + names  ->  seaborn (aggregate + style)  ->  Matplotlib Axes  ->  PNG
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Data "tidy" (long) format में रखें: हर observation एक row, हर variable एक column
Step 2 → data=df और column names (x=, y=, hue=) के साथ plot function बुलाएं
Step 3 → Seaborn rows को group/aggregate करती है (default में mean + confidence interval)
Step 4 → यह Matplotlib से draw करती है और Matplotlib का Axes लौटाती है (axes-level functions)
Step 5 → Figure-level functions (displot, relplot, catplot, pairplot) FacetGrid लौटाते हैं
Step 6 → Customize और save normal Matplotlib API से करें: ax.set_title, fig.savefig
```

---

## 🟡 Real World Example
An analyst at a food-delivery company checks if delivery time grows with distance: a scatter plot colored by city (`hue="city"`), a box plot of delivery time per city to spot outliers, and a correlation heatmap of numeric columns before training a model. This exploratory data analysis (EDA) is the daily use of Seaborn.

## 🟡 Real Example Hindi mein
Food-delivery कंपनी का analyst देखता है कि distance बढ़ने पर delivery time बढ़ता है या नहीं: शहर के रंग (`hue="city"`) वाला scatter plot, outliers पकड़ने के लिए हर शहर का box plot, और model train करने से पहले numeric columns का correlation heatmap। यह exploratory data analysis (EDA) Seaborn का रोज का इस्तेमाल है।

---

## 💻 Code Example — Basic
```python
# Basic seaborn (0.13) on a small DataFrame
import matplotlib                                     # backend control
matplotlib.use("Agg")                                 # headless rendering
import matplotlib.pyplot as plt                       # figure/axes creation
import pandas as pd                                   # data
import seaborn as sns                                 # statistical plots

df: pd.DataFrame = pd.DataFrame({                     # tidy data: one row per order
    "city": ["Delhi", "Delhi", "Mumbai", "Mumbai", "Pune", "Pune"],   # category
    "amount": [250, 300, 400, 380, 150, 170],         # order value
    "tip": [10, 12, 30, 25, 5, 8],                    # tip
})
sns.set_theme(style="whitegrid")                      # clean global theme
fig, axes = plt.subplots(1, 3, figsize=(12, 3))       # three plots side by side
sns.barplot(data=df, x="city", y="amount", ax=axes[0])        # mean amount per city
sns.scatterplot(data=df, x="amount", y="tip", hue="city", ax=axes[1])   # colored by city
sns.boxplot(data=df, x="city", y="amount", ax=axes[2])        # spread and outliers
print(type(axes[0]).__name__, len(axes[0].patches))   # Axes, 3 bars
print([t.get_text() for t in axes[0].get_xticklabels()])      # bar labels
corr: pd.DataFrame = df[["amount", "tip"]].corr()     # correlation matrix
print(corr.round(2).values.tolist())                  # numbers
fig2, ax2 = plt.subplots()                            # another figure
sns.heatmap(corr, annot=True, fmt=".2f", cmap="Blues", ax=ax2)   # colored matrix with numbers
print(len(ax2.collections), len(ax2.texts))           # 1 mesh, 4 text labels
plt.close("all")                                      # free memory
print(sns.__version__)                                # library version

# Output:
# Axes 3
# ['Delhi', 'Mumbai', 'Pune']
# [[1.0, 0.94], [0.94, 1.0]]
# 1 4
# 0.13.2          (your version may differ)
```

## 💻 Code Example — Advanced
```python
# Production style: validated EDA image returned as PNG bytes, no pyplot global state
from __future__ import annotations                    # modern hints
import io                                             # in-memory file
import matplotlib                                     # backend
matplotlib.use("Agg")                                 # headless
import pandas as pd                                   # data
import seaborn as sns                                 # plots
from matplotlib.figure import Figure                  # state-free Figure


def eda_png(df: pd.DataFrame, x: str, y: str, hue: str | None = None) -> bytes:
    """Histogram of y + scatter of y vs x, returned as PNG bytes."""
    wanted: tuple[str, ...] = (x, y) + ((hue,) if hue else ())   # required columns
    for col in wanted:                                # validate every column
        if col not in df.columns:                     # missing -> fail early
            raise KeyError(f"column not found: {col}")
    sns.set_theme(style="whitegrid", context="notebook")          # consistent look
    fig: Figure = Figure(figsize=(10, 4))             # not tracked by pyplot
    ax1, ax2 = fig.subplots(1, 2)                     # two axes
    sns.histplot(data=df, x=y, bins=5, kde=False, ax=ax1)         # distribution
    sns.scatterplot(data=df, x=x, y=y, hue=hue, ax=ax2)           # relationship
    ax1.set_title(f"Distribution of {y}")             # left title
    ax2.set_title(f"{y} vs {x}")                      # right title
    buf: io.BytesIO = io.BytesIO()                    # memory buffer
    fig.savefig(buf, format="png", bbox_inches="tight")           # render
    return buf.getvalue()                             # PNG bytes


df: pd.DataFrame = pd.DataFrame({                     # delivery data
    "distance_km": [1, 2, 3, 4, 5, 6, 7, 8],          # distance
    "delivery_min": [12, 15, 21, 24, 30, 31, 38, 41], # time
    "city": ["Delhi", "Pune"] * 4,                    # category
})
png: bytes = eda_png(df, "distance_km", "delivery_min", hue="city")   # build image
print(png[:4] == b"\x89PNG", len(png) > 1000)         # valid PNG
try:                                                  # error demo
    eda_png(df, "nope", "delivery_min")               # unknown column
except KeyError as e:                                 # catch
    print("Error:", e)                                # message

# Output:
# True True
# Error: 'column not found: nope'
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (Seaborn) | JavaScript |
|---------|------------------|-----------|
| Input | DataFrame + column names | array of objects + accessor functions |
| Grouping/mean | automatic | manual (d3.rollup) or library config |
| Theme | `sns.set_theme()` | CSS / chart options |
| Output | static image | interactive SVG/canvas |

```python
# Python way
import seaborn as sns                                      # seaborn
import pandas as pd                                        # data
df = pd.DataFrame({"c": ["a", "a", "b"], "v": [1, 3, 5]})  # tidy data
ax = sns.barplot(data=df, x="c", y="v", errorbar=None)     # groups by c, plots the mean
```
```javascript
// JavaScript way (d3 rollup + manual draw)
const rows = [{c: "a", v: 1}, {c: "a", v: 3}, {c: "b", v: 5}];   // data
const means = d3.rollup(rows, g => d3.mean(g, d => d.v), d => d.c);   // group + mean by hand
// then draw rectangles with scales and axes...
```

Key difference: Seaborn aggregates and styles automatically from column names. In JavaScript you often group data and build scales yourself (or configure a library like Plotly or Vega-Lite).

---

## 🟠 FastAPI Connection
Seaborn is not used inside request logic often, but ML/analytics services expose EDA images: `/reports/delivery.png`. Use `Figure` objects and `BytesIO` (as in the advanced example), run it in a sync `def` endpoint, and cache images because plotting is slow. For frontend dashboards, return JSON and let a JS chart library draw.

```python
# FastAPI example — return the EDA image (pattern; same as the Matplotlib topic, verified there)
import pandas as pd                                        # data
from fastapi import FastAPI, Response                      # FastAPI
# from eda import eda_png                                  # function from the Advanced example

app: FastAPI = FastAPI()                                   # create app
DF: pd.DataFrame = pd.DataFrame({"d": [1, 2, 3], "t": [10, 20, 30]})   # demo data


@app.get("/reports/delivery.png")                          # GET image
def delivery_report() -> Response:                         # sync endpoint
    png: bytes = eda_png(DF, "d", "t")                     # render in memory
    return Response(content=png, media_type="image/png")   # send as PNG
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Passing wide-format data
✅ Correct: reshape to long format with `melt`

```python
import pandas as pd
wide = pd.DataFrame({"day": [1, 2], "delhi": [5, 6], "pune": [3, 4]})
# Wrong: sns.lineplot(data=wide, x="day", y=?)  — no single y column for both cities
# Right
long = wide.melt(id_vars="day", var_name="city", value_name="sales")
print(long.columns.tolist())                          # ['day', 'city', 'sales']  -> use hue="city"
```

❌ Mistake 2: Thinking `displot` returns an Axes
✅ Correct: figure-level functions return a `FacetGrid`; use `histplot` for an Axes

```python
import matplotlib; matplotlib.use("Agg")
import pandas as pd, seaborn as sns
df = pd.DataFrame({"b": [1, 2]})
print(type(sns.displot(data=df, x="b")).__name__)     # FacetGrid  (has .figure, not .set_title)
print(type(sns.histplot(data=df, x="b")).__name__)    # Axes
```

❌ Mistake 3: Forgetting that bars/lines show the MEAN by default
✅ Correct: pass `estimator=` or `errorbar=None` when you need sums or raw values

```python
# Wrong: sns.barplot(data=df, x="city", y="amount")   -> shows mean, with error bars
# Right: sns.barplot(data=df, x="city", y="amount", estimator="sum", errorbar=None)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import matplotlib
matplotlib.use("Agg")
import pandas as pd, seaborn as sns
d = pd.DataFrame({"x": [1, 1, 2, 2], "y": [10, 20, 30, 50]})
ax = sns.lineplot(data=d, x="x", y="y", errorbar=None)
print(ax.lines[0].get_ydata().tolist())
```
Answer: `[15.0, 40.0]`. The data has 4 rows, but the line has only 2 points. `lineplot` groups rows with the same x and plots their mean: (10+20)/2 = 15 and (30+50)/2 = 40. Seaborn aggregates by default, so what you see is not the raw data.

---

## ⚫ Interview Questions + Answers

Q1: What is the relationship between Seaborn and Matplotlib?
A1: Seaborn is a high-level layer over Matplotlib. It returns Matplotlib objects (`Axes` or `FacetGrid` wrapping a `Figure`), so you can customize with normal Matplotlib calls.

Q2: Axes-level vs figure-level functions?
A2: Axes-level (`scatterplot`, `barplot`, `histplot`, `boxplot`, `heatmap`) draw on one `Axes` and accept `ax=`. Figure-level (`relplot`, `displot`, `catplot`, `pairplot`) create their own figure, can facet into rows/columns with `col=`/`row=`, and return a `FacetGrid`.

Q3: What is "tidy data" and why does Seaborn want it?
A3: One row per observation, one column per variable. Seaborn maps columns to x, y, hue, size, so long format works directly; wide format needs `melt`.

Q4: How do you check correlations visually?
A4: `sns.heatmap(df.corr(numeric_only=True), annot=True)`; or `sns.pairplot(df)` for all pairwise scatter plots.

Q5: What does `hue` do?
A5: It splits data by a column and colors each group differently, adding a legend automatically.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Exploratory data analysis on DataFrames
- Distribution, category comparison, correlation plots
- Quick, good-looking static charts

❌ Avoid when:
- You need interactive web charts: use Plotly or a JS library
- You need pixel-perfect custom charts: drop to Matplotlib
- Data has millions of points: aggregate or sample first

---

## 📊 Visual Diagram
```
 sns.barplot(data=df, x="city", y="amount")

 df rows            group by city          mean + error bar
 Delhi 250,300  ->  Delhi  [250,300]  ->   ▇ 275
 Mumbai 400,380 ->  Mumbai [400,380]  ->   ▇ 390
 Pune 150,170   ->  Pune   [150,170]  ->   ▇ 160

 Seaborn (aggregate + theme)  ->  Matplotlib Axes  ->  PNG
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tidy data | One row per observation | हर observation की एक row |
| hue | Color groups by a column | Column से रंग बांटना |
| Axes-level | Draws on one Axes | एक Axes पर draw |
| Figure-level | Makes whole figure (FacetGrid) | पूरा figure बनाने वाला |
| Heatmap | Colored matrix of values | रंगों वाला matrix |
| Box plot | Shows median, quartiles, outliers | Median, quartiles और outliers |

---

## ⚡ 3-Line Summary
English: Seaborn draws statistical charts from tidy DataFrames in one line on top of Matplotlib. Axes-level functions return an `Axes`, figure-level ones return a `FacetGrid`. By default it aggregates to the mean, so check what you are really plotting.
Hindi: Seaborn tidy DataFrames से Matplotlib के ऊपर एक line में statistical charts बनाती है। Axes-level functions `Axes` लौटाते हैं, figure-level `FacetGrid`। यह default में mean निकालती है, इसलिए ध्यान रखें कि असल में क्या plot हो रहा है।

---

## ➡️ Next Topic
**385. Scikit-learn Overview** — the standard ML toolkit: fit, predict, pipelines, train/test split and metrics.
