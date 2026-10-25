# 238. Cron Jobs in Node (node-cron)
# हिंदी में: Node में Cron Jobs (node-cron)

---

## 🔵 Simple Definition (English)
`node-cron` is a lightweight Node.js library for scheduling tasks to run at specific times or intervals using standard cron syntax (e.g., "every day at 2 AM"), directly inside your Node.js process, without needing an external queue system or OS-level cron.

## 🔵 सरल परिभाषा (Hindi)
`node-cron` एक lightweight Node.js library है जो standard cron syntax (जैसे "हर दिन 2 AM पर") का use करके specific times या intervals पर tasks schedule करने देती है, directly Node.js process के अंदर, बिना किसी external queue system या OS-level cron की जरूरत के।

---

## 🔴 Problem it Solves
Many apps need recurring tasks — cleaning up expired sessions, sending daily digest emails, generating nightly reports, syncing data with a third-party service. Relying on OS-level cron (crontab) requires separate deployment/configuration outside the app and doesn't travel well with containerized or serverless deployments. `node-cron` solves this by letting you define and run scheduled tasks as plain JavaScript, co-located with your application code, deployable as part of the same app/container.

## 🔴 यह क्यों बना? (Hindi)
बहुत से apps को recurring tasks चाहिए — expired sessions clean करना, daily digest emails भेजना, nightly reports generate करना, third-party service से data sync करना। OS-level cron (crontab) पर depend करने के लिए app के बाहर separate deployment/configuration चाहिए और यह containerized या serverless deployments के साथ अच्छे से नहीं चलता। `node-cron` scheduled tasks को plain JavaScript के रूप में define और run करने देकर यह solve करता है, application code के साथ co-located, same app/container के part के रूप में deployable।

---

## 🟢 How it Works — Step by Step

Step 1 → Install `node-cron` and define a cron expression (5 or 6 fields: minute, hour, day-of-month, month, day-of-week).
Step 2 → Call `cron.schedule(expression, callback)` — the library internally sets up a timer that checks the current time against the expression.
Step 3 → When the current time matches the expression, the callback function executes.
Step 4 → The scheduled task runs INSIDE the same Node.js process — if the process isn't running, the task doesn't fire (unlike OS cron, which is independent of any single app process).
Step 5 → Optionally set a timezone so scheduling is consistent regardless of server location.
Step 6 → Tasks can be started/stopped dynamically (`task.start()`, `task.stop()`) at runtime.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `node-cron` install करो और एक cron expression define करो (5 या 6 fields: minute, hour, day-of-month, month, day-of-week)।
Step 2 → `cron.schedule(expression, callback)` call करो — library internally एक timer setup करती है जो current time को expression से check करती है।
Step 3 → जब current time expression से match करे, callback function execute होता है।
Step 4 → Scheduled task SAME Node.js process के अंदर चलता है — अगर process नहीं चल रहा, task fire नहीं होता (OS cron के विपरीत, जो किसी single app process से independent होता है)।
Step 5 → Optionally एक timezone set करो ताकि server location के बावजूद scheduling consistent रहे।
Step 6 → Tasks runtime में dynamically start/stop किए जा सकते हैं (`task.start()`, `task.stop()`)।

---

## 🟡 Real World Example
**Flipkart's "abandoned cart" reminder:** Every day at 6 PM, a scheduled job scans for carts that haven't been checked out in 24+ hours and queues reminder emails/push notifications. Using `node-cron`, this logic lives right inside the notification service's codebase (`cron.schedule('0 18 * * *', scanAbandonedCarts)`) — no separate infrastructure needed, deployed and version-controlled together with the rest of the service.

## 🟡 Real Example Hindi mein
**Flipkart का "abandoned cart" reminder:** हर दिन 6 PM पर, एक scheduled job उन carts को scan करती है जो 24+ घंटों से checkout नहीं हुए और reminder emails/push notifications queue करती है। `node-cron` use करके, यह logic notification service के codebase के अंदर ही रहता है (`cron.schedule('0 18 * * *', scanAbandonedCarts)`) — कोई अलग infrastructure नहीं चाहिए, बाकी service के साथ deployed और version-controlled।

---

## 💻 Code Example — Basic

```javascript
// node-cron-basic.js
// Run: node node-cron-basic.js (requires npm i node-cron)

const cron = require('node-cron');

// Cron expression format: 'minute hour day-of-month month day-of-week'
// '* * * * *' = every minute (good for testing)
cron.schedule('* * * * *', () => {
  console.log('Running every minute:', new Date().toISOString());
});

// Every day at 2:00 AM: clean up expired sessions
cron.schedule('0 2 * * *', () => {
  console.log('Running daily cleanup at 2 AM');
  cleanupExpiredSessions();
});

function cleanupExpiredSessions() {
  console.log('Expired sessions cleaned');   // placeholder for real DB cleanup logic
}

console.log('Cron jobs scheduled. Process must stay running for them to fire.');
```

