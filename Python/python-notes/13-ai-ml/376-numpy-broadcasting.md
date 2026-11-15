---

# 376. NumPy Broadcasting
# हिंदी में: NumPy Broadcasting (अलग shape के arrays पर एक साथ operation)

---

## 🔵 Simple Definition (English)
Broadcasting is the set of rules NumPy uses to do maths between arrays of different shapes. The smaller array is virtually stretched to match the bigger one, without copying data. It lets you write `x - mean` instead of a Python loop.

## 🔵 सरल परिभाषा (Hindi)
Broadcasting वे rules हैं जिनसे NumPy अलग-अलग shape वाले arrays के बीच maths करता है। छोटे array को virtually बड़े के बराबर खींच लिया जाता है, data की copy बनाए बिना। इससे आप loop की जगह सीधे `x - mean` लिख सकते हैं।

---

## 🔴 Problem it Solves
Without broadcasting you must write nested Python loops to subtract a column mean from every row, or manually `np.tile` the small array to full size (wasting memory). Loops are 50-100x slower than vectorised code, and tiled copies use extra RAM. Broadcasting gives short, fast, memory-free code. It is the base of normalisation, distance matrices, softmax and every ML library.

## 🔴 यह क्यों बना? (Hindi)
Broadcasting के बिना हर row से column mean घटाने के लिए nested Python loops लिखने पड़ते, या छोटे array को `np.tile` से पूरा बड़ा बनाना पड़ता (RAM की बर्बादी)। Loops, vectorised code से 50-100 गुना धीमे होते हैं और tile की copies extra memory खाती हैं। Broadcasting छोटा, तेज़ और बिना extra memory वाला code देता है। Normalisation, distance matrix, softmax और हर ML library की नींव यही है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write both shapes, aligned from the RIGHT:   (2,3) and    (3,)
Step 2 → Pad the shorter shape with 1s on the LEFT:    (2,3) and (1,3)
Step 3 → Compare each dimension pair from the right:
         equal -> ok | one of them is 1 -> stretch it | else -> ValueError
Step 4 → Result shape = max of each pair:               (2,3)
Step 5 → NumPy loops in C over the virtual stretch (no real copy of the data)

(3,1) + (3,)  ->  (3,1) + (1,3)  ->  (3,3)   # a full grid
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → दोनों shapes को दाएं (RIGHT) से align करके लिखो:   (2,3) और    (3,)
Step 2 → छोटी shape के बाईं ओर 1 जोड़ो:                    (2,3) और (1,3)
Step 3 → दाएं से हर dimension की जोड़ी देखो:
         बराबर -> ठीक | कोई एक 1 है -> उसे खींच दो | वरना -> ValueError
Step 4 → Result shape = हर जोड़ी का बड़ा मान:                (2,3)
Step 5 → NumPy C में loop चलाता है (data की असली copy नहीं बनती)

(3,1) + (3,)  ->  (3,1) + (1,3)  ->  (3,3)   # पूरा grid
```

---

## 🟡 Real World Example
A Razorpay fraud model standardises every transaction feature: `(X - mean) / std`, where X is (1,000,000 x 20) and mean/std are only (20,). Broadcasting does it in milliseconds. A Swiggy delivery planner builds a 500x500 distance matrix between restaurants using `p[:, None] - p[None, :]`. An AI app converts raw model scores to probabilities with a row-wise softmax.

## 🟡 Real Example Hindi mein
Razorpay का fraud model हर transaction feature को standardise करता है: `(X - mean) / std`, जहां X (10,00,000 x 20) है और mean/std सिर्फ (20,)। Broadcasting यह milliseconds में कर देता है। Swiggy का delivery planner restaurants के बीच 500x500 distance matrix `p[:, None] - p[None, :]` से बनाता है। AI app model के raw scores को row-wise softmax से probabilities में बदलती है।

---

## 💻 Code Example — Basic
```python
# Basic broadcasting examples
import numpy as np                                # import NumPy

a: np.ndarray = np.array([1, 2, 3])               # shape (3,)
print(a + 10)                                     # scalar stretched to every element
m: np.ndarray = np.array([[1, 2, 3],
                          [4, 5, 6]])             # shape (2, 3)
