# 67. CSS Overflow
# हिंदी में: CSS Overflow — जब Content Box से बड़ा हो जाए

---

## 🔵 Simple Definition (English)
`overflow` controls what happens when content is bigger than its container. **visible** (default) lets it spill out. **hidden** clips it. **scroll** always shows scrollbars. **auto** shows scrollbars only when needed. `overflow-x` and `overflow-y` control each axis separately.

## 🔵 सरल परिभाषा (Hindi)
`overflow` तय करता है कि content अपने container से बड़ा हो तो क्या होगा। **visible** (default) बाहर निकलने देता है। **hidden** काट देता है। **scroll** हमेशा scrollbar दिखाता है। **auto** ज़रूरत पड़ने पर ही scrollbar दिखाता है। `overflow-x` और `overflow-y` से हर दिशा अलग control होती है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  .card { height: 100px; }  <- andar 500px ka text
  Text card ke bahar niklkar neeche ke elements pe chadh jata hai.

  Chat window me 200 messages -> page lamba ho jata hai.
  Image zoom hover pe card se bahar nikal jati hai.
  Long URL/text mobile pe horizontal scroll bana deta hai.

overflow = "sambhalo ki extra content kaha jaye": clip, scroll ya ellipsis.
```

## 🔴 यह क्यों बना? (Hindi)
Fixed size container में unknown length का content (user comments, long names, chat) आ सकता है। बिना नियम के वह बाहर गिरकर layout बिगाड़ता है। `overflow` से हम तय करते हैं कि content कटे, scroll हो या "..." बने।

---

## 🟢 How it Works — Step by Step

```
VALUES:
  visible : default. Content paints outside the box. No clipping/scroll.
  hidden  : clips at the padding edge. No scrollbar (but can still scroll by JS).
  scroll  : clips + ALWAYS shows scrollbar track.
  auto    : clips + scrollbar ONLY when content overflows. (Best default for lists)
  clip    : like hidden but NOT a scroll container (cannot be scrolled even by JS).

SHORTHAND:
  overflow: hidden auto;   /* x then y */
  overflow-x: auto; overflow-y: hidden;
  NOTE: if one axis is visible and the other is not, visible computes to auto!

WHEN DOES OVERFLOW HAPPEN?
  Only when the box has a limited size (height/max-height/width) or
  a flex/grid child cannot shrink (min-width: auto trap).

COMMON RECIPES:
  1. Scrollable list:    max-height: 300px; overflow-y: auto;
  2. Clip rounded image: border-radius: 12px; overflow: hidden;
  3. Single-line ellipsis:
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  4. Multi-line clamp (widely supported incl. modern Chrome/Safari/Firefox):
        display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
        (modern shorthand: line-clamp: 3 is arriving, but still use -webkit- version now)
  5. Horizontal carousel: display:flex; overflow-x: auto; scroll-snap-type: x mandatory;
  6. Prevent scroll chaining: overscroll-behavior: contain;
  7. Hide scrollbar visually: scrollbar-width: none; (Firefox + newer Chrome),
        ::-webkit-scrollbar { display: none } for older WebKit
  8. Clearfix / contain floats: overflow: hidden (old trick) or display: flow-root (modern)

SIDE EFFECTS OF overflow != visible:
  - Creates a new Block Formatting Context (contains floats, stops margin collapse).
  - Becomes the scroll container -> position: sticky inside will stick to IT.
  - Clips absolutely positioned descendants (tooltips/dropdowns get cut off!).

FLEX TRAP: a flex child with long text will not shrink below content width
  .child { min-width: 0; }   /* allows shrinking so overflow/ellipsis can work */
