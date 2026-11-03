# 112. Build a Card Component
# हिंदी में: Card Component बनाओ — Image, Title, Text और Button

Files: [`index.html`](./index.html) (page with 3 cards) and [`style.css`](./style.css) (styles). Open `index.html` in a browser.

---

## 🔵 Simple Definition (English)
A **card** is a self-contained box that groups related content: an image, title, short text, meta info and an action. It is the most common UI building block (product, restaurant, blog post, profile). Good cards use Flexbox for internal layout, Grid for the card list, and have hover/focus states.

## 🔵 सरल परिभाषा (Hindi)
**Card** एक अलग box है जिसमें जुड़ा हुआ content रहता है: image, title, छोटा text, meta info और एक action। यह सबसे common UI building block है (product, restaurant, blog post, profile)। अच्छे cards में अंदर का layout Flexbox से, cards की list Grid से बनती है और hover/focus states होती हैं।

---

## 🔴 Problem it Solves
```
- Cards in a row have different text lengths -> uneven heights, buttons at different levels.
- Images stretch or jump while loading (layout shift).
- Long titles push the rating badge out; long text makes one card huge.
- Only the small button is clickable: poor UX. Keyboard users get no focus indicator.
- Interviewers check: box model, flex column, aspect-ratio, object-fit, line-clamp,
  responsive grid, pseudo-elements, accessibility.
```

## 🔴 यह क्यों बना? (Hindi)
```
- एक row के cards में text की लंबाई अलग -> ऊँचाई असमान, buttons अलग level पर।
- Images खिंच जाती हैं या load होते समय layout कूदता है।
- लंबा title rating badge को बाहर धकेल देता है; लंबा text एक card को बहुत बड़ा कर देता है।
- सिर्फ छोटा button clickable: UX खराब। Keyboard users को focus दिखता नहीं।
- Interview में box model, flex column, aspect-ratio, object-fit, line-clamp,
  responsive grid, pseudo-elements और accessibility परखी जाती है।
```

---

## 🟢 How it Works — Step by Step

```
1. GRID of cards:
     grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
   -> columns appear/disappear by available width; no media query needed.
2. CARD = flex column:  .card { display: flex; flex-direction: column; }
     .card__body { flex: 1 }   -> body grows, footer sticks at the bottom -> equal alignment.
   Grid rows stretch cards to equal height by default (align-items: stretch).
3. IMAGE: wrapper with aspect-ratio: 16 / 9 and img { width:100%; height:100%; object-fit: cover }
   plus width/height attributes in HTML to reserve space (no layout shift).
4. ROUNDED CORNERS: border-radius + overflow: hidden on the card clips the image.
5. TITLE ROW: flex, space-between; rating has flex-shrink: 0 so it never squishes.
6. LINE CLAMP: -webkit-line-clamp: 3 (+ display: -webkit-box, -webkit-box-orient: vertical).
7. WHOLE CARD CLICKABLE (stretched link): the title <a> has ::after { position:absolute; inset:0 }
   covering the card (card is position: relative). Button gets z-index: 2 to stay clickable.
   Better than wrapping everything in <a>: valid HTML, and a clean accessible name for the link.
8. STATES: :hover lift (translateY + bigger shadow), :focus-within outline for keyboard users.
9. MOTION: respect prefers-reduced-motion.
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. Cards का GRID:
     grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
   -> उपलब्ध width के हिसाब से columns अपने-आप; media query नहीं चाहिए।
2. CARD = flex column:  .card { display: flex; flex-direction: column; }
     .card__body { flex: 1 }   -> body बढ़ती है, footer नीचे चिपका रहता है।
   Grid में rows के cards default से बराबर ऊँचाई (align-items: stretch) लेते हैं।
3. IMAGE: aspect-ratio: 16 / 9 वाला wrapper और img { width:100%; height:100%; object-fit: cover };
   HTML में width/height attributes से जगह reserve (layout shift नहीं)।
4. गोल कोने: card पर border-radius + overflow: hidden से image कट जाती है।
5. TITLE ROW: flex, space-between; rating पर flex-shrink: 0 ताकि दबे नहीं।
6. LINE CLAMP: -webkit-line-clamp: 3 (+ display: -webkit-box, -webkit-box-orient: vertical)।
7. पूरा CARD CLICKABLE (stretched link): title <a> का ::after { position:absolute; inset:0 }
   पूरे card को ढक लेता है (card पर position: relative)। Button पर z-index: 2 ताकि वो भी चले।
8. STATES: :hover पर उठना (translateY + बड़ा shadow), :focus-within पर outline।
9. MOTION: prefers-reduced-motion का सम्मान।
```

---

## 🟡 Real World Example
**Zomato / Swiggy restaurant listing and Amazon product grid:** each tile has an image, name, rating chip, cuisine/price line and a CTA; tiles in the same row stay aligned even when names differ in length, and tapping anywhere on the tile opens the restaurant page.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy restaurant listing और Amazon product grid:** हर tile में image, नाम, rating chip, cuisine/price line और CTA होता है; नाम की लंबाई अलग होने पर भी एक row के tiles सीध में रहते हैं, और tile पर कहीं भी tap करने से restaurant page खुलता है।

---

## 💻 Live Code Example

Full files: `index.html` and `style.css` in this folder. Key parts:

```html
<article class="card">
  <div class="card__media"><img src="..." alt="Plate of biryani" width="400" height="225"></div>
  <div class="card__body">
    <h2 class="card__title"><a href="#" class="card__link">Biryani House</a></h2>
    <p class="card__text">Slow-cooked dum biryani...</p>
  </div>
  <footer class="card__footer"><span>&#8377;249</span><button class="btn">Order</button></footer>
</article>
```

