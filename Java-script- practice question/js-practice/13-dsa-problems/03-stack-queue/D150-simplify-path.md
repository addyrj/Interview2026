---

# D150. Simplify Path
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #71 | Asked: Microsoft, Amazon, Facebook, Google

---

## ❓ Problem
Given an absolute Unix-style file path, return its simplified canonical path. `.` is the current directory, `..` goes up one level, multiple slashes count as one.

```
Input:  "/home//foo/../bar/./baz/"
Output: "/home/bar/baz"
```

---

## 💡 Quick Concept (2 lines only)
Split the path by `/`. Skip empty and `.`; for `..` pop the stack (if non-empty); otherwise push the folder name. Join with `/` and prefix with `/`.
हिंदी: `/` से split करो; `..` पर pop, normal नाम पर push, `.` और खाली को ignore।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute force — repeated string replace
// ============================================

function simplifyPathBrute(path) {
  let p = path;
  while (p.includes('//')) p = p.replace('//', '/');         // collapse slashes
  p = p.replace(/\/\.(?=\/|$)/g, '');                        // remove '/.' segments
  let prev;
  do {
    prev = p;
    p = p.replace(/\/[^\/]+\/\.\.(?=\/|$)/, '');             // remove 'name/..'
  } while (p !== prev);
  p = p.replace(/^\/\.\.(?=\/|$)/, '');                      // '..' at root stays at root
  p = p.replace(/\/$/, '');                                  // remove trailing slash
  return p === '' ? '/' : p;
}

// ============================================
// APPROACH 2: Stack — O(n) time, O(n) space ✅ PREFERRED
// ============================================

function simplifyPath(path) {
  const stack = [];                                  // valid directory names
  const parts = path.split('/');                     // split into components

  for (const part of parts) {
    if (part === '' || part === '.') continue;       // nothing to do
    if (part === '..') {
      if (stack.length) stack.pop();                 // go up (ignored at root)
    } else {
      stack.push(part);                              // real directory name
    }
  }
  return '/' + stack.join('/');                      // rebuild canonical path
}

// ============================================
// TEST CASES
// ============================================

console.log(simplifyPath("/home/"));                       // /home
console.log(simplifyPath("/../"));                         // /
console.log(simplifyPath("/home//foo/"));                  // /home/foo
console.log(simplifyPath("/a/./b/../../c/"));              // /c
console.log(simplifyPath("/a/../../b/../c//.//"));         // /c
console.log(simplifyPath("/..."));                         // /...
console.log(simplifyPathBrute("/home//foo/../bar/./baz/")); // /home/bar/baz
console.log(simplifyPath("/home//foo/../bar/./baz/"));     // /home/bar/baz
```

---

## 🔍 Why It Works
```
"/a/./b/../../c/"  parts: ["", "a", ".", "b", "..", "..", "c", ""]
a   push   [a]
.   skip
b   push   [a,b]
..  pop    [a]
..  pop    []
c   push   [c]    -> "/c"
```
हिंदी: Directory path एक stack की तरह है — `..` का मतलब है आख़िरी folder हटाओ।

---

## 📊 Complexity
```
Brute force (regex): Time O(n^2) worst | Space O(n)
Stack:               Time O(n)         | Space O(n)
```

---

## ⚡ Variations
```
- Relative path normalisation (keep leading '..' when stack empty)
- Windows paths (split on '\\')
- Longest absolute file path (#388)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: treating "..." as special — it is a valid folder name
// ❌ Wrong: popping from an empty stack on ".." at root -> must be ignored
// ❌ Wrong: returning stack.join('/') without the leading '/' (empty -> '' instead of '/')
```

---

## 🎯 Interview Tip
Say: "Split on slash, ignore empty and dot, `..` pops, everything else pushes." Mention the edge cases: root `..`, triple dots, trailing slash.

---

## 🔗 Related Problems
→ D149 (Remove Adjacent Duplicates) | D148 (Decode String) | D010 (Valid Parentheses)
