# CSS Cheatsheet (Topics 46-110 + Problems 111-125)
Quick revision: gist + key snippet + हिंदी hint. Full notes: `../css/basic`, `../css/intermediate`, `../css/advanced`, `../interview-problems`.

---

## A. BASIC (46-68)

### 46. What is CSS / how it works
HTML = structure, CSS = presentation. Browser builds DOM + CSSOM -> render tree -> layout -> paint -> composite. Cascade + inheritance decide final values.
हिंदी: CSS = HTML की सजावट।

### 47. Syntax
Rule = `selector { property: value; }`. Invalid declarations silently skipped. At-rules: `@media`, `@keyframes`. Comments `/* */`.
```css
h1, h2 { color: navy; margin: 0; }
```
हिंदी: selector + property + value।

### 48. Ways to add CSS
Inline (`style`), internal (`<style>`), external (`<link>`, standard). Inline beats rules; internal/external tie, source order wins. Avoid `@import`.
```html
<link rel="stylesheet" href="style.css">
```
हिंदी: External CSS best; @import से बचो।

### 49. Selectors
Element `p`, class `.x`, id `#x`, universal `*`. Prefer classes. `p.x` = same element, `p .x` = descendant.
हिंदी: Space का मतलब बदल देता है।

### 50. Combinators
| Sym | Meaning |
|---|---|
| ` ` | descendant |
| `>` | direct child |
| `+` | next sibling |
| `~` | all later siblings |

Only down/forward; use `:has()` for parent. Keep chains short.
हिंदी: Parent चुनना हो तो `:has()`।

### 51. Pseudo-classes
State/position without JS: `:hover :focus :checked :nth-child`. Link order LVHA; `:focus-visible` for keyboard; guard hover with `@media (hover: hover)`.
```css
li:nth-child(odd) { background: #eee; } a:focus-visible { outline: 2px solid; }
```
हिंदी: Pseudo-class = state पर style।

### 52. Pseudo-elements
`::before ::after ::placeholder ::selection`. Need `content`, not in DOM, not on `<img>/<input>`. Decoration only.
```css
.badge::after { content: "NEW"; }
```
हिंदी: दो colon = element का हिस्सा।

### 53. Specificity
Order: `*` < element < class/attr/pseudo-class < id < inline < `!important`. Count `(inline, ids, classes, elements)` left to right.
```css
#a .b p  /* (0,1,1,1) */   .b p /* (0,0,1,1) */
```
हिंदी: बाएँ से दाएँ compare।

### 54. Cascade & inheritance
Order: importance, layer, specificity, source order (last wins). Text props (`color font-* line-height`) inherit; box props (`margin border background`) do not. `inherit initial unset revert`.
हिंदी: Text inherit होता है, box नहीं।

### 55. Box model
Content -> padding -> border -> margin. Vertical margins of blocks collapse (not in flex/grid).
```css
.box { width: 200px; padding: 10px; border: 1px solid; margin: 20px; }
```
हिंदी: Margin collapse = दोनों में से बड़ा।

### 56. box-sizing
`content-box` adds padding+border to width; `border-box` keeps them inside. Margin never included.
```css
*, *::before, *::after { box-sizing: border-box; }
```
हिंदी: हमेशा border-box।

### 57. Colors
Named, hex, `rgb()`, `hsl()` (alpha `/ 0.5`), `currentColor`. Store in `:root` variables for themes.
```css
color: hsl(220 90% 50% / .5); border-color: currentColor;
```
हिंदी: Shades के लिए hsl।

### 58. Units
`px` fixed, `rem` root, `em` element, `%` parent, `vw/vh` viewport. rem for text/spacing, px for borders/shadows; `dvh` over `vh` on mobile; avoid `100vw`.
हिंदी: Text के लिए rem।

### 59. Typography
`font-family` stack ending in generic; size in `rem`; weight 400-700; unitless `line-height` 1.5-1.7; 45-75 chars per line. Next.js: `next/font`.
```css
body { font: 1rem/1.6 system-ui, sans-serif; }
```
हिंदी: line-height unitless।

### 60. Text properties
`text-align`, `text-transform`, `text-decoration`, `letter-spacing` (em). Ellipsis needs three lines; multi-line uses `line-clamp`.
```css
.t { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
```
हिंदी: Ellipsis = तीन properties।

### 61. Background
Colour, image, gradient, size, position, repeat, attachment, clip. Shorthand resets omitted values. Meaningful images use `<img>`.
```css
.hero { background: linear-gradient(#0008,#0008), url(h.jpg) center / cover no-repeat; }
```
हिंदी: Hero = center / cover no-repeat।

