# 122. Animated API — React Native Built-in
# हिंदी में: React Native का Built-in Animated API
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
React Native's built-in `Animated` API is the first-party way to create animations. It uses **Animated Values** that drive style changes directly — no re-renders on every frame. With `useNativeDriver: true`, animations run on the **UI thread** (not JS thread), giving smooth 60fps even when JavaScript is busy. For complex gestures or UI-thread-locked animations, use Reanimated v3 instead.

## 🔵 सरल परिभाषा (Hindi)
React Native का built-in `Animated` API animations बनाने का first-party तरीका है। यह **Animated Values** use करता है जो style changes directly drive करते हैं — हर frame पर re-render नहीं। `useNativeDriver: true` के साथ, animations **UI thread** पर run होते हैं (JS thread नहीं), 60fps smooth चाहे JavaScript busy हो। Complex gestures या UI-thread-locked animations के लिए Reanimated v3 use करो।

---

## 🔴 Problem it Solves
```
ANIMATION WITHOUT Animated API:
  useState for animation values → re-render on every frame
  At 60fps: 60 setState calls/second → TERRIBLE performance
  JS Thread blocked → UI freezes

Animated API solution:
  Animated.Value('opacity') → not stored in React state
  Animated.timing(opacity, { toValue: 1 }) → sends to UI thread
  useNativeDriver: true → bypasses JS thread entirely!
  Result: 60fps smooth even when JS is busy
```

## 🔴 यह क्यों बना? (Hindi)
```
setState animation = हर frame re-render = 60 setState/second = slow
Animated API: Value → style change → UI thread directly
useNativeDriver: true → JS thread involved नहीं = 60fps guaranteed
```

---

## 🟢 How it Works — Step by Step

```
ANIMATED VALUE LIFECYCLE:
──────────────────────────────────────────────────────
  Step 1 → Create an Animated.Value
           const opacity = useRef(new Animated.Value(0)).current;
           // Initial value: 0

  Step 2 → Attach to a style
           <Animated.View style={{ opacity }} />
           // React Native knows this is an Animated.Value

  Step 3 → Create animation driver
           Animated.timing(opacity, {
             toValue: 1,         // animate to this value
             duration: 500,      // 500ms
             useNativeDriver: true, // UI thread!
           })

  Step 4 → Start the animation
           Animated.timing(opacity, { ... }).start(() => {
             // callback when animation finishes
           })

  Step 5 → UI Thread drives the animation
           opacity: 0 → 0.1 → 0.2 → ... → 1.0
           Each frame computed on UI thread
           JS thread not involved! ✅

ANIMATION TYPES:
  Animated.timing()   → linear/eased, specific duration
  Animated.spring()   → physics-based bounce
  Animated.decay()    → friction-based deceleration
  Animated.delay()    → wait then animate
  Animated.sequence() → one after another
  Animated.parallel() → all at once
  Animated.stagger()  → sequential with delay between each
```

## 🟢 कैसे काम करता है? (Hindi)
```
Animated.Value create → Animated.View style में attach
→ timing/spring/decay → start() → UI thread पर animate
useNativeDriver: true = JS thread bypass, 60fps guaranteed
```

---

## 🟡 Real World Example
**Swiggy "Add to Cart" animation:** When user taps "+" button, a small food item icon flies from the restaurant card to the cart icon (top right). This uses `Animated.parallel()` — simultaneously animating: `translateX` (moves right → cart position), `translateY` (moves up → cart position), `scale` (shrinks from 1 to 0.2), `opacity` (fades out). All with `useNativeDriver: true` = smooth 60fps even while new items are loading.

## 🟡 Real Example Hindi मे
**Swiggy Cart Animation:** "+" tap → food icon card से cart icon तक fly करती है। `Animated.parallel()` — एक साथ: translateX, translateY (position move), scale (shrink), opacity (fade)। `useNativeDriver: true` = 60fps smooth, items load होते रहें।

---

## 💻 Code Example — Basic

