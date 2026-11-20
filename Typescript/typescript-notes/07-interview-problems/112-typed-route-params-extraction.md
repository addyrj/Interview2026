# 112. Typed Route Params Extraction (template literal types)
# हिंदी में: Typed Route Params निकालना (template literal types से)

> TypeScript 5.x | सारे blocks `tsc --strict` (TS 5.9) से verify किए गए। Template literal types और `infer` inside them = **TS 4.1+**, `const` assertions = 3.4+।

---

## 🔵 Simple Definition (English)
Given a route string like `'/users/:userId/orders/:orderId'`, **route params extraction** computes the type `{ userId: string; orderId: string }` *from the string itself* using **template literal types** + `infer` + recursion. The path literal becomes the single source of truth: no separate interface to keep in sync.

## 🔵 सरल परिभाषा (Hindi)
`'/users/:userId/orders/:orderId'` जैसी route string से `{ userId: string; orderId: string }` type **उसी string से** निकालना ही route params extraction है। इसमें **template literal types**, `infer` और recursion इस्तेमाल होते हैं। Path literal ही अकेला source of truth बन जाता है, अलग interface को sync रखने की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
In Express/React Router you write the path in one place and read `req.params.orderId` in another. Rename `:orderId` to `:id` in the path and the handler still compiles (if `params` is `Record<string, string>`) but returns `undefined` at runtime. A hand-written `interface Params { orderId: string }` drifts over time. Extraction ties the two together: change the path and every wrong usage turns red.

## 🔴 यह क्यों बना? (Hindi)
Express/React Router में path एक जगह लिखते हैं और `req.params.orderId` दूसरी जगह पढ़ते हैं। Path में `:orderId` को `:id` कर दो और `params` अगर `Record<string, string>` है तो handler फिर भी compile होता है, पर runtime पर `undefined` मिलता है। हाथ से लिखा `interface Params` धीरे-धीरे अलग पड़ जाता है। Extraction दोनों को बाँध देता है: path बदलो और हर गलत usage लाल हो जाएगा।

---

## 🟢 How it Works — Step by Step
Step 1 → Constrain input: `P extends string`, and make sure callers pass a **literal** (`'/orders/:id'`, not a `string` variable).
Step 2 → Pattern-match with a template literal: `P extends `${string}:${infer Name}/${infer Rest}``. `${string}` skips everything before `:`; `infer Name` grabs text up to the next `/`.
Step 3 → Recurse on the rest: `Name | ExtractParams<`/${Rest}`>` (re-add the `/` so every recursive input has the same shape).
Step 4 → Base case: the last param has no `/` after it, so match `${string}:${infer Name}`. No `:` at all gives `never`.
Step 5 → Turn the union of names into an object with a **mapped type**: `{ [K in Names]: string }`.
Step 6 → Optional params (`:page?`): split into segments, collect required and optional keys separately, intersect, then `Prettify`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Input को `P extends string` से बाँधो और ध्यान रखो कि caller **literal** दे (`'/orders/:id'`), `string` variable नहीं।
Step 2 → Template literal से pattern-match करो: `P extends `${string}:${infer Name}/${infer Rest}``। `${string}` `:` से पहले का सब छोड़ देता है; `infer Name` अगले `/` तक का text पकड़ता है।
Step 3 → बाकी path पर recursion: `Name | ExtractParams<`/${Rest}`>` (`/` वापस जोड़ो ताकि हर recursive input एक ही shape का रहे)।
Step 4 → Base case: आखिरी param के बाद `/` नहीं होता, तब `${string}:${infer Name}` match होता है। `:` बिल्कुल न हो तो `never`।
Step 5 → Names की union को **mapped type** से object बनाओ: `{ [K in Names]: string }`।
Step 6 → Optional params (`:page?`) के लिए path को segments में तोड़ो, required और optional keys अलग इकट्ठा करो, intersect करो, फिर `Prettify`।

---

## 🟡 Real World Example
**Zomato's web app** has `/restaurants/:restaurantId/menu/:itemId`. The same pattern string is used to (1) register the Express route in the BFF, (2) build links in React (`href('menuItem', { restaurantId, itemId })`), and (3) parse the incoming URL for analytics. With extraction, forgetting `itemId` in a link is a compile error, not a broken page in production.

## 🟡 Real Example Hindi mein
**Zomato के web app** में `/restaurants/:restaurantId/menu/:itemId` route है। यही pattern string (1) BFF में Express route register करने, (2) React में link बनाने (`href('menuItem', { restaurantId, itemId })`), और (3) analytics के लिए incoming URL parse करने में इस्तेमाल होती है। Extraction के साथ link में `itemId` भूलना compile error है, production का टूटा page नहीं।

