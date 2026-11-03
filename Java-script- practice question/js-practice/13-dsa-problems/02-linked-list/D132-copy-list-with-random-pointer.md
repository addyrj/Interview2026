---

# D132. Copy List with Random Pointer
# Category: DSA — Linked List
# Difficulty: ⭐⭐ Medium | LeetCode #138 | Asked: Amazon, Microsoft, Facebook, Google

---

## ❓ Problem
Each node has a `next` pointer and a `random` pointer (to any node in the list or null). Create a deep copy: n brand-new nodes whose next/random pointers point to new nodes, never to the originals.

```
Input:  [[7,null],[13,0],[11,4],[10,2],[1,0]]   (value, random index)
Output: same structure, all new nodes
```

---

## 💡 Quick Concept (2 lines only)
Map each original node to its copy (HashMap), then wire next and random using the map. O(1) space trick: interleave copies after originals, set randoms, then split.
हिंदी: हर original node का copy बनाकर Map में रखो, फिर next और random को Map से जोड़ो; या copy को original के ठीक बाद डालकर O(1) space में करो।

---

## ✅ Solution

```javascript
// Node class with random pointer:
class Node {
  constructor(val, next = null, random = null) {
    this.val = val;         // node value
    this.next = next;       // next pointer
    this.random = random;   // random pointer
  }
}

// Helper: build from [[val, randomIndex], ...]
function buildList(pairs) {
  const nodes = pairs.map(([v]) => new Node(v));       // create all nodes
  pairs.forEach(([, r], i) => {                        // wire pointers
    if (i + 1 < nodes.length) nodes[i].next = nodes[i + 1]; // next link
    if (r !== null) nodes[i].random = nodes[r];        // random link
  });
  return nodes[0] || null;                             // head
}

// Helper: serialize back to [[val, randomIndex], ...]
function serialize(head) {
  const idx = new Map();                               // node -> index
  const nodes = [];                                    // nodes in order
  for (let p = head; p; p = p.next) { idx.set(p, nodes.length); nodes.push(p); } // index nodes
  return nodes.map((n) => [n.val, n.random ? idx.get(n.random) : null]); // value + random index
}

// Helper: verify no node is shared between lists
function noSharedNodes(a, b) {
  const set = new Set();                               // originals
  for (let p = a; p; p = p.next) set.add(p);           // collect
  for (let p = b; p; p = p.next) {                     // check copy
    if (set.has(p) || (p.random && set.has(p.random))) return false; // points to original
  }
  return true;                                         // fully separate
}

// ============================================
// APPROACH 1: HashMap old -> new — O(n) time, O(n) space
// ============================================
function copyRandomListMap(head) {
  if (!head) return null;                              // empty list
  const map = new Map();                               // original -> copy
  for (let p = head; p; p = p.next) map.set(p, new Node(p.val)); // pass 1: create copies
  for (let p = head; p; p = p.next) {                  // pass 2: wire pointers
    const copy = map.get(p);                           // copy of p
    copy.next = p.next ? map.get(p.next) : null;       // copy's next
    copy.random = p.random ? map.get(p.random) : null; // copy's random
  }
  return map.get(head);                                // copy of head
}

// ============================================
// APPROACH 2: Interleave copies — O(n) time, O(1) extra space ✅ PREFERRED
// ============================================
function copyRandomList(head) {
  if (!head) return null;                              // empty list

  // Step 1: insert a copy right after every original: A → A' → B → B' ...
  for (let p = head; p; p = p.next.next) {
    p.next = new Node(p.val, p.next);                  // copy points to original's old next
  }

  // Step 2: set random of copies (copy.random = original.random.next)
  for (let p = head; p; p = p.next.next) {
    if (p.random) p.next.random = p.random.next;       // random's copy sits right after random
  }

  // Step 3: separate the two lists and restore the original
  const newHead = head.next;                           // head of copy list
  for (let p = head; p; p = p.next) {
    const copy = p.next;                               // copy of p
    p.next = copy.next;                                // restore original's next
    copy.next = copy.next ? copy.next.next : null;     // copy's next = next copy
  }
  return newHead;                                      // copy list
}

// ============================================
// TEST CASES
// ============================================
const input = [[7, null], [13, 0], [11, 4], [10, 2], [1, 0]];
const orig1 = buildList(input);
const c1 = copyRandomListMap(orig1);
console.log(JSON.stringify(serialize(c1)));            // [[7,null],[13,0],[11,4],[10,2],[1,0]]
console.log(noSharedNodes(orig1, c1));                 // true

const orig2 = buildList(input);
const c2 = copyRandomList(orig2);
console.log(JSON.stringify(serialize(c2)));            // [[7,null],[13,0],[11,4],[10,2],[1,0]]
console.log(noSharedNodes(orig2, c2));                 // true
console.log(JSON.stringify(serialize(orig2)));         // [[7,null],[13,0],[11,4],[10,2],[1,0]]  (original restored)

console.log(JSON.stringify(serialize(copyRandomList(buildList([[1, 1], [2, 1]])))));  // [[1,1],[2,1]]
console.log(copyRandomList(null));                     // null
```

---

## 🔍 Why It Works
```
Original: A → B → C       randoms: A.r=C, B.r=A
Step 1:   A → A' → B → B' → C → C'
Step 2:   A'.random = A.random.next = C'
          B'.random = B.random.next = A'
Step 3:   split: A→B→C   and   A'→B'→C'
```
हिंदी: Copy हमेशा original के ठीक बाद होता है, इसलिए original.random.next ही random का copy निकलता है — Map की ज़रूरत नहीं।

---

## 📊 Complexity
```
HashMap:    Time O(n) | Space O(n)
Interleave: Time O(n) | Space O(1) extra (output excluded) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Clone a graph (LeetCode #133) - same "old -> new" Map idea with DFS/BFS
// VARIANT 2: Clone a binary tree with random pointers - Map + DFS
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: copy.random = p.random    // points into the ORIGINAL list (shallow copy)

// ❌ Wrong: not restoring the original list in the interleave approach
// ❌ Wrong: Step 2 after splitting - randoms can't be resolved once lists are separated

// ✅ Correct: map every old node to its new node, then wire both pointers via the map
```

---

## 🎯 Interview Tip
Say: "Deep copy needs old-to-new mapping, because random can point forward or backward. HashMap is clean and O(n) space; interleaving gets O(1) extra space but modifies then restores the input." Start with the Map.

---

## 🔗 Related Problems
→ D020 (Reverse Linked List) | D120 (Merge Two Sorted Lists) | D126 (Intersection of Two LLs)
