---

# D163. Symmetric Tree
# Category: DSA — Trees & Graphs
# Difficulty: ⭐ Easy | LeetCode #101 | Asked: Amazon, Microsoft, LinkedIn, Bloomberg

---

## ❓ Problem
Given the root of a binary tree, check whether it is a mirror of itself (symmetric around its center).

```
Symmetric:      1            Not symmetric:    1
              /   \                          /   \
             2     2                        2     2
            / \   / \                        \     \
           3   4 4   3                        3     3
```

---

## 💡 Quick Concept (2 lines only)
Compare left subtree with right subtree as mirrors: left.left with right.right, and left.right with right.left.
हिंदी: left और right subtree को mirror की तरह compare करो - बाहर वाले जोड़े और अंदर वाले जोड़े।

---

## ✅ Solution

```javascript
// TreeNode class
class TreeNode {
  constructor(val, left = null, right = null) {
    this.val = val; this.left = left; this.right = right; // value + children
  }
}

// Build tree from level-order array
function buildTree(arr) {
  if (!arr || !arr.length) return null;           // empty tree
  const root = new TreeNode(arr[0]);              // root node
  const queue = [root];                           // parents waiting for children
  let i = 1;                                      // next value index
  while (queue.length && i < arr.length) {
    const node = queue.shift();                   // next parent
    if (arr[i] != null) { node.left = new TreeNode(arr[i]); queue.push(node.left); }
    i++;
    if (i < arr.length && arr[i] != null) { node.right = new TreeNode(arr[i]); queue.push(node.right); }
    i++;
  }
  return root;
}

// ============================================
// APPROACH 1 (Brute force): Invert a copy, then compare with original
// Time: O(n) | Space: O(n) — extra tree built
// ============================================
function cloneInverted(n) {
  if (!n) return null;                            // empty
  return new TreeNode(n.val, cloneInverted(n.right), cloneInverted(n.left)); // swap while copying
}
function same(a, b) {
  if (!a && !b) return true;                      // both empty
  if (!a || !b || a.val !== b.val) return false;  // mismatch
  return same(a.left, b.left) && same(a.right, b.right);
}
function isSymmetricBrute(root) {
  if (!root) return true;                         // empty is symmetric
  return same(root.left, cloneInverted(root.right)); // left must equal mirrored right
}

// ============================================
// APPROACH 2: Recursive mirror check (Optimal)
// Time: O(n) | Space: O(h)
// ============================================
function isSymmetric(root) {
  function isMirror(a, b) {
    if (!a && !b) return true;                    // both missing: ok
    if (!a || !b) return false;                   // one missing: not mirror
    return a.val === b.val &&                     // values match
           isMirror(a.left, b.right) &&           // outer pair
           isMirror(a.right, b.left);             // inner pair
  }
  return root === null || isMirror(root.left, root.right); // empty tree is symmetric
}

// ============================================
// APPROACH 3: Iterative with queue
// Time: O(n) | Space: O(w)
// ============================================
function isSymmetricIter(root) {
  if (!root) return true;                         // empty is symmetric
  const queue = [root.left, root.right];          // pairs stored consecutively
  while (queue.length) {
    const a = queue.shift();                      // take a pair
    const b = queue.shift();
    if (!a && !b) continue;                       // both null: fine
    if (!a || !b || a.val !== b.val) return false; // mismatch
    queue.push(a.left, b.right);                  // outer pair
    queue.push(a.right, b.left);                  // inner pair
  }
  return true;
}

// ============================================
// TEST CASES
// ============================================
const sym = buildTree([1, 2, 2, 3, 4, 4, 3]);
const asym = buildTree([1, 2, 2, null, 3, null, 3]);
console.log(isSymmetric(sym));          // true
console.log(isSymmetric(asym));         // false
console.log(isSymmetricIter(sym));      // true
console.log(isSymmetricIter(asym));     // false
console.log(isSymmetricBrute(sym));     // true
console.log(isSymmetricBrute(asym));    // false
console.log(isSymmetric(null));         // true
console.log(isSymmetric(buildTree([1]))); // true
```

---

## 🔍 Why It Works
A tree is symmetric when its left subtree is the mirror of its right subtree. Two trees are mirrors if their roots match and the first's left is the mirror of the second's right (and vice versa) — hence the crossed recursion.
हिंदी: Mirror में crossed जोड़े बनते हैं: a.left <-> b.right और a.right <-> b.left।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| Invert + compare | O(n) | O(n) |
| Recursive mirror | O(n) | O(h) |
| Iterative queue | O(n) | O(w) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Count symmetric level by level using values only (needs null markers)
// VARIANT 2: Check if two trees are mirrors -> isMirror(p, q) directly (see D161)
console.log(isSymmetric(buildTree([1, 2, 2, null, 3, 3]))); // true
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: compare left.left with right.left (that is Same Tree, not mirror)
isMirror(a.left, b.left) && isMirror(a.right, b.right)

// ✅ Correct: cross them
isMirror(a.left, b.right) && isMirror(a.right, b.left)

// ❌ Wrong: check only inorder is a palindrome — structure can still differ
```

---

## 🎯 Interview Tip
Say: "It is Same Tree with crossed children." Offer both recursive and iterative solutions; interviewers often ask for the iterative one as a follow-up.

---

## 🔗 Related Problems
→ D161 (Invert Tree) | D162 (Same Tree) | D160 (Max Depth) | D025 (Tree Traversals)