---

## 💻 Code Example — Basic

```typescript
// Compile-time test helpers (type-challenges style)
type Equal<X, Y> = (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

// "/users/:userId/orders/:orderId" -> 'userId' | 'orderId'
type ExtractParams<P extends string> =
  P extends `${string}:${infer Name}/${infer Rest}` // ':' ke baad naam, phir '/' aur baaki path
    ? Name | ExtractParams<`/${Rest}`> // naam lo, baaki path pe recursion
    : P extends `${string}:${infer Name}` // aakhri param (aage '/' nahi)
      ? Name
      : never; // koi param nahi bacha

type Params<P extends string> = { [K in ExtractParams<P>]: string }; // har naam -> string

type Tests = [
  Expect<Equal<ExtractParams<'/orders/:orderId'>, 'orderId'>>,
  Expect<Equal<ExtractParams<'/users/:userId/orders/:orderId'>, 'userId' | 'orderId'>>,
  Expect<Equal<ExtractParams<'/health'>, never>>, // param nahi to never
];

type P = Params<'/restaurants/:restaurantId/menu/:itemId'>;
const p: P = { restaurantId: 'r-101', itemId: 'm-7' }; // dono keys zaroori
console.log(p);
// OUTPUT:
// { restaurantId: 'r-101', itemId: 'm-7' }
```

## 💻 Code Example — Advanced

Optional params, `buildPath` (routes without params need no 2nd argument), and a runtime `matchPath` whose result type is the same `RouteParams<P>`.

```typescript
type Prettify<T> = { [K in keyof T]: T[K] } & {}; // intersection ko flat object dikhao

type Split<P extends string> = P extends `${infer Head}/${infer Tail}` ? [Head, ...Split<Tail>] : [P];
type Required_<S> = S extends `:${infer N}` ? (N extends `${string}?` ? never : N) : never;
type Optional_<S> = S extends `:${infer N}?` ? N : never;

type RouteParams<P extends string> = Prettify<
  { [K in Required_<Split<P>[number]>]: string } & // zaroori params
  { [K in Optional_<Split<P>[number]>]?: string } // ':page?' optional params
>;

type HasParams<P extends string> = keyof RouteParams<P> extends never ? false : true;

// buildPath: params na ho to 2nd argument hi mat maango
function buildPath<P extends string>(
  pattern: P,
  ...args: HasParams<P> extends true ? [params: RouteParams<P>] : []
): string {
  const params = (args[0] ?? {}) as Record<string, string | undefined>;
  return pattern
    .split('/')
    .map((seg) => {
      if (!seg.startsWith(':')) return seg; // static segment
      const name = seg.slice(1).replace('?', '');
      const value = params[name];
      return value === undefined ? null : encodeURIComponent(value); // optional missing
    })
    .filter((s): s is string => s !== null)
    .join('/');
}

// matchPath: runtime pe URL se params nikalo (type wahi RouteParams<P>)
function matchPath<P extends string>(pattern: P, url: string): RouteParams<P> | null {
  const ps = pattern.split('/');
  const us = url.split('/');
  const out: Record<string, string> = {};
  for (let i = 0; i < ps.length; i++) {
    const p = ps[i]!;
    const u = us[i];
    if (p.startsWith(':')) {
      const optional = p.endsWith('?');
      if (u === undefined || u === '') { if (optional) continue; return null; }
      out[p.slice(1).replace('?', '')] = decodeURIComponent(u);
    } else if (p !== u) return null; // static segment match nahi hua
  }
  return out as RouteParams<P>;
}

console.log(buildPath('/orders/:orderId', { orderId: 'ORD 42' }));
console.log(buildPath('/menu/:restaurantId/:page?', { restaurantId: 'r1' }));
console.log(buildPath('/health'));
const m = matchPath('/orders/:orderId/items/:itemId', '/orders/42/items/pizza');
console.log(m?.orderId, m?.itemId); // dono string
console.log(matchPath('/orders/:orderId', '/users/42'));
// OUTPUT:
// /orders/ORD%2042
// /menu/r1
// /health
// 42 pizza
// null
```

---

## 🟠 Node/Express + React Integration

**Express** already does this internally: `@types/express-serve-static-core` exports `RouteParameters<Route>`, so `req.params` is typed from the path literal.

