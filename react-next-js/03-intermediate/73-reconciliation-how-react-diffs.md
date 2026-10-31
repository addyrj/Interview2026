# 73. Reconciliation — How React Diffs
# हिंदी में: Reconciliation — React पुराने और नए UI की तुलना कैसे करता है

---

## 🔵 Simple Definition (English)
**Reconciliation** is the algorithm React uses to compare the previous render tree with the new one and work out the minimum set of DOM changes needed. It compares **element types** and **keys** level by level, and reuses existing component instances (and their state) wherever it can.

## 🔵 सरल परिभाषा (Hindi)
**Reconciliation** वह algorithm है जिससे React पिछले render वाले tree और नए tree की तुलना करता है, और DOM में सबसे कम ज़रूरी बदलाव तय करता है। यह हर level पर **element type** और **keys** देखता है, और जहां हो सके वहां पुराने component instances (और उनका state) दोबारा use करता है।

---

## 🔴 Problem it Solves
अगर हर state change पर React पूरा DOM दोबारा बनाता, तो हर keystroke पर पूरा page नए सिरे से build होता और बहुत धीमा होता। दूसरी तरफ, अगर React सिर्फ "कुछ बदला है" कहकर छोड़ देता, तो DOM सही नहीं रहता। Reconciliation एक तय नियम-सेट देता है जिससे React तेज़ी से पता कर सके कि कौन-सा node बदला, कौन-सा नया है, और कौन-सा हटाना है। पूरे tree की generic diff (O(n³)) की जगह React O(n) heuristics use करता है।

## 🔴 यह क्यों बना? (Hindi)
Razorpay checkout जैसी page पर हर input change पर पूरा form नए सिरे से बने तो typing lag होगी। Reconciliation से सिर्फ बदला हुआ input node अपडेट होता है, बाकी form वैसे ही रहता है। साथ ही, state कहां सुरक्षित रहेगा (किस component instance में), यह भी इसी नियम से तय होता है, इसलिए इसे समझना bugs ढूंढने में बहुत मदद करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Render phase: React component functions call करता है और नया element tree बनाता है
         (यह phase pure है, इसे React रोक भी सकता है — concurrent rendering में)

Step 2 → Diffing: हर level पर पुराने और नए elements compare करो
         Rule A: Type अलग? (div → section) → पुरा subtree unmount, नया mount
         Rule B: Type same? (div → div) → instance reuse, सिर्फ props update
         Rule C: Lists में keys मिलाओ → same key = same item

Step 3 → Children की तुलना recursively होती है (depth-first)

Step 4 → Commit phase: सिर्फ जरूरी DOM mutations एक साथ लागू होते हैं
         और effects (useLayoutEffect, फिर useEffect) चलते हैं

Step 5 → Fiber tree: हर element एक fiber node है (child, sibling, return pointers)
         React दो trees रखता है: current (स्क्रीन पर) और work-in-progress (नया)

KEY: Type + Key = identity. Identity बदली → state नया। Identity वही → state सुरक्षित।
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Render phase: components चलाकर नया element tree बनता है
Step 2 → Diff: हर level पर type और key देखो
         Type अलग → पूरा subtree नया (state खत्म)
         Type same → instance और state रहता है, props अपडेट
         Lists में key से match करो
