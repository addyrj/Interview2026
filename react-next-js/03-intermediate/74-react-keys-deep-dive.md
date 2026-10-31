# 74. React Keys — Deep Dive
# हिंदी में: React Keys — List में identity कैसे तय होती है

---

## 🔵 Simple Definition (English)
A **key** is a special attribute (string or number) that gives an element a stable identity among its **siblings**. React uses it during reconciliation to match old and new items. Keys must be unique among siblings (not globally), and they are **not** passed to the component as a prop.

## 🔵 सरल परिभाषा (Hindi)
**Key** एक खास attribute है (string या number) जो किसी element को उसके **siblings** के बीच stable पहचान देता है। Reconciliation में React इसी से पुराने और नए items को match करता है। Key सिर्फ siblings में unique होनी चाहिए (पूरे app में नहीं), और यह component को **prop के रूप में नहीं** जाती।

---

## 🔴 Problem it Solves
List में items को React बिना key के सिर्फ position (0, 1, 2) से पहचानता है। जब कोई item बीच से हटता है, जुड़ता है या जगह बदलता है, तो हर position का state अगले item पर चला जाता है। उदाहरण: किसी item पर लिखा हुआ note दूसरे item पर दिखने लगता है। React इसके लिए warning देता है: "Each child in a list should have a unique "key" prop."

## 🔴 यह क्यों बना? (Hindi)
Zomato के cart में 5 items हैं, और user बीच वाला item हटाता है। बिना key के, हटाए गए item की quantity या special instructions अगले item पर दिख सकते हैं। Key से React हर item को उसकी असली पहचान (id) से जानता है, इसलिए state सही item के साथ रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List render करते समय हर element को key दो
         {items.map(item => <Row key={item.id} item={item} />)}

Step 2 → React old children की keys का map बनाता है: { a1: fiberA, b2: fiberB, ... }

Step 3 → New children की keys से match करता है:
         key मिला → fiber reuse (state सुरक्षित), सिर्फ props update या move
         key नहीं मिला → नया fiber बनाओ (mount)
         पुरानी key बची → fiber हटाओ (unmount)

Step 4 → Key बदलना = "यह दूसरा item है" का संकेत → पूरा subtree remount

KEY: key = identity. Key stable हो, unique हो, और data से आए, index से नहीं।
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर list item को key दो
Step 2 → React पुरानी keys का map बनाता है
Step 3 → नई keys से match: मिला → state सुरक्षित, नहीं मिला → नया, बची पुरानी → हटाओ
Step 4 → Key बदलना = नया item → remount
KEY: key = पहचान। Stable, unique, data से हो।
```

---

## 🟡 Real World Example
**Zomato cart:** Cart में "Biryani", "Raita", "Coke" हैं। हर item पर special instruction input है। User "Raita" हटाता है। `key={item.id}` से React जानता है कि "Biryani" और "Coke" वही items हैं, इसलिए उनके instructions बचे रहते हैं। अगर key index होती, तो "Coke" का instruction अब position 1 पर आए item को दिख जाता।

## 🟡 Real Example Hindi mein
**Zomato cart:** Cart में "Biryani", "Raita", "Coke" हैं, हर item पर special instruction input है। User "Raita" हटाता है। `key={item.id}` से "Biryani" और "Coke" के instructions सुरक्षित रहते हैं। Index key होती, तो "Coke" का instruction अगली position पर आए item पर दिख जाता।

---

## 💻 Code Example — Basic

```jsx
import { useState } from 'react';

// ── BASIC: key = stable unique id ──
export default function ShoppingList() {
  const [items, setItems] = useState([
    { id: 'a1', name: 'Atta' },        // unique id — यह कभी नहीं बदलती
    { id: 'b2', name: 'Dal' },         // unique id
    { id: 'c3', name: 'Chawal' },      // unique id
  ]);

  // id से हटाओ, index से नहीं (index बीच में हटने पर बदल जाता है)
  function removeItem(id) {
    setItems(prev => prev.filter(item => item.id !== id)); // नई array, वही ids
  }

  return (
    <ul>
      {items.map(item => (
        // key = item.id: React जानता है कि कौन-सा <li> वही item है
        <li key={item.id}>
          {item.name}
          <input placeholder="मात्रा" />           {/* uncontrolled input: value DOM में है, key से जुड़ी */}
          <button onClick={() => removeItem(item.id)}>हटाओ</button>
        </li>
      ))}
    </ul>
  );
}
// "Dal" की input में कुछ लिखो, फिर "Atta" हटाओ → "Dal" की लिखी मात्रा उसी row में रहेगी
```

## 💻 Code Example — Advanced

```jsx
import { Fragment, useState } from 'react';

