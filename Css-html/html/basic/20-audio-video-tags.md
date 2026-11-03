# 20. Audio + Video Tags
# हिंदी में: Audio और Video Tags — बिना Plugin के Media चलाना

---

## 🔵 Simple Definition (English)
`<audio>` and `<video>` embed sound and video directly in a web page with built-in controls, no plugin needed. You give one or more `<source>` files, and the browser picks the first format it can play. Attributes like `controls`, `autoplay`, `muted`, `loop`, `poster`, `preload` and `<track>` (subtitles) control behavior.

## 🔵 सरल परिभाषा (Hindi)
`<audio>` और `<video>` आवाज़ और video को सीधे web page में built-in controls के साथ embed करते हैं, plugin की ज़रूरत नहीं। आप एक या ज़्यादा `<source>` files देते हो और browser पहली play हो सकने वाली format चुनता है। `controls`, `autoplay`, `muted`, `loop`, `poster`, `preload` और `<track>` (subtitles) जैसे attributes behavior तय करते हैं।

---

## 🔴 Problem it Solves
```
BEFORE (2000s):
  <object> / <embed> + Adobe Flash plugin
  - User must install a plugin; crashes, security holes, battery drain
  - Not supported on iPhone/iPad -> Apple refused Flash
  - No standard controls, no accessibility, no SEO
  - Flash ended 31 Dec 2020

WITH <video> / <audio>:
  <video src="movie.mp4" controls></video>
  - Works everywhere, hardware-accelerated, battery friendly
  - Styleable with CSS, scriptable with JS (play(), pause(), currentTime)
  - Captions with <track>, fallbacks with <source>
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले (2000s):
  <object> / <embed> + Adobe Flash plugin
  - User को plugin install करना पड़ता था; crash, security खतरे, battery खर्च
  - iPhone/iPad पर नहीं चलता -> Apple ने Flash मना कर दिया
  - कोई standard controls, accessibility या SEO नहीं
  - Flash 31 Dec 2020 को खत्म

<video> / <audio> के साथ:
  <video src="movie.mp4" controls></video>
  - हर जगह चलता है, hardware-accelerated, battery के लिए अच्छा
  - CSS से style, JS से control (play(), pause(), currentTime)
  - <track> से captions, <source> से fallbacks
```

---

## 🟢 How it Works — Step by Step

```
BASIC SYNTAX:
  <video controls width="640" poster="thumb.jpg" preload="metadata">
    <source src="clip.webm" type="video/webm">   <- tried first
    <source src="clip.mp4"  type="video/mp4">    <- fallback
    <track kind="subtitles" src="hi.vtt" srclang="hi" label="Hindi" default>
    Your browser does not support video. <a href="clip.mp4">Download</a>
  </video>

STEPS THE BROWSER TAKES:
1. Reads <source> children in order. Checks the type attribute (MIME + codec).
2. Picks the first it can decode; downloads only that one.
3. Loads according to `preload`; shows `poster` until playback starts.
4. Provides default UI if `controls` is present; otherwise you build custom UI via JS.
5. Fires events: loadedmetadata, canplay, play, pause, ended, timeupdate, error.

KEY ATTRIBUTES:
  controls     show play/pause/volume/seek UI
  autoplay     start automatically (BLOCKED by browsers unless muted - see below)
  muted        start silent (required for autoplay on most browsers)
  loop         restart at the end
  poster       image shown before playback (video only)
  preload      none | metadata | auto  (hint: how much to fetch up front)
  playsinline  play inside the page on iOS instead of fullscreen
  width/height set size (also prevents layout shift)
  crossorigin  needed for tracks/canvas from another origin
  controlsList="nodownload"  hide some controls; disablePictureInPicture etc.

FORMATS (broad support):
  Video: MP4 (H.264/AAC) works everywhere; WebM (VP9/AV1) smaller; Ogg legacy.
  Audio: MP3, AAC (m4a), Ogg Vorbis/Opus, WAV.
  Tip: one MP4 (H.264) alone covers nearly all modern browsers.

AUTOPLAY POLICY:
  Browsers allow autoplay only if the video is muted (or the user interacted with
  the site). Hence the common background-video recipe:
  <video autoplay muted loop playsinline>

SUBTITLES: <track> uses WebVTT (.vtt). kind: subtitles | captions | descriptions | chapters.

STREAMING: for long videos (YouTube, Netflix) use HLS/DASH via a library (hls.js)
or the Media Source Extensions. A plain <video src> downloads progressively.

JS API:
  video.play() (returns a Promise!), video.pause(), video.currentTime = 30,
  video.volume = 0.5, video.playbackRate = 1.5, video.requestFullscreen()
```