### 62. Border & border-radius
`border: width style colour` (style mandatory). Radius: `8px` soft, `50%` circle, `999px` pill; `overflow: hidden` clips children. Use `outline`/`box-shadow` for hover to avoid shift.
हिंदी: Circle = 50% (square box)।

### 63. display
block (new line, full width), inline (ignores width/height), inline-block, `none` (removed from layout and a11y tree). Use flex/grid for rows.
हिंदी: none = पूरी तरह गायब।

### 64. visibility vs display:none vs opacity
| | Space | Clickable | Animatable |
|---|---|---|---|
| `display:none` | gone | no | no |
| `visibility:hidden` | kept | no | discrete |
| `opacity:0` | kept | yes | yes |

Fade = opacity + visibility.
हिंदी: opacity:0 अभी भी click होता है।

### 65. position
static (default), relative (reference), absolute (nearest positioned ancestor), fixed (viewport), sticky (pins on scroll; needs threshold, breaks under overflow ancestors).
```css
.parent { position: relative; } .badge { position: absolute; top: 0; right: 0; }
```
हिंदी: absolute का parent relative।

### 66. z-index & stacking context
z-index works within the same stacking context. New context: positioned + z-index, `transform`, `opacity<1`, fixed/sticky, `isolation: isolate`. Use a small z-scale, portals for modals.
हिंदी: Parent का context child को क़ैद करता है।

### 67. overflow
`visible | hidden | scroll | auto` (prefer auto). Non-visible creates scroll container: clips dropdowns, changes sticky. In flex ellipsis add `min-width: 0`.
हिंदी: overflow ≠ visible = sticky टूट सकता है।

### 68. opacity vs rgba
`opacity` fades element + children; `rgba()` fades one colour. Overlays/glass = rgba. `opacity<1` makes stacking context.
हिंदी: Text crisp रखना हो तो rgba।

---

## B. INTERMEDIATE (69-90)

### 69. Flexbox
`display:flex` on parent: 1D layout. `justify-content` main axis, `align-items` cross axis.
```css
.c { display: flex; justify-content: center; align-items: center; gap: 1rem; }
```
हिंदी: दो line में centering।

### 70. Flexbox properties
`flex-direction` swaps axes; `flex-wrap` + `gap`; `flex: 1` equal share; `margin: auto` pushes apart; `min-width: 0` lets items shrink; `align-content` only multi-line.
```css
.item { flex: 1 1 0; } .push { margin-left: auto; }
```
हिंदी: flex: 1 = बराबर बँटवारा।

### 71. Grid
`display:grid` 2D layout; `fr` unit; `grid-template-areas`; responsive without media queries.
```css
.g { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
```
हिंदी: auto-fill + minmax = responsive grid।

### 72. Grid properties
Container: `grid-template-columns/rows`, `gap`, `grid-template-areas`. Items: `grid-column`, `grid-row`, `grid-area`. n tracks = n+1 lines; `minmax(0, 1fr)` stops blowout.
```css
.hdr { grid-area: header; } .g { grid-template-areas: "header header" "side main"; }
```
हिंदी: Lines numbered, tracks से एक ज़्यादा।

### 73. Flexbox vs Grid
Flex = 1D, content-driven (navbars, components). Grid = 2D, layout-driven (pages, card grids). Combine: Grid outside, Flex inside.
हिंदी: एक दिशा = flex, दो दिशा = grid।

### 74. Responsive design
Viewport meta + fluid layout + flexible images + media queries. Prefer intrinsic tools (flex-wrap, auto-fit, clamp); 44px tap targets.
```css
img { max-width: 100%; height: auto; }
```
हिंदी: Breakpoint वहाँ जहाँ content टूटे।

### 75. Media queries
`@media (cond) {}` for width, orientation, hover, dark mode, print. Write `min-width` small to large.
```css
@media (min-width: 768px) { .nav { display: flex; } }
```
हिंदी: Order मायने रखता है।

### 76. Mobile-first vs desktop-first
Mobile-first = base for phones + `min-width` additions (Tailwind: unprefixed = mobile, `md:` = 768px+). Desktop-first = `max-width` undoing. Pick one.
हिंदी: Mobile-first = कम CSS, कम override।

### 77. CSS variables
`--name: value`, read `var(--name, fallback)`. Inherit, live in browser (JS can change), best for tokens/themes; not usable in media conditions.
```css
:root { --brand: #36c; } .btn { background: var(--brand); }
```
हिंदी: Runtime पर बदलने वाले variables।

