# DSA Patterns Cheatsheet
# 5+ YOE JavaScript Interview — Pattern Recognition

---

## 🧠 Pattern Recognition — Most Important Skill

```
PROBLEM CLUE               →  PATTERN TO USE
─────────────────────────────────────────────────────────────────
Sorted array, find target  →  Binary Search  O(log n)
Subarray/substring         →  Sliding Window O(n)
Pair/triplet in array      →  Two Pointers   O(n) or O(n²)
Brackets, undo/redo        →  Stack          O(n)
Level-by-level tree        →  BFS (Queue)    O(n)
Tree path, DFS             →  Recursion/DFS  O(n)
Optimal substructure       →  DP             O(n²) or better
Find missing/duplicate     →  XOR or Math    O(n)
HashMap lookup             →  HashMap        O(1) per op
Top/bottom K elements      →  Heap           O(n log k)
```

---

## 📊 All Patterns — Quick Code

### 1. Binary Search
```javascript
// Template — works for all binary search variants:
function binarySearch(nums, target) {
  let left = 0, right = nums.length - 1;
  while (left <= right) {
    const mid = left + Math.floor((right - left) / 2);  // safe mid
    if (nums[mid] === target) return mid;
    else if (nums[mid] < target) left = mid + 1;
    else right = mid - 1;
  }
  return -1;
}
// Time: O(log n) | Space: O(1)
// Variations: first/last occurrence, rotated array, peak element
```

### 2. Sliding Window
```javascript
// Fixed window (size k):
function maxSumK(nums, k) {
  let sum = nums.slice(0, k).reduce((a, b) => a + b, 0);
  let max = sum;
  for (let i = k; i < nums.length; i++) {
    sum += nums[i] - nums[i - k];
    max = Math.max(max, sum);
  }
  return max;
}

// Variable window (condition-based):
function longestNoRepeat(s) {
  const map = new Map();
  let left = 0, max = 0;
  for (let right = 0; right < s.length; right++) {
    if (map.has(s[right]) && map.get(s[right]) >= left) {
      left = map.get(s[right]) + 1;
    }
    map.set(s[right], right);
    max = Math.max(max, right - left + 1);
  }
  return max;
}
// Time: O(n) | Space: O(k) where k = window/charset size
```

### 3. Two Pointers
```javascript
// Opposite ends (sorted array):
function twoSumSorted(nums, target) {
  let left = 0, right = nums.length - 1;
  while (left < right) {
    const sum = nums[left] + nums[right];
    if (sum === target) return [left, right];
    else if (sum < target) left++;
    else right--;
  }
  return [];
}

// Same direction (fast/slow pointer):
function hasCycle(head) {
  let slow = head, fast = head;
  while (fast && fast.next) {
    slow = slow.next;
    fast = fast.next.next;
    if (slow === fast) return true;
  }
  return false;
}
// Time: O(n) | Space: O(1)
```

### 4. HashMap Pattern
```javascript
// Two Sum style — complement lookup:
function twoSum(nums, target) {
  const map = new Map();  // value → index
  for (let i = 0; i < nums.length; i++) {
    const complement = target - nums[i];
    if (map.has(complement)) return [map.get(complement), i];
    map.set(nums[i], i);
  }
}

// Frequency counter:
function isAnagram(s, t) {
  if (s.length !== t.length) return false;
  const freq = {};
  for (const c of s) freq[c] = (freq[c] || 0) + 1;
  for (const c of t) {
    if (!freq[c]) return false;
    freq[c]--;
  }
  return true;
}
// Time: O(n) | Space: O(k) unique chars
```

### 5. Stack Pattern
```javascript
// Valid parentheses template:
function isValid(s) {
  const stack = [];
  const map = { ')': '(', '}': '{', ']': '[' };
  for (const c of s) {
    if ('({['.includes(c)) stack.push(c);
    else if (stack.length === 0 || stack.pop() !== map[c]) return false;
  }
  return stack.length === 0;
}

// Monotonic Stack (next greater element):
function nextGreater(nums) {
  const result = new Array(nums.length).fill(-1);
  const stack = [];  // indices
  for (let i = 0; i < nums.length; i++) {
    while (stack.length && nums[i] > nums[stack[stack.length - 1]]) {
      result[stack.pop()] = nums[i];
    }
    stack.push(i);
  }
  return result;
}
// [2,1,2,4,3] → [4,2,4,-1,-1]
```

### 6. BFS (Level Order)
```javascript
// Tree level order:
function levelOrder(root) {
  if (!root) return [];
  const result = [], queue = [root];
  while (queue.length) {
    const size = queue.length;
    const level = [];
    for (let i = 0; i < size; i++) {
      const node = queue.shift();
      level.push(node.val);
      if (node.left) queue.push(node.left);
      if (node.right) queue.push(node.right);
    }
    result.push(level);
  }
  return result;
}

// Graph BFS (shortest path):
function shortestPath(graph, start, end) {
  const queue = [[start, 0]];
  const visited = new Set([start]);
  while (queue.length) {
    const [node, dist] = queue.shift();
    if (node === end) return dist;
    for (const neighbor of graph[node] || []) {
      if (!visited.has(neighbor)) {
        visited.add(neighbor);
        queue.push([neighbor, dist + 1]);
      }
    }
  }
  return -1;
}
```