## 🟢 कैसे काम करता है? (Hindi)

```
BASIC SYNTAX:
  <video controls width="640" poster="thumb.jpg" preload="metadata">
    <source src="clip.webm" type="video/webm">   <- पहले यह try होता है
    <source src="clip.mp4"  type="video/mp4">    <- fallback
    <track kind="subtitles" src="hi.vtt" srclang="hi" label="Hindi" default>
    Browser video support नहीं करता।
  </video>

Browser के steps:
1. <source> को क्रम से पढ़ता है और type (MIME + codec) देखता है।
2. जो पहली decode हो सके उसे चुनता है; सिर्फ वही download होती है।
3. `preload` के अनुसार load करता है; play शुरू होने तक `poster` दिखाता है।
4. `controls` हों तो default UI देता है; वरना JS से अपनी UI बनाओ।
5. Events आते हैं: loadedmetadata, canplay, play, pause, ended, timeupdate, error।

मुख्य ATTRIBUTES:
  controls     play/pause/volume/seek UI दिखाता है
  autoplay     अपने आप शुरू (muted न हो तो browsers रोक देते हैं)
  muted        बिना आवाज़ के शुरू
  loop         खत्म होकर फिर शुरू
  poster       play से पहले दिखने वाली image
  preload      none | metadata | auto  (कितना पहले से लाना है)
  playsinline  iOS पर fullscreen की जगह page में चलाना
  width/height size तय करता है (layout shift भी रोकता है)

FORMATS:
  Video: MP4 (H.264/AAC) हर जगह; WebM छोटा size। Audio: MP3, AAC, Ogg/Opus।

AUTOPLAY नियम:
  Browser autoplay तभी देते हैं जब video muted हो (या user ने site से interact किया हो)।
  इसीलिए background video: <video autoplay muted loop playsinline>

SUBTITLES: <track> WebVTT (.vtt) file use करता है।

JS API: video.play() (Promise लौटाता है!), pause(), currentTime, volume, playbackRate।
```

---

## 🟡 Real World Example
**Instagram Reels / Amazon product videos:** Reels play a muted looping `<video autoplay muted loop playsinline>` as you scroll, with a `poster` so there is no blank box. **Zomato / Swiggy hero banners** use short muted background videos. **Spotify / Gaana-style previews** and podcasts use `<audio controls>` or a custom UI via the Audio API. **Netflix/YouTube** use `<video>` with a streaming library (the browser plays the stream fed by Media Source Extensions) and `<track>` for subtitles.

