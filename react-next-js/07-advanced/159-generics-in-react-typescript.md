# 159. Generics in React TypeScript
# हिंदी में: Generics — किसी भी Data Type के साथ चलने वाले Type-Safe Components

---

## 🔵 Simple Definition (English)
**Generics** let you write a component, hook or function once and let the caller choose the data type: `<Select<Restaurant> />`, `useFetch<Dish[]>()`. TypeScript then keeps every prop and callback consistent with that one type, without using `any`.

## 🔵 सरल परिभाषा (Hindi)
**Generics** से आप component, hook या function एक बार लिखते हैं और data type caller तय करता है: `<Select<Restaurant> />`, `useFetch<Dish[]>()`। फिर TypeScript हर prop और callback को उसी एक type के अनुरूप रखता है, `any` के बिना।

---

## 🔴 Problem it Solves

A reusable `Table` or `Select` must handle restaurants, dishes, orders and users. If you type rows as `any`, you lose autocomplete and safety. If you write `RestaurantTable`, `DishTable`, `OrderTable`, you duplicate code. Generics give one implementation that stays fully typed for each use.

```tsx
// PROBLEM 1: any → no safety
function List({ items, render }: { items: any[]; render: (item: any) => ReactNode }) { /* ... */ }
<List items={dishes} render={(d) => d.nmae} />      // typo is NOT caught

// PROBLEM 2: duplication → DishList, RestaurantList, OrderList ...
```

## 🔴 यह क्यों बना? (Hindi)
Reusable `Table` या `Select` को restaurants, dishes, orders और users सबके साथ चलना होता है। Rows को `any` लिखें तो autocomplete और safety चली जाती है। `RestaurantTable`, `DishTable`, `OrderTable` अलग-अलग लिखें तो code दोहराता है। Generics एक ही implementation देते हैं जो हर उपयोग में पूरी तरह typed रहती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Declare a type parameter after the function/component name: function List<T>(...)
Step 2 → Use T in props: items: T[]; render: (item: T) => ReactNode; onSelect: (item: T) => void
Step 3 → Caller passes data; TypeScript INFERS T from items (<List items={dishes} /> => T = Dish)
Step 4 → Constrain when needed: <T extends { id: string }> guarantees item.id exists
Step 5 → Use keyof T for column/field names: key: keyof T keeps strings valid fields of T
Step 6 → Give defaults if useful: <T = unknown>; pass explicitly if inference fails: <List<Dish> ... />
Step 7 → In .tsx files, write arrow generics as <T,> or <T extends unknown> to avoid JSX ambiguity

Re-render behavior: generics are erased at compile time; re-render behavior is the same as a normal
component (wrap rows in React.memo and keep callbacks stable if lists are large).
Performance impact: none at runtime; slightly more complex type-checking at build time.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Function/component के नाम के बाद type parameter लिखो: function List<T>(...)
Step 2 → Props में T इस्तेमाल करो: items: T[]; render: (item: T) => ReactNode; onSelect: (item: T) => void
Step 3 → Caller data देता है; TypeScript items से T अपने-आप समझ लेता है (<List items={dishes} /> => T = Dish)
Step 4 → ज़रूरत पर सीमा लगाओ: <T extends { id: string }> से item.id का होना पक्का होता है
Step 5 → Column/field नामों के लिए keyof T: key: keyof T से strings सिर्फ T के असली fields रहते हैं
Step 6 → चाहें तो default: <T = unknown>; inference फेल हो तो साफ़ दो: <List<Dish> ... />
Step 7 → .tsx files में arrow generics को <T,> या <T extends unknown> लिखो ताकि JSX से भ्रम न हो

