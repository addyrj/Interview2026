---

# 192. datetime Module
# हिंदी में: datetime Module (तारीख, समय और time zone)

---

## 🔵 Simple Definition (English)
`datetime` gives classes for dates (`date`), clock times (`time`), both together (`datetime`), differences between them (`timedelta`) and fixed time zones (`timezone`). Together with `zoneinfo` it handles real-world time zones and daylight saving time.

## 🔵 सरल परिभाषा (Hindi)
`datetime` तारीख (`date`), घड़ी का समय (`time`), दोनों साथ (`datetime`), उनके बीच का अंतर (`timedelta`) और fixed time zones (`timezone`) के classes देता है। `zoneinfo` के साथ यह असली time zones और daylight saving time संभालता है।

---

## 🔴 Problem it Solves
Date math by hand is full of traps: months with 28 to 31 days, leap years, time zones, daylight saving shifts and string formats. Storing dates as plain strings or numbers makes sorting, subtracting and comparing error prone. `datetime` gives correct calendar arithmetic and parsing and formatting built in.

## 🔴 यह क्यों बना? (Hindi)
हाथ से date का हिसाब फँसाने वाला है: 28 से 31 दिन के महीने, leap year, time zones, daylight saving और string formats। Dates को plain string या number में रखने से sort, घटाना और तुलना गलत हो सकती है। `datetime` सही calendar arithmetic, parsing और formatting देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → date = year/month/day, time = hour/minute/second, datetime = both
Step 2 → Naive datetime = no timezone info. Aware datetime = has tzinfo
Step 3 → datetime - datetime = timedelta (days, seconds, microseconds)
Step 4 → datetime + timedelta = new datetime (objects are immutable)
Step 5 → strftime(fmt) → text, strptime(text, fmt) → datetime, fromisoformat → ISO text
Step 6 → astimezone(tz) converts the SAME moment to another zone
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → date = साल/महीना/दिन, time = घंटा/मिनट/सेकंड, datetime = दोनों
Step 2 → Naive datetime = timezone info नहीं। Aware datetime = tzinfo है
Step 3 → datetime - datetime = timedelta (days, seconds, microseconds)
Step 4 → datetime + timedelta = नया datetime (objects immutable हैं)
Step 5 → strftime(fmt) → text, strptime(text, fmt) → datetime, fromisoformat → ISO text
Step 6 → astimezone(tz) उसी पल को दूसरे zone में बदलता है
```

---

## 🟡 Real World Example
A Razorpay payment link expires after 15 minutes: `created_at + timedelta(minutes=15)`. A Swiggy order shows "delivered at 9:30 PM" in the customer's zone while the database keeps UTC. An OTP service rejects tokens older than 5 minutes. A reporting job builds "last 7 days" and "first day of the month" ranges.

## 🟡 Real Example Hindi mein
Razorpay payment link 15 मिनट बाद expire होता है: `created_at + timedelta(minutes=15)`। Swiggy order "9:30 PM पर delivered" ग्राहक के zone में दिखाता है जबकि database में UTC रहता है। OTP service 5 मिनट से पुराने tokens reject करती है। Reporting job "पिछले 7 दिन" और "महीने का पहला दिन" की ranges बनाती है।

---

## 💻 Code Example — Basic
```python
# Basic datetime examples - every line commented (fixed dates so output is stable)
from datetime import date, datetime, time, timedelta, timezone  # core classes

d: date = date(2025, 11, 10)  # a calendar date
t: time = time(9, 30, 15)  # a clock time
dt: datetime = datetime(2025, 11, 10, 9, 30, 15)  # date + time (naive: no timezone)
print(d, t, dt)  # default ISO-like print
print(d.year, d.month, d.day, d.weekday(), d.isoweekday())  # Monday=0 / Monday=1
print(dt.strftime("%d %b %Y, %I:%M %p"))  # format -> '10 Nov 2025, 09:30 AM'
print(dt.isoformat())  # ISO 8601 text

parsed: datetime = datetime.strptime("25/12/2025 18:45", "%d/%m/%Y %H:%M")  # text -> datetime
print(parsed)  # 2025-12-25 18:45:00
print(datetime.fromisoformat("2025-11-10T09:30:00+05:30"))  # ISO text with offset

delta: timedelta = parsed - dt  # subtraction gives a timedelta
print(delta, delta.days, delta.total_seconds())  # 45 days, ...
print(dt + timedelta(days=1, hours=2))  # add 1 day 2 hours
print(dt - timedelta(weeks=1))  # one week earlier
print(dt.replace(hour=0, minute=0, second=0))  # start of that day

