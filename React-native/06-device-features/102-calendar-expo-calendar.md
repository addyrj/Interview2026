# 102. Calendar — expo-calendar
# हिंदी में: Calendar — फ़ोन के calendar में event बनाना
# Platform: Android ✅ | iOS ✅ | Both ✅ (Reminders सिर्फ़ iOS)

> Target: Expo SDK 52 (React Native 0.76) + `expo-calendar` (check current docs — APIs change between SDKs). iOS 17+ में full vs write-only calendar access अलग हैं; Expo Go में चलता है पर पूरा test dev build पर करें।

---

## 🔵 Simple Definition (English)
**expo-calendar** lets your app read and write the device's calendars and events (and reminders on iOS). You can list calendars, create an event with title, start/end time and alarms, update or delete it.

## 🔵 सरल परिभाषा (Hindi)
**expo-calendar** से app फ़ोन के calendars और events (और iOS पर reminders) को पढ़/लिख सकता है। Calendars की list, title, शुरू/ख़त्म समय और alarm वाला event बनाना, बदलना या हटाना संभव है।

---

## 🔴 Problem it Solves
```
❌ User ko booking date manually calendar me daalni padti hai
❌ Reminder app ke andar hi rehta hai, calendar me nahi dikhta
✅ "Add to Calendar" ek tap me
✅ Android ke Google Calendar aur iOS ke Calendar dono me sync
```

## 🔴 यह क्यों बना? (Hindi)
```
Booking की तारीख़ हाथ से calendar में डालना झंझट है।
App के अंदर का reminder user के असली calendar में नहीं दिखता।
expo-calendar से "Add to Calendar" एक tap में हो जाता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-calendar
Step 2 → app.json plugin ["expo-calendar", { "calendarPermission": "...", "remindersPermission": "..." }]
Step 3 → Calendar.requestCalendarPermissionsAsync() -> granted
Step 4 → Calendar.getCalendarsAsync(Calendar.EntityTypes.EVENT) -> calendars list
Step 5 → Writable calendar chuno (allowsModifications === true) ya naya banao
Step 6 → Calendar.createEventAsync(calendarId, { title, startDate, endDate, timeZone, alarms })
Step 7 → updateEventAsync / deleteEventAsync(eventId) se badlo ya hatao
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Package + plugin, फिर calendar permission।
Step 2 → Calendars की list लेकर writable calendar चुनें।
Step 3 → createEventAsync से event बनाएँ; यह event id लौटाता है।
Step 4 → id को सहेजें ताकि बाद में update/delete हो सके।
```

---

## 🟡 Real World Example
**MakeMyTrip / IRCTC:** After booking a flight/train, "Add to Calendar" creates an event with the departure time and a 2-hour alarm. **BookMyShow:** movie show added to calendar. **Practo:** doctor appointment reminder in Google Calendar.

## 🟡 Real Example Hindi mein
**MakeMyTrip / IRCTC:** बुकिंग के बाद "Add to Calendar" से departure समय का event 2 घंटे पहले alarm के साथ बनता है। **BookMyShow:** फ़िल्म शो calendar में जुड़ता है। **Practo:** डॉक्टर की appointment Google Calendar में।

---

## 💻 Code Example — Basic
```jsx
// CalendarBasic.jsx — "Calendar me add karo" button
import React from 'react';                                             // React
import { View, Button, Alert, Platform } from 'react-native';          // RN
import * as Calendar from 'expo-calendar';                             // calendar API

async function getWritableCalendarId() {
  const cals = await Calendar.getCalendarsAsync(Calendar.EntityTypes.EVENT); // saare event calendars
  const writable = cals.find((c) => c.allowsModifications);            // jisme likh sakte hain
  if (writable) return writable.id;                                    // mil gaya
  if (Platform.OS === 'ios') {                                         // iOS: default calendar
    const def = await Calendar.getDefaultCalendarAsync();
    return def.id;
  }
  return null;                                                         // Android: koi writable nahi
}

export default function CalendarBasic() {
  const add = async () => {
    const { status } = await Calendar.requestCalendarPermissionsAsync(); // permission
    if (status !== 'granted') return Alert.alert('Permission chahiye');  // deny
    const calId = await getWritableCalendarId();                       // calendar id
    if (!calId) return Alert.alert('Koi calendar nahi mila');          // fallback
    const start = new Date(Date.now() + 24 * 60 * 60 * 1000);          // kal isi time
    const end = new Date(start.getTime() + 60 * 60 * 1000);            // 1 ghanta baad
    await Calendar.createEventAsync(calId, {
      title: 'Doctor Appointment',                                      // event title
      startDate: start,                                                // shuru
      endDate: end,                                                    // khatam
      timeZone: 'Asia/Kolkata',                                        // IST (Android me zaroori)
    });
    Alert.alert('Added ✅');                                            // success
  };
  return <View style={{ padding: 40 }}><Button title="Add to Calendar" onPress={add} /></View>;
}
```