print(m + a)                                      # (2,3) + (3,) -> row copied down
col: np.ndarray = np.array([[10], [20]])          # shape (2, 1)
print(m + col)                                    # (2,3) + (2,1) -> column copied across
print((np.arange(3)[:, None] + np.arange(3)).shape)   # (3,1) + (3,) -> (3,3) grid
print(np.arange(3)[:, None] + np.arange(3))       # the actual grid
try:                                              # incompatible shapes
    np.ones((2, 3)) + np.ones((2,))               # trailing dims 3 vs 2
except ValueError as e:                           # catch it
    print("Error:", e)                            # message from NumPy

# Output:
# [11 12 13]
# [[2 4 6]
#  [5 7 9]]
# [[11 12 13]
#  [24 25 26]]
# (3, 3)
# [[0 1 2]
#  [1 2 3]
#  [2 3 4]]
# Error: operands could not be broadcast together with shapes (2,3) (2,) 
```

## 💻 Code Example — Advanced
```python
# Advanced: normalise features, pairwise distance, softmax without loops
import numpy as np                                # import NumPy


def standardize(x: np.ndarray) -> np.ndarray:
    """Column-wise z-score: (x - mean) / std using broadcasting."""
    mean: np.ndarray = x.mean(axis=0, keepdims=True)   # shape (1, n_features)
    std: np.ndarray = x.std(axis=0, keepdims=True)     # shape (1, n_features)
    if np.any(std == 0):                          # constant column would divide by zero
        raise ValueError("constant feature found")    # clear error
    return (x - mean) / std                       # (n, f) - (1, f) broadcasts


def pairwise_distances(p: np.ndarray) -> np.ndarray:
    """Euclidean distance between all points, no Python loop."""
    diff: np.ndarray = p[:, None, :] - p[None, :, :]   # (n,1,d) - (1,n,d) -> (n,n,d)
    return np.sqrt((diff ** 2).sum(axis=-1))      # sum over d -> (n, n)


def softmax(logits: np.ndarray) -> np.ndarray:
    """Row-wise softmax; subtract the max for numerical stability."""
    shifted: np.ndarray = logits - logits.max(axis=1, keepdims=True)   # (n,c) - (n,1)
    e: np.ndarray = np.exp(shifted)               # exponentiate
    return e / e.sum(axis=1, keepdims=True)       # (n,c) / (n,1)


features = np.array([[170.0, 60.0], [180.0, 80.0], [160.0, 50.0]])   # height, weight
z = standardize(features)                         # normalise
print(np.round(z, 3))                             # rounded z-scores
print(np.round(z.mean(axis=0), 6))                # means ~ 0
pts = np.array([[0.0, 0.0], [3.0, 4.0], [6.0, 8.0]])   # three points
print(pairwise_distances(pts))                    # 3x3 distance matrix
print(np.round(softmax(np.array([[1.0, 2.0, 3.0], [1000.0, 1000.0, 1000.0]])), 3))   # stable
try:                                              # error handling
    standardize(np.array([[1.0, 2.0], [1.0, 3.0]]))   # first column constant
except ValueError as e:                           # catch
    print("Error:", e)                            # message