Step 3 → Children पर वही नियम, नीचे तक
Step 4 → Commit: DOM में सिर्फ बदलाव लागू, फिर effects
Step 5 → Fiber: हर node का अपना work record; current और work-in-progress tree
KEY: Type + Key = पहचान। पहचान बदली तो state भी नया।
```

---

## 🟡 Real World Example
**Swiggy order tracking:** Order status page पर एक "Track" section है जिसमें map और timeline है। Status "Preparing" से "On the way" होने पर सिर्फ status text और map marker बदलता है, क्योंकि दोनों पिछले render में same type के थे। Map का internal state (zoom, pan) बचा रहता है। लेकिन अगर Developer ने conditional rendering में `<div>` को `<section>` से बदल दिया, तो पूरा map unmount और दोबारा mount होता, और user का zoom reset हो जाता।

## 🟡 Real Example Hindi mein
**Swiggy order tracking:** Status "Preparing" से "On the way" होने पर सिर्फ status text और map marker बदलते हैं, क्योंकि element types वही थे। Map का zoom और pan बचा रहता है। पर अगर conditional render में `<div>` को `<section>` से बदल दिया, तो पूरा map unmount होकर दोबारा बनता और user का zoom reset हो जाता।

---

## 💻 Code Example — Basic

```jsx
import { useState } from 'react';                  // useState React से

// ── BASIC: element type बदलने पर state खो जाता है ──
function Counter() {
  const [count, setCount] = useState(0);           // state इस component के fiber में रहता है
  return (
    <button onClick={() => setCount(c => c + 1)}>
      Count: {count}                               {/* अभी का count दिखाओ */}
    </button>
  );
}

export default function App() {
  const [isWrapped, setIsWrapped] = useState(false); // toggle: किस wrapper में Counter है

  return (
    <div>
      <button onClick={() => setIsWrapped(w => !w)}>Wrapper बदलो</button>
      {isWrapped
        ? <section><Counter /></section>            // type "section" — पहले "div" था
        : <div><Counter /></div>}                   // type "div" — type बदला → Counter remount, count 0
    </div>
  );
}
// Counter को 5 बार बढ़ाओ, फिर wrapper बदलो → count 0 हो जाएगा, क्योंकि Counter नया mount हुआ
```

## 💻 Code Example — Advanced

```jsx
import { useCallback, useState } from 'react';

// ── ADVANCED: List reconciliation — keys से state कहां जाता है ──

// Row का अपना local state है (हर row का अलग draft text)
function TodoRow({ todo, onToggleExpand }) {
  const [draft, setDraft] = useState('');          // यह state row के fiber से बंधा है
  return (
    <li>
      <button onClick={() => onToggleExpand(todo.id)}>{todo.title}</button>
      <input value={draft} onChange={e => setDraft(e.target.value)} placeholder="note" />
    </li>
  );
}

export default function TodoList({ initialTodos }) {
  const [todos, setTodos] = useState(initialTodos); // [{ id, title }, ...]
  const [expanded, setExpanded] = useState(null);   // कौन-सा item खुला है

  // useCallback: child को stable function मिले (memo से पहले भी अच्छी आदत)
  const handleToggle = useCallback(
    id => setExpanded(e => (e === id ? null : id)), // same id दोबारा → बंद
    []
  );

  // पहला item आख़िर में भेजो। नई array बनती है, पर हर item की key (id) वही रहती है।
  function moveFirstToLast() {
    setTodos(prev => [...prev.slice(1), prev[0]]);
  }

  return (
    <div>
      <button onClick={moveFirstToLast}>पहला item आखिर में</button>
      <ul>
        {todos.map(todo => (
          // key = todo.id: reconciliation हर row को उसकी id से पहचानता है।
          // Reorder होने पर React rows को move करता है, दोबारा नहीं बनाता, इसलिए draft text सही row के साथ रहता है।
          // key={index} होती तो text गलत row में चला जाता।
          <TodoRow key={todo.id} todo={todo} onToggleExpand={handleToggle} />
        ))}
      </ul>
      <p>Expanded: {expanded ?? 'none'}</p>
    </div>
  );
}
```

---

## 🟠 Real app integration

Next.js (App Router) में अक्सर आप **key** से जानबूझकर remount करवाते हैं, जैसे route बदलने पर page-level animation या state reset करने के लिए।

```jsx
// app/components/PageTransition.js — Client Component
'use client';                                       // usePathname सिर्फ client पर चलता है
import { usePathname } from 'next/navigation';      // वर्तमान URL path