```

## 🟢 कैसे काम करता है? (Hindi)
1. Overflow तभी होता है जब box की size सीमित हो (height, max-height, width) और content उससे बड़ा हो।
2. `hidden`: बाहर का हिस्सा कट जाता है। `auto`: ज़रूरत पर scrollbar। `scroll`: हमेशा scrollbar। `visible`: बाहर निकलने दो।
3. Rounded image के corners कटवाने के लिए parent पर `border-radius` + `overflow: hidden`।
4. एक line में "..." के लिए तीनों साथ चाहिए: `white-space: nowrap; overflow: hidden; text-overflow: ellipsis;`।
5. Side effect: `overflow` लगाते ही element scroll container बन जाता है, इसलिए अंदर का `sticky` उसी के हिसाब से चिपकता है और अंदर के absolute dropdown कट सकते हैं।
6. Flex child में लंबा text हो तो `min-width: 0` लगाना पड़ता है, वरना वह सिकुड़ता ही नहीं।

---

## 🟡 Real World Example
**Swiggy / Zomato:** the restaurant name shows "Pizza Hut - Connaught Pl..." with ellipsis (`text-overflow`); the horizontal "Top picks" carousel uses `overflow-x: auto`. **Instagram:** profile photos are circles made with `border-radius: 50%; overflow: hidden`; the comments panel scrolls independently with `overflow-y: auto`. **Gmail:** the email list scrolls inside its own pane while the header stays fixed. **Amazon:** product titles are clamped to 2 lines with `-webkit-line-clamp: 2`.

## 🟡 Real Example Hindi mein
**Swiggy / Zomato** में restaurant का लंबा नाम "..." के साथ कटता है (ellipsis) और "Top picks" की horizontal list `overflow-x: auto` से scroll होती है। **Instagram** में profile photo गोल दिखती है (`border-radius: 50%` + `overflow: hidden`) और comments अपने अलग panel में scroll होते हैं। **Gmail** में email list अपने pane में scroll होती है और header स्थिर रहता है। **Amazon** में product title 2 line पर कट जाता है (`line-clamp`)।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CSS Overflow Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 20px; background: #f5f5f5; }
    h2 { font-size: 15px; margin: 22px 0 6px; }

    /* Shared small box with fixed height */
    .box {
      width: 260px; height: 70px;
      border: 2px solid #1976d2; background: #e3f2fd;
      padding: 6px; font-size: 14px;
    }
    .visible { overflow: visible; }                 /* spills out (default) */
    .hidden  { overflow: hidden; }                  /* clipped */
    .scroll  { overflow: scroll; }                  /* always scrollbars */
    .auto    { overflow: auto; }                    /* scrollbar only if needed */

    /* Ellipsis: single line */
    .title {
      width: 260px;
      white-space: nowrap;           /* do not wrap */
      overflow: hidden;              /* clip extra */
      text-overflow: ellipsis;       /* show ... */
      background: #fff; padding: 6px; border: 1px solid #ccc;
    }

    /* Multi-line clamp: 2 lines */
    .clamp {
      width: 260px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      background: #fff; padding: 6px; border: 1px solid #ccc;
    }

    /* Circular avatar: border-radius + overflow hidden */
    .avatar {
      width: 80px; height: 80px;
      border-radius: 50%;
      overflow: hidden;              /* clips the square child to a circle */
      background: #ffcc80;
    }
    .avatar span { display: block; width: 100%; height: 100%;
                   background: linear-gradient(135deg, #ef5350, #ffca28); }

    /* Scrollable chat list */
    .chat {
      width: 260px;
      max-height: 120px;             /* limit height */
      overflow-y: auto;              /* vertical scroll when needed */
      background: #fff; border: 1px solid #ccc;
      overscroll-behavior: contain;  /* do not scroll the page at the end */
    }
    .chat p { margin: 0; padding: 8px; border-bottom: 1px solid #eee; }

    /* Horizontal scroller (like Swiggy carousel) */
    .carousel {
      display: flex; gap: 10px;
      overflow-x: auto;
      scroll-snap-type: x mandatory;   /* snap to items */
      padding: 6px 0;
    }
    .carousel .item {
      flex: 0 0 120px;                 /* do not shrink */
      height: 80px;
      background: #c8e6c9;
      scroll-snap-align: start;
      display: grid; place-items: center;
    }
  </style>
</head>
<body>
  <h2>visible / hidden / scroll / auto (same long text)</h2>
  <div style="display:flex; gap:12px; flex-wrap:wrap">
    <div class="box visible">visible: This long text keeps going outside the little box and overlaps what is below it. Overflowing text overflowing text.</div>
    <div class="box hidden">hidden: This long text keeps going outside the little box and is clipped. Overflowing text overflowing text.</div>
    <div class="box scroll">scroll: This long text keeps going outside the little box and has scrollbars. Overflowing text overflowing text.</div>
    <div class="box auto">auto: This long text keeps going outside the little box and scrolls only when needed. Overflowing text overflowing text.</div>
  </div>

  <h2 style="margin-top:60px">Ellipsis (1 line)</h2>
  <div class="title">Pizza Hut - Connaught Place, New Delhi, India</div>

  <h2>Line clamp (2 lines)</h2>
  <div class="clamp">Apple iPhone 15 (128 GB) - Black. A long Amazon style product title that would normally take many lines but gets cut after two lines with dots.</div>

  <h2>Circle avatar</h2>
  <div class="avatar"><span></span></div>

  <h2>Scrollable chat (overflow-y: auto)</h2>
  <div class="chat">
    <p>Message 1</p><p>Message 2</p><p>Message 3</p>
    <p>Message 4</p><p>Message 5</p><p>Message 6</p>
  </div>

  <h2>Horizontal carousel (overflow-x + snap)</h2>
  <div class="carousel">
    <div class="item">1</div><div class="item">2</div><div class="item">3</div>
    <div class="item">4</div><div class="item">5</div><div class="item">6</div>
    <div class="item">7</div><div class="item">8</div>
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind overflow utilities
<div className="h-40 overflow-y-auto">scrollable</div>
<div className="overflow-hidden rounded-full w-20 h-20"><img src="/a.jpg" alt="" /></div>
<p className="truncate">Single-line ellipsis (overflow-hidden + text-ellipsis + whitespace-nowrap)</p>
<p className="line-clamp-2">Two-line clamp (built in Tailwind v3.3+)</p>
<div className="flex gap-3 overflow-x-auto snap-x snap-mandatory">
  <div className="snap-start shrink-0 w-32">Item</div>
</div>

// 2. Flex child with truncate needs min-w-0
<div className="flex">
  <p className="min-w-0 flex-1 truncate">Very long restaurant name...</p>
  <button>Order</button>
</div>

// 3. Next.js <Image fill /> inside a relative + overflow-hidden wrapper
<div className="relative h-48 overflow-hidden rounded-lg">
  <Image src="/food.jpg" alt="Food" fill className="object-cover" />
</div>

// 4. Body scroll lock while a modal is open (React effect)
useEffect(() => {
  if (open) document.body.style.overflow = 'hidden';
  return () => { document.body.style.overflow = ''; };
}, [open]);
```