```jsx
import React, { useRef, useEffect } from 'react';
import { View, Text, TouchableOpacity, Animated, StyleSheet } from 'react-native';

// FADE IN animation
function FadeInView({ children }) {
  // useRef to keep Animated.Value across renders (not useState!)
  const fadeAnim = useRef(new Animated.Value(0)).current;  // start invisible

  useEffect(() => {
    // Start animation when component mounts
    Animated.timing(fadeAnim, {
      toValue: 1,           // fade to fully visible
      duration: 600,        // 600ms
      useNativeDriver: true, // run on UI thread ← IMPORTANT for performance!
    }).start();
  }, []);

  return (
    // Animated.View — not View! wraps Animated.Value styles
    <Animated.View style={[styles.container, { opacity: fadeAnim }]}>
      {children}
    </Animated.View>
  );
}

// SLIDE IN + FADE animation
function SlideInCard() {
  const translateY = useRef(new Animated.Value(50)).current;  // starts 50px below
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Run both animations simultaneously
    Animated.parallel([
      Animated.timing(translateY, {
        toValue: 0,           // slide to normal position
        duration: 400,
        useNativeDriver: true,
      }),
      Animated.timing(opacity, {
        toValue: 1,           // fade in
        duration: 400,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  return (
    <Animated.View style={[
      styles.card,
      {
        opacity,
        transform: [{ translateY }],  // transform array!
      }
    ]}>
      <Text style={styles.cardText}>Swiggy Card</Text>
    </Animated.View>
  );
}

// BUTTON PRESS animation (scale down on press)
function AnimatedButton({ onPress, children }) {
  const scale = useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    Animated.spring(scale, {
      toValue: 0.95,           // shrink slightly
      useNativeDriver: true,
    }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scale, {
      toValue: 1,              // bounce back
      friction: 3,             // spring bounciness
      useNativeDriver: true,
    }).start();
  };

  return (
    <TouchableOpacity
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      onPress={onPress}
      activeOpacity={1}   // disable default opacity — we handle it
    >
      <Animated.View style={[styles.button, { transform: [{ scale }] }]}>
        <Text style={styles.buttonText}>{children}</Text>
      </Animated.View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    margin: 16,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  cardText: { fontSize: 18, fontWeight: '700' },
  button: {
    backgroundColor: '#f97316',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: { color: '#fff', fontWeight: '700', fontSize: 16 },
});
```

## 💻 Code Example — Advanced