```typescript
import express from 'express';

const app = express();

// Express khud RouteParameters<Route> use karta hai: path string se req.params type hota hai
app.get('/restaurants/:restaurantId/menu/:itemId', (req, res) => {
  const { restaurantId, itemId } = req.params; // dono string
  res.json({ restaurantId, itemId });
});

// Param ko number me convert karna ho to apna helper
function numericParam(raw: string): number {
  const n = Number(raw);
  if (!Number.isInteger(n)) throw new Error(`Invalid id: ${raw}`);
  return n;
}
app.get('/orders/:orderId', (req, res) => {
  const orderId = numericParam(req.params.orderId); // number, ab SQL Server query me safe
  res.json({ orderId });
});
export default app;
```

**React**: a route table with `as const`, and a `TypedLink` whose `params` prop is required only for routes that have params.

```tsx
import type { AnchorHTMLAttributes } from 'react';

type Split<P extends string> = P extends `${infer H}/${infer T}` ? [H, ...Split<T>] : [P];
type Req<S> = S extends `:${infer N}` ? (N extends `${string}?` ? never : N) : never;
type Params<P extends string> = { [K in Req<Split<P>[number]>]: string };

const routes = {
  order: '/orders/:orderId',
  menuItem: '/restaurants/:restaurantId/menu/:itemId',
  home: '/',
} as const; // as const: values literal rehte hain

type Routes = typeof routes;
type RouteName = keyof Routes;

// Link component: name + params, dono type-checked
type TypedLinkProps<N extends RouteName> = Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href'> &
  (keyof Params<Routes[N]> extends never ? { to: N; params?: undefined } : { to: N; params: Params<Routes[N]> });

function href<N extends RouteName>(name: N, params?: Params<Routes[N]>): string {
  const p = (params ?? {}) as Record<string, string>;
  return routes[name].replace(/:(\w+)/g, (_, key: string) => encodeURIComponent(p[key] ?? ''));
}

function TypedLink<N extends RouteName>({ to, params, ...rest }: TypedLinkProps<N>) {
  return <a {...rest} href={href(to, params as Params<Routes[N]>)} />;
}

export const demo = (
  <>
    <TypedLink to="order" params={{ orderId: '42' }}>Track order</TypedLink>
    <TypedLink to="home">Home</TypedLink>
  </>
);
```

**Redux note**: store only `orderId: string` in state; build URLs with `href()` in a selector or thunk, never by string concatenation in components.
**Hindi**: Redux state में सिर्फ `orderId` रखो; URL हमेशा `href()` से बनाओ, components में string जोड़कर नहीं।

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Typo in a param name, and a wrong expectation in a type test.

```typescript
type Equal<X, Y> = (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;
type ExtractParams<P extends string> =
  P extends `${string}:${infer Name}/${infer Rest}` ? Name | ExtractParams<`/${Rest}`>
  : P extends `${string}:${infer Name}` ? Name : never;
type Params<P extends string> = { [K in ExtractParams<P>]: string };
declare function get<P extends string>(path: P, h: (params: Params<P>) => void): void;
get('/orders/:orderId', (p) => p.userId); // ❌ typo param
// error TS2339: Property 'userId' does not exist on type 'Params<"/orders/:orderId">'.
type T1 = Expect<Equal<ExtractParams<'/a/:b'>, 'x'>>; // ❌ galat expectation
// error TS2344: Type 'false' does not satisfy the constraint 'true'.
```

❌ Mistake 2: Passing a non-literal `string`. The extraction degrades to `{}`, so every param access errors (and if you "fix" it with a `Record<string, string>` fallback you silently lose all safety).

```typescript
type ExtractParams<P extends string> =
  P extends `${string}:${infer Name}/${infer Rest}` ? Name | ExtractParams<`/${Rest}`>
  : P extends `${string}:${infer Name}` ? Name : never;
type Params<P extends string> = { [K in ExtractParams<P>]: string };
declare function get<P extends string>(path: P, h: (params: Params<P>) => void): void;
const dynamic: string = '/orders/' + Math.random();
get(dynamic, (p) => p.anything); // ❌ path literal nahi hai
// error TS2339: Property 'anything' does not exist on type 'Params<string>'.
// Right: path ko literal rakho: const path = '/orders/:orderId' (type: the literal)
```

---

## 🧠 Tricky Interview Question

**"What do these evaluate to: `ExtractParams<'/a/:x/:y'>`, `ExtractParams<'/files/:name.json'>`, `ExtractParams<'/orders/:orderId/'>`?"**