## 🟡 Real Example Hindi mein
**Instagram Reels / Amazon product videos:** Reels scroll करते समय muted looping `<video autoplay muted loop playsinline>` चलाते हैं और `poster` देते हैं ताकि खाली box न दिखे। **Zomato / Swiggy hero banners** में छोटे muted background videos होते हैं। **Spotify / Gaana जैसे previews** और podcasts `<audio controls>` या Audio API से बनी custom UI use करते हैं। **Netflix/YouTube** `<video>` के साथ streaming library (Media Source Extensions) और subtitles के लिए `<track>` use करते हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Audio + Video Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; max-width: 760px; margin: 24px auto; padding: 0 16px; line-height: 1.5; }
    h2 { margin: 28px 0 8px; font-size: 18px; border-bottom: 2px solid #333; padding-bottom: 4px; }

    /* Responsive video: width 100% and keep ratio. aspect-ratio avoids layout shift. */
    video { width: 100%; height: auto; aspect-ratio: 16 / 9; background: #000; border-radius: 8px; }
    audio { width: 100%; }

    /* Hero background video recipe: video covers the box, text sits on top */
    .hero { position: relative; height: 200px; overflow: hidden; border-radius: 8px; background: #222; }
    .hero video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; border-radius: 0; }
    .hero h3 { position: relative; color: #fff; text-align: center; margin: 0; line-height: 200px; text-shadow: 0 2px 6px #000; }

    /* Custom controls */
    .controls { display: flex; gap: 8px; margin-top: 8px; align-items: center; }
    button { background: #e23744; color: #fff; border: 0; padding: 8px 14px; border-radius: 6px; cursor: pointer; }
    #time { font-variant-numeric: tabular-nums; color: #555; }
  </style>
</head>
<body>
  <h1>Audio + Video</h1>

  <h2>1. Video with controls, poster, multiple sources, captions</h2>
  <!-- Replace src with your own files. Sample public file used below (needs internet). -->
  <video id="v" controls preload="metadata" playsinline
         poster="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='360'%3E%3Crect width='640' height='360' fill='%23333'/%3E%3Ctext x='320' y='190' fill='white' font-size='28' text-anchor='middle'%3EClick play%3C/text%3E%3C/svg%3E">
    <!-- Browser picks the first format it supports -->
    <source src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.webm" type="video/webm">
    <source src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4" type="video/mp4">
    <!-- Subtitles file would go here: <track kind="subtitles" src="hi.vtt" srclang="hi" label="Hindi" default> -->
    <!-- Fallback content for very old browsers -->
    <p>Your browser cannot play this video. <a href="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4">Download it</a>.</p>
  </video>

  <!-- Custom controls built with the JS API -->
  <div class="controls">
    <button id="play" type="button">Play</button>
    <button id="mute" type="button">Mute</button>
    <button id="fast" type="button">1x</button>
    <span id="time">0:00</span>
  </div>

  <h2>2. Audio player</h2>
  <audio controls preload="none">
    <source src="https://interactive-examples.mdn.mozilla.net/media/cc0-audio/t-rex-roar.mp3" type="audio/mpeg">
    Your browser does not support audio.
  </audio>

  <h2>3. Background hero video (autoplay needs muted)</h2>
  <div class="hero">
    <video autoplay muted loop playsinline aria-hidden="true">
      <source src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4" type="video/mp4">
    </video>
    <h3>Hungry? Order now</h3>
  </div>

  <script>
    const v = document.getElementById('v');
    const playBtn = document.getElementById('play');

    // play() returns a Promise: it can be rejected (autoplay policy), so handle errors
    playBtn.addEventListener('click', async () => {
      try {
        if (v.paused) { await v.play(); playBtn.textContent = 'Pause'; }
        else { v.pause(); playBtn.textContent = 'Play'; }
      } catch (err) { console.warn('Playback blocked or failed:', err.name); }
    });

    document.getElementById('mute').addEventListener('click', e => {
      v.muted = !v.muted; e.target.textContent = v.muted ? 'Unmute' : 'Mute';
    });

    document.getElementById('fast').addEventListener('click', e => {
      v.playbackRate = v.playbackRate === 1 ? 2 : 1; e.target.textContent = v.playbackRate + 'x';
    });

    // timeupdate fires several times per second while playing
    v.addEventListener('timeupdate', () => {
      const s = Math.floor(v.currentTime);
      document.getElementById('time').textContent = Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
    });
    v.addEventListener('ended', () => { playBtn.textContent = 'Play'; });
  </script>
</body>
</html>
```

```css
/* Pause-on-scroll/Reduced motion respect (pair with JS/IntersectionObserver) */
@media (prefers-reduced-motion: reduce) {
  .hero video { display: none; }   /* skip decorative background video for sensitive users */
}
```

---

## 🟠 React/Next.js Connection

```jsx
// <video> in JSX: camelCase attributes: autoPlay, playsInline, crossOrigin
// IMPORTANT: React does not always set `muted` as an attribute, only as a property,
// which can break autoplay on iOS/SSR. Setting it via ref is the safest fix.
'use client';
import { useRef, useEffect } from 'react';

export default function HeroVideo() {
  const ref = useRef(null);

  useEffect(() => {
    if (ref.current) ref.current.muted = true;     // ensure muted property
    ref.current?.play().catch(() => {});            // autoplay might be blocked
  }, []);

  return (
    <video ref={ref} autoPlay muted loop playsInline poster="/poster.jpg"
           className="w-full aspect-video object-cover rounded-lg">
      <source src="/hero.webm" type="video/webm" />
      <source src="/hero.mp4" type="video/mp4" />
    </video>
  );
}

// Controlled playback: keep the element in a ref, call ref.current.play()/pause()
// from onClick; mirror state with onPlay / onPause / onTimeUpdate props.

// Next.js: put files in /public and reference with "/hero.mp4".
// Next.js <Image> is for images only; for video use <video> or a service
// (Mux, Cloudinary, YouTube embed) and load lazily: preload="none" + IntersectionObserver.
// Libraries: react-player (YouTube/Vimeo/HLS), video.js, hls.js for streaming.
// Tailwind: "aspect-video", "object-cover", "w-full".
```

---

## ⚫ Interview Questions + Answers

**Q1: Why use multiple `<source>` elements inside `<video>`?**
A1: Different browsers support different codecs/containers. The browser tests each `<source>` in order (using `type`) and plays the first one it supports, downloading only that file. Listing WebM/AV1 first and MP4/H.264 as the fallback gives smaller files for modern browsers and compatibility for all. Text inside `<video>` is fallback content for browsers without support.

**Q2: Why doesn't my `autoplay` video play? How do you fix it?**
A2: Browsers block autoplay with sound to avoid annoying users. Autoplay works when the video is `muted` (and on iOS also `playsinline`), or when the user has interacted with the site. Use `<video autoplay muted loop playsinline>`. Also `video.play()` returns a Promise that rejects when blocked, so catch it.

**Q3: What does `preload` do and which value should you pick?**
A3: It is a hint for how much media to fetch before the user presses play: `none` (nothing, saves bandwidth), `metadata` (duration/dimensions only, a good default), `auto` (browser may download the whole file). On mobile data or pages with many videos use `none` or `metadata`, and a `poster` image so the player does not look empty.

**Q4: How do you add subtitles and make video accessible?**
A4: Add `<track kind="subtitles" src="en.vtt" srclang="en" label="English" default>` with a WebVTT file; use `kind="captions"` for deaf/hard-of-hearing users (includes sound descriptions). Provide a transcript for audio-only content, keep `controls` available (keyboard accessible), avoid autoplay with sound, and respect `prefers-reduced-motion` for decorative backgrounds.

**Q5: How do you build custom video controls?**
A5: Remove `controls`, and build your own buttons that call the Media API: `play()`, `pause()`, set `currentTime`, `volume`, `muted`, `playbackRate`, `requestFullscreen()`, and listen to events such as `timeupdate`, `loadedmetadata`, `ended`. Keep the controls keyboard accessible with real `<button>`s and ARIA labels, and handle the promise from `play()`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Autoplay with sound
```html
<video autoplay src="ad.mp4"></video>   <!-- blocked by most browsers -->
```
✅ **Correct way:** `<video autoplay muted loop playsinline src="ad.mp4"></video>` and let the user unmute.

❌ **Mistake 2:** No `controls` and no custom UI, or huge unoptimized files
```html
<video src="raw-4k-recording.mov"></video>
```
✅ **Correct way:** Add `controls` (or custom buttons), compress to MP4/H.264 or WebM, use `preload="metadata"` and a `poster`.

❌ **Mistake 3:** Not reserving space (layout shift)
✅ **Correct way:** Set `width`/`height` attributes or CSS `aspect-ratio: 16/9`.

❌ **Mistake 4:** Using `<video>` for a GIF-like short loop as a heavy GIF file
✅ **Correct way:** Replace animated GIFs with `<video autoplay muted loop playsinline>`: often 80-90% smaller.

❌ **Mistake 5:** Ignoring `play()` Promise rejections
✅ **Correct way:** `video.play().catch(() => { /* show a play button */ })`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `<video>` / `<audio>` | Native media elements | Native media elements |
| `<source>` | One media file option with type | एक media file विकल्प |
| `controls` | Show built-in player UI | Player की UI दिखाना |
| `poster` | Image before video plays | Play से पहले की image |
| `<track>` | Subtitles/captions (WebVTT) | Subtitles |
| Codec | Method of encoding/decoding media | Media encode/decode का तरीका |
| `preload` | Hint for how much to load early | पहले कितना load करना है |
| Autoplay policy | Browser rule blocking unmuted autoplay | बिना mute autoplay रोकने का नियम |

---

## ⚡ 3-Line Summary
**English:**
1. `<video>` and `<audio>` play media natively; list several `<source>` formats, add `controls`, `poster`, `preload` and `<track>` for subtitles.
2. Autoplay works only when `muted` (use `autoplay muted loop playsinline`); `play()` returns a Promise to handle.
3. In React set `muted` via ref, use `autoPlay`/`playsInline`, reserve space with `aspect-ratio`, and prefer lazy loading.

**Hindi:**
1. `<video>` और `<audio>` native media चलाते हैं; कई `<source>` formats दो, और `controls`, `poster`, `preload` व subtitles के लिए `<track>` जोड़ो।
2. Autoplay सिर्फ `muted` होने पर चलता है (`autoplay muted loop playsinline`); `play()` Promise देता है जिसे handle करो।
3. React में `muted` ref से set करो, `autoPlay`/`playsInline` लिखो, `aspect-ratio` से जगह reserve करो और lazy loading रखो।

---

## ➡️ Next Topic
**21. DOM — Document Object Model** — HTML intermediate level शुरू: browser इस पूरे HTML को JavaScript के लिए tree में कैसे बदलता है, और उसे कैसे बदलें।