```jsx
import React, { useRef, useState } from 'react';
import {
  View, Text, TouchableOpacity, Animated, StyleSheet, Dimensions
} from 'react-native';

const { width } = Dimensions.get('window');

// SEQUENCE + LOOP — loading skeleton pulse
function SkeletonPulse() {
  const opacity = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    // Create a looping pulse animation
    const pulse = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, {
          toValue: 1,          // fade to full
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.timing(opacity, {
          toValue: 0.3,        // fade back
          duration: 800,
          useNativeDriver: true,
        }),
      ])
    );
    pulse.start();
    return () => pulse.stop();  // cleanup!
  }, []);

  return (
    <View style={styles.skeletonContainer}>
      <Animated.View style={[styles.skeletonLine, { opacity, width: '60%' }]} />
      <Animated.View style={[styles.skeletonLine, { opacity, width: '100%' }]} />
      <Animated.View style={[styles.skeletonLine, { opacity, width: '80%' }]} />
    </View>
  );
}

// INTERPOLATION — map Animated.Value to different output ranges
function ColorChangingCard() {
  const animation = useRef(new Animated.Value(0)).current;
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    Animated.timing(animation, {
      toValue: isExpanded ? 0 : 1,
      duration: 300,
      useNativeDriver: false,  // ⚠️ color animation CANNOT use native driver!
    }).start(() => setIsExpanded(!isExpanded));
  };

  // Interpolate: map 0→1 to a color range
  const backgroundColor = animation.interpolate({
    inputRange: [0, 1],
    outputRange: ['#f9f9f9', '#fff7ed'],  // light gray → light orange
  });

  // Interpolate: map 0→1 to height range
  const height = animation.interpolate({
    inputRange: [0, 1],
    outputRange: [60, 150],  // collapsed → expanded
  });

  // Interpolate: map 0→1 to rotation
  const rotate = animation.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '180deg'],  // chevron rotation
  });

  return (
    <TouchableOpacity onPress={toggleExpand}>
      <Animated.View style={[styles.expandCard, { backgroundColor, height }]}>
        <View style={styles.expandHeader}>
          <Text style={styles.expandTitle}>Tap to expand</Text>
          <Animated.Text style={{ transform: [{ rotate }] }}>▼</Animated.Text>
        </View>
        <Text>Expanded content here...</Text>
      </Animated.View>
    </TouchableOpacity>
  );
}

// STAGGER — list items appear one by one
function StaggeredList({ items }) {
  const animations = useRef(
    items.map(() => new Animated.Value(0))
  ).current;

  useEffect(() => {
    Animated.stagger(
      100,                        // 100ms between each
      animations.map((anim) =>
        Animated.timing(anim, {
          toValue: 1,
          duration: 400,
          useNativeDriver: true,
        })
      )
    ).start();
  }, []);

  return (
    <View>
      {items.map((item, index) => (
        <Animated.View
          key={item.id}
          style={{
            opacity: animations[index],
            transform: [{
              translateX: animations[index].interpolate({
                inputRange: [0, 1],
                outputRange: [-50, 0],  // slide in from left
              })
            }],
          }}
        >
          <Text style={styles.listItem}>{item.name}</Text>
        </Animated.View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  skeletonContainer: { padding: 16, gap: 8 },
  skeletonLine: {
    height: 16, backgroundColor: '#e5e7eb', borderRadius: 8, marginBottom: 8
  },
  expandCard: {
    margin: 16, borderRadius: 12, padding: 16, overflow: 'hidden',
    borderWidth: 1, borderColor: '#e5e7eb',
  },
  expandHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  expandTitle: { fontSize: 16, fontWeight: '600' },
  listItem: { padding: 16, borderBottomWidth: 1, borderBottomColor: '#eee', fontSize: 16 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `useNativeDriver: true` | ✅ Runs on UI Thread | ✅ Runs on UI Thread |
| Color animations | ❌ Native driver NOT supported | ❌ Native driver NOT supported |
| Layout (width/height) | ❌ Native driver NOT supported | ❌ Native driver NOT supported |
| transform, opacity | ✅ Native driver supported | ✅ Native driver supported |
| Reanimated v3 | ✅ All props on UI thread | ✅ All props on UI thread |

---

## 🟠 Expo vs CLI Difference

Expo way:
```jsx
// Animated API — built into react-native, no extra install
import { Animated } from 'react-native';
// Expo also includes react-native-reanimated pre-configured
// app.json: "plugins": [["react-native-reanimated"]]
```

CLI way:
```jsx
// Same Animated API
import { Animated } from 'react-native';
// Reanimated: npm install react-native-reanimated
// Needs babel plugin in babel.config.js:
// plugins: ['react-native-reanimated/plugin']
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `useNativeDriver: true`
```jsx
// WRONG: runs on JS thread → can drop frames
Animated.timing(opacity, {
  toValue: 1,
  duration: 300,
  // missing useNativeDriver!
}).start();

// CORRECT: always add useNativeDriver
Animated.timing(opacity, {
  toValue: 1,
  duration: 300,
  useNativeDriver: true,  // ← required for smooth 60fps!
}).start();
```

