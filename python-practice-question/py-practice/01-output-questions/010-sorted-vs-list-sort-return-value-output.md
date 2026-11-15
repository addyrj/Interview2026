---

# Q010. sorted() vs list.sort() Return Value Output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐ Easy

---

## ❓ Question
What will the following code print?

```python
nums = [3, 1, 2]
r = nums.sort()
print(r, nums)

nums = [3, 1, 2]
r = sorted(nums)
print(r, nums)
```

---

## 💡 Quick Concept (2 lines only)
`list.sort()` sorts IN PLACE and returns `None`; `sorted()` returns a NEW sorted list from any iterable and leaves the original alone.
हिंदी: `.sort()` वही list बदलता है और None देता है; `sorted()` नई list देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Step 1: list.sort() mutates and returns None
nums = [3, 1, 2]                        # unsorted list
r = nums.sort()                         # sorts nums in place, returns None
print(r, nums)                          # Expected: None [1, 2, 3]

# Step 2: sorted() returns a new list
nums = [3, 1, 2]                        # reset to unsorted
r = sorted(nums)                        # new sorted list, nums untouched
print(r, nums)                          # Expected: [1, 2, 3] [3, 1, 2]

# Step 3: sorted() works on any iterable and always returns a list
print(sorted("cab"))                    # Expected: ['a', 'b', 'c']
print(sorted({3: "a", 1: "b"}))         # Expected: [1, 3]   (sorts the dict keys)
print(sorted((3, 1, 2), reverse=True))  # Expected: [3, 2, 1]
```

---

## 🔍 Why This Works (3 lines max)
Python's convention: methods that mutate in place return `None` so you don't confuse them with copies. `sorted()` consumes any iterable, builds a list, and sorts it with the same stable Timsort.
हिंदी: In-place method None लौटाते हैं — इसलिए `x = lst.sort()` करने पर x None होगा।

---

## ⚡ Alternative Solution
```python
# key= for custom ordering; both sort() and sorted() are stable
words = ["bb", "a", "cc", "d"]          # mixed-length words
print(sorted(words, key=len))           # Expected: ['a', 'd', 'bb', 'cc']  (ties keep original order)
print(sorted(words, key=len, reverse=True))  # Expected: ['bb', 'cc', 'a', 'd']  (reverse keeps stability)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assigning the result of .sort()
# nums = nums.sort()      # nums is now None -> TypeError / AttributeError later

# ✅ Correct
# nums.sort()             # in place, OR
# nums = sorted(nums)     # new list
```

---

## 🎯 Interview Tip (1 line)
Say: "`.sort()` is in-place returning `None`, `sorted()` returns a new list from any iterable; both are stable Timsort, O(n log n)."

---

## 🔗 Related Questions
→ Q258 (sorted() key tricks) | Q065 (sort list of dicts) | Q113 (implement sorted with key) | Q009 (+= vs + on lists)
