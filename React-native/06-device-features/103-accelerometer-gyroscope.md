# 103. Accelerometer + Gyroscope
# हिंदी में: Accelerometer + Gyroscope (गति और घुमाव के sensors)
# Platform: Android ✅ | iOS ✅ | Both ✅ (real device पर best; web ❌ mostly)

> Target: Expo SDK 52 (React Native 0.76) + `expo-sensors` (check current docs — APIs change between SDKs). Expo Go में चलता है; simulator/emulator में values नकली/शून्य हो सकती हैं।

---

## 🔵 Simple Definition (English)
The **accelerometer** measures acceleration (movement and gravity) along the x, y, z axes. The **gyroscope** measures how fast the phone **rotates** around those axes. `expo-sensors` gives both as live streams of `{ x, y, z }`.

## 🔵 सरल परिभाषा (Hindi)
**Accelerometer** x, y, z अक्षों पर गति (acceleration) और gravity नापता है। **Gyroscope** बताता है कि फ़ोन इन अक्षों पर कितनी तेज़ी से **घूम** रहा है। `expo-sensors` दोनों को `{ x, y, z }` की live धारा के रूप में देता है।

---

## 🔴 Problem it Solves
```
❌ Shake, tilt, step-count jaise features ke liye raw hardware access chahiye
❌ Android SensorManager aur iOS CoreMotion alag APIs
✅ Ek JS listener: addListener(({x,y,z}) => ...)
✅ Update interval control (battery vs smoothness)
```

## 🔴 यह क्यों बना? (Hindi)
```
Shake, tilt, game controls जैसे features के लिए sensor डेटा चाहिए।
Android और iOS के native sensor APIs अलग हैं।
expo-sensors एक जैसा listener API देता है और update speed भी बदलने देता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-sensors
Step 2 → await Accelerometer.isAvailableAsync() (hardware hai?)
Step 3 → Accelerometer.setUpdateInterval(100) (ms)
Step 4 → const sub = Accelerometer.addListener(({x,y,z}) => ...)
Step 5 → Magnitude = sqrt(x²+y²+z²); ~1 = rest (1g), bada = shake
Step 6 → Gyroscope.addListener -> rad/s me rotation rate
Step 7 → Unmount par sub.remove() (battery bachao)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले जाँचें कि sensor मौजूद है।
Step 2 → Update interval तय करें (कम ms = ज़्यादा तेज़, ज़्यादा battery)।
Step 3 → Listener लगाएँ; हर update पर x, y, z मिलते हैं।
Step 4 → Accelerometer का magnitude ~1g आराम में, shake पर 1.8g से ज़्यादा।
Step 5 → ज़रूरत ख़त्म होते ही subscription हटाएँ।
```

---

## 🟡 Real World Example
**Swiggy / Zomato:** "Shake to reorder / feedback" style gestures (shake detection via accelerometer). **Dream11 / games:** tilt to steer. **Google Fit / Fitbit style apps:** step counting from accelerometer patterns. **Camera/Maps apps:** gyroscope for rotation-aware views.

## 🟡 Real Example Hindi mein
**Swiggy / Zomato जैसे apps:** "Shake करके feedback" gesture accelerometer से detect होता है। **Games:** फ़ोन झुकाकर गाड़ी चलाना। **Fitness apps:** accelerometer pattern से steps गिनना। **Maps/AR:** gyroscope से घुमाव के हिसाब से view बदलना।

---