❌ **Mistake 2:** Using native driver with non-supported properties
```jsx
// WRONG: backgroundColor and width don't support native driver!
Animated.timing(animation, {
  toValue: 1,
  useNativeDriver: true,  // ❌ ERROR: native driver can't handle these
}).start();
// With: Animated.View style={{ backgroundColor: animation, width: animation }}

// CORRECT: For layout/color animations, use useNativeDriver: false
// AND consider using Reanimated v3 which supports ALL props on UI thread
Animated.timing(animation, {
  toValue: 1,
  useNativeDriver: false,  // ✅ required for color/layout
}).start();
```

❌ **Mistake 3:** Creating Animated.Value in render (not in useRef/useMemo)
```jsx
// WRONG: Creates a NEW Animated.Value on every re-render!
function BadComponent() {
  const opacity = new Animated.Value(0);  // ❌ recreated each render!
  // ...
}

// CORRECT: useRef keeps it stable across renders
function GoodComponent() {
  const opacity = useRef(new Animated.Value(0)).current;  // ✅ stable!
  // ...
}
```

---

## 🧠 Tricky Interview Question

**Q: Why can't you use `useNativeDriver: true` with width, height, or backgroundColor animations?**

**Answer:** `useNativeDriver: true` sends animation to the native UI thread and the animation runs entirely in C++ on the UI thread — no JavaScript involved per frame. But `width`, `height`, `backgroundColor` and other layout properties require the Yoga layout engine to recalculate the layout tree — which is a JavaScript operation managed by React. The native thread doesn't know how to recalculate flexbox layout or interpolate color values by itself. **Supported with native driver**: `opacity`, `transform` (translateX, translateY, scale, rotate, skewX, skewY) — these are pure visual changes that don't affect layout. **Not supported**: any layout property (width, height, margin, padding), color properties (backgroundColor, color, borderColor). Solution for color/layout: use `useNativeDriver: false` (JS-driven) or switch to **Reanimated v3** which uses JSI to run on the UI thread with full layout/color support.

---

## ⚫ Interview Questions + Answers

**Q1: What is `useNativeDriver` in Animated API?**
A1: `useNativeDriver: true` tells React Native to run the animation on the native UI thread instead of the JavaScript thread. Without it, every animation frame requires a JS → Bridge → Native round trip. With it, the animation parameters are serialized once to the native thread; subsequent frames run in C++ at 60fps without any JS involvement. Supported properties: `transform`, `opacity`. Not supported: layout properties (`width`, `height`, `margin`, `padding`) and color properties. Always set it to `true` unless you're animating unsupported properties.

**Q2: What is the difference between `Animated.timing()` and `Animated.spring()`?**
A2: `Animated.timing()`: linear or eased animation with a fixed duration. Input: `toValue`, `duration`, `easing`. Predictable, time-based. `Animated.spring()`: physics-based simulation — the value "springs" to its target, potentially overshooting and bouncing. Input: `toValue`, `friction` (damping, reduces oscillation), `tension` (spring stiffness). Not time-based — ends when physics settle. `timing` feels mechanical; `spring` feels natural and alive. iOS uses spring physics everywhere; use `Animated.spring()` to match iOS feel.

**Q3: What is `Animated.interpolate()`?**
A3: `interpolate()` maps an Animated.Value's range to a different output range. The Animated.Value might go 0→1, but you want the opacity to go 0.3→1, or the Y position to go 50→0, or the rotation to go '0deg'→'360deg'. `animation.interpolate({ inputRange: [0, 1], outputRange: ['0deg', '360deg'] })` — as animation goes 0→1, the output goes 0deg→360deg. Extrapolation: by default, values outside inputRange are clamped to the endpoint. Can be set to `'extend'` (linear extrapolation) or `'clamp'`.

**Q4: How do you run animations in sequence vs parallel?**
A4: `Animated.sequence([anim1, anim2, anim3])` — runs one after another; anim2 starts when anim1 finishes. `Animated.parallel([anim1, anim2])` — all start simultaneously. `Animated.stagger(100, [anim1, anim2, anim3])` — like parallel but each starts 100ms after the previous. `Animated.delay(500)` — wait 500ms (useful in sequence). Combo: `Animated.sequence([Animated.delay(200), Animated.parallel([anim1, anim2])])` — wait 200ms, then run anim1 and anim2 together.

