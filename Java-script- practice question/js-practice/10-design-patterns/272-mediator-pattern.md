---

# Q272. Mediator Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a `ChatRoom` mediator so users send messages through the room instead of referencing each other directly.

---

## 💡 Quick Concept (2 lines only)
A mediator centralizes communication between objects so they don't depend on each other directly.
हिंदी: Mediator बीच का ऑफिस है, objects आपस में नहीं, उसके जरिए बात करते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Mediator keeps track of participants
// Step 2: Participants only know the mediator
// Step 3: Mediator routes messages

class ChatRoom {
  users = new Map();                               // name -> User

  register(user) {
    this.users.set(user.name, user);               // add participant
    user.room = this;                              // give user the mediator reference
  }

  send(message, from, to) {
    if (to) {
      this.users.get(to)?.receive(message, from);  // direct message
    } else {
      for (const [name, u] of this.users) {        // broadcast
        if (name !== from) u.receive(message, from); // everyone except sender
      }
    }
  }
}

class User {
  constructor(name) { this.name = name; this.inbox = []; } // own inbox
  send(msg, to) { this.room.send(msg, this.name, to); }    // go through mediator
  receive(msg, from) { this.inbox.push(`${from}: ${msg}`); } // store received
}

// ============================================
// TEST CASES
// ============================================

const room = new ChatRoom();                       // mediator
const a = new User('A'), b = new User('B'), c = new User('C'); // users
[a, b, c].forEach((u) => room.register(u));        // join room
a.send('hi all');                                  // broadcast from A
b.send('psst', 'C');                               // direct B -> C
console.log(b.inbox);                              // Expected: [ 'A: hi all' ]
console.log(c.inbox);                              // Expected: [ 'A: hi all', 'B: psst' ]
console.log(a.inbox);                              // Expected: []
```

---

## 🔍 Why This Works (3 lines max)
Users hold a single reference (the room) instead of N references to each other. Routing rules live in one place.
हिंदी: Users के बीच सीधा जुड़ाव नहीं होता, सारा routing room के पास है।

---

## ⚡ Alternative Solution
```javascript
// Minimal event-bus mediator
const bus = new Map();                                  // event -> handlers[]
const on = (e, f) => bus.set(e, [...(bus.get(e) || []), f]); // register
const emit = (e, d) => (bus.get(e) || []).forEach((f) => f(d)); // dispatch
on('x', (d) => console.log('got', d));                  // subscribe
emit('x', 7);                                           // Expected: got 7
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: users store references to every other user (N*N coupling)
// ✅ Correct: route everything through the mediator
```

---

## 🎯 Interview Tip (1 line)
Contrast: Mediator = central coordinator that knows participants; Pub/Sub = anonymous topics.

---

## 🔗 Related Questions
→ Q273 (Pub/Sub) | Q263 (Observer) | Q187 (Event bus)