// ── ADVANCED: key के तीन उपयोग ──
// 1) stable identity  2) key बदलकर जानबूझकर reset  3) Fragment के साथ group

// Form: initial state सिर्फ पहली बार mount पर लिया जाता है
function ProfileEditor({ user }) {
  const [name, setName] = useState(user.name);     // user.name बदलने पर यह अपने-आप नहीं बदलता
  return (
    <form>
      <label>
        नाम:
        <input value={name} onChange={e => setName(e.target.value)} />
      </label>
    </form>
  );
}

export default function Users({ users }) {           // users: कम से कम एक user होना चाहिए
  const [selectedId, setSelectedId] = useState(users[0].id); // कौन-सा user चुना है
  const selected = users.find(u => u.id === selectedId);     // वह user object

  return (
    <div>
      {users.map(u => (
        <button key={u.id} onClick={() => setSelectedId(u.id)}>{u.name}</button>
      ))}
      {/* key={selected.id}: user बदला → key बदली → ProfileEditor remount → नया user का name */}
      <ProfileEditor key={selected.id} user={selected} />
      {/* बिना key के, input में पुराने user का नाम रह जाता, क्योंकि state सिर्फ पहली बार लिया गया */}
    </div>
  );
}

// Fragment के साथ key: एक item के लिए दो elements (dt + dd) group करने हों
// <>...</> shorthand में key नहीं लगती, इसलिए full Fragment लिखो
function Glossary({ terms }) {
  return (
    <dl>
      {terms.map(t => (
        <Fragment key={t.id}>                       {/* key यहां, Fragment पर */}
          <dt>{t.word}</dt>
          <dd>{t.meaning}</dd>
        </Fragment>
      ))}
    </dl>
  );
}
```

---

## 🟠 Real app integration

Next.js Server Component में DB से आए data की `id` ही key बनती है। Search query बदलने पर पूरे results section को नए सिरे से दिखाने के लिए `Suspense` पर key का उपयोग होता है।

```jsx
// app/orders/page.js — Server Component: DB id से key
export default async function OrdersPage() {
  const orders = await getOrders();                    // तुम्हारा data layer (illustrative)
  return (
    <ul>
      {orders.map(order => (
        <li key={order.id}>                            {/* DB की stable id, index नहीं */}
          Order #{order.id} — {order.status}
        </li>
      ))}
    </ul>
  );
}
```

```jsx
// app/search/page.js — query बदलने पर Suspense fallback फिर से दिखे
import { Suspense } from 'react';
import Results from './Results';                       // async Server Component