export default function PageTransition({ children }) {
  const pathname = usePathname();                   // जैसे "/orders" या "/cart"
  return (
    // key = pathname: path बदलते ही यह div नया बनता है → अंदर का state और animation reset
    <div key={pathname} className="fade-in">
      {children}
    </div>
  );
}
```

```jsx
// app/layout.js — layout में wrap करो
import PageTransition from './components/PageTransition';
export default function RootLayout({ children }) {
  return (
    <html lang="hi">
      <body>
        <PageTransition>{children}</PageTransition> {/* हर route change पर remount */}
      </body>
    </html>
  );
}
```

ध्यान दें: `key` का यह इस्तेमाल जानबूझकर है। बिना किसी कारण के key बदलना performance और state दोनों को बिगाड़ता है।

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Component को conditionally अलग wrapper में डालना, जिससे type बदले
```jsx
// ❌ Wrong: type बदलने से Video player का state (play position) खो जाता है
{isFullscreen ? <div className="full"><Player /></div> : <section><Player /></section>}

// ✅ Right: wrapper का type एक जैसा रखो, सिर्फ className बदलो
<section className={isFullscreen ? 'full' : 'normal'}>
  <Player />                                 {/* Player का instance बचा रहेगा */}
</section>
```

❌ **Mistake 2:** Component definition को render के अंदर लिखना
```jsx
// ❌ Wrong: हर render पर नया function बनता है → नया type → हर बार remount
function Parent() {
  function Inner() { return <input />; }     // हर render पर नया component type
  return <Inner />;                          // input का focus और text हर बार खो जाता है
}

// ✅ Right: component को module scope पर रखो
function Inner() { return <input />; }       // एक बार define
function Parent() { return <Inner />; }      // same type हर render में
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';

function Child() {
  const [text, setText] = useState('');            // Child का अपना state
  return <input value={text} onChange={e => setText(e.target.value)} />;
}

export default function App() {
  const [showBanner, setShowBanner] = useState(true);
  return (
    <div>
      {showBanner && <p>Welcome!</p>}              {/* slot 0 */}
      <Child />                                    {/* slot 1 */}
      <button onClick={() => setShowBanner(false)}>Banner बंद करो</button>
    </div>
  );
}
// Question: Child के input में "abc" type करने के बाद Banner बंद करो।
// क्या input का text "abc" बचेगा, या खाली हो जाएगा?
```

**Answer:** Text **बचेगा**, यानी `abc` दिखता रहेगा। `showBanner && <p>` जब `false` होता है तो React उस slot में `false` रखता है, खाली जगह नहीं छोड़ता। यानी `Child` हर render में children के दूसरे position (index 1) पर रहता है। Element type (`Child`) और position दोनों वही हैं, इसलिए reconciliation उसी fiber को reuse करता है और state सुरक्षित रहता है। लोग अक्सर सोचते हैं कि banner हटने से component remount होगा, पर ऐसा नहीं होता। अगर banner को `{showBanner ? <Banner /> : <Other />}` के रूप में बदलते, तब type बदलता और state खो जाता।

---

## ⚫ Interview Questions + Answers

**Q1: Reconciliation क्या है?**
A1: React का वह algorithm जो पिछले और नए element tree की तुलना करके सबसे कम DOM बदलाव तय करता है। यह element type, key और position देखता है।

**Q2: React दो elements को "same" कब मानता है?**
A2: Same position पर, same type (जैसे `div` और `div`, या एक ही component function), और lists में same key। Type या key अलग हो तो React पूरा subtree नया बनाता है।

**Q3: Fiber क्या है?**
A3: Fiber React का internal data structure है, हर element/component के लिए एक node, जिसमें child, sibling और return pointers होते हैं। Fiber से React work को टुकड़ों में कर सकता है, रोक सकता है और प्राथमिकता तय कर सकता है। React दो fiber trees रखता है: current (स्क्रीन पर) और work-in-progress (अगला)।

**Q4: Render phase और commit phase में क्या फर्क है?**
A4: Render phase में components चलते हैं और नया tree बनता है, यह pure होना चाहिए और रोका जा सकता है। Commit phase में DOM बदलता है और effects चलते हैं, यह synchronous और अटल होता है।

**Q5: List में index को key बनाना क्यों खतरनाक है?**
A5: Index key से React reorder, insert या delete में items को गलत पहचानता है। Row का local state (जैसे input text) अगले item पर चला जाता है। Stable और unique id (जैसे database id) का इस्तेमाल करो।

---

## 🔷 When to Use + When Not to Use
✅ **Understand and use reconciliation knowledge when:**
- Conditional rendering में wrapper या component type बदल रहे हो
- Lists में reorder, insert या delete होता है
- State अचानक खो रहा हो, और यह समझना हो कि remount क्यों हुआ
- Animation या route-level reset के लिए key को जानबूझकर बदलना हो

❌ **Avoid / Don't do when:**
- Element type को बिना कारण हर render में बदलना
- Component के अंदर function या class define करना
- List में index को key बनाना, जब items बदलते हों
- Key को random (`Math.random()`) बनाना, जिससे हर render पर नया identity बने

---

## 📊 Visual Diagram

```
Render 1 (पुराना tree)              Render 2 (नया tree)           Result
─────────────────────────────────────────────────────────────────────────────
<div>                               <div>                         same type
  <Counter/>   (fiber A, count=5)     <Counter/>  (fiber A)       → state रहा ✅