```typescript
type Equal<X, Y> = (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;
type ExtractParams<P extends string> =
  P extends `${string}:${infer Name}/${infer Rest}` ? Name | ExtractParams<`/${Rest}`>
  : P extends `${string}:${infer Name}` ? Name : never;
type A = Expect<Equal<ExtractParams<'/a/:x/:y'>, 'x' | 'y'>>; // compiles: 'x' | 'y'
type B = Expect<Equal<ExtractParams<'/files/:name.json'>, 'name.json'>>; // compiles: dot naam ka hissa ban gaya
type C = Expect<Equal<ExtractParams<'/orders/:orderId/'>, 'orderId'>>; // compiles: trailing slash theek
```

Answer: (1) `'x' | 'y'`; (2) `'name.json'`, because the extractor only splits on `/`, so the param name swallows the `.json` suffix. If you support extensions, add a refinement `Name extends `${infer N}.${string}` ? N : Name`. (3) `'orderId'`: the first pattern matches with `Rest = ''`, then `ExtractParams<'/'>` has no `:` and returns `never`. Hindi: extractor सिर्फ `/` पर तोड़ता है, इसलिए `.json` नाम में चला जाता है।

---

## ⚫ Interview Questions + Answers

Q1: What are template literal types and what makes `infer` special inside them?
A1: Types built like strings: `type Id = `order_${number}``. With `infer`, the compiler captures the part of a string literal that matches the placeholder, like a regex capture group, but at compile time.

Q2: Why does `ExtractParams<string>` give `never`?
A2: `string` is not a literal, so nothing can match `:${infer Name}`. Both branches fail and the conditional falls through to `never`. Hence "pass literals" (a `const` declaration keeps the literal type).

Q3: How does Express type `req.params` for you?
A3: `app.get<Route extends string>(path: Route, ...handlers: RequestHandler<RouteParameters<Route>>[])`. `RouteParameters` is the same trick with extra rules (optional `?`, wildcard, regex). So `/orders/:orderId` gives `{ orderId: string }` automatically.

Q4: Params are always `string`. How do you get a `number`?
A4: URL segments are strings. Parse and validate at the boundary (`Number()` + `Number.isInteger`, or `z.coerce.number()` in Zod) and pass the validated `number` onward. Never cast `as number`.

Q5: What is the recursion-limit risk?
A5: Conditional types have an instantiation depth limit (about 50 for non-tail-recursive, 1000 for tail-recursive since TS 4.5). Real routes have fewer than 10 params, so it is safe; still, write it tail-recursive when possible.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You own a router/link-builder layer and want paths as the single source of truth.
- Building a typed API client (`api.get('/orders/:orderId', { params: { orderId } })`).
- Sharing a route table between an Express BFF and React.

❌ Avoid when:
- Paths are built dynamically at runtime (type information is gone).
- A huge router makes compile times slow: prefer OpenAPI code generation.
- You only have 2-3 routes: a plain interface is clearer.

---

## 📊 Visual Diagram
```
'/users/:userId/orders/:orderId'
        |
        |  P extends `${string}:${infer Name}/${infer Rest}`
        v
   Name = 'userId'        Rest = 'orders/:orderId'
        |                        |
        |                        v  ExtractParams<`/${Rest}`>
        |                   Name = 'orderId' (no '/' after) -> base case
        v                        v
      'userId'      |      'orderId'     =>  'userId' | 'orderId'
        |
        v  mapped type: { [K in 'userId' | 'orderId']: string }
   { userId: string; orderId: string }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Template literal type | String type built with `${}` placeholders | `${}` से बना string type |
| `infer` | Capture part of a matched type | Match हुए हिस्से को पकड़ना |
| Recursive conditional type | Type that calls itself | खुद को बुलाने वाला type |
| Mapped type | Build object type from a key union | Key union से object type बनाना |
| Literal type | Exact value as a type (`'abc'`) | Exact value वाला type |
| Prettify | Flatten an intersection for display | Intersection को flat दिखाना |

---

## ⚡ 3-Line Summary
English:
1. Use a template literal pattern with `infer` plus recursion to pull `:param` names out of a path literal.
2. Convert the name union to `{ [K in Names]: string }`; add optional keys for `:param?`.
3. Needs literal paths; Express and React Router do the same internally.

Hindi:
1. Path literal से `:param` नाम निकालने के लिए template literal + `infer` + recursion इस्तेमाल करो।
2. Names की union को `{ [K in Names]: string }` में बदलो; `:param?` के लिए optional keys जोड़ो।
3. Literal path ज़रूरी है; Express और React Router अंदर यही करते हैं।

---

## ➡️ Next Topic
**113. Type-challenges: Medium Set 1** — `MyReturnType`, `MyOmit`, `TupleToUnion`, `Trim`, `Replace` जैसे classic medium problems।