---

## ⚫ Interview Questions + Answers

**Q1: What are the values of `overflow`?**
A1: `visible` (default, spills), `hidden` (clips), `scroll` (always scrollbars), `auto` (scrollbars if needed), and `clip` (clips without creating a scroll container). Use `overflow-x`/`overflow-y` for separate axes.

**Q2: How do you make single-line text end with "..."?**
A2: Three properties together: `white-space: nowrap; overflow: hidden; text-overflow: ellipsis;` and the element needs a constrained width. In a flex child also add `min-width: 0`.

**Q3: Why does `position: sticky` or an absolute dropdown break inside an overflow container?**
A3: Any `overflow` other than `visible` makes the element a scroll container and clips descendants. Sticky then sticks relative to that container (not the page), and absolutely positioned dropdowns inside get clipped. Fix: remove overflow, or render the dropdown with a portal.

**Q4: What is the difference between `overflow: hidden` and `overflow: clip`?**
A4: Both clip. `hidden` creates a scroll container (programmatic scroll still works, creates a BFC). `clip` does not create a scroll container or BFC and cannot be scrolled at all; it also allows `overflow-clip-margin`. Supported in all modern browsers.

**Q5: How do you remove horizontal scroll on mobile?**
A5: First find the culprit (a wide element, `100vw` with scrollbar, long unbroken text, fixed-width image) using DevTools, then fix it: `max-width: 100%`, `overflow-wrap: anywhere`, `box-sizing: border-box`. Avoid hiding it with `body { overflow-x: hidden }` as a first fix because it masks the bug and can break sticky.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Ellipsis not working
```css
/* WRONG: missing nowrap and width limit */
.title { overflow: hidden; text-overflow: ellipsis; }
```
✅ **Correct way:**
```css
.title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
```

❌ **Mistake 2:** `overflow: scroll` everywhere shows ugly empty scrollbars
✅ **Correct way:** use `overflow: auto` so scrollbars appear only when needed.

❌ **Mistake 3:** Setting `height: 300px` on a scrolling area and the content just overflows
```css
.list { height: 300px; }           /* content spills out */
```
✅ **Correct way:**
```css
.list { max-height: 300px; overflow-y: auto; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| overflow | Handling of too-big content | ज़्यादा content का नियम |
| hidden | Clip extra content | बाहर का हिस्सा काटो |
| auto | Scrollbar only when needed | ज़रूरत पर scrollbar |
| text-overflow | Ellipsis for clipped text | कटे text पर "..." |
| Scroll container | Element that scrolls its content | Scroll होने वाला box |
| BFC | Block formatting context | स्वतंत्र layout क्षेत्र |
| line-clamp | Limit text to N lines | N lines पर रोकना |
| scroll-snap | Snap to positions on scroll | Scroll पर अटकना |

---

## ⚡ 3-Line Summary
**English:**
1. `overflow` decides whether too-big content is visible, clipped or scrollable; prefer `auto` over `scroll`.
2. Ellipsis needs `nowrap` + `overflow: hidden` + `text-overflow: ellipsis` (and `min-width: 0` in flex).
3. Overflow other than visible creates a scroll container, which clips dropdowns and changes sticky behaviour.

**Hindi:**
1. `overflow` तय करता है कि बड़ा content दिखे, कटे या scroll हो; `scroll` की जगह `auto` बेहतर।
2. "..." के लिए `nowrap` + `overflow: hidden` + `text-overflow: ellipsis` (flex में `min-width: 0` भी)।
3. visible के अलावा overflow scroll container बनाता है, जिससे dropdown कटते हैं और sticky का व्यवहार बदलता है।

---

## ➡️ Next Topic
**68. CSS Opacity vs RGBA** — पारदर्शिता दो तरीकों से: पूरे element की (opacity) या सिर्फ colour की (rgba)।