```css
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.card { position: relative; display: flex; flex-direction: column; overflow: hidden; border-radius: 14px; }
.card__body { flex: 1; }                                 /* footer pinned to bottom */
.card__media { aspect-ratio: 16 / 9; }
.card__media img { width: 100%; height: 100%; object-fit: cover; }
.card__link::after { content: ""; position: absolute; inset: 0; z-index: 1; }   /* stretched link */
.btn { position: relative; z-index: 2; }                 /* stays independently clickable */
```

Note: the demo images are inline SVG colored rectangles so the page runs offline; replace the `src` with real photos.

---

## 🟠 React/Next.js Connection

```jsx
import Image from 'next/image';
import Link from 'next/link';

// Reusable Card with props. Layout lives in CSS/Tailwind, data comes from props.
export function RestaurantCard({ r }) {
  return (
    <article className="group relative flex flex-col overflow-hidden rounded-2xl border bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-lg focus-within:ring-2 focus-within:ring-rose-500">
      <div className="relative aspect-video">
        {/* next/image handles lazy loading, sizes and format */}
        <Image src={r.img} alt={r.name} fill sizes="(min-width: 768px) 33vw, 100vw" className="object-cover" />
      </div>

      <div className="flex-1 p-4">
        <div className="flex items-start justify-between gap-2">
          <h2 className="text-lg font-semibold">
            {/* stretched link: after:absolute after:inset-0 */}
            <Link href={`/r/${r.id}`} className="after:absolute after:inset-0">{r.name}</Link>
          </h2>
          <span className="shrink-0 rounded bg-green-600 px-2 text-sm text-white">{r.rating}</span>
        </div>
        <p className="mt-2 line-clamp-3 text-sm text-gray-600">{r.desc}</p>   {/* Tailwind line-clamp */}
      </div>

      <footer className="flex items-center justify-between border-t px-4 py-3">
        <span className="font-semibold">&#8377;{r.price}</span>
        <button className="relative z-10 rounded-lg bg-rose-600 px-4 py-2 text-white">Order</button>
      </footer>
    </article>
  );
}

// List:  <div className="grid grid-cols-[repeat(auto-fill,minmax(280px,1fr))] gap-5">{items.map(r => <RestaurantCard key={r.id} r={r} />)}</div>
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you make all cards in a row the same height with buttons aligned at the bottom?**
A1: Put cards in a Grid (or flex row); items stretch to equal height by default. Make each card a flex column and give the body `flex: 1` (or `margin-top: auto` on the footer). For aligning inner sections across cards (title, text, button), use subgrid.

**Q2: How do you keep image proportions and avoid layout shift?**
A2: Use `aspect-ratio: 16/9` on the wrapper (or width/height attributes on `<img>`) and `object-fit: cover` so the image fills the box without distortion. Add `loading="lazy"` for below-the-fold images.

**Q3: How do you make the entire card clickable while keeping a button inside?**
A3: Use the stretched-link pattern: card is `position: relative`, the main link's `::after` is `position: absolute; inset: 0`. Interactive children (button) get `position: relative; z-index: 2`. Avoid nesting an `<a>` inside another `<a>` or a `<button>` inside `<a>` (invalid HTML).

**Q4: How do you truncate text to a fixed number of lines?**
A4: `display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 3; overflow: hidden;` (with standard `line-clamp: 3` added). Works in all modern browsers. For one line: `white-space: nowrap; overflow: hidden; text-overflow: ellipsis`.

**Q5: How do you create a responsive card grid without media queries?**
A5: `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))` (use `auto-fit` to stretch the remaining cards when fewer than a row). Each column is at least 280px and shares leftover space.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Fixed heights on cards
```css
/* WRONG: text overflows with long content or other languages */
.card { height: 380px; }
/* CORRECT: let content define height; use grid stretch + flex: 1 */
```

❌ **Mistake 2:** Missing `overflow: hidden` with rounded corners
```css
/* WRONG: image corners poke out of the rounded card */
/* CORRECT: .card { border-radius: 14px; overflow: hidden; } */
```

❌ **Mistake 3:** Hover-only interactions
```css
/* WRONG: .card:hover { ... } only; keyboard users see nothing */
/* CORRECT: add .card:focus-within and :focus-visible; keep hover effects subtle (touch has no hover) */
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Card | Boxed group of related content | संबंधित content का box |
| aspect-ratio | Fixed width:height proportion | चौड़ाई:ऊँचाई अनुपात |
| object-fit | How media fills its box | Image box कैसे भरे |
| line-clamp | Limit text to N lines | N lines तक सीमित text |
| Stretched link | Link ::after covers the card | पूरे card पर link |
| auto-fill / auto-fit | Auto number of grid columns | अपने-आप columns |
| :focus-within | Parent matches when child focused | Child focus पर parent |

---

## ⚡ 3-Line Summary
**English:**
1. Lay cards out with `grid` + `repeat(auto-fill, minmax(280px, 1fr))`; make each card a flex column with a growing body.
2. Use `aspect-ratio` + `object-fit: cover`, `overflow: hidden`, and `line-clamp` to keep media and text tidy.
3. Make the whole card clickable with a stretched link and add `:hover`/`:focus-within` states for accessibility.

**Hindi:**
1. Cards को `grid` + `repeat(auto-fill, minmax(280px, 1fr))` से रखो; हर card flex column हो और body बढ़ने वाली।
2. `aspect-ratio` + `object-fit: cover`, `overflow: hidden` और `line-clamp` से media और text साफ़ रखो।
3. Stretched link से पूरा card clickable बनाओ और accessibility के लिए `:hover`/`:focus-within` states जोड़ो।

---

## ➡️ Next Topic
**113. CSS Centering (5 different ways)** — Interview का सबसे क्लासिक सवाल: element को horizontally और vertically center करने के 5 तरीके।