## 💻 Code Example — Basic
```jsx
// SensorBasic.jsx — live accelerometer + gyroscope values
import React, { useEffect, useState } from 'react';                    // React + hooks
import { View, Text } from 'react-native';                             // RN UI
import { Accelerometer, Gyroscope } from 'expo-sensors';               // sensors

const fmt = (v) => `x:${v.x.toFixed(2)} y:${v.y.toFixed(2)} z:${v.z.toFixed(2)}`; // 2 decimal format

export default function SensorBasic() {
  const [acc, setAcc] = useState({ x: 0, y: 0, z: 0 });                // accelerometer state
  const [gyro, setGyro] = useState({ x: 0, y: 0, z: 0 });              // gyroscope state

  useEffect(() => {
    Accelerometer.setUpdateInterval(200);                              // 200ms par update
    Gyroscope.setUpdateInterval(200);                                  // 200ms par update
    const a = Accelerometer.addListener(setAcc);                       // listener (g units)
    const g = Gyroscope.addListener(setGyro);                          // listener (rad/s)
    return () => { a.remove(); g.remove(); };                          // cleanup: battery bachao
  }, []);                                                              // sirf mount par

  return (
    <View style={{ padding: 40, gap: 8 }}>
      <Text>Accelerometer {fmt(acc)}</Text>
      <Text>Gyroscope {fmt(gyro)}</Text>
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// useShake.js — shake detection (debounce + availability check + cleanup)
import { useEffect, useRef } from 'react';
import { Accelerometer } from 'expo-sensors';

// Pure logic alag function: test karna aasan
export function isShake(v, threshold = 1.8) {
  const magnitude = Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z);      // total force in g
  return magnitude > threshold;                                        // rest ~1.0g
}

export function useShake(onShake, { threshold = 1.8, cooldownMs = 1000 } = {}) {
  const last = useRef(0);                                              // last shake time
  const cb = useRef(onShake);                                          // latest callback
  cb.current = onShake;                                                // closure stale na ho

  useEffect(() => {
    let sub;                                                           // subscription
    let cancelled = false;                                             // unmount guard
    (async () => {
      const ok = await Accelerometer.isAvailableAsync();               // sensor hai?
      if (!ok || cancelled) return;                                    // nahi to skip
      Accelerometer.setUpdateInterval(100);                            // 10 Hz kaafi hai
      sub = Accelerometer.addListener((v) => {
        const now = Date.now();
        if (isShake(v, threshold) && now - last.current > cooldownMs) { // debounce
          last.current = now;                                          // time update
          cb.current();                                                // user callback
        }
      });
    })();
    return () => { cancelled = true; sub?.remove(); };                 // cleanup
  }, [threshold, cooldownMs]);
}

// Use: useShake(() => Alert.alert('Shake!'));
// Gyroscope se rotation angle (approx): theta += gyro.z * dt  (dt seconds me)
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission | None for basic rate; Android 12+ >200Hz needs `HIGH_SAMPLING_RATE_SENSORS` | None (Motion usage string for some Core Motion — `NSMotionUsageDescription` for pedometer/activity, not raw sensors) |
| Accelerometer unit | expo-sensors reports in **g** (consistent across platforms) | g |
| Gyroscope unit | rad/s | rad/s |
| Update rate | Hardware dependent | Up to ~100 Hz via CoreMotion |
| Simulator | Emulator has virtual sensors panel | Simulator: no real sensors |
| Background | Sensors stop/limited in background | Stop in background |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-sensors
import { Accelerometer } from 'expo-sensors';                          // no native setup
const sub = Accelerometer.addListener(({ x, y, z }) => console.log(x, y, z));
```
CLI way:
```jsx
// npm i react-native-sensors ; cd ios && pod install
import { accelerometer, setUpdateIntervalForType, SensorTypes } from 'react-native-sensors'; // RxJS based
setUpdateIntervalForType(SensorTypes.accelerometer, 200);              // interval
const sub = accelerometer.subscribe(({ x, y, z }) => console.log(x, y, z)); // subscribe
// sub.unsubscribe() cleanup
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Listener को `remove()` न करना (battery drain, memory leak)।
✅ Correct: `useEffect` cleanup में `sub.remove()`।

❌ Mistake 2: बहुत तेज़ interval (जैसे 10ms) पर `setState` करना (re-render storm)।
✅ Correct: 100-200ms, या `useRef`/Reanimated shared value में रखें।

❌ Mistake 3: Shake threshold बिना debounce के (एक shake = 10 callbacks)।
✅ Correct: cooldown (1 sec) लगाएँ।

❌ Mistake 4: Gyroscope को angle मान लेना (यह rate है)।
✅ Correct: Angle के लिए समय से integrate करें या `DeviceMotion` use करें।

❌ Mistake 5: Simulator पर test करके "काम नहीं करता" कहना।
✅ Correct: Real device पर जाँचें।

---

## 🧠 Tricky Interview Question
A phone lies still on a table. What values does the accelerometer report, and why is `z` not 0?

Answer: About `{x: 0, y: 0, z: ±1}` in g units. The accelerometer measures **proper acceleration including gravity**, so a resting device feels 1g upward from the table. A free-falling phone would read ~0. To get motion without gravity use `DeviceMotion` (`acceleration` vs `accelerationIncludingGravity`).

हिंदी: Accelerometer gravity समेत नापता है, इसलिए आराम में भी z लगभग ±1g आता है; free fall में ~0।

---

## ⚫ Interview Questions + Answers
Q1: Accelerometer vs Gyroscope?
A1: Accelerometer = रैखिक acceleration (+gravity); Gyroscope = घूमने की गति (rad/s)।

Q2: Shake कैसे detect करते हैं?
A2: Magnitude `sqrt(x²+y²+z²)` threshold (~1.8g) से ज़्यादा + cooldown।

Q3: Sensor availability कैसे जाँचें?
A3: `await Accelerometer.isAvailableAsync()`।

Q4: Update interval क्यों मायने रखता है?
A4: कम interval = ज़्यादा smooth पर ज़्यादा battery/CPU; ज़रूरत भर रखें।

Q5: Angle कैसे निकालें?
A5: Gyroscope rate को dt से गुणा करके जोड़ें (drift होगा) या sensor fusion/`DeviceMotion`।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Shake, tilt, orientation, simple games
- Step/motion heuristics (simple)
- Parallax effects

❌ Avoid when:
- Accurate step counting (Pedometer API बेहतर)
- High-frequency sensor डेटा में JS state बार-बार update
- Background tracking (OS रोक देता है)

---

## 📊 Visual Diagram
```
        +y (top)
         ▲
         │      z (out of screen)
         │    ╱
 -x ◀────┼────▶ +x      Accelerometer: x,y,z in g (gravity included)
         │
         ▼ -y             Gyroscope: rotation rate about x,y,z (rad/s)

 Hardware ─▶ OS (SensorManager / CoreMotion) ─▶ expo-sensors ─▶ addListener({x,y,z})
 magnitude = sqrt(x²+y²+z²)  > 1.8 ? SHAKE : still
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Accelerometer | Measures acceleration | त्वरण नापने वाला sensor |
| Gyroscope | Measures rotation rate | घुमाव की दर |
| g | Earth gravity unit (9.8 m/s²) | गुरुत्व की इकाई |
| Magnitude | Vector length | सदिश की लंबाई |
| Debounce | Ignore rapid repeats | बार-बार trigger रोकना |
| Update interval | Time between readings | दो readings के बीच समय |

---

## ⚡ 3-Line Summary
English: expo-sensors streams accelerometer (movement + gravity) and gyroscope (rotation rate) values.
Set an interval, add a listener and always remove it.
Use magnitude plus cooldown to detect a shake.

Hindi: expo-sensors accelerometer (गति + gravity) और gyroscope (घुमाव दर) की live values देता है।
Interval तय करें, listener लगाएँ और हमेशा हटाएँ।
Shake के लिए magnitude और cooldown का इस्तेमाल करें।

---

## ➡️ Next Topic
**104. Biometric Authentication** — fingerprint/face से user को सुरक्षित तरीक़े से verify करना।

---
