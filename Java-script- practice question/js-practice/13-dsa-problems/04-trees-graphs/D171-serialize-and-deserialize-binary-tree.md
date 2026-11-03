---

# D171. Serialize and Deserialize Binary Tree
# Category: DSA — Trees & Graphs
# Difficulty: ⭐⭐⭐ Hard | LeetCode #297 | Asked: Amazon, Meta, Google, Microsoft, LinkedIn

---

## ❓ Problem
Design an algorithm to convert a binary tree to a string (`serialize`) and rebuild the exact same tree from that string (`deserialize`). Any format is allowed as long as it round-trips.

```
Tree:     1
         / \
        2   3
           / \
          4   5

Serialized (preorder with null markers): "1,2,#,#,3,4,#,#,5,#,#"
```

---

## 💡 Quick Concept (2 lines only)
Preorder DFS with an explicit marker for null children uniquely identifies the tree. Deserialize by consuming tokens in the same order.
हिंदी: Preorder + null का marker (#) = tree की unique पहचान; वही order में पढ़कर वापस बनाओ।

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
// APPROACH 1 (Brute force-ish): inorder only — NOT enough!
// Inorder alone cannot rebuild a tree uniquely (ambiguous), shown for contrast.
// ============================================

// ============================================
// APPROACH 2: Preorder DFS with null markers (Optimal & simple)
// Time: O(n) | Space: O(n)
// ============================================
function serialize(root) {
  const out = [];                                 // tokens
  function dfs(n) {
    if (!n) { out.push("#"); return; }           // null marker
    out.push(String(n.val));                      // root first
    dfs(n.left);                                  // then left
    dfs(n.right);                                 // then right
  }
  dfs(root);
  return out.join(",");                           // single string
}

function deserialize(data) {
  const tokens = data.split(",");                 // back to tokens
  let i = 0;                                      // shared read pointer
  function build() {
    const t = tokens[i++];                        // consume next token
    if (t === "#") return null;                   // null marker -> no node
    const node = new TreeNode(Number(t));         // root
    node.left = build();                          // left subtree consumes its tokens
    node.right = build();                         // right subtree next
    return node;
  }
  return build();
}

// ============================================
// APPROACH 3: Level-order (BFS) — LeetCode's own format
// Time: O(n) | Space: O(n)
// ============================================
function serializeBFS(root) {
  if (!root) return "";                           // empty tree
  const out = [], queue = [root];                 // BFS including nulls
  while (queue.length) {
    const n = queue.shift();
    if (n) { out.push(n.val); queue.push(n.left, n.right); } // real node
    else out.push("#");                           // null marker
  }
  return out.join(",");
}

function deserializeBFS(data) {
  if (!data) return null;                         // empty string -> empty tree
  const t = data.split(",");                      // tokens
  const root = new TreeNode(Number(t[0]));        // first is root
  const queue = [root];
  let i = 1;                                      // next token
  while (queue.length) {
    const n = queue.shift();                      // parent
    if (t[i] !== "#") { n.left = new TreeNode(Number(t[i])); queue.push(n.left); }
    i++;
    if (t[i] !== "#") { n.right = new TreeNode(Number(t[i])); queue.push(n.right); }
    i++;
  }
  return root;
}

// ============================================
// TEST CASES
// ============================================
const t1 = buildTree([1, 2, 3, null, null, 4, 5]);
console.log(serialize(t1));                                  // 1,2,#,#,3,4,#,#,5,#,#
console.log(serialize(deserialize(serialize(t1))));          // 1,2,#,#,3,4,#,#,5,#,#
console.log(serializeBFS(t1));                               // 1,2,3,#,#,4,5,#,#,#,#
console.log(serializeBFS(deserializeBFS(serializeBFS(t1)))); // 1,2,3,#,#,4,5,#,#,#,#
console.log(serialize(null));                                // #
console.log(deserialize("#"));                               // null
const neg = buildTree([-1, 0, 1]);
console.log(serialize(deserialize(serialize(neg))));         // -1,0,#,#,1,#,#
```

---

## 🔍 Why It Works
Preorder visits root before children, and null markers tell the parser exactly where each subtree ends. Because deserialization consumes tokens in the same order serialization produced them, the shared pointer always lines up with the right subtree.
हिंदी: null marker से पता चलता है subtree कहाँ खत्म हुआ; वही order में पढ़ने से tree वैसा ही बनता है।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| Preorder DFS | O(n) | O(n) string + O(h) recursion |
| BFS | O(n) | O(n) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Serialize/Deserialize a BST (LeetCode #449) — preorder WITHOUT null markers,
//   rebuild using min/max bounds (BST order replaces markers) -> shorter string
function serializeBST(root) {
  const out = [];
  (function pre(n) { if (n) { out.push(n.val); pre(n.left); pre(n.right); } })(root); // preorder
  return out.join(",");
}
function deserializeBST(data) {
  if (!data) return null;                         // empty tree
  const vals = data.split(",").map(Number);       // preorder values
  let i = 0;
  function build(lo, hi) {
    if (i >= vals.length || vals[i] < lo || vals[i] > hi) return null; // out of range
    const node = new TreeNode(vals[i++]);         // take value
    node.left = build(lo, node.val);              // left values < node
    node.right = build(node.val, hi);             // right values > node
    return node;
  }
  return build(-Infinity, Infinity);
}
console.log(serializeBST(deserializeBST("5,3,2,4,7")));     // 5,3,2,4,7
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: preorder WITHOUT null markers for a general tree -> ambiguous
//    [1,2] and [1,null,2] both serialize to "1,2"

// ❌ Wrong: using a delimiter-less format ("123") — multi-digit and negative values break
// ✅ Correct: separate tokens with ',' and mark nulls with '#'

// ❌ Wrong: recreating `i` inside the recursive function instead of sharing the pointer
```

---

## 🎯 Interview Tip
Say: "Preorder with null sentinels is unambiguous and O(n); delimiter handles multi-digit and negative values." Mention BFS format as the alternative (matches LeetCode's input) and the BST optimisation that drops null markers.

---

## 🔗 Related Problems
→ D025 (Traversals) | D162 (Same Tree) | D167 (Level Order) | D164 (Validate BST)
