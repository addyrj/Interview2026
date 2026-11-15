---

# Q272. Mediator Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a `ChatRoom` mediator: users never reference each other directly — they send messages through the room, which delivers to everyone except the sender (and supports private messages).

---

## 💡 Quick Concept (2 lines only)
Mediator centralises communication between objects so they depend on one hub instead of on each other (N-to-N becomes N-to-1).
हिंदी: Mediator सारे objects की आपसी बातचीत एक केंद्र (hub) से करवाता है, ताकि वे एक-दूसरे पर निर्भर न रहें।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class ChatRoom:  # Step 1: the mediator
    def __init__(self) -> None:
        self._users: dict[str, "User"] = {}  # registry name -> user

    def join(self, user: "User") -> None:
        self._users[user.name] = user  # register the user
        user.room = self  # give user a link to the mediator

    def send(self, sender: "User", text: str, to: str | None = None) -> None:
        if to is not None:  # Step 2: private message
            self._users[to].receive(sender.name, text)  # deliver to one user
            return  # done
        for name, user in self._users.items():  # broadcast case
            if name != sender.name:  # skip the sender
                user.receive(sender.name, text)  # deliver to others


class User:  # Step 3: colleague - only knows the mediator
    def __init__(self, name: str) -> None:
        self.name = name  # user name
        self.room: ChatRoom | None = None  # set by join()
        self.inbox: list[str] = []  # received messages

    def say(self, text: str, to: str | None = None) -> None:
        assert self.room is not None  # must have joined a room
        self.room.send(self, text, to)  # ask the mediator to deliver

    def receive(self, sender: str, text: str) -> None:
        self.inbox.append(f"{sender}: {text}")  # store the message


# ============================================
# TEST CASES
# ============================================
room = ChatRoom()  # create mediator
a, b, c = User("amit"), User("bela"), User("chen")  # three users
for u in (a, b, c):  # register all
    room.join(u)  # join the room
a.say("hi all")  # broadcast from amit
b.say("psst", to="chen")  # private from bela to chen
print(a.inbox)  # Expected: []
print(b.inbox)  # Expected: ['amit: hi all']
print(c.inbox)  # Expected: ['amit: hi all', 'bela: psst']
```

---

## 🔍 Why This Works (3 lines max)
Users hold a reference only to the room, never to each other. Routing rules (skip sender, private) live in one place, so adding a rule never touches `User`.
हिंदी: Users सिर्फ room को जानते हैं; routing के नियम एक ही जगह हैं, इसलिए बदलाव आसान है।

---

## ⚡ Alternative Solution
```python
# Callback-based mediator: users register a handler function
from collections.abc import Callable  # type hint


class Hub:
    def __init__(self) -> None:
        self.handlers: dict[str, Callable[[str], None]] = {}  # name -> callback

    def register(self, name: str, fn: Callable[[str], None]) -> None:
        self.handlers[name] = fn  # store callback

    def broadcast(self, sender: str, msg: str) -> None:
        for name, fn in self.handlers.items():  # loop over recipients
            if name != sender:  # skip sender
                fn(f"{sender}: {msg}")  # call handler


got: list[str] = []  # collector
hub = Hub()  # create hub
hub.register("x", got.append)  # x collects messages
hub.register("y", lambda m: None)  # y ignores them
hub.broadcast("y", "hello")  # y sends to everyone else
print(got)  # Expected: ['y: hello']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: users hold references to each other (tight coupling, N*N links)
class BadUser:
    def __init__(self, name: str) -> None:
        self.name = name  # name
        self.friends: list["BadUser"] = []  # direct links to every other user

# ✅ Correct: users know only the mediator; add/remove users in ONE place
```

---

## 🎯 Interview Tip (1 line)
Say: "Mediator reduces many-to-many coupling to many-to-one; the risk is the mediator becoming a god object, and it differs from Observer because it controls routing."

---

## 🔗 Related Questions
→ Q263 (observer) | Q187 (event bus) | Q097 (pub/sub)