Re-render behavior: generics compile time पर हट जाते हैं; re-render व्यवहार सामान्य component जैसा ही है
(बड़ी lists में rows को React.memo में रखो और callbacks स्थिर रखो)।
Performance impact: runtime पर कुछ नहीं; build में type-check थोड़ा जटिल।
```

---

## 🟡 Real World Example
**Swiggy admin dashboard:** One `DataTable<T>` shows restaurants (name, rating), orders (id, status, amount) and delivery partners (name, phone). Columns are declared as `{ key: 'rating', header: 'Rating' }`, and TypeScript only accepts keys that exist on that row type. `useFetch<Order[]>('/api/orders')` returns `data` typed as `Order[] | null`, so `data.map(o => o.amount)` autocompletes.

## 🟡 Real Example Hindi mein
**Swiggy admin dashboard:** एक `DataTable<T>` restaurants (name, rating), orders (id, status, amount) और delivery partners (name, phone) दिखाता है। Columns `{ key: 'rating', header: 'Rating' }` की तरह दिए जाते हैं, और TypeScript सिर्फ वही keys मानता है जो उस row type में हैं। `useFetch<Order[]>('/api/orders')` का `data` `Order[] | null` होता है, इसलिए `data.map(o => o.amount)` में autocomplete मिलता है।

---

## 💻 Code Example — Basic

```tsx
// Basic: a generic list component and a generic hook
import { useState, type ReactNode } from 'react';
import { createRoot } from 'react-dom/client';

// T is chosen by the caller (inferred from items)
interface ListProps<T> {
  items: T[];                                    // array of any one type
  renderItem: (item: T) => ReactNode;            // callback receives that same type
  getKey: (item: T) => string | number;          // how to read a unique key
}