ist: timezone = timezone(timedelta(hours=5, minutes=30))  # fixed offset +05:30
aware: datetime = datetime(2025, 11, 10, 9, 30, tzinfo=ist)  # timezone-aware
print(aware, aware.utcoffset())  # shows +05:30
print(aware.astimezone(timezone.utc))  # same moment in UTC
print(d < date(2026, 1, 1), max(d, date(2024, 1, 1)))  # dates compare naturally
print(datetime.now().tzinfo, datetime.now(timezone.utc).tzinfo)  # naive vs aware "now"
```

Output (verified by running; ids/timestamps/paths may vary):
```
2025-11-10 09:30:15 2025-11-10 09:30:15
2025 11 10 0 1
10 Nov 2025, 09:30 AM
2025-11-10T09:30:15
2025-12-25 18:45:00
2025-11-10 09:30:00+05:30
45 days, 9:14:45 45 3921285.0
2025-11-11 11:30:15
2025-11-03 09:30:15
2025-11-10 00:00:00
2025-11-10 09:30:00+05:30 5:30:00
2025-11-10 04:00:00+00:00
True 2025-11-10
None UTC
```

## 💻 Code Example — Advanced
```python
# Production style: UTC storage, zoneinfo, DST, business logic, injectable clock
from datetime import date, datetime, timedelta, timezone  # core classes
from typing import Callable, List  # type hints
from zoneinfo import ZoneInfo  # IANA time zones (3.9+)

UTC = timezone.utc  # also available as datetime.UTC (3.11+)
IST = ZoneInfo("Asia/Kolkata")  # India: no DST
NY = ZoneInfo("America/New_York")  # US: has DST

Clock = Callable[[], datetime]  # type of a "now" function


def utc_now() -> datetime:
    """Always an AWARE UTC datetime (utcnow() is deprecated since 3.12)."""
    return datetime.now(UTC)  # aware now


def to_local(dt_utc: datetime, tz: ZoneInfo) -> datetime:
    """Convert an aware UTC time for display."""
    if dt_utc.tzinfo is None:  # naive input is a bug
        raise ValueError("naive datetime not allowed")  # fail loudly
    return dt_utc.astimezone(tz)  # convert


def is_expired(created: datetime, ttl: timedelta, now: Clock = utc_now) -> bool:
    """Token / OTP expiry; the clock can be replaced in tests."""
    return now() >= created + ttl  # compare aware datetimes


fixed: Clock = lambda: datetime(2025, 11, 10, 12, 0, tzinfo=UTC)  # fake clock for tests
print(is_expired(datetime(2025, 11, 10, 11, 50, tzinfo=UTC), timedelta(minutes=5), fixed))  # True
print(is_expired(datetime(2025, 11, 10, 11, 58, tzinfo=UTC), timedelta(minutes=5), fixed))  # False
print(utc_now().tzinfo)  # UTC

stored: datetime = datetime(2025, 11, 10, 4, 0, tzinfo=UTC)  # store/transmit UTC
print(to_local(stored, IST))  # 09:30 in India
print(to_local(stored, NY))  # 23:00 previous day in New York

# DST: same wall clock, different offsets
winter = datetime(2025, 1, 15, 12, 0, tzinfo=NY)  # EST
summer = datetime(2025, 7, 15, 12, 0, tzinfo=NY)  # EDT
print(winter.utcoffset(), summer.utcoffset())  # -5h vs -4h

# Adding a day across the spring-forward gap keeps wall clock (Mar 9 2025, 2:00 -> 3:00)
before = datetime(2025, 3, 8, 12, 0, tzinfo=NY)  # day before DST starts
print(before + timedelta(days=1))  # wall clock arithmetic: 12:00 next day
after = before + timedelta(days=1)  # the next day
print(after - before)  # same tzinfo -> wall clock difference: 1 day
print(after.astimezone(UTC) - before.astimezone(UTC))  # real elapsed time: 23 hours

def business_days(start: date, end: date) -> int:
    """Count Mon-Fri days in [start, end)."""
    days: int = (end - start).days  # total days
    return sum(1 for i in range(days) if (start + timedelta(days=i)).weekday() < 5)  # weekdays

print(business_days(date(2025, 11, 10), date(2025, 11, 17)))  # 5

def month_end(d: date) -> date:
    """Last day of month: first of next month minus one day."""
    first_next: date = (d.replace(day=28) + timedelta(days=4)).replace(day=1)  # jump to next month
    return first_next - timedelta(days=1)  # step back one day

