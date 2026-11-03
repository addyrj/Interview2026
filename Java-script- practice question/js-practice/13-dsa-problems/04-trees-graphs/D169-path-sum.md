---

# D169. Path Sum
# Category: DSA — Trees & Graphs
# Difficulty: ⭐ Easy | LeetCode #112 | Asked: Amazon, Microsoft, Google, Adobe

---

## ❓ Problem
Given the root of a binary tree and an integer `targetSum`, return true if the tree has a ROOT-TO-LEAF path whose node values add up to `targetSum`.

```
Tree:        5
           /   \
          4     8
         /     / \
        11    13  4
       /  \         \
      7    2         1

targetSum = 22  -> true  (5 -> 4 -> 11 -> 2)
targetSum = 5   -> false (5 is not a leaf)
```

---

## 💡 Quick Concept (2 lines only)
Subtract the node value from the target while going down; at a leaf check whether the remaining target equals the leaf's value.
हिंदी: नीचे जाते हुए target में से node की value घटाओ; leaf पर remaining बराबर हो तो true।

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
// APPROACH 1 (Brute force): collect all root-to-leaf sums, then search
// Time: O(n) | Space: O(h) + O(#leaves)
// ============================================
function hasPathSumBrute(root, target) {
  const sums = [];                                // all root-to-leaf sums
  function dfs(node, acc) {
    if (!node) return;                            // nothing here
    acc += node.val;                              // add this node
    if (!node.left && !node.right) sums.push(acc); // leaf: store sum
    dfs(node.left, acc);                          // go left
    dfs(node.right, acc);                         // go right
  }
  dfs(root, 0);
  return sums.includes(target);                   // search for target
}

// ============================================
// APPROACH 2: Recursive DFS with remaining sum (Optimal)
// Time: O(n) | Space: O(h)
// ============================================
function hasPathSum(root, target) {
  if (!root) return false;                        // no tree -> no path
  if (!root.left && !root.right) return root.val === target; // leaf: exact match
  const rest = target - root.val;                 // what children must still make
  return hasPathSum(root.left, rest) || hasPathSum(root.right, rest); // either side
}

// ============================================
// APPROACH 3: Iterative DFS with stack of [node, remaining]
// Time: O(n) | Space: O(h)
// ============================================
function hasPathSumIter(root, target) {
  if (!root) return false;                        // empty tree
  const stack = [[root, target - root.val]];      // node + remaining after it
  while (stack.length) {
    const [node, rest] = stack.pop();             // take entry
    if (!node.left && !node.right && rest === 0) return true; // leaf with zero left
    if (node.right) stack.push([node.right, rest - node.right.val]);
    if (node.left) stack.push([node.left, rest - node.left.val]);
  }
  return false;
}

// ============================================
// TEST CASES
// ============================================
const t = buildTree([5, 4, 8, 11, null, 13, 4, 7, 2, null, null, null, 1]);
console.log(hasPathSum(t, 22));                   // true
console.log(hasPathSum(t, 26));                   // true  (5+8+13)
console.log(hasPathSum(t, 5));                    // false (5 is not a leaf)
console.log(hasPathSumIter(t, 22));               // true
console.log(hasPathSumIter(t, 100));              // false
console.log(hasPathSumBrute(t, 22));              // true
console.log(hasPathSum(null, 0));                 // false
console.log(hasPathSum(buildTree([1, 2]), 1));    // false (must end at a leaf)
console.log(hasPathSum(buildTree([-2, null, -3]), -5)); // true (negative values)
```

---

## 🔍 Why It Works
Each recursive call asks: "can my subtree supply the remaining sum on some root-to-leaf path?" Only a leaf can answer directly, so the answer bubbles up through `||`. Handling the leaf case separately prevents counting partial paths.
हिंदी: सिर्फ leaf पर final जाँच होती है, ऊपर `||` से जवाब पहुँचता है।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| Collect all sums | O(n) | O(h + leaves) |
| Recursive | O(n) | O(h) |
| Iterative | O(n) | O(h) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Path Sum II (LeetCode #113) — return all such paths (backtracking)
function pathSumAll(root, target) {
  const res = [], path = [];                      // answers + current path
  function dfs(n, rest) {
    if (!n) return;                               // dead end
    path.push(n.val);                             // choose
    if (!n.left && !n.right && rest === n.val) res.push([...path]); // leaf match: copy path
    dfs(n.left, rest - n.val);
    dfs(n.right, rest - n.val);
    path.pop();                                   // un-choose (backtrack)
  }
  dfs(root, target);
  return res;
}
console.log(JSON.stringify(pathSumAll(t, 22)));   // [[5,4,11,2]]

// VARIANT 2: Path Sum III (LeetCode #437) — any downward path, prefix-sum hashmap
function pathSumIII(root, target) {
  const freq = new Map([[0, 1]]);                 // prefix sum frequency
  function dfs(n, sum) {
    if (!n) return 0;
    sum += n.val;                                 // running sum from root
    let count = freq.get(sum - target) || 0;      // paths ending here
    freq.set(sum, (freq.get(sum) || 0) + 1);      // record prefix
    count += dfs(n.left, sum) + dfs(n.right, sum);
    freq.set(sum, freq.get(sum) - 1);             // backtrack
    return count;
  }
  return dfs(root, 0);
}
console.log(pathSumIII(buildTree([10, 5, -3, 3, 2, null, 11, 3, -2, null, 1]), 8)); // 3
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: returning true when target hits 0 at a non-leaf
if (!root) return target === 0;   // [1,2] with target 1: root.right null -> true (wrong!)

// ✅ Correct: check the sum only at real leaves (both children null)

// ❌ Wrong: assuming values are positive and pruning when sum > target
//    (negative values break that shortcut)
```

---

## 🎯 Interview Tip
Say: "Carry the remaining sum down; only a leaf may declare success." Ask whether values can be negative and whether the path must end at a leaf. Offer Path Sum II/III as natural follow-ups.

---

## 🔗 Related Problems
→ D168 (Diameter) | D160 (Max Depth) | D166 (LCA) | D025 (Traversals)
