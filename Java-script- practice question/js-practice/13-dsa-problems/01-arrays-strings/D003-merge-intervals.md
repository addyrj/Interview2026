---

# D003. Merge Intervals
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐ Medium | LeetCode #56 | Asked: Google, Amazon, Flipkart, Swiggy

---

## ❓ Problem
Given an array of intervals `[[start, end], ...]`, merge all overlapping intervals and return the result.

```javascript
merge([[1,3],[2,6],[8,10],[15,18]]);  // [[1,6],[8,10],[15,18]]
merge([[1,4],[4,5]]);                  // [[1,5]]  (touching = overlapping)
merge([[1,4],[0,4]]);                  // [[0,4]]
```

---

## 💡 Quick Concept (2 lines only)
Sort by start time. Walk through: if current interval overlaps with previous (current.start ≤ prev.end), merge by extending end. Otherwise, push as new interval.
हिंदी: Start से sort करो — अगला interval overlap करे (start ≤ prev end) तो merge करो, नहीं तो नया add करो।

---

## ✅ Solution

```javascript
// ============================================
// SOLUTION — O(n log n) time, O(n) space
// ============================================

function merge(intervals) {
  if (intervals.length <= 1) return intervals;
  
  // Step 1: Sort by start time
  intervals.sort((a, b) => a[0] - b[0]);
  
  const result = [intervals[0]];  // Step 2: start with first interval
  
  for (let i = 1; i < intervals.length; i++) {
    const current = intervals[i];
    const last = result[result.length - 1];  // last merged interval
    
    // Step 3: Does current overlap with last?
    if (current[0] <= last[1]) {
      // YES — merge: extend the end if current end is larger
      last[1] = Math.max(last[1], current[1]);
    } else {
      // NO — no overlap, add as new interval
      result.push(current);
    }
  }
  
  return result;
}

// ============================================
// TEST CASES
// ============================================

console.log(merge([[1,3],[2,6],[8,10],[15,18]]));
// [[1,6],[8,10],[15,18]]

console.log(merge([[1,4],[4,5]]));
// [[1,5]] — touching intervals DO overlap (4 ≤ 4)

console.log(merge([[1,4],[0,4]]));
// [[0,4]] — unsorted input, sort handles it

console.log(merge([[1,4],[2,3]]));
// [[1,4]] — completely contained: [2,3] inside [1,4]

console.log(merge([[1,4]]));
// [[1,4]] — single interval

// WALKTHROUGH for [[1,3],[2,6],[8,10],[15,18]]:
// After sort: [[1,3],[2,6],[8,10],[15,18]]
// result = [[1,3]]
// [2,6]: 2 ≤ 3 → overlap, end = max(3,6) = 6 → result = [[1,6]]
// [8,10]: 8 > 6 → no overlap → result = [[1,6],[8,10]]
// [15,18]: 15 > 10 → no overlap → result = [[1,6],[8,10],[15,18]]
```

---

## 🔍 Why This Works
After sorting by start, overlapping intervals are always adjacent. For overlap check: `current.start ≤ last.end` (not `<` — touching counts). Merge by taking `max(last.end, current.end)` to handle contained intervals.
हिंदी: Sort के बाद overlapping intervals adjacent होते हैं — `current.start ≤ last.end` होने पर merge करो।

---

## 📊 Complexity
```
Time:  O(n log n) — dominated by sort
Space: O(n) — output array
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Insert new interval into sorted merged list (LeetCode #57)
function insertInterval(intervals, newInterval) {
  const result = [];
  let i = 0, n = intervals.length;
  const [newStart, newEnd] = newInterval;
  
  // Add all intervals that end before newInterval starts
  while (i < n && intervals[i][1] < newStart) result.push(intervals[i++]);
  
  // Merge overlapping intervals with newInterval
  let mergedStart = newStart, mergedEnd = newEnd;
  while (i < n && intervals[i][0] <= mergedEnd) {
    mergedStart = Math.min(mergedStart, intervals[i][0]);
    mergedEnd = Math.max(mergedEnd, intervals[i][1]);
    i++;
  }
  result.push([mergedStart, mergedEnd]);
  
  // Add remaining
  while (i < n) result.push(intervals[i++]);
  return result;
}
console.log(insertInterval([[1,3],[6,9]], [2,5]));  // [[1,5],[6,9]]

// VARIANT 2: Meeting Rooms — can one person attend all? (LeetCode #252)
function canAttendMeetings(intervals) {
  intervals.sort((a, b) => a[0] - b[0]);
  for (let i = 1; i < intervals.length; i++) {
    if (intervals[i][0] < intervals[i-1][1]) return false;  // overlap!
  }
  return true;
}

// VARIANT 3: Minimum meeting rooms needed (LeetCode #253)
function minMeetingRooms(intervals) {
  const starts = intervals.map(i => i[0]).sort((a,b) => a-b);
  const ends = intervals.map(i => i[1]).sort((a,b) => a-b);
  let rooms = 0, endPtr = 0;
  for (let i = 0; i < starts.length; i++) {
    if (starts[i] < ends[endPtr]) rooms++;
    else endPtr++;
  }
  return rooms;
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting to sort first
// Intervals might not be in order — algorithm only works on sorted input

// ❌ Wrong: checking strict overlap (misses touching intervals)
if (current[0] < last[1]) { ... }  // misses [[1,4],[4,5]] case
// ✅ Correct: use <= 
if (current[0] <= last[1]) { ... }  // [4,5] touches [1,4] → merge to [1,5]

// ❌ Wrong: not handling contained intervals (current end < last end)
last[1] = current[1];  // WRONG: [1,4] then [2,3] would set end to 3!
// ✅ Correct: take max of both ends
last[1] = Math.max(last[1], current[1]);
```

---

## 🎯 Interview Tip
Say: "Key steps: sort by start → iterate → if overlap (current.start ≤ last.end) merge by taking max end; edge case: contained intervals — always use Math.max for end."

---

## 🔗 Related Problems
→ D001 (Two Sum) | D004 (Valid Parentheses) | D011 (Meeting Rooms II)