**Q5: What Animated components are available?**
A5: React Native ships: `Animated.View`, `Animated.Text`, `Animated.Image`, `Animated.ScrollView`, `Animated.FlatList`. For custom components: `Animated.createAnimatedComponent(YourComponent)` wraps any component to accept Animated.Value styles. `Animated.FlatList` enables scroll-position-driven animations (sticky headers that fade, parallax effects). Note: components must accept a `style` prop to work with `Animated.createAnimatedComponent`.

---

## 🔷 When to Use + When Not to Use
✅ **Use Animated API when:**
- Simple fade, slide, scale, rotate animations
- One-time or triggered animations
- Small projects where Reanimated v3 feels like overkill
- `useNativeDriver: true` covers your animation properties (transform, opacity)

✅ **Use Reanimated v3 instead when:**
- Gesture-driven animations (drag, swipe, pinch)
- Animations that depend on scroll position
- Need color or layout animations on UI thread
- Complex interpolations with worklets
- React Native's New Architecture project

---

## 📊 Visual Diagram

```
ANIMATED VALUE FLOW:
──────────────────────────────────────────────────────
  JS Thread:
  const fadeAnim = new Animated.Value(0)
  Animated.timing(fadeAnim, { toValue: 1, useNativeDriver: true })
  .start()
       │
       │ (sent to UI thread ONCE)
       ▼
  UI Thread (Native):
  Frame 1: opacity = 0.0
  Frame 2: opacity = 0.1
  Frame 3: opacity = 0.2
  ...
  Frame 30: opacity = 1.0
  ✅ NO JS involvement per frame → 60fps!

ANIMATION COMPOSING:
──────────────────────────────────────────────────────
  sequence([A, B, C]):   A → B → C  (one after another)
  parallel([A, B, C]):   A + B + C  (all at once)
  stagger(100, [A,B,C]): A → (100ms) → B → (100ms) → C

NATIVE DRIVER SUPPORT:
──────────────────────────────────────────────────────
  ✅ useNativeDriver: true:     ❌ useNativeDriver: false only:
  opacity                       backgroundColor
  transform: translateX/Y       width / height
  transform: scale              margin / padding
  transform: rotate             left / top / right / bottom
  transform: skewX/Y            borderRadius (in some cases)
  ← Reanimated v3 supports ALL properties on UI thread!
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Animated.Value | Animatable number value | Animate होने वाला number |
| useNativeDriver | Run animation on UI thread | UI thread पर animation |
| timing | Duration-based animation | Duration-based animation |
| spring | Physics-based animation | Physics-based animation |
| interpolate | Map value range to output range | Value range को output range में map |
| sequence | Animations one after another | एक के बाद एक animations |
| parallel | Animations all at once | सब animations एक साथ |
| stagger | Sequential with delay between | Delay के साथ sequential |

---

## ⚡ 3-Line Summary
**English:**
1. `Animated.Value` drives style changes without re-renders; always use `useNativeDriver: true` for transform/opacity — animations run on the UI thread at 60fps.
2. Types: `timing` (duration-based), `spring` (bouncy physics), and composing: `sequence` (one after another), `parallel` (simultaneous), `stagger` (sequential with delay).
3. Native driver doesn't support color/layout properties — use `useNativeDriver: false` for those, or switch to Reanimated v3 for full UI-thread animation support.

**Hindi:**
1. `Animated.Value` re-renders के बिना styles drive करती है; transform/opacity के लिए `useNativeDriver: true` — UI thread पर 60fps।
2. Types: `timing`, `spring`, composing: `sequence`, `parallel`, `stagger`।
3. Native driver color/layout support नहीं करता — `false` use करो या Reanimated v3 switch करो।

---

## ➡️ Next Topic
**130. React Native Reanimated v3** — JSI-based animations, useSharedValue, worklets, gesture integration।