### 78. Transitions
`transition: property duration timing delay` between two states. Put on base selector; prefer `transform`/`opacity`; avoid `all`. Cannot animate `display` / `height:auto` classically.
```css
.btn { transition: transform .2s ease; } .btn:hover { transform: translateY(-2px); }
```
हिंदी: Trigger चाहिए; base पर लिखो।

### 79. Animations & keyframes
No trigger, can loop/alternate/pause. Animate `transform`/`opacity`; `forwards` keeps end state; respect `prefers-reduced-motion`.
```css
@keyframes spin { to { transform: rotate(360deg); } }
.s { animation: spin 1s linear infinite; }
```
हिंदी: Animation अपने-आप चलता है।

### 80. transform
`translate rotate scale skew`; layout not affected; order matters; `transform-origin` pivot; not on inline. GPU-friendly.
```css
.x { transform: translate(-50%, -50%) rotate(45deg); }
```
हिंदी: top/left की जगह transform।

### 81. Shadows
`box-shadow: x y blur spread colour` (+`inset`); layer two low-opacity shadows; `text-shadow` has no spread; `drop-shadow()` for non-rect shapes.
```css
.card { box-shadow: 0 1px 2px #0003, 0 8px 24px #0002; }
```
हिंदी: Shadow layout नहीं बदलता।

### 82. Gradients
`linear-gradient`, `radial-gradient`, `conic-gradient` in `background-image`. Same-position stops = hard edge. Not directly transitionable; animate position/size.
```css
background: linear-gradient(135deg, #6a11cb, #2575fc);
```
हिंदी: Gradient = image, color नहीं।

### 83. Filters
`blur brightness grayscale drop-shadow` chained; `backdrop-filter` blurs behind (glass UI, needs translucent bg). Creates stacking context; GPU-costly.
```css
.glass { background: #fff3; backdrop-filter: blur(10px); }
```
हिंदी: backdrop-filter = पीछे का blur।

### 84. object-fit / position
`cover` fills + crops, `contain` shows all, `fill` distorts. `object-position` picks visible part. Box needs height or `aspect-ratio`.
```css
img { width: 100%; height: 200px; object-fit: cover; object-position: top; }
```
हिंदी: cover = भरो और काटो।

### 85. clip-path
Shapes `circle() inset() polygon() path()`; layout unchanged; clipped area gets no clicks; animate same shape + same point count. Shadow via `filter: drop-shadow` on parent.
```css
.tri { clip-path: polygon(50% 0, 100% 100%, 0 100%); }
```
हिंदी: Shape के बाहर सब छुप जाता है।

### 86. float & clear
`float` wraps text around; `clear` goes below floats. Parent collapses: fix with `display: flow-root` or `::after` clearfix. Layout = flex/grid.
```css
.wrap { display: flow-root; }
```
हिंदी: float अब सिर्फ text wrap के लिए।

### 87. calc()
Mix units at render time. Spaces around `+`/`-` mandatory; `*` `/` need a unitless side.
```css
.main { width: calc(100% - 250px); }
```
हिंदी: + - के दोनों ओर space।

### 88. min() max() clamp()
`min` = cap, `max` = floor, `clamp(MIN, PREF, MAX)`. Fluid font without breakpoints; include `rem` term for accessibility.
```css
h1 { font-size: clamp(1.5rem, 1rem + 2vw, 3rem); } .c { width: min(100% - 2rem, 1100px); }
```
हिंदी: clamp = न कम, न ज़्यादा।

### 89. :not()
Select everything except; adds no specificity itself (its most specific argument counts). `:not(.a, .b)` = not a AND not b.
```css
li:not(:last-child) { border-bottom: 1px solid #ddd; }
```
हिंदी: Exception सीधे चुनो।

### 90. Attribute selectors
`[x] [x="v"] ^= $= *= ~= |=`; specificity (0,1,0); `i` flag for case-insensitive.
```css
a[href^="https"]::after { content: " ↗"; } input[type="email"] { }
```
हिंदी: Attribute = class जितनी specificity।

---

## C. ADVANCED (91-110)

### 91. CSS architecture
CSS is global; BEM `block__element--modifier` keeps selectors flat (0,1,0). OOCSS, SMACSS. In React: CSS Modules/Tailwind, same ideas.
```css
.card__title--big { }
```
हिंदी: BEM = flat और predictable नाम।

### 92. Specificity wars / !important
Cascade: importance, inline, layer, specificity, source order. `!important` last resort (utilities, 3rd-party inline, reduced motion). Use flat selectors, `:where()`, `@layer`.
हिंदी: !important से बचो; layer इस्तेमाल करो।