print(month_end(date(2025, 2, 10)), month_end(date(2024, 2, 10)))  # 2025-02-28 2024-02-29

dates: List[date] = [date(2025, 3, 1), date(2025, 1, 5)]  # unsorted
print(sorted(dates), (datetime(2025, 1, 1, tzinfo=UTC).timestamp()))  # sorted + epoch seconds
print(datetime.fromtimestamp(1735689600, tz=UTC))  # epoch -> aware UTC datetime
try:  # naive vs aware comparison
    datetime(2025, 1, 1) < datetime(2025, 1, 1, tzinfo=UTC)  # not allowed
except TypeError as exc:  # expected
    print("TypeError:", exc)  # message
```

Output (verified by running; ids/timestamps/paths may vary):
```
True
False
UTC
2025-11-10 09:30:00+05:30
2025-11-09 23:00:00-05:00
-1 day, 19:00:00 -1 day, 20:00:00
2025-03-09 12:00:00-04:00
1 day, 0:00:00
23:00:00
5
2025-02-28 2024-02-29
[datetime.date(2025, 1, 5), datetime.date(2025, 3, 1)] 1735689600.0
2025-01-01 00:00:00+00:00
TypeError: can't compare offset-naive and offset-aware datetimes
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
from datetime import datetime, timedelta, timezone
now = datetime.now(timezone.utc)                 # aware UTC
tomorrow = now + timedelta(days=1)               # add a day
print(now.isoformat())                           # 2025-11-10T04:00:00+00:00
dt = datetime.fromisoformat("2025-11-10T09:30:00+05:30")
```

```javascript
// JavaScript
const now = new Date();                          // always an absolute instant (UTC based)
const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);   // add a day
console.log(now.toISOString());                  // 2025-11-10T04:00:00.000Z
const dt = new Date("2025-11-10T09:30:00+05:30");
```

Key differences: JavaScript `Date` is always an instant in time; Python separates naive and aware datetimes and refuses to compare them. Python months are 1 to 12 (JS months are 0 to 11). Python has the readable `timedelta`; JS uses milliseconds. Python's `weekday()` has Monday as 0, JS `getDay()` has Sunday as 0.

---

## 🟠 FastAPI Connection
FastAPI/Pydantic parse ISO 8601 strings into `datetime` automatically and write them back as ISO strings. Use `AwareDatetime` to reject naive input, store UTC in the database, and convert to the user's zone only when displaying. Never use `datetime.utcnow()` (deprecated in 3.12): use `datetime.now(timezone.utc)`.

```python
# FastAPI: UTC in the API, local time for display (pip install fastapi httpx)
from datetime import datetime, timedelta, timezone  # date types
from typing import Dict  # type hints
from zoneinfo import ZoneInfo  # time zones
from fastapi import FastAPI, HTTPException  # app + errors
from pydantic import AwareDatetime, BaseModel  # reject naive datetimes

app: FastAPI = FastAPI()  # create app


class Booking(BaseModel):
    starts_at: AwareDatetime  # client MUST send a timezone, e.g. ...+05:30 or Z


@app.post("/bookings")  # POST /bookings
def book(b: Booking) -> Dict[str, str]:
    utc = b.starts_at.astimezone(timezone.utc)  # normalise to UTC for the DB
    if utc < datetime(2025, 1, 1, tzinfo=timezone.utc):  # simple business rule
        raise HTTPException(400, "too old")  # error
    return {"utc": utc.isoformat(), "ist": utc.astimezone(ZoneInfo("Asia/Kolkata")).isoformat()}
```

Output (verified by running; ids/timestamps/paths may vary):
```
{'utc': '2025-11-10T04:00:00+00:00', 'ist': '2025-11-10T09:30:00+05:30'}
422
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Naive datetimes and `utcnow()`
```python
# Wrong - naive object, deprecated since Python 3.12, mixes silently with local time
# datetime.utcnow()

# Correct
from datetime import datetime, timezone
now = datetime.now(timezone.utc)      # aware UTC
```

❌ Mistake 2: Comparing naive with aware
```python
# Wrong - TypeError: can't compare offset-naive and offset-aware datetimes
# datetime(2025, 1, 1) < datetime.now(timezone.utc)

# Correct - make both aware
# datetime(2025, 1, 1, tzinfo=timezone.utc) < datetime.now(timezone.utc)
```