# Output (rounded values; -0. is numerical noise sign):
# [[ 0.    -0.267]
#  [ 1.225  1.336]
#  [-1.225 -1.069]]
# [ 0. -0.]
# [[ 0.  5. 10.]
#  [ 5.  0.  5.]
#  [10.  5.  0.]]
# [[0.09  0.245 0.665]
#  [0.333 0.333 0.333]]
# Error: constant feature found
```



---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (NumPy) | JavaScript |
|---------|---------------|-----------|
| Add scalar to every item | `a + 10` | `a.map(x => x + 10)` |
| Subtract column mean from a matrix | `X - X.mean(axis=0)` | nested `map` / loops |
| Different-shape maths | automatic broadcasting | none in core JS (TensorFlow.js has it) |
| Speed | C loops | JS loops per element |

```python
# Python way — one line, runs in C
import numpy as np                                # NumPy
X: np.ndarray = np.array([[1.0, 2.0], [3.0, 4.0]])   # 2x2
print(X - X.mean(axis=0))                         # subtract each column's mean
```
```javascript
// JavaScript way — manual loops, no broadcasting in core JS
const X = [[1, 2], [3, 4]];
const mean = [0, 1].map(j => (X[0][j] + X[1][j]) / 2);   // column means by hand
console.log(X.map(row => row.map((v, j) => v - mean[j])));
```

Key difference: in JavaScript you write the loop yourself. In NumPy the rules of broadcasting do the loop in C, and incompatible shapes raise a clear `ValueError` instead of silently giving wrong numbers.

---

## 🟠 FastAPI Connection
FastAPI model-serving endpoints receive a batch of rows and must preprocess them with training-time `mean` and `std`. Those vectors are shape `(features,)` and the batch is `(n, features)`, so broadcasting normalises the whole batch with no loop. Run heavy NumPy work in a plain `def` endpoint (thread pool) so the event loop is not blocked.

```python
# FastAPI: score a batch of feature rows using broadcasting (no Python loops)
import numpy as np                                # NumPy
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # in-process test client
from pydantic import BaseModel                    # request schema

app: FastAPI = FastAPI()                          # create app
WEIGHTS: np.ndarray = np.array([0.5, 0.3, 0.2])   # shape (3,)  one weight per feature
MEAN: np.ndarray = np.array([50.0, 10.0, 5.0])    # training mean, shape (3,)
STD: np.ndarray = np.array([10.0, 2.0, 1.0])      # training std, shape (3,)


class Batch(BaseModel):
    rows: list[list[float]]                       # n rows x 3 features


@app.post("/score")
def score(batch: Batch) -> dict[str, list[float]]:
    x: np.ndarray = np.asarray(batch.rows, dtype=float)   # shape (n, 3)
    z: np.ndarray = (x - MEAN) / STD              # (n,3) with (3,) -> broadcast per row
    s: np.ndarray = z @ WEIGHTS                   # (n,3) @ (3,) -> (n,)
    return {"scores": np.round(s, 3).tolist()}    # JSON-friendly list


client = TestClient(app)                          # call the app without a server
print(client.post("/score", json={"rows": [[60, 12, 6], [50, 10, 5]]}).json())

# Output:
# {'scores': [1.0, 0.0]}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mixing up a row vector and a column vector
✅ Correct: add the axis you mean with `[:, None]` or `reshape`

```python
import numpy as np
a = np.arange(3)                      # shape (3,)
# Wrong — (3,) + (3,) is just element-wise, not a grid
print((a + a).shape)                  # (3,)
# Right — column + row gives the full grid
print((a[:, None] + a).shape)         # (3, 3)
```

❌ Mistake 2: Assuming any two shapes work
✅ Correct: check trailing dimensions first, reshape if needed

```python
import numpy as np
# Wrong — trailing dims 4 vs 3 do not match
try:
    np.ones((3, 4)) + np.ones((3,))
except ValueError as e:
    print(e)                          # operands could not be broadcast together with shapes (3,4) (3,)
# Right — make the (3,) a column: (3,1) stretches across 4 columns
print((np.ones((3, 4)) + np.ones((3,))[:, None]).shape)   # (3, 4)
```

❌ Mistake 3: In-place operators (`+=`) cannot change the shape of the left array
✅ Correct: use `a = a + b` when the result is bigger

```python
import numpy as np
v = np.ones(3)
# Wrong
try:
    v += np.ones((2, 3))              # result (2,3) does not fit into v (3,)
except ValueError as e:
    print(e)                          # non-broadcastable output operand with shape (3,) doesn't match the broadcast shape (2,3)
# Right
v = v + np.ones((2, 3))               # new array, shape (2, 3)
print(v.shape)                        # (2, 3)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import numpy as np
a = np.zeros(3)                  # shape (3,)
b = np.ones((3, 1))              # shape (3, 1)
print((a + b).shape)
print(np.array([1, 2, 3]) + np.array([[1], [2]]))
```
Answer: `(3, 3)` and `[[2 3 4] [3 4 5]]` (printed as two rows). `(3,)` is padded to `(1,3)`, and `(3,1)` is stretched across columns, so the result is a full 3x3 grid, not 3 elements. People expect `(3,)` because they think both are 'length 3'. The second line: shape `(3,)` with `(2,1)` gives `(2,3)`; row 1 adds 1, row 2 adds 2. Verified by running on NumPy 2.5.