### 93. CSS performance
CSS is render-blocking: small, remove unused, inline critical, no `@import`. Animate `transform`/`opacity` only; no `transition: all`; `content-visibility`, `font-display: swap`.
हिंदी: सिर्फ composite properties animate।

### 94. Critical CSS
Inline CSS for first screen (~14 KB), load rest non-blocking (`media="print"` + `onload`, or preload). Tools: critical, Critters; Next.js splits per route.
```html
<link rel="stylesheet" href="rest.css" media="print" onload="this.media='all'">
```
हिंदी: पहली screen की CSS head में inline।

### 95. Containment
`contain` makes subtree independent. `content-visibility: auto` skips off-screen rendering; add `contain-intrinsic-size`. Side effects: clipping, size collapse, stacking context.
```css
.sec { content-visibility: auto; contain-intrinsic-size: 0 500px; }
```
हिंदी: Off-screen render skip।

### 96. will-change
Hints a property will change (GPU layer). Use sparingly, apply just before, remove after. Creates stacking context; misuse wastes GPU memory.
हिंदी: हर जगह मत लगाओ।

### 97. scroll-behavior & snap
`scroll-behavior: smooth` (guard with reduced-motion). Snap: container `scroll-snap-type`, child `scroll-snap-align`. `scroll-padding` for sticky headers.
```css
.row { scroll-snap-type: x mandatory; overflow-x: auto; } .row > * { scroll-snap-align: start; }
```
हिंदी: Carousel = mandatory snap।

### 98. aspect-ratio
Replaces padding-top hack; preferred ratio (explicit width+height override). Pair with `object-fit: cover`.
```css
.v { aspect-ratio: 16 / 9; }
```
हिंदी: Layout shift से बचाव।

### 99. Logical properties
`margin-inline-start`, `padding-block`, `inline-size`, `inset-inline-end`, `text-align: start` follow writing direction. `dir="rtl"` mirrors; transforms/icons need manual care.
हिंदी: left/right की जगह start/end।

### 100. Writing modes
`writing-mode: horizontal-tb | vertical-rl | vertical-lr`; inline-size becomes height in vertical modes; `text-orientation` fine-tunes. Vertical text needs height.
हिंदी: Vertical text rotate hack के बिना।

### 101. Dark mode (prefers-color-scheme)
`@media (prefers-color-scheme: dark)` overrides variables; `color-scheme: light dark`; `light-dark()`. Manual toggle: `data-theme` + localStorage + blocking script (or `next-themes`).
```css
:root { color-scheme: light dark; } @media (prefers-color-scheme: dark) { :root { --bg: #111; } }
```
हिंदी: Variables बदलो, components नहीं।

### 102. Print styles
`@media print`: hide nav/ads, white bg, black text. `break-inside`, `orphans`, `widows`, `@page`; show URLs with `attr(href)`.
```css
@media print { nav { display: none; } a::after { content: " (" attr(href) ")"; } }
```
हिंदी: Print में nav छुपाओ।

### 103. Subgrid
Nested grid borrows parent's tracks so siblings align. `grid-row: span N; display: grid; grid-template-rows: subgrid;`. Use `@supports` fallback.
हिंदी: Parent की rows उधार।

### 104. Container queries
Style by parent size: `container-type: inline-size` then `@container (min-width: ...)`. Media for page layout, container for components.
```css
.wrap { container-type: inline-size; } @container (min-width: 400px) { .card { display: flex; } }
```
हिंदी: Viewport नहीं, parent देखो।

### 105. CSS nesting
Child rules inside parent; `&` for same-element states (`&:hover`), parent context (`.dark &`). Keep shallow.
```css
.btn { color: #fff; &:hover { opacity: .9; } }
```
हिंदी: Sass जैसा nesting, native।

### 106. @layer
`@layer a, b, c;` later layers win regardless of specificity; unlayered beats all layers; `!important` reverses order. Tames third-party CSS.
```css
@layer reset, base, components, utilities;
```
हिंदी: Layer order > specificity।

### 107. Houdini
`@property` (typed, animatable custom properties; all modern browsers), Typed OM, Paint API (Chromium-only, progressive enhancement).
```css
@property --angle { syntax: "<angle>"; inherits: false; initial-value: 0deg; }
```
हिंदी: Variables को type देता है।