## 💻 Code Example — Advanced
```jsx
// calendarService.js — app ka apna calendar, alarm, update/delete, error handling
import * as Calendar from 'expo-calendar';
import { Platform } from 'react-native';

const APP_CAL = 'MyApp Bookings';                                      // apne calendar ka naam

export async function ensureAppCalendar() {
  const { granted } = await Calendar.requestCalendarPermissionsAsync(); // permission
  if (!granted) throw new Error('Calendar permission denied');

  const cals = await Calendar.getCalendarsAsync(Calendar.EntityTypes.EVENT);
  const existing = cals.find((c) => c.title === APP_CAL);              // pehle se hai?
  if (existing) return existing.id;

  // Source chuno: iOS me default calendar ka source, Android me LOCAL account
  const source = Platform.OS === 'ios'
    ? (await Calendar.getDefaultCalendarAsync()).source
    : { isLocalAccount: true, name: APP_CAL, type: Calendar.SourceType.LOCAL };

  return Calendar.createCalendarAsync({
    title: APP_CAL,                                                    // naam
    color: '#E23744',                                                  // Zomato-red jaisa
    entityType: Calendar.EntityTypes.EVENT,                            // events ke liye
    sourceId: source.id,                                               // iOS: source id
    source,                                                            // Android: local source
    name: 'myapp-bookings',                                            // internal name
    ownerAccount: 'personal',                                          // Android owner
    accessLevel: Calendar.CalendarAccessLevel.OWNER,                   // Android access
  });
}

export async function addBooking({ title, start, end, location }) {
  const calId = await ensureAppCalendar();
  try {
    return await Calendar.createEventAsync(calId, {
      title, startDate: start, endDate: end, location,
      timeZone: 'Asia/Kolkata',
      alarms: [{ relativeOffset: -120 }],                              // 120 minute pehle alarm
    });                                                                // event id return
  } catch (e) {
    console.warn('createEvent failed', e);                             // log + rethrow
    throw e;
  }
}

export const moveBooking = (id, start, end) =>
  Calendar.updateEventAsync(id, { startDate: start, endDate: end });   // time badlo
export const removeBooking = (id) => Calendar.deleteEventAsync(id);    // hatao
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission | `READ_CALENDAR` + `WRITE_CALENDAR` | `NSCalendarsUsageDescription` (iOS 17: full/write-only keys) |
| Reminders API | ❌ Not supported | ✅ `NSRemindersUsageDescription`, `getRemindersAsync` etc. |
| `timeZone` in event | Required | Optional |
| Create calendar | Needs `source`, `ownerAccount`, `accessLevel` | Needs `sourceId` |
| `getDefaultCalendarAsync` | ❌ iOS only | ✅ |
| Event UI | `createEventInCalendarAsync` opens system UI | Same (system UI, no permission needed) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-calendar ; plugin: ["expo-calendar", { "calendarPermission": "Booking calendar me add karne ke liye" }]
import * as Calendar from 'expo-calendar';                             // Expo module
await Calendar.createEventAsync(calId, { title: 'Trip', startDate, endDate, timeZone: 'Asia/Kolkata' });
```
CLI way:
```jsx
// npm i react-native-calendar-events ; AndroidManifest + Info.plist permissions khud likho
import RNCalendarEvents from 'react-native-calendar-events';          // alag library
await RNCalendarEvents.requestPermissions();                           // permission
await RNCalendarEvents.saveEvent('Trip', { startDate: s.toISOString(), endDate: e.toISOString() }); // save
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Read-only calendar (जैसे Holidays) में event लिखना।
✅ Correct: `allowsModifications === true` वाला calendar चुनें।

❌ Mistake 2: Android पर `timeZone` न देना (error)।
✅ Correct: `timeZone: 'Asia/Kolkata'`.

❌ Mistake 3: `getDefaultCalendarAsync()` को Android पर बुलाना।
✅ Correct: `Platform.OS === 'ios'` से बचाएँ।

❌ Mistake 4: Event id सेव न करना (बाद में delete नहीं हो पाता)।
✅ Correct: id को अपने backend/AsyncStorage में रखें।

❌ Mistake 5: iOS plist keys न जोड़ना।
✅ Correct: plugin options `calendarPermission` दें।

---

## 🧠 Tricky Interview Question
`createEventAsync` works on iOS but throws on Android with the same code. Why?

Answer: Common causes: (1) no `timeZone` (Android requires it), (2) the chosen calendar isn't writable / calendar id is iOS default fetched via `getDefaultCalendarAsync`, which doesn't exist on Android, (3) `WRITE_CALENDAR` permission not declared. Fix: pass `timeZone`, pick `allowsModifications` calendar, and guard iOS-only calls.

हिंदी: Android पर `timeZone` और writable calendar ज़रूरी है; iOS-only API (`getDefaultCalendarAsync`) वहाँ नहीं चलता।

---

## ⚫ Interview Questions + Answers
Q1: Calendar permission कैसे माँगते हैं?
A1: `Calendar.requestCalendarPermissionsAsync()`; reminders (iOS) के लिए `requestRemindersPermissionsAsync()`।

Q2: Event delete कैसे करें?
A2: `Calendar.deleteEventAsync(eventId)`.

Q3: Permission के बिना event जोड़ने का तरीका?
A3: `Calendar.createEventInCalendarAsync(details)` system UI खोलता है जहाँ user खुद save करता है।

Q4: Alarm कैसे लगाएँ?
A4: Event में `alarms: [{ relativeOffset: -120 }]` (मिनटों में, event से पहले)।

Q5: Reminders Android पर क्यों नहीं?
A5: Android में reminders का system API अलग से नहीं है; expo-calendar का Reminders feature iOS-only है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Booking / appointment / event "Add to Calendar"
- Recurring schedule sync
- Travel itinerary

❌ Avoid when:
- सिर्फ़ in-app reminder चाहिए (Local Notifications बेहतर)
- User का पूरा calendar पढ़ना बिना कारण (privacy)

---

## 📊 Visual Diagram
```
 requestCalendarPermissionsAsync()
              │ granted
              ▼
 getCalendarsAsync(EVENT) ──▶ pick allowsModifications calendar
              │
 createEventAsync(calId, {title, start, end, timeZone, alarms})
              │
     Android CalendarProvider | iOS EventKit
              ▼
   Google/iCloud/Local calendar me event dikhta hai
              │
   eventId ──▶ update / delete baad me
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Calendar | A container of events | events का समूह |
| Event | Scheduled item | तय कार्यक्रम |
| Alarm | Pre-event alert | event से पहले चेतावनी |
| Source | Account owning calendar | calendar का account |
| EventKit | iOS calendar framework | iOS का framework |
| Time zone | Region time offset | समय क्षेत्र |

---

## ⚡ 3-Line Summary
English: expo-calendar creates and edits events in the device calendar after permission.
Pick a writable calendar, set a time zone, and keep the event id.
Reminders work only on iOS.

Hindi: expo-calendar permission के बाद device calendar में event बनाता और बदलता है।
Writable calendar चुनें, time zone दें और event id सहेजें।
Reminders सिर्फ़ iOS पर चलते हैं।

---

## ➡️ Next Topic
**103. Accelerometer + Gyroscope** — फ़ोन की गति और झुकाव के sensors पढ़ना (shake detect जैसे features)।

---