## 💻 Code Example — Advanced

```javascript
// node-cron-advanced.js — timezone, dynamic control, error handling, overlapping-run prevention
const cron = require('node-cron');

let isReportRunning = false;   // simple lock to prevent overlapping runs of a long task

const dailyReportTask = cron.schedule('0 9 * * *', async () => {
  if (isReportRunning) {
    console.warn('Previous report run still in progress — skipping this trigger');
    return;   // prevents two overlapping runs if the job takes longer than 24 hours (edge case)
  }

  isReportRunning = true;
  try {
    console.log('Generating daily report...');
    await generateDailyReport();
    console.log('Daily report generated successfully');
  } catch (err) {
    console.error('Daily report generation failed:', err.message);
    await alertOnCallEngineer(err);   // don't let a scheduled job fail silently
  } finally {
    isReportRunning = false;
  }
}, {
  scheduled: true,
  timezone: 'Asia/Kolkata',   // ensures 9 AM IST regardless of server's local timezone
});

async function generateDailyReport() {
  await new Promise(resolve => setTimeout(resolve, 2000));   // simulate heavy report generation
}

async function alertOnCallEngineer(err) {
  console.log('ALERT sent to on-call engineer:', err.message);
}

// ─── Dynamically controlling a scheduled task ─────────────────────────────────
const maintenanceWindowTask = cron.schedule('0 3 * * 0', () => {
  console.log('Weekly maintenance running (Sunday 3 AM)');
}, { scheduled: false });   // created but NOT started automatically

// Start it only when a maintenance window is enabled via admin action
function enableMaintenanceWindow() {
  maintenanceWindowTask.start();
  console.log('Maintenance window scheduling enabled');
}

function disableMaintenanceWindow() {
  maintenanceWindowTask.stop();
  console.log('Maintenance window scheduling disabled');
}

enableMaintenanceWindow();
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const cron = require('node-cron');

const app = express();
app.use(express.json());

let lastRunStatus = { lastRun: null, success: null };

// Scheduled job runs alongside the Express server in the same process
cron.schedule('0 */6 * * *', async () => {   // every 6 hours
  console.log('Running scheduled inventory sync...');
  try {
    await syncInventoryWithWarehouse();
    lastRunStatus = { lastRun: new Date(), success: true };
  } catch (err) {
    lastRunStatus = { lastRun: new Date(), success: false, error: err.message };
  }
});

async function syncInventoryWithWarehouse() {
  // placeholder for real sync logic
  return true;
}

// Expose the scheduled job's last-run status via a normal Express endpoint — useful for monitoring
app.get('/admin/inventory-sync/status', (req, res) => {
  res.json(lastRunStatus);
});

app.listen(3000, () => console.log('Server + cron jobs running on 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running the same cron schedule in EVERY instance of a horizontally-scaled app
✅ Correct: Use a distributed lock (Redis) or run scheduled jobs in a single dedicated instance/service

```javascript
// Wrong — if you run 5 instances of this app, the daily report runs 5 TIMES
cron.schedule('0 9 * * *', generateDailyReport);

// Right — use a Redis-based lock so only ONE instance actually executes the task
cron.schedule('0 9 * * *', async () => {
  const gotLock = await redis.set('lock:daily-report', '1', 'NX', 'EX', 60);
  if (gotLock) await generateDailyReport();
});
```

❌ Mistake 2: Assuming the cron job fires even when the process is down
✅ Correct: `node-cron` only fires while the Node.js process is running — for critical, must-run-even-if-app-restarts tasks, use OS cron or a managed scheduler (e.g., cloud cron triggers) instead

```javascript
// Wrong assumption: "it'll catch up and run the missed job when the app restarts" — it won't
// Right: for critical tasks, use a durable scheduler (BullMQ repeatable jobs, cloud scheduler, OS cron)
```

---

## 🧠 Tricky Interview Question

```javascript
const cron = require('node-cron');

