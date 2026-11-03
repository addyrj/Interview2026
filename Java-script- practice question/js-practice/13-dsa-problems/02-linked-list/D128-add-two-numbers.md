---

# D128. Add Two Numbers
# Category: DSA — Linked List
# Difficulty: ⭐⭐ Medium | LeetCode #2 | Asked: Amazon, Microsoft, Google, Adobe, Flipkart

---

## ❓ Problem
Two non-empty linked lists represent two non-negative integers with digits stored in reverse order (one digit per node). Add the numbers and return the sum as a linked list in the same format.

```
Input:  l1 = 2 → 4 → 3 (342), l2 = 5 → 6 → 4 (465)
Output: 7 → 0 → 8 (807)
```

---

## 💡 Quick Concept (2 lines only)
Simulate grade-school addition: add digits plus carry, store sum % 10, carry = floor(sum / 10). Continue while any list or carry remains.
हिंदी: Digit by digit जोड़ो, carry आगे ले जाओ — sum % 10 node में डालो और sum / 10 carry बनेगा।

---

## ✅ Solution

```javascript
// Node class (given in interview):
class ListNode {
  constructor(val, next = null) {
    this.val = val;     // node value (a digit)
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

// Helper: print list
function printList(head) {
  const vals = [];                                        // collected values
  while (head) { vals.push(head.val); head = head.next; } // walk
  return vals.length ? vals.join(' → ') : 'null';         // readable string
}

// ============================================
// APPROACH 1: Convert to BigInt, add, rebuild — O(n+m) time, O(n+m) space
// (Number would lose precision for long lists, so BigInt is needed)
// ============================================
function addTwoNumbersBigInt(l1, l2) {
  const toBig = (h) => {                      // list -> BigInt (reverse order digits)
    let s = '';                               // build digit string
    while (h) { s = h.val + s; h = h.next; }  // prepend so most significant is first
    return BigInt(s);                         // convert to BigInt
  };
  const sum = (toBig(l1) + toBig(l2)).toString(); // add and stringify
  const digits = sum.split('').reverse().map(Number); // back to reverse digit array
  return createList(digits);                  // rebuild list
}

// ============================================
// APPROACH 2: Digit-by-digit with carry — O(max(n,m)) time, O(1) extra space ✅ PREFERRED
// ============================================
function addTwoNumbers(l1, l2) {
  const dummy = new ListNode(0);              // dummy head for result
  let tail = dummy;                           // tail of result list
  let carry = 0;                              // carry from previous digit

  while (l1 !== null || l2 !== null || carry !== 0) { // keep going while anything is left
    const x = l1 !== null ? l1.val : 0;       // digit from l1 (0 if ended)
    const y = l2 !== null ? l2.val : 0;       // digit from l2 (0 if ended)
    const sum = x + y + carry;                // column sum
    carry = Math.floor(sum / 10);             // new carry (0 or 1)
    tail.next = new ListNode(sum % 10);       // append the digit
    tail = tail.next;                         // advance tail
    if (l1 !== null) l1 = l1.next;            // move l1 if possible
    if (l2 !== null) l2 = l2.next;            // move l2 if possible
  }
  return dummy.next;                          // skip dummy
}

// ============================================
// TEST CASES
// ============================================
console.log(printList(addTwoNumbersBigInt(createList([2, 4, 3]), createList([5, 6, 4])))); // 7 → 0 → 8
console.log(printList(addTwoNumbers(createList([2, 4, 3]), createList([5, 6, 4]))));      // 7 → 0 → 8
console.log(printList(addTwoNumbers(createList([0]), createList([0]))));                  // 0
console.log(printList(addTwoNumbers(createList([9, 9, 9, 9, 9, 9, 9]), createList([9, 9, 9, 9])))); // 8 → 9 → 9 → 9 → 0 → 0 → 0 → 1
console.log(printList(addTwoNumbers(createList([5]), createList([5]))));                  // 0 → 1
console.log(printList(addTwoNumbers(createList([1, 8]), createList([0]))));               // 1 → 8
```

---

## 🔍 Why It Works
```
  2 4 3      (342)
+ 5 6 4      (465)
col 1: 2+5 = 7,  carry 0 -> 7
col 2: 4+6 = 10, carry 1 -> 0
col 3: 3+4+1 = 8, carry 0 -> 8
Result: 7 → 0 → 8   (807)
Reverse order means the least significant digit comes first, exactly the order we add in.
```
हिंदी: Digits reverse order में हैं, यानी units वाला digit पहले आता है — बिल्कुल वही क्रम जिसमें हम जोड़ते हैं।

---

## 📊 Complexity
```
BigInt:     Time O(n+m) | Space O(n+m)
Carry loop: Time O(max(n,m)) | Space O(1) extra (output list excluded) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Digits stored in FORWARD order (LeetCode #445) - use two stacks
function addTwoNumbersForward(l1, l2) {
  const s1 = [], s2 = [];                      // stacks of digits
  for (let p = l1; p; p = p.next) s1.push(p.val); // push l1 digits
  for (let p = l2; p; p = p.next) s2.push(p.val); // push l2 digits
  let carry = 0, head = null;                  // result built by prepending
  while (s1.length || s2.length || carry) {    // while digits or carry remain
    const sum = (s1.pop() || 0) + (s2.pop() || 0) + carry; // pop least significant
    carry = Math.floor(sum / 10);              // new carry
    head = new ListNode(sum % 10, head);       // prepend digit
  }
  return head;                                 // most significant first
}
console.log(printList(addTwoNumbersForward(createList([7, 2, 4, 3]), createList([5, 6, 4]))));  // 7 → 8 → 0 → 7
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: stopping when both lists end, forgetting the final carry
while (l1 || l2) { ... }          // 5 + 5 gives 0 instead of 0 → 1

// ❌ Wrong: converting lists to Number and adding -> precision loss beyond 2^53
// ✅ Correct: loop while (l1 || l2 || carry), treat missing digits as 0
```

---

## 🎯 Interview Tip
Say: "Reverse order is a gift — I add from the least significant digit just like by hand. Loop until both lists and the carry are done, using a dummy head." Mention BigInt/Number overflow is why we do not convert to integers.

---

## 🔗 Related Problems
→ D120 (Merge Two Sorted Lists) | D020 (Reverse Linked List) | D133 (Merge K Sorted Lists)