### 108. Tailwind basics
Utility-first; only used classes generated; variants `hover: md: dark:` mobile-first. Extract components (not `@apply`), no dynamic class strings, `clsx` + `tailwind-merge`.
```html
<button class="px-4 py-2 rounded-xl hover:bg-blue-700 md:px-6">Go</button>
```
हिंदी: Class नाम पूरे लिखो, जोड़ो नहीं।

### 109. CSS Modules
`*.module.css` hashes class names (local scope); `styles.name`; `:global()`, `composes`. Zero runtime; built into Next.js/Vite.
```jsx
import styles from "./Card.module.css"; <div className={styles.card} />
```
हिंदी: Class नाम का टकराव खत्म।

### 110. styled-components
CSS-in-JS tagged templates; props, `$transient` props, `ThemeProvider`. Runtime cost, needs client components + SSR registry in Next.js; in maintenance mode, weigh Modules/Tailwind.
```jsx
const Btn = styled.button`background: ${p => p.$primary ? "blue" : "gray"};`;
```
हिंदी: Runtime cost है; नए project में सोचो।

---

## D. Interview problems 111-125 (key trick each)
| # | Problem | Key trick |
|---|---|---|
| 111 | Responsive navbar | Mobile-first collapsed menu; `min-width: 768px` -> flex row; `aria-expanded` button; `max-height` transition |
| 112 | Card component | Grid `repeat(auto-fill, minmax(280px, 1fr))`; card = flex column with growing body; stretched link |
| 113 | Centering (5 ways) | Flex `justify/align: center`; grid `place-items: center`; absolute + `translate(-50%,-50%)`; `margin: 0 auto` (horizontal only) |
| 114 | Modal | Native `<dialog>` + `showModal()`; style `::backdrop`; lock body scroll |
| 115 | Responsive grid | `repeat(auto-fit, minmax(200px, 1fr))`; `gap`; no media queries |
| 116 | Triangle | Zero-size box, thick border, one side coloured, others transparent (or `clip-path: polygon`) |
| 117 | Sticky header | `position: sticky; top: 0`; fails with ancestor `overflow` |
| 118 | Hamburger | 3 spans; rotate outer two +/-45deg, fade middle; animate transform/opacity |
| 119 | Loading spinner | Bordered circle, one side coloured, `rotate(360deg)` `linear infinite`; skeleton via sliding gradient |
| 120 | Responsive table | `overflow-x: auto` wrapper, or rows -> cards with `td::before { content: attr(data-label) }` |
| 121 | Image gallery | Grid auto-fill + `grid-auto-rows` + `span` tiles; `object-fit: cover` |
| 122 | Tooltip | Relative trigger + absolute `::after { content: attr(data-tip) }`; show on `:hover` and `:focus-visible` |
| 123 | Form styling | `font: inherit`, border-box, `:focus-visible` ring, `:user-invalid`, `accent-color` |
| 124 | Button hover effects | `transition` on base, animate `transform`/`box-shadow` not `all`; `@media (hover: hover)` |
| 125 | Dark mode toggle | Colours as variables, `[data-theme="dark"]` override; inline head script + localStorage prevents flash |

---

## Top 20 CSS interview questions (quick list)
1. Explain the box model and `box-sizing: border-box`. -> #55-56
2. How is specificity calculated? Order of ids/classes/elements/inline. -> #53
3. Cascade vs inheritance; which properties inherit? -> #54
4. `display: none` vs `visibility: hidden` vs `opacity: 0`. -> #64
5. Explain `position` values and when sticky fails. -> #65, #117
6. What is a stacking context? Why does z-index sometimes fail? -> #66
7. Flexbox vs Grid; when to use each. -> #73
8. How to center a div (multiple ways)? -> #113
9. `rem` vs `em` vs `px` vs `%` vs `vw`. -> #58
10. Mobile-first vs desktop-first; media queries. -> #75-76
11. `opacity` vs `rgba()`. -> #68
12. Pseudo-class vs pseudo-element; `:not`, `:has`. -> #50-52, #89
13. CSS variables vs Sass variables; how do you theme/dark mode? -> #77, #101, #125
14. Transition vs animation; what properties are cheap to animate? -> #78-79, #93
15. `auto-fit` vs `auto-fill`; `minmax`, `fr`. -> #71-72
16. What is margin collapse? -> #55
17. How to clear floats / what is `flow-root`? -> #86
18. `clamp()`, `min()`, `max()` for fluid sizing. -> #88
19. Container queries vs media queries; `@layer`; nesting. -> #104-106
20. How do you avoid `!important` wars / organise CSS (BEM, Modules, Tailwind)? -> #91-92, #108-109