cron.schedule('* * * * *', async () => {
  console.log('Job started');
  await new Promise(r => setTimeout(r, 90000));   // takes 90 seconds
  console.log('Job finished');
});
// This runs every minute, but each run takes 90 seconds. What happens?
```
Answer: Without overlap protection, `node-cron` will trigger a NEW run every minute regardless of whether the previous run finished — since the task takes 90 seconds but fires every 60 seconds, you'll get overlapping executions stacking up indefinitely (run 1 still going when run 2 and run 3 start), potentially exhausting memory/connections. The fix is an overlap guard (a boolean flag or distributed lock) that skips a trigger if the previous run of the same job is still in progress, as shown in the Advanced example above.

---

## ⚫ Interview Questions + Answers

Q1: How does `node-cron` differ from OS-level cron (crontab)?
A1: OS-level cron is managed by the operating system, independent of any specific application process — it fires its configured command at the scheduled time regardless of whether a particular app is running, and survives app restarts/crashes. `node-cron` runs entirely inside a Node.js process — if that process isn't running, scheduled callbacks simply don't fire; it's convenient because the scheduling logic lives in your app code (version-controlled, deployed together), but it is NOT durable across process restarts/crashes the way OS cron is.

Q2: What problem arises when running `node-cron` in a horizontally-scaled app with multiple instances, and how do you fix it?
A2: If the same cron schedule is defined in application code and you run N instances (for horizontal scaling), the scheduled task will fire N times simultaneously — e.g., sending a daily report email 5 times if you have 5 instances. The fix is to either (1) run scheduled jobs in a single, dedicated instance/service separate from the horizontally-scaled web tier, or (2) use a distributed lock (e.g., Redis `SET key value NX EX ttl`) so only the first instance to acquire the lock actually executes the task, and others skip it.

Q3: What does the cron expression `'0 2 * * *'` mean?
A3: It represents: minute=0, hour=2, day-of-month=any (*), month=any (*), day-of-week=any (*) — meaning "run at 2:00 AM every day." The standard 5-field cron format is `minute hour day-of-month month day-of-week`, each field accepting specific values, ranges, lists, or `*` for "any."

Q4: How would you handle a scheduled task that might take longer than its own interval to complete?
A4: Add an overlap guard: a simple in-process flag (for single-instance scenarios) or a distributed lock (Redis, for multi-instance scenarios) that's set when the task starts and checked/cleared at completion. If a new trigger fires while the flag/lock indicates a previous run is still active, skip that trigger (and optionally log a warning) rather than letting runs stack up and compound resource usage.

Q5: When would you choose `node-cron` over BullMQ's repeatable jobs for scheduled tasks?
A5: `node-cron` is simpler and sufficient when: the task is lightweight, you have a single dedicated process/instance running it (no horizontal scaling concerns), and you don't need retry/failure tracking or persistence across restarts. BullMQ's repeatable jobs are better when: you need the task's execution to be reliable across multiple worker instances without duplicate runs (BullMQ naturally handles this via its queue semantics), you want retry/backoff on failure, or you want visibility (via Bull Board) into scheduled job history and status.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have a single dedicated process/service for scheduled tasks, or can add simple distributed locking
- Tasks are lightweight and don't need sophisticated retry/failure handling
- You want scheduling logic co-located with application code for simplicity

❌ Avoid when:
- Running multiple instances of the SAME app without a locking mechanism (causes duplicate executions)
- The task is business-critical and must run exactly once even if the app restarts mid-schedule (use a durable scheduler like BullMQ repeatable jobs, a cloud scheduler service, or OS cron with a proper job runner)

---

## 📊 Visual Diagram
```
Node.js process
┌───────────────────────────────┐
│  Express server (handles HTTP) │
│                                  │
│  node-cron timer ───────────────┤──▶ fires callback at scheduled time
│  (checks time every tick)       │       │
└───────────────────────────────┘       ▼
                                   runs INSIDE this same process
                                   (dies if process dies — no durability)

Multi-instance problem:
Instance A: cron fires "send report" ──┐
Instance B: cron fires "send report" ──┼──▶ report sent 3 TIMES (bug!)
Instance C: cron fires "send report" ──┘
Fix: distributed lock → only ONE instance actually executes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cron expression | Time pattern string for scheduling | Scheduling के लिए time pattern string |
| Overlap guard | Prevents concurrent runs of same job | एक job के concurrent runs रोकना |
| Distributed lock | Shared lock preventing duplicate execution across instances | Instances में duplicate execution रोकने वाला shared lock |
| Timezone-aware scheduling | Scheduling fixed to a specific timezone | Specific timezone से fixed scheduling |

---

## ⚡ 3-Line Summary
**English:**
1. `node-cron` schedules recurring tasks using cron syntax directly inside a Node.js process, co-located with app code.
2. It is NOT durable across process restarts and fires duplicate times across horizontally-scaled instances unless locked.
3. Always add overlap protection and consider a durable alternative (BullMQ repeatable jobs) for business-critical schedules.

**Hindi:**
1. `node-cron` cron syntax use करके recurring tasks को directly Node.js process के अंदर schedule करता है, app code के साथ co-located।
2. यह process restarts के across durable नहीं है और horizontally-scaled instances में बिना lock के duplicate बार fire होता है।
3. हमेशा overlap protection add करो और business-critical schedules के लिए durable alternative (BullMQ repeatable jobs) consider करो।

---

## ➡️ Next Topic
**239. Event-Driven Architecture in Node** — Designing systems around events rather than direct calls, building on queues and schedulers.
