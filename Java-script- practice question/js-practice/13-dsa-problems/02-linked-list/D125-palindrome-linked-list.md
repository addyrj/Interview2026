---

# D125. Palindrome Linked List
# Category: DSA — Linked List
# Difficulty: ⭐ Easy | LeetCode #234 | Asked: Amazon, Microsoft, Facebook, Adobe

---

## ❓ Problem
Given the head of a singly linked list, return true if it is a palindrome (reads the same forward and backward).

```
Input:  1 → 2 → 2 → 1
Output: true

Input:  1 → 2 → 3
Output: false
```

---

## 💡 Quick Concept (2 lines only)
Find the middle with slow/fast, reverse the second half in place, then compare both halves node by node.
हिंदी: Middle ढूँढो, दूसरे आधे हिस्से को reverse करो, फिर पहले और दूसरे half को compare करो।

---

## ✅ Solution

```javascript
// Node class (given in interview):
class ListNode {
  constructor(val, next = null) {
    this.val = val;     // node value
    this.next = next;   // next pointer
  }
}

// Helper: build list from array
function createList(arr) {
  const dummy = new ListNode(0);              // dummy head
  let curr = dummy;                           // tail pointer
  for (const v of arr) {                      // each value
    curr.next = new ListNode(v);              // append node
    curr = curr.next;                         // advance tail
  }
  return dummy.next;                          // real head
}

// ============================================
// APPROACH 1: Copy to array + two pointers — O(n) time, O(n) space
// ============================================
function isPalindromeArray(head) {
  const vals = [];                                        // store values
  while (head) { vals.push(head.val); head = head.next; } // copy list to array
  let i = 0, j = vals.length - 1;                         // two ends
  while (i < j) {                                         // compare inward
    if (vals[i] !== vals[j]) return false;                // mismatch => not palindrome
    i++; j--;                                             // move inward
  }
  return true;                                            // all matched
}

// ============================================
// APPROACH 2: Reverse second half in place — O(n) time, O(1) space ✅ PREFERRED
// ============================================
function isPalindrome(head) {
  if (head === null || head.next === null) return true;   // 0 or 1 node is a palindrome

  // Step 1: find middle (slow ends at middle / second middle)
  let slow = head, fast = head;                           // both start at head
  while (fast !== null && fast.next !== null) {           // fast needs 2 nodes ahead
    slow = slow.next;                                     // 1 step
    fast = fast.next.next;                                // 2 steps
  }

  // Step 2: reverse the list starting from slow
  let prev = null, curr = slow;                           // standard reverse
  while (curr !== null) {                                 // until end
    const nextNode = curr.next;                           // save next
    curr.next = prev;                                     // flip link
    prev = curr;                                          // advance prev
    curr = nextNode;                                      // advance curr
  }

  // Step 3: compare first half with reversed second half
  let left = head, right = prev;                          // right = head of reversed half
  while (right !== null) {                                // second half is the shorter/equal one
    if (left.val !== right.val) return false;             // mismatch
    left = left.next;                                     // advance left
    right = right.next;                                   // advance right
  }
  return true;                                            // all matched
}

// ============================================
// TEST CASES
// ============================================
console.log(isPalindromeArray(createList([1, 2, 2, 1])));  // true
console.log(isPalindrome(createList([1, 2, 2, 1])));       // true
console.log(isPalindrome(createList([1, 2, 3, 2, 1])));    // true
console.log(isPalindrome(createList([1, 2, 3])));          // false
console.log(isPalindrome(createList([1, 2])));             // false
console.log(isPalindrome(createList([7])));                // true
console.log(isPalindrome(null));                           // true
```

---

## 🔍 Why It Works
```
1 → 2 → 3 → 2 → 1
Middle = 3. Reverse from 3: second half becomes 1 → 2 → 3 (read from the old tail).
First half (from head): 1 → 2 → 3 (node 3 still links to the old tail's side but we stop with right)
Compare while right != null: 1=1, 2=2, 3=3 => true
```
हिंदी: Reverse करने के बाद दूसरा half पीछे से आगे पढ़ा जाता है, तो सीधा compare करके palindrome पता चल जाता है।

---

## 📊 Complexity
```
Array copy:       Time O(n) | Space O(n)
Reverse 2nd half: Time O(n) | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Restore the list after checking (good practice - don't mutate input)
// After comparison, reverse the second half again and attach it to the first half's tail.

// VARIANT 2: Recursive check using the call stack (O(n) space)
function isPalindromeRec(head) {
  let front = head;                           // pointer moving forward
  function check(node) {
    if (node === null) return true;           // reached end
    if (!check(node.next)) return false;      // go deep first (comes back from the end)
    const ok = node.val === front.val;        // compare back node vs front node
    front = front.next;                       // move front forward
    return ok;                                // result for this level
  }
  return check(head);                         // start recursion
}
console.log(isPalindromeRec(createList([1, 2, 2, 1])));  // true
console.log(isPalindromeRec(createList([1, 2, 3])));     // false
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: comparing the reversed list with the original in a way that breaks
// after reversing from slow, the node before slow still points to slow
// (so the first half "looks" longer by one on odd length) - loop on `right`, not `left`

// ❌ Wrong: converting to a string and comparing - fails for multi-digit values
// [1, 12] -> "112" vs reverse "211" ... ambiguous with other lists

// ✅ Correct: compare value by value; loop until the reversed half ends
```

---

## 🎯 Interview Tip
Say: "Array copy is O(n) space; I can do O(1) space by reversing the second half. I'd mention that this mutates the input, and I can restore it by reversing again if needed." This combines D123 (middle) and D020 (reverse).

---

## 🔗 Related Problems
→ D020 (Reverse Linked List) | D123 (Middle of LL) | D129 (Reorder List)
