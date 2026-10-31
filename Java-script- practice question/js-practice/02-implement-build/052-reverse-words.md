---

# Q052. Reverse Words in Sentence
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `reverseWords(sentence)` that reverses the ORDER of words in a sentence (not the letters inside each word). Extra spaces should be ignored.

```javascript
reverseWords('I love JavaScript'); // 'JavaScript love I'
```

---

## 💡 Quick Concept (2 lines only)
Split the sentence into words, reverse the word array, join back with a space.
हिंदी: वाक्य को शब्दों में तोड़ो, array को उल्टा करो, फिर जोड़ दो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: trim + split on any whitespace run
// Step 2: reverse the words array
// Step 3: join with single space

function reverseWords(sentence) {
  const words = sentence.trim().split(/\s+/); // split on one-or-more spaces
  return words.reverse().join(' ');           // reverse order and join back
}

// ============================================
// TEST CASES
// ============================================

console.log(reverseWords('I love JavaScript'));   // Expected: JavaScript love I
console.log(reverseWords('  hello   world  '));   // Expected: world hello
console.log(reverseWords('single'));              // Expected: single
console.log(reverseWords(''));                    // Expected: (empty line)
```

---

## 🔍 Why This Works (3 lines max)
`/\s+/` treats many spaces as one separator, and `trim()` removes edge spaces so no empty words appear. `reverse()` flips word order and `join(' ')` rebuilds the string.
हिंदी: regex से extra spaces हटते हैं, reverse() शब्दों का क्रम पलटता है।

---

## ⚡ Alternative Solution
```javascript
// Manual loop from the end
function reverseWords2(s) {
  const words = s.split(' ').filter(Boolean); // drop empty strings
  let out = [];                               // result array
  for (let i = words.length - 1; i >= 0; i--) { // walk backwards
    out.push(words[i]);                       // push each word
  }
  return out.join(' ');                       // join result
}
console.log(reverseWords2('a b c')); // Expected: c b a
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: split(' ') keeps empty strings for multiple spaces
console.log('a  b'.split(' ').reverse().join(' ')); // 'b  a' (double space kept, empty word)
// ✅ Correct: split(/\s+/) after trim()
console.log('a  b'.trim().split(/\s+/).reverse().join(' ')); // 'b a'
```

---

## 🎯 Interview Tip (1 line)
Mention edge cases (extra spaces, empty string) and that reversing letters in each word is a different follow-up.

---

## 🔗 Related Questions
→ Q051 (reverse string) | Q053 (palindrome) | Q054 (count vowels)