---

## ⚫ Interview Questions + Answers

Q1: What are the broadcasting rules?
A1: Align shapes from the right, pad the shorter with 1s on the left. For each dimension the sizes must be equal or one of them must be 1. A size of 1 is stretched. Otherwise NumPy raises `ValueError`.

Q2: Does broadcasting copy data?
A2: No. NumPy uses stride 0 on the stretched axis, so the memory is not duplicated. Only the result array is allocated (unless you use `out=` or in-place ops).

Q3: How do you compute all pairwise distances without loops?
A3: `diff = p[:, None, :] - p[None, :, :]` gives shape (n,n,d); then `np.sqrt((diff**2).sum(-1))`. Memory is O(n²·d), so for huge n use `scipy.spatial.distance.cdist` or chunking.

Q4: Why subtract the max in softmax?
A4: `exp(1000)` overflows to `inf`. Subtracting the row max (`logits - logits.max(axis=1, keepdims=True)`, a broadcast) keeps numbers small and the result is mathematically the same. Needs `keepdims=True` so the shape is (n,1) and broadcasts per row.

Q5: What does `keepdims=True` do and why is it important?
A5: It keeps the reduced axis as size 1 (shape (n,1) instead of (n,)), so the result broadcasts back correctly against the original array. Without it, `x - x.mean(axis=1)` on a (n,f) array fails or gives wrong pairing.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Normalising/scaling features, centring data
- Pairwise distances, outer products, grids
- Applying a per-row or per-column bias or weight
- Any place you would write a nested loop over array elements

❌ Avoid when:
- The expanded intermediate is huge (n x n x d may exhaust RAM) - chunk it
- Shapes only 'accidentally' match and hide a bug - assert shapes in production code
- You need clear intent: use `reshape`/`[:, None]` explicitly instead of relying on luck

---

## 📊 Visual Diagram
```
A shape (2,3)          b shape (3,)  -> treated as (1,3)

 [[1 2 3]       +      [10 20 30]  (virtually repeated for every row)
  [4 5 6]]

 = [[11 22 33]
    [14 25 36]]

Column + row:  (3,1) + (1,3) -> (3,3)

 [[0]      [[0 1 2]      [[0 1 2]
  [1]   +   ... ]     =   [1 2 3]
  [2]]                    [2 3 4]]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Broadcasting | Rules for maths on different shapes | अलग shapes पर maths के rules |
| Shape | Tuple of dimension sizes | Dimensions के sizes का tuple |
| Axis | A dimension index | Dimension का नंबर |
| `keepdims` | Keep reduced axis as size 1 | Reduce होने के बाद भी axis को size 1 रखना |
| `None` / `newaxis` | Insert a size-1 axis | नया size-1 axis जोड़ना |
| Vectorisation | Operating on whole arrays at once | पूरे array पर एक साथ operation |

---

## ⚡ 3-Line Summary
English: Broadcasting lets NumPy combine arrays of different shapes by aligning shapes from the right and stretching size-1 dimensions. It replaces loops with fast C code and no data copy. Use `keepdims=True` and `[:, None]` to control the shape, and expect `ValueError` when dimensions do not match.
Hindi: Broadcasting से NumPy अलग shapes के arrays को दाएं से align करके और size-1 dimensions को खींचकर जोड़ता है। यह loops की जगह तेज़ C code चलाता है और data की copy नहीं बनती। Shape control करने के लिए `keepdims=True` और `[:, None]` इस्तेमाल करें, और dimensions न मिलें तो `ValueError` आता है।

---

## ➡️ Next Topic
**377. Pandas — Complete Guide** — load, clean, filter, group and merge tabular data with pandas.