function List<T>({ items, renderItem, getKey }: ListProps<T>) {
  return (
    <ul>
      {items.map((item) => (
        <li key={getKey(item)}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}

// Generic hook: state typed by T
function useToggleList<T>(initial: T[]) {
  const [selected, setSelected] = useState<T[]>(initial);          // array of T
  const toggle = (item: T) =>                                      // add or remove
    setSelected((s) => (s.includes(item) ? s.filter((x) => x !== item) : [...s, item]));
  return { selected, toggle };
}

type Dish = { id: number; name: string; price: number };
const dishes: Dish[] = [{ id: 1, name: 'Dosa', price: 90 }, { id: 2, name: 'Idli', price: 60 }];

function App() {
  const { selected, toggle } = useToggleList<Dish>([]);            // explicit generic
  return (
    <>
      <List
        items={dishes}                                             // T inferred as Dish
        getKey={(d) => d.id}                                       // d is Dish
        renderItem={(d) => <button onClick={() => toggle(d)}>{d.name} (Rs. {d.price})</button>}
      />
      <p>Selected: {selected.map((d) => d.name).join(', ')}</p>
    </>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
```

## 💻 Code Example — Advanced

```tsx
// Advanced: DataTable<T> with constraints, keyof columns, a generic useFetch hook and a typed Select
import { useEffect, useState, type ReactNode } from 'react';

// ---- 1. Table: columns can only refer to real keys of the row type -------------
type Column<T> = {
  key: keyof T;                                              // must be a field of T
  header: string;                                            // column title
  render?: (value: T[keyof T], row: T) => ReactNode;         // optional custom cell
};

interface DataTableProps<T extends { id: string | number }> {  // constraint: rows must have id
  rows: T[];
  columns: Column<T>[];
  onRowClick?: (row: T) => void;                             // gets the full typed row
}

export function DataTable<T extends { id: string | number }>({ rows, columns, onRowClick }: DataTableProps<T>) {
  return (
    <table>
      <thead>
        <tr>{columns.map((c) => <th key={String(c.key)}>{c.header}</th>)}</tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id} onClick={() => onRowClick?.(row)}>
            {columns.map((c) => (
              <td key={String(c.key)}>
                {c.render ? c.render(row[c.key], row) : String(row[c.key])}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ---- 2. Generic data hook with loading/error and abort handling --------------------
type FetchState<T> =
  | { status: 'loading' }
  | { status: 'error'; error: string }
  | { status: 'success'; data: T };                          // discriminated union

export function useFetch<T>(url: string): FetchState<T> {
  const [state, setState] = useState<FetchState<T>>({ status: 'loading' });
  useEffect(() => {
    const ctrl = new AbortController();                      // cancel on url change/unmount
    setState({ status: 'loading' });
    fetch(url, { signal: ctrl.signal })
      .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() as Promise<T>; })
      .then((data) => setState({ status: 'success', data }))
      .catch((e: unknown) => {
        if (e instanceof DOMException && e.name === 'AbortError') return; // ignore cancellations
        setState({ status: 'error', error: e instanceof Error ? e.message : 'Unknown error' });
      });
    return () => ctrl.abort();                               // cleanup
  }, [url]);
  return state;
}

// ---- 3. Typed Select: value is the actual object, not a string ---------------------
interface SelectProps<T> {
  options: T[];
  value: T | null;
  onChange: (value: T) => void;
  getLabel: (option: T) => string;
  getValue: (option: T) => string;                           // string used by the <select>
}

export function Select<T>({ options, value, onChange, getLabel, getValue }: SelectProps<T>) {
  return (
    <select
      value={value ? getValue(value) : ''}
      onChange={(e) => {
        const next = options.find((o) => getValue(o) === e.target.value); // map string back to object
        if (next) onChange(next);                            // caller receives T, not a string
      }}
    >
      <option value="" disabled>Choose...</option>
      {options.map((o) => <option key={getValue(o)} value={getValue(o)}>{getLabel(o)}</option>)}
    </select>
  );
}

// ---- usage -------------------------------------------------------------------------
type Order = { id: number; status: 'placed' | 'delivered'; amount: number };

export function OrdersPage() {
  const res = useFetch<Order[]>('/api/orders');              // T = Order[]
  if (res.status === 'loading') return <p>Loading...</p>;
  if (res.status === 'error') return <p>Error: {res.error}</p>;
  return (
    <DataTable<Order>                                        // explicit generic for clearer errors
      rows={res.data}                                        // narrowed: data exists only on success
      columns={[
        { key: 'id', header: 'Order' },
        { key: 'status', header: 'Status' },
        { key: 'amount', header: 'Amount', render: (v) => `Rs. ${v}` },
        // { key: 'price', header: 'Price' }                 // ✗ compile error: 'price' is not in Order
      ]}
    />
  );
}
```

---

## 🟠 Next.js Connection

Generics are everywhere in Next.js App Router code: typed fetch wrappers shared between Server Components, and typed Server Actions. A generic result type lets every action return the same envelope. Remember that server action arguments and results must be serializable.

```tsx
// lib/result.ts : a generic result type shared by server actions and components
export type Result<T> =
  | { ok: true; data: T }
  | { ok: false; error: string };

// lib/api.ts : typed fetch for Server Components
export async function getJson<T>(url: string): Promise<Result<T>> {
  try {
    const res = await fetch(url, { next: { revalidate: 60 } });   // cached for 60 seconds
    if (!res.ok) return { ok: false, error: `HTTP ${res.status}` };
    return { ok: true, data: (await res.json()) as T };           // cast: validate with zod in real apps
  } catch {
    return { ok: false, error: 'Network error' };
  }
}

// app/orders/page.tsx
import { getJson } from '@/lib/api';
type Order = { id: number; amount: number };

export default async function Page() {
  const res = await getJson<Order[]>('https://api.example.com/orders');
  if (!res.ok) return <p>{res.error}</p>;                         // narrowed by the "ok" field
  return <ul>{res.data.map((o) => <li key={o.id}>Rs. {o.amount}</li>)}</ul>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Casting the response (`as T`) and trusting it
✅ **Correct:** Generics describe what you EXPECT; validate real data at runtime (zod, valibot) at the boundary

```tsx
// Wrong: the API might return something else; TS cannot know
const data = (await res.json()) as Order[];            // ❌ blind trust
// Right
const data = OrderSchema.array().parse(await res.json());  // ✅ runtime check, type inferred from the schema
```

❌ **Mistake 2:** Writing `<T>(props) => ...` arrow generics in a `.tsx` file (parsed as a JSX tag)
✅ **Correct:** Use a function declaration, or `<T,>` / `<T extends unknown>`

```tsx
// Wrong (in .tsx)
const Item = <T>(p: { v: T }) => <p>{String(p.v)}</p>;        // ❌ syntax error
// Right
const Item = <T,>(p: { v: T }) => <p>{String(p.v)}</p>;       // ✅
function Item2<T>(p: { v: T }) { return <p>{String(p.v)}</p>; } // ✅
```

❌ **Mistake 3:** Using `React.memo` or `forwardRef` on a generic component and losing the generic
✅ **Correct:** Cast the wrapped component back to its generic signature

```tsx
// Wrong: memo erases the type parameter, T collapses to its constraint
const MemoTable = memo(DataTable);                               // ❌ T lost
// Right
const MemoTable = memo(DataTable) as typeof DataTable;           // ✅ keeps <T>
```

---

## 🧠 Tricky Interview Question

```tsx
function pick<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
const dish = { name: 'Dosa', price: 90 };
const a = pick(dish, 'price');
const b = pick(dish, 'rating');
```
**Answer:** `a` has type `number` because `K` is inferred as the literal `'price'` and `T['price']` is `number`. The call for `b` is a compile error: `'rating'` is not assignable to `'name' | 'price'` (that is `keyof typeof dish`). The constraint `K extends keyof T` links the second argument to the first, which is the main trick behind type-safe column and field APIs. At runtime the types vanish, so without TypeScript `b` would simply be `undefined`.

---

## ⚫ Interview Questions + Answers

Q1: What are generics and why use them in React?
A1: Type parameters that let one component or hook work with many data types while remaining type-safe. They are used for tables, selects, lists, data hooks, and API helpers, avoiding both `any` and duplicated components.

Q2: What does `T extends { id: string }` mean?
A2: A constraint: T can be any type that has at least an `id: string`. Inside the component you can safely read `item.id`, and callers with incompatible types get a compile error.

Q3: How does TypeScript infer T in `<List items={dishes} />`?
A3: It looks at the prop where T appears (`items: T[]`) and uses the argument's type. If T appears only in callbacks or there are conflicting candidates, inference may fail, so pass it explicitly: `<List<Dish> ... />`.

Q4: What does `keyof T` do and how is it used?
A4: It produces a union of the property names of T. Used for column keys, sort keys and `pick` helpers: `key: keyof T` guarantees the key exists, and `T[K]` gives the matching value type.

Q5: Do generics affect runtime?
A5: No. They are erased by the compiler, so there is no runtime or bundle cost. They also do not validate real data; combine them with runtime validation at API boundaries.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- A component or hook is reused with different data shapes (tables, selects, lists, fetchers)
- Props depend on each other (callback gets the same type as the items)
- You build a shared UI library

❌ **Avoid when:**
- The component is used with exactly one type (use a plain type)
- Generic signatures become unreadable (split into smaller types)
- You use generics only to avoid writing a real type for the data

---

## 📊 Visual Diagram

```
   DataTable<T extends {id}>
        │
  caller passes rows: Order[]
        │ inference
        ▼
     T = Order
        │
        ├─ columns:   key: keyof Order  →  'id' | 'status' | 'amount'
        ├─ render:    (value, row: Order) => ReactNode
        └─ onRowClick:(row: Order) => void

   <DataTable rows={dishes} />  → T = Dish  (same code, different types)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Generic | Type parameter chosen by caller | Caller द्वारा चुना गया type parameter |
| Type parameter (T) | Placeholder for a type | Type का placeholder |
| Constraint (extends) | Limit what T can be | T पर सीमा लगाना |
| Inference | TypeScript guesses T | TypeScript का T समझ लेना |
| keyof | Union of property names | Property नामों का union |
| Indexed access T[K] | Type of a property | किसी property का type |
| Discriminated union | Union with tag field | Tag field वाला union |
| Type erasure | Types removed at build | Build पर types का हटना |

---

## ⚡ 3-Line Summary
**English:**
1. Generics let one component or hook work with many types while keeping props and callbacks linked.
2. Use constraints (`extends`), `keyof T` and inference; pass `<T>` explicitly when inference fails.
3. They exist only at compile time, so validate real data at runtime and take care with `memo` and arrow generics in `.tsx`.

**Hindi:**
1. Generics से एक component या hook कई types के साथ चलता है और props व callbacks आपस में जुड़े रहते हैं।
2. Constraints (`extends`), `keyof T` और inference इस्तेमाल करो; inference फेल हो तो `<T>` खुद दो।
3. ये सिर्फ compile time पर होते हैं, इसलिए असली data runtime पर जाँचो और `memo` व `.tsx` में arrow generics का ध्यान रखो।

---

## ➡️ Next Topic
**160. React + WebSockets** — अब real-time data की बारी है: live order tracking और chat जैसी चीज़ें WebSocket से React में कैसे जोड़ें, और connection को सुरक्षित तरीके से कैसे संभालें।