❌ Mistake 3: Using a fixed offset for a place with daylight saving
```python
# Wrong - New York is -5h in winter but -4h in summer
# tz = timezone(timedelta(hours=-5))

# Correct
# from zoneinfo import ZoneInfo
# tz = ZoneInfo("America/New_York")
# also: on Windows or slim Docker images run `pip install tzdata`
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from datetime import date, datetime, timedelta
print(date(2025, 1, 31) + timedelta(days=30))
print(timedelta(hours=-1), timedelta(seconds=90000))
print((datetime(2025, 3, 1) - datetime(2025, 2, 1)).days)
print(datetime(2025, 1, 1).strftime("%y/%m/%d %j %A"))
try:
    date(2025, 2, 29)
except ValueError as e:
    print(e)
print(datetime.strptime("2025-1-5", "%Y-%m-%d").date())
```

**Answer**:
```
2025-03-02
-1 day, 23:00:00 1 day, 1:00:00
28
25/01/01 001 Wednesday
day is out of range for month
2025-01-05
```
`timedelta` stores days, seconds, microseconds, so `-1 hour` prints as `-1 day, 23:00:00`. January 31 plus 30 days is 2 March (February has 28 days in 2025). `strptime` accepts `1` and `5` for `%m` and `%d` without leading zeros. 2025 is not a leap year, so `Feb 29` is invalid. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: Naive vs aware datetime?
A1: Naive has no `tzinfo`, so it is ambiguous. Aware knows its offset or zone. Naive and aware cannot be compared or subtracted. Best practice: store and process aware UTC, convert to local only for display.

Q2: Why is `datetime.utcnow()` discouraged?
A2: It returns a naive datetime that looks like local time but is UTC. Since Python 3.12 it emits a `DeprecationWarning`. Use `datetime.now(timezone.utc)` (or `datetime.UTC` alias from 3.11).

Q3: `timezone` vs `ZoneInfo`?
A3: `timezone` is a fixed offset (e.g. +05:30) and cannot know about DST. `ZoneInfo("Region/City")` uses the IANA database and handles DST rules and history.

Q4: What does `datetime + timedelta(days=1)` do across a DST change?
A4: Within one `ZoneInfo`, arithmetic is wall-clock based: 12:00 stays 12:00 the next day even if only 23 real hours passed. Convert to UTC first when you need real elapsed time.

Q5: How do you parse and print ISO 8601?
A5: `datetime.fromisoformat(s)` and `dt.isoformat()`. From Python 3.11, `fromisoformat` accepts most ISO 8601 forms including `Z`. For other formats use `strptime` / `strftime`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Handling dates, expiry, schedules, ranges and time zones
- Parsing/printing ISO strings in APIs
- Writing testable code with an injectable clock

❌ Avoid when:
- Measuring code speed or timeouts (use `time.perf_counter()` / `time.monotonic()`)
- You need rich human parsing like "next Friday" (use `dateutil` or `pendulum`)
- Storing local time without a zone

---

## 📊 Visual Diagram

```
 date ───┐
         ├──► datetime ──astimezone──► same instant, another zone
 time ───┘        │
                  ├─ naive  (no tzinfo)  ✖ never mix with aware
                  └─ aware  (tzinfo)     ✔ store as UTC

 datetime ─ datetime = timedelta        datetime + timedelta = datetime
 text ──strptime──► datetime ──strftime──► text
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Naive | Datetime without timezone | बिना timezone वाला |
| Aware | Datetime with timezone | timezone वाला |
| timedelta | A length of time | समय की अवधि |
| UTC | World reference time | विश्व संदर्भ समय |
| ISO 8601 | Standard text format `2025-11-10T09:30:00Z` | तारीख-समय का मानक text |
| DST | Daylight saving time shift | गर्मियों में घड़ी बदलना |
| Epoch | Seconds since 1970-01-01 UTC | 1970 से सेकंड |

---

## ⚡ 3-Line Summary
English: Use aware datetimes, store UTC, convert with `ZoneInfo` only for display. Subtracting gives `timedelta`; parse and print with `fromisoformat` / `isoformat` and `strptime` / `strftime`. Avoid `utcnow()`.
Hindi: Aware datetimes इस्तेमाल करें, UTC में store करें, display के लिए ही `ZoneInfo` से बदलें। घटाने पर `timedelta` मिलता है; `fromisoformat` / `isoformat` और `strptime` / `strftime` से parse व print करें। `utcnow()` से बचें।

---

## ➡️ Next Topic
**193. time Module** — low level clocks, sleeping, and measuring how long code takes.
