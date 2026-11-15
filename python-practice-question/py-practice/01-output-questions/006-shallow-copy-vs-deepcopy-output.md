---

# Q006. Shallow Copy vs deepcopy Output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
import copy

orig = [1, [2, 3], {"k": [4]}]
shallow = orig.copy()
deep = copy.deepcopy(orig)

orig[1].append(99)
orig[0] = 100
orig[2]["k"].append(5)

print(orig)
print(shallow)
print(deep)
```

---

## 💡 Quick Concept (2 lines only)
A shallow copy duplicates only the outer container; nested objects are still shared. `deepcopy` recursively duplicates everything.
हिंदी: Shallow copy में अंदर की चीज़ें shared रहती हैं, deepcopy सब कुछ नया बनाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import copy                             # standard library copy module

# Step 1: build a nested structure
orig = [1, [2, 3], {"k": [4]}]          # int, inner list, dict holding a list

# Step 2: make a shallow and a deep copy
shallow = orig.copy()                   # new outer list, SAME inner list and dict
deep = copy.deepcopy(orig)              # fully independent clone

# Step 3: mutate the original in three ways
orig[1].append(99)                      # mutate the shared inner list in place
orig[0] = 100                           # rebind slot 0 of the OUTER list only
orig[2]["k"].append(5)                  # mutate a list nested two levels deep

print(orig)                             # Expected: [100, [2, 3, 99], {'k': [4, 5]}]
print(shallow)                          # Expected: [1, [2, 3, 99], {'k': [4, 5]}]
print(deep)                             # Expected: [1, [2, 3], {'k': [4]}]
print(shallow[1] is orig[1], deep[1] is orig[1])  # Expected: True False
```

---

## 🔍 Why This Works (3 lines max)
The shallow copy has its own outer list (so `orig[0] = 100` isn't seen) but its slots point to the same inner list and dict (so in-place changes are seen). `deepcopy` clones every level, so `deep` never changes.
हिंदी: Outer बदलाव दिखता नहीं, पर inner in-place बदलाव shallow copy में भी दिखता है।

---

## ⚡ Alternative Solution
```python
import copy                             # needed for deepcopy

# Other ways to shallow copy: slice, list(), copy.copy -> all behave the same
a = [[1], [2]]                          # list of lists
print(a[:][0] is a[0], list(a)[0] is a[0], copy.copy(a)[0] is a[0])  # Expected: True True True

# deepcopy handles self-referencing structures via a memo dict
loop = [1, 2]                           # start with a normal list
loop.append(loop)                       # make it contain itself
clone = copy.deepcopy(loop)             # does not recurse forever
print(clone, clone[2] is clone, clone is loop)  # Expected: [1, 2, [...]] True False
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assuming .copy() / [:] / list() protects nested data
# backup = settings.copy(); settings["db"]["host"] = "x"   # backup["db"]["host"] is "x" too!

# ✅ Correct: deepcopy when the structure is nested and you will mutate it
# backup = copy.deepcopy(settings)
```

---

## 🎯 Interview Tip (1 line)
Say: "Shallow copy shares nested objects; I use `copy.deepcopy` for nested mutable data, knowing it is slower and handles cycles via a memo."

---

## 🔗 Related Questions
→ Q005 (list multiplication aliasing) | Q071 (deep clone a dict) | Q176 (copy semantics) | Q293 (shallow vs deep copy)