### 7. DFS + Backtracking
```javascript
// Tree DFS:
function maxDepth(root) {
  if (!root) return 0;
  return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
}

// Backtracking template (subsets/permutations/combinations):
function subsets(nums) {
  const result = [];
  function backtrack(start, path) {
    result.push([...path]);
    for (let i = start; i < nums.length; i++) {
      path.push(nums[i]);
      backtrack(i + 1, path);
      path.pop();  // undo (backtrack)
    }
  }
  backtrack(0, []);
  return result;
}
```

### 8. Dynamic Programming
```javascript
// 1D DP template (Fibonacci-like):
function dp1D(n) {
  if (n <= 1) return n;
  let prev2 = 0, prev1 = 1;
  for (let i = 2; i <= n; i++) {
    const curr = prev1 + prev2;
    prev2 = prev1; prev1 = curr;
  }
  return prev1;
}

// 2D DP template (grid paths, LCS):
function dp2D(m, n) {
  const dp = Array.from({length: m + 1}, () => new Array(n + 1).fill(0));
  // fill base cases
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      dp[i][j] = dp[i-1][j] + dp[i][j-1];  // example: unique paths
    }
  }
  return dp[m][n];
}

// Knapsack template:
function knapsack(weights, values, capacity) {
  const dp = new Array(capacity + 1).fill(0);
  for (let i = 0; i < weights.length; i++) {
    for (let j = capacity; j >= weights[i]; j--) {  // backward for 0/1
      dp[j] = Math.max(dp[j], dp[j - weights[i]] + values[i]);
    }
  }
  return dp[capacity];
}
```

---

## 🎯 Top 25 DSA Problems to Know (5+ YOE)

```
ARRAYS:
✅ D001 Two Sum                    HashMap O(n)
✅ D002 Maximum Subarray           Kadane's O(n)
✅ D003 Merge Intervals            Sort+Scan O(n log n)
✅ D004 Binary Search              BS O(log n)
   D005 Product Except Self        Prefix O(n)
   D006 Container with Most Water  Two Pointers O(n)
   D007 Trapping Rain Water        Two Pointers O(n)

SLIDING WINDOW:
✅ D015 Max Sum Subarray K         SW O(n)
   D016 Longest Substring No Repeat SW+Map O(n)
   D017 Minimum Window Substring   SW O(n)

TWO POINTERS:
✅ D007 Three Sum                  Sort+2P O(n²)
   D008 Four Sum                   Sort+2P O(n³)

LINKED LIST:
✅ D020 Reverse Linked List        3-ptrs O(n)
   D021 Cycle Detection            Floyd's O(n)
   D022 Merge Two Sorted Lists     2-ptrs O(n)
   D023 Find Middle                Fast/Slow O(n)

STACK:
✅ D010 Valid Parentheses          Stack O(n)
   D011 Daily Temperatures         Monotonic Stack O(n)
   D012 Min Stack                  Two stacks O(1)

TREES:
✅ D025 Tree Traversals (all 4)    Recursion O(n)
   D026 Validate BST               DFS O(n)
   D027 Lowest Common Ancestor     DFS O(n)

DP:
✅ D030 Climbing Stairs            Fibonacci DP O(n)
✅ D031 Coin Change                DP O(n×coins)
   D032 House Robber               1D DP O(n)
   D033 Longest Common Subsequence 2D DP O(m×n)
```

---

## ⏱️ Time Complexity Quick Reference

```
O(1)        → HashMap lookup, Stack push/pop, Array index
O(log n)    → Binary Search, Balanced BST operations
O(n)        → Single pass, Two Pointers, Sliding Window, Hash traversal
O(n log n)  → Sorting (quicksort, mergesort), Heap operations for n items
O(n²)       → Nested loops, Bubble sort, brute force two-sum
O(n³)       → Three nested loops (brute three-sum)
O(2^n)      → Recursive without memo (power set, Fibonacci naive)
O(n!)       → Permutations
```

---

## 🚀 Interview Approach (5+ YOE)

```
1. Clarify (2 min):
   - Input constraints? (n=10⁵ means O(n log n) max)
   - Edge cases: empty, single element, all same, negative numbers
   - Return type: indices or values? 

2. Brute Force (1 min):
   - State it briefly
   - Mention time complexity
   - "Can we do better?"

3. Optimal Approach (5 min):
   - State the pattern (HashMap/Sliding Window/DP...)
   - Walk through example before coding
   - Code clean + readable

4. Test (2 min):
   - Happy path
   - Edge cases
   - Walk through your code

5. Complexity (1 min):
   - Time + Space with reasoning
```