export default async function Page({ searchParams }) {
  const { q = '' } = await searchParams;               // Next 15+: searchParams एक Promise है
  return (
    // key={q}: q बदला → Suspense boundary नया बना → fallback दोबारा दिखता है
    <Suspense key={q} fallback={<p>"{q}" खोजा जा रहा है...</p>}>
      <Results query={q} />
    </Suspense>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Reorder या delete वाली list में index को key बनाना
```jsx
// ❌ Wrong: item हटने पर हर row का state अगले item पर चला जाता है
{items.map((item, index) => <CartRow key={index} item={item} />)}

// ✅ Right: data की stable id को key बनाओ
{items.map(item => <CartRow key={item.id} item={item} />)}
```

❌ **Mistake 2:** Render के दौरान random key बनाना
```jsx
// ❌ Wrong: हर render पर नई key → हर बार remount → input focus और text खो जाता है
{items.map(item => <Row key={Math.random()} item={item} />)}

// ✅ Right: key एक बार बनाओ और data के साथ रखो (जैसे creation के समय)
const [items, setItems] = useState(() =>
  rawData.map(d => ({ ...d, uid: crypto.randomUUID() })) // एक बार, initial state में
);
{items.map(item => <Row key={item.uid} item={item} />)}  // uid stable
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';

function Item({ label }) {
  const [clicks, setClicks] = useState(0);         // हर Item का अपना counter
  return <button onClick={() => setClicks(c => c + 1)}>{label}: {clicks}</button>;
}

export default function App() {
  const [items, setItems] = useState(['A', 'B']);
  return (
    <div>
      <button onClick={() => setItems(['X', ...items])}>X आगे जोड़ो</button>
      {items.map((label, i) => <Item key={i} label={label} />)} {/* index key */}
    </div>
  );
}
// मान लो: पहले "A" पर 2 बार click किया (A: 2, B: 0)।
// फिर "X आगे जोड़ो" दबाया। अब बटन क्या दिखाएंगे?
```

**Answer:** Screen पर `X: 2`, `A: 0`, `B: 0` दिखेगा। Index keys के कारण React key `0` वाले `Item` को पहचानता है, जिसका state `clicks = 2` था। नया label `X` उसी instance को मिलता है, इसलिए `X: 2` दिखता है। Key `1` वाला instance (state 0) अब label `A` पाता है, तो `A: 0` दिखता है, जबकि असल में `A` के clicks 2 थे। Key `2` नया है, इसलिए `B: 0`। यानी count गलत item पर चला गया। Fix: `key={label}` (unique हो तो) या हर item को stable id दो।

---

## ⚫ Interview Questions + Answers

**Q1: Key का मुख्य काम क्या है?**
A1: Reconciliation में siblings के बीच element की identity तय करना। Key same रहे तो React instance और state reuse करता है। Key बदले तो पुराना instance हटाकर नया बनाता है।

**Q2: Key को component के अंदर prop के रूप में पढ़ा जा सकता है?**
A2: नहीं। `key` React द्वारा reserved है और props में नहीं जाती। अगर component को id चाहिए, तो उसे अलग नाम से पास करो, जैसे `id={item.id}`।

**Q3: Key कितनी जगह unique होनी चाहिए?**
A3: सिर्फ उसी parent के siblings के बीच। अलग-अलग lists में same key हो सकती है, कोई problem नहीं।

**Q4: `key` से component को जानबूझकर reset कैसे करते हैं?**
A4: Key बदल दो। जैसे `<Editor key={docId} />`: docId बदला तो Editor पूरी तरह नया बनता है, और उसका internal state initial values से शुरू होता है। यह "uncontrolled state reset" का सबसे साफ तरीका है।

**Q5: Index key कब ठीक है?**
A5: जब list static हो (कभी reorder, insert, delete न हो), items में कोई state न हो, और items की संख्या बदलती न हो। Dynamic lists में index key से bugs आते हैं।

---

## 🔷 When to Use + When Not to Use
✅ **Use keys when:**
- List के items में state (input, toggle, animation) हो
- Items reorder, insert या delete होते हों
- Database id या unique slug उपलब्ध हो
- Component को जानबूझकर reset करना हो (`key={entityId}`)

❌ **Avoid when:**
- Index को key बनाना, जबकि list dynamic हो
- `Math.random()` या `Date.now()` को key बनाना (हर render पर बदलता है)
- Duplicate keys देना (React warning देता है और gaps में bugs आते हैं)
- Key को component को पास करके उसके अंदर prop की तरह पढ़ने की उम्मीद करना

---

## 📊 Visual Diagram

```
Items: [Atta(a1), Dal(b2), Chawal(c3)]     Remove "Dal"

INDEX KEYS:
  before: 0→Atta   1→Dal   2→Chawal
  after:  0→Atta   1→Chawal          (key 1 अब Chawal है)
  React:  key 1 का state (Dal की मात्रा) → Chawal को मिलता है ❌
          key 2 unmount

ID KEYS:
  before: a1→Atta   b2→Dal   c3→Chawal
  after:  a1→Atta            c3→Chawal
  React:  b2 unmount (Dal का state हटा) ✅
          a1 और c3 के state सही जगह ✅
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Key | Siblings में element की पहचान | Siblings में element की पहचान |
| Sibling | एक ही parent के नीचे के elements | एक ही parent के नीचे के elements |
| Identity | Reconciliation में instance पहचानने का आधार | Instance पहचानने का आधार |
| Remount | Component को नए सिरे से mount करना | Component को नए सिरे से बनाना |
| Index key | Array की position को key बनाना | Array की position को key बनाना |
| Fragment key | `<Fragment key>` से group को key देना | Group को key देना |

---

## ⚡ 3-Line Summary
**English:**
1. Key siblings में element की stable identity है; React इसी से state को सही item के साथ रखता है।
2. Dynamic lists में index key न लगाओ, और render के दौरान random key मत बनाओ।
3. Key बदलकर किसी component को जानबूझकर remount और reset करो, जैसे `key={docId}`।

**Hindi:**
1. Key siblings में element की stable identity है; React इसी से state को सही item के साथ रखता है।
2. Dynamic lists में index key न लगाओ, और render के दौरान random key मत बनाओ।
3. Key बदलकर किसी component को जानबूझकर remount और reset करो, जैसे `key={docId}`।

---

## ➡️ Next Topic
**75. Controlled Forms — Best Practices** — `value` और `onChange` से forms बनाना, derived state से बचना, और React 19 form actions।