</div>                              </div>

<div>                               <section>                     type बदला
  <Counter/>   (fiber A, count=5)     <Counter/>  (fiber B, 0)    → Counter remount ❌
</div>                              </section>

List with keys:
  old: [A, B, C]                    new: [C, A, B]
  key-match:  A↔A  B↔B  C↔C         → React सिर्फ move करता है,
                                      state सबका सुरक्षित ✅

  old: [0:A, 1:B, 2:C]              new: [0:C, 1:A, 2:B]   (index keys)
  index-match: 0↔0  1↔1  2↔2        → React सोचता है "text बदला",
                                      state गलत item पर चला जाता है ❌
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reconciliation | पुराने और नए tree की तुलना करने की प्रक्रिया | पुराने और नए tree की तुलना |
| Diffing | दो trees में अंतर निकालना | दो trees में फर्क निकालना |
| Element type | Tag (`div`) या component function, जो identity तय करता है | पहचान तय करने वाला tag या component |
| Fiber | React का internal node, हर element के लिए | हर element के लिए React का internal node |
| Render phase | Components चलाकर नया tree बनाने का चरण | नया tree बनाने का चरण |
| Commit phase | DOM में बदलाव लागू करने का चरण | DOM में बदलाव लागू करने का चरण |
| Work-in-progress tree | अगला render तैयार करने वाला tree | अगला render तैयार करने वाला tree |

---

## ⚡ 3-Line Summary
**English:**
1. Reconciliation पुराने और नए element tree की तुलना element type, key और position से करता है।
2. Type या key बदले तो subtree remount होता है और state खो जाता है; वही रहे तो state सुरक्षित रहता है।
3. Lists में stable keys दो, index नहीं; और wrapper या component को render के अंदर बदलने से बचो।

**Hindi:**
1. Reconciliation पुराने और नए element tree की तुलना element type, key और position से करता है।
2. Type या key बदले तो subtree remount होता है और state खो जाता है; वही रहे तो state सुरक्षित रहता है।
3. Lists में stable keys दो, index नहीं; और wrapper या component को render के अंदर बदलने से बचो।

---

## ➡️ Next Topic
**74. React Keys — Deep Dive** — key के हर उपयोग, index key के खतरे, और key से जानबूझकर reset करने की तकनीक।
