# P10. Real-Time Admin / Analytics Dashboard (End-to-End Design)
# हिंदी में: Real-Time Admin/Analytics Dashboard — ops और business टीम के लिए live स्क्रीन: हर मिनट के orders, GMV, payment success rate, शहर-वार riders, charts, filters, लाखों rows वाली tables, alerts और export — events की streaming से लेकर तेज़ frontend तक

---

## 🔵 Simple Definition (English)
A **real-time dashboard** shows **live and historical metrics** (orders per minute, GMV in ₹, payment success rate, active riders by city, error rates) with **filters, drill-downs, charts, large tables, alerts and exports**, for ops teams (Swiggy control room), merchants (Razorpay/Shopify dashboard) or internal admins.
End to end:
- **Ingestion**: services emit events to **Kafka**.
- **Stream processing** (Flink/Kafka Streams/Spark Streaming): cleans, enriches and pre-aggregates into rollups (per minute, city, merchant).
- **Real-time OLAP store** (**ClickHouse**, Apache **Pinot**, **Druid**) for sub-second slice-and-dice queries, plus a warehouse (BigQuery/Snowflake) for deep history.
- **Query API** with caching, row-level security (merchant sees only their data) and query guardrails.
- **Push updates** to clients via **WebSocket/SSE** (or smart polling).
- **Frontend** (React/Next.js):
  - performant charts (canvas/WebGL: ECharts, uPlot) with **downsampling**
  - **virtualized data grids** (100k+ rows)
  - **URL-synced filters**, throttled re-renders, Web Workers for transforms
  - **Indian number formatting** (lakh/crore) and time zones (IST)
  - RBAC, audit logs, async exports

## 🔵 सरल परिभाषा (Hindi)
Real-time dashboard = live और पुराने आँकड़े (हर मिनट के orders, ₹ में GMV, payment success %, शहर-वार riders, errors) filters, drill-down, charts, बड़ी tables, alerts और export के साथ — ops टीम, merchants (Razorpay dashboard) या admins के लिए।
पूरा रास्ता: services → Kafka events → stream processing (Flink) से साफ़ करना और मिनट/शहर/merchant के हिसाब से जोड़ना → real-time OLAP (ClickHouse/Pinot/Druid) में सेकंड से कम में query → cache और permissions वाला query API → WebSocket/SSE से live अपडेट → तेज़ frontend (canvas charts, downsampling, virtualized tables, URL में filters, lakh/crore format, IST)।

---

## 🔴 Problem it Solves
Ops and business teams need to **see problems as they happen**:
- Payment success drops from 92% to 70% in one city because a bank's UPI is down. They need to know in **minutes, not tomorrow's report**.
- During IPL nights or rain, a control room watches orders, rider availability and delays per zone to trigger surge or incentives.
- Merchants want their **sales and settlements live**.
Naive approaches fail:
- Running analytics queries on the **production OLTP database** (Postgres/MySQL) slows down checkout (full scans, locks).
- **Batch ETL** (nightly) is too late for operations.
- Dashboards that fetch 1M rows and render 50 charts **freeze the browser**, and auto-refreshing every second **DDoSes your own backend**.
- Without **row-level security**, a merchant could see another merchant's data.

## 🔴 यह क्यों बना? (Hindi)
Ops और business टीमों को समस्या होते ही दिखनी चाहिए: किसी शहर में bank का UPI बंद होने से payment success 92% से 70% हुआ — मिनटों में पता चले, कल की report में नहीं; IPL रात या बारिश में control room हर zone के orders, riders और देरी देखकर surge/incentive चालू करे; merchants को अपनी बिक्री live चाहिए।
ग़लत तरीके: production DB पर analytics query (checkout धीमा), रात वाला batch (देर), 10 लाख rows और 50 charts से browser अटके, हर सेकंड refresh से अपना ही backend गिरे, और row-level security नहीं तो एक merchant दूसरे का डेटा देखे।

---

## 🟢 How it Works — Step by Step

### 1. Requirements

```
Metrics: orders/min, GMV (₹), AOV, payment success rate by method/bank/PSP, delivery time p50/p90,
         active riders & utilization by zone, cancellations by reason, API error rates
Views: overview tiles (live), time-series charts (last 15 min … 90 days), breakdowns (city/zone/
       merchant/method), drill-down tables (order-level, 100k+ rows), anomaly alerts, CSV/Excel export
Freshness: < 10–30 s for live tiles; historical queries < 1–2 s p95
Users: internal ops (all data), merchants (own data only — row-level security), managers (region scope)
Scale (assume): 5k events/s avg, 50k/s peak; 2B events/90 days; 2k concurrent dashboard users
```

### 2. Architecture (Lambda-lite / Kappa style)

```
Services (order, payment, rider, app) ──events──► Kafka (topics, schema registry: Avro/Protobuf)
                                                     │
            ┌────────────────────────────────────────┼──────────────────────────────────┐
            ▼                                        ▼                                  ▼
  Stream processor (Flink)                  Raw sink → data lake (S3/Parquet)   Alerting (Flink CEP /
  - dedupe, enrich (city, merchant tier)    → warehouse (BigQuery/Snowflake)    rules on rollups) →
  - windowed aggregates (1-min tumbling)      for deep history & BI             PagerDuty/Slack
  - late events (watermarks, 5-min allowed lateness)
            │
            ▼
  Real-time OLAP: ClickHouse / Pinot / Druid
   - raw events table (recent 30–90 days, partitioned by day)
   - rollup tables / materialized views (per minute × city × method)
            │
            ▼
  Query API (Node/FastAPI): auth + RBAC + row-level filters (merchant_id = token claim),
   parameterized query templates, limits/timeouts, result caching (Redis, 5–30 s), pagination
            │                                 │
            ▼ REST (historical, drill-down)   ▼ WS/SSE (live tiles: push deltas every 5–10 s)
  Dashboard frontend (Next.js/React): charts (canvas), virtualized grid, URL filters, exports
```

### 3. Why OLAP, not the production DB

```
OLTP (Postgres) = row-oriented, optimized for point reads/writes, transactions → checkout
OLAP (ClickHouse/Pinot/Druid) = column-oriented, compressed, vectorized scans, aggregates over billions
  of rows in sub-second, pre-aggregation (rollups/star-tree indexes), high ingest from Kafka
Use CDC (Debezium) or events to feed OLAP — never run heavy GROUP BYs on the primary
```

### 4. Query patterns & guardrails

```
Pre-aggregated rollups for common views (per minute → per hour → per day) → cheap tiles & charts
Raw table for drill-downs with mandatory time range + LIMIT + selected columns
Guardrails: max time range per granularity (1-min buckets only for ≤ 48 h), query timeout (5 s),
  concurrency limits per user/tenant, result caching keyed by normalized query + tenant
Row-level security: every query template injects tenant filters from the auth token (never from the client)
```

### 5. Frontend performance

```
Charts:
  - canvas/WebGL renderers (ECharts, uPlot) for thousands of points; SVG for small charts
  - downsample server-side to ≤ ~1–2k points per series (time buckets / LTTB) — screens have ~1–2k px
  - update live series incrementally (append last bucket) instead of re-rendering everything
Tables:
  - virtualized data grid (TanStack Table + TanStack Virtual, or AG Grid) for 100k rows
  - server-side sorting/filtering/pagination for large datasets; column pinning, resizing
State:
  - filters (city, date range, method) in the URL → shareable links, back button works
  - React Query for server state (staleTime per widget), WS deltas update cache
  - throttle re-render of live widgets to ~1/s; pause updates when tab hidden (visibilitychange)
Work off main thread: heavy transforms/CSV parsing in Web Workers (Comlink)
Layout: lazy-load widgets below the fold; skeletons; error boundary per widget (one failing query
  doesn't blank the dashboard)
Formatting: Intl.NumberFormat('en-IN') → ₹1,23,45,678; compact "₹1.2 Cr"; times in IST (Asia/Kolkata)
  with explicit timezone labels; accessible charts (data table alternative, aria labels)
```

### 6. Exports & heavy reports

```
"Export 2M rows" → async job: API enqueues → worker runs OLAP query in chunks → writes CSV to S3 →
  presigned link via notification/email; never stream millions of rows through the browser
```

### 7. Mobile considerations

```
Ops leaders want a mobile view: React Native app or responsive web with key tiles + alerts (push),
simplified charts, offline last snapshot; push notifications for anomaly alerts with deep links to the
filtered dashboard view
```

## 🟢 कैसे काम करता है? (Hindi)
1. Services events Kafka में भेजती हैं (schema registry); Flink duplicate हटाता, city/merchant जोड़ता, 1 मिनट की windows में जोड़ता (देर से आए events के लिए watermarks); raw events data lake/warehouse में भी।
2. Real-time OLAP (ClickHouse/Pinot/Druid) — column वाला, compressed, अरबों rows पर सेकंड से कम में aggregate; production DB पर भारी GROUP BY कभी नहीं (CDC या events से भरो)।
3. Query API: auth + RBAC, merchant वाला filter token से (client से नहीं), तय query templates, समय-सीमा/LIMIT/timeout, Redis में 5–30 सेकंड cache; live tiles के लिए WS/SSE हर 5–10 सेकंड बदलाव।
4. Frontend: canvas charts (ECharts/uPlot), सर्वर से ~1–2k points तक downsample, live series में सिर्फ़ नया bucket जोड़ो; 1 लाख rows की virtualized table, sorting/filter सर्वर पर; filters URL में; live widgets ~1/सेकंड, tab छुपा तो रोको; भारी काम Web Worker में; हर widget का अपना error boundary।
5. ₹ के लिए `en-IN` format (₹1,23,45,678, "₹1.2 Cr"), IST साफ़ लिखो; बड़ा export async job से S3 link; mobile पर मुख्य tiles + anomaly alerts का push।

---

## 🟡 Real World Example

**LinkedIn → Apache Pinot** — LinkedIn built Pinot for real-time analytics behind features like "Who viewed my profile" and internal dashboards, and later open-sourced it. **Uber** uses Pinot (and earlier Druid and its own systems) for real-time operational dashboards such as city-level supply and demand and restaurant manager dashboards for Uber Eats.

**ClickHouse** — originally built at Yandex for web analytics, now widely used for real-time dashboards (Cloudflare analytics is a famous adopter). Indian startups commonly pick ClickHouse for product and ops analytics because it ingests Kafka streams and aggregates billions of rows quickly.

**Razorpay / Stripe merchant dashboards** — merchants see live payments, success rates by method and settlement status, with strict per-merchant data isolation and async exports for large reports.

**Swiggy / Zomato control rooms** — ops teams monitor live orders, rider supply and delivery delays per zone during peaks (rain, IPL), triggering interventions such as surge, incentives and serviceability changes from real-time dashboards and alerts.

## 🟡 Real Example Hindi में
LinkedIn ने "Who viewed my profile" और dashboards के लिए **Apache Pinot** बनाया और open-source किया; Uber इसे शहर-वार supply/demand और Uber Eats के restaurant dashboards में इस्तेमाल करता है; Yandex में बना **ClickHouse** Cloudflare analytics जैसी जगहों और कई भारतीय startups में लोकप्रिय।
Razorpay/Stripe के merchant dashboards में live payments और success rates (हर merchant का डेटा अलग, बड़े export async); Swiggy/Zomato के control rooms बारिश/IPL में zone-वार orders और riders देखकर surge/incentive चालू करते हैं।

---

## 🟠 My Stack Example

### ClickHouse: raw events + per-minute rollup via materialized view
```sql
CREATE TABLE events_payments (
  ts DateTime64(3, 'UTC'), event_id UUID, merchant_id UInt64, city LowCardinality(String),
  method LowCardinality(String), bank LowCardinality(String), status LowCardinality(String), amount_paise UInt64
) ENGINE = ReplacingMergeTree PARTITION BY toDate(ts) ORDER BY (merchant_id, ts, event_id)
TTL toDateTime(ts) + INTERVAL 90 DAY;

CREATE TABLE payments_1m (
  minute DateTime('UTC'), merchant_id UInt64, city LowCardinality(String), method LowCardinality(String),
  attempts AggregateFunction(count), success AggregateFunction(countIf, UInt8), gmv AggregateFunction(sumIf, UInt64, UInt8)
) ENGINE = AggregatingMergeTree ORDER BY (merchant_id, minute, city, method);

CREATE MATERIALIZED VIEW payments_1m_mv TO payments_1m AS
SELECT toStartOfMinute(ts) AS minute, merchant_id, city, method,
       countState() AS attempts, countIfState(status = 'captured') AS success,
       sumIfState(amount_paise, status = 'captured') AS gmv
FROM events_payments GROUP BY minute, merchant_id, city, method;
-- Ingest from Kafka via ClickHouse Kafka engine or a consumer service
```

### Query API with row-level security, guardrails and caching (Node)
```js
const MAX_RANGE_HOURS = { '1m': 48, '1h': 24 * 31, '1d': 24 * 365 };
app.get('/api/metrics/payments', auth, async (req, res) => {
  const { from, to, granularity = '1m', city } = req.query;
  const hours = (new Date(to) - new Date(from)) / 36e5;
  if (!MAX_RANGE_HOURS[granularity] || hours > MAX_RANGE_HOURS[granularity]) return res.status(422).json({ error: { code: 'RANGE_TOO_LARGE' } });
  const merchantId = req.user.role === 'merchant' ? req.user.merchantId : (req.query.merchantId ?? null);   // RLS from token
  const key = `m:pay:${merchantId}:${city ?? '*'}:${granularity}:${from}:${to}`;
  const cached = await redis.get(key); if (cached) return res.type('json').send(cached);

  const bucket = { '1m': 'minute', '1h': 'toStartOfHour(minute)', '1d': 'toDate(minute)' }[granularity];
  const rows = await clickhouse.query({
    query: `SELECT ${bucket} AS t, countMerge(attempts) AS attempts, countIfMerge(success) AS success, sumIfMerge(gmv) AS gmv_paise
            FROM payments_1m WHERE minute BETWEEN {from:DateTime} AND {to:DateTime}
            ${merchantId ? 'AND merchant_id = {merchantId:UInt64}' : ''} ${city ? 'AND city = {city:String}' : ''}
            GROUP BY t ORDER BY t`,
    query_params: { from, to, merchantId, city }, format: 'JSONEachRow',
    clickhouse_settings: { max_execution_time: 5 },                                   // timeout guardrail
  }).then((r) => r.json());
  const body = JSON.stringify({ series: rows.map((r) => ({ t: r.t, successRate: r.attempts ? r.success / r.attempts : null, gmvPaise: Number(r.gmv_paise) })) });
  await redis.set(key, body, 'EX', granularity === '1m' ? 10 : 300);
  res.type('json').send(body);
});
```

### Live tiles via SSE (push latest minute every 10 s)
```js
app.get('/api/live/overview', auth, async (req, res) => {
  res.set({ 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
  const send = async () => res.write(`event: tick\ndata: ${JSON.stringify(await latestOverview(req.user))}\n\n`);
  await send(); const id = setInterval(send, 10_000);
  req.on('close', () => clearInterval(id));
});
```

### Frontend: URL-synced filters, React Query, throttled live chart (uPlot), virtualized table
```tsx
'use client';
import uPlot from 'uplot';

export function PaymentsDashboard() {
  const sp = useSearchParams(); const router = useRouter();
  const filters = { from: sp.get('from') ?? isoMinusHours(6), to: sp.get('to') ?? isoNow(), city: sp.get('city') ?? undefined, granularity: sp.get('g') ?? '1m' };
  const setFilter = (k: string, v?: string) => { const p = new URLSearchParams(sp); v ? p.set(k, v) : p.delete(k); router.replace(`?${p}`); };

  const series = useQuery({ queryKey: ['pay', filters], queryFn: () => http.get('/api/metrics/payments', { params: filters }).then((r) => r.data.series), staleTime: 10_000, placeholderData: (prev) => prev });
  const live = useLiveOverview();                                                   // SSE → state, paused when tab hidden

  return (
    <main>
      <Filters value={filters} onChange={setFilter} />
      <section aria-label="Live overview" className="tiles">
        <Tile label="GMV today" value={formatINRCompact(live?.gmvPaise)} />          {/* ₹1.2 Cr */}
        <Tile label="Payment success" value={pct(live?.successRate)} tone={live?.successRate < 0.85 ? 'danger' : 'ok'} />
        <Tile label="Orders / min" value={live?.ordersPerMin?.toLocaleString('en-IN')} />
      </section>
      <ErrorBoundary fallback={<WidgetError />}><SuccessRateChart data={series.data ?? []} /></ErrorBoundary>
      <ErrorBoundary fallback={<WidgetError />}><TransactionsGrid filters={filters} /></ErrorBoundary>
    </main>
  );
}

function SuccessRateChart({ data }: { data: { t: string; successRate: number | null }[] }) {
  const ref = useRef<HTMLDivElement>(null); const plot = useRef<uPlot>();
  useEffect(() => {
    const xs = data.map((d) => Date.parse(d.t) / 1000), ys = data.map((d) => d.successRate);
    if (!plot.current) plot.current = new uPlot({ width: ref.current!.clientWidth, height: 260, tzDate: (ts) => uPlot.tzDate(new Date(ts * 1e3), 'Asia/Kolkata'),
      series: [{}, { label: 'Success rate', stroke: '#1a73e8', value: (_u, v) => (v == null ? '—' : `${(v * 100).toFixed(1)}%`) }] }, [xs, ys], ref.current!);
    else plot.current.setData([xs, ys]);                                             // incremental update, canvas render
  }, [data]);
  return <div ref={ref} role="img" aria-label="Payment success rate over time (IST)" />;
}

export const formatINRCompact = (paise?: number) =>
  paise == null ? '—' : new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', notation: 'compact', maximumFractionDigits: 1 }).format(paise / 100);
```

### Async export job (FastAPI)
```python
@app.post("/api/exports")
async def create_export(body: ExportRequest, user=Depends(current_user)):
    job_id = str(uuid4())
    await queue.enqueue("export_transactions", job_id=job_id, merchant_id=scope(user, body), from_=body.from_, to=body.to, columns=body.columns)
    return {"jobId": job_id, "status": "QUEUED"}          # worker streams ClickHouse → CSV → S3, then notifies with a presigned link
```

---

## ⚫ Interview Questions + Answers

**Q1: Why not run dashboard queries directly on the production database?**
A1: OLTP databases are row-oriented and tuned for transactional point reads and writes. Large aggregations over millions of rows cause full scans, high CPU and I/O, cache eviction and lock contention that slow customer-facing traffic like checkout. Analytical workloads belong in column-oriented OLAP stores (ClickHouse, Pinot, Druid) or warehouses fed by event streams or CDC. They compress data, scan only needed columns with vectorized execution, support rollups and pre-aggregation, and isolate analytics load from production.

**Q2: How do you keep a live dashboard fresh without overloading the backend?**
A2: Pre-aggregate in the stream processor into per-minute rollups, so live queries are tiny. Push updates from the server (SSE or WebSocket) every 5–10 seconds per channel or tenant, computed once and fanned out, rather than having every client poll heavy queries. Cache query results briefly (10–30 s) keyed by normalized query and tenant, throttle client re-renders, pause updates for hidden tabs, and apply per-user concurrency limits and query timeouts. Incrementally append new buckets to charts instead of refetching full ranges.

**Q3: How do you render charts and tables with lots of data in the browser?**
A3: Downsample on the server to roughly the number of horizontal pixels (time bucketing or LTTB), and render with canvas or WebGL libraries (uPlot, ECharts) that handle thousands of points efficiently, updating series incrementally. For tables, use server-side pagination, sorting and filtering, plus a virtualized grid that only renders visible rows and columns. Move heavy transforms (CSV parsing, client aggregations) to Web Workers, lazy-load off-screen widgets, and isolate each widget with error boundaries and skeletons.

**Q4: How do you ensure merchants only see their own data?**
A4: Enforce row-level security on the server. The tenant or merchant ID comes from the authenticated token (never from client parameters), and every parameterized query template injects the tenant filter. Optionally use database-level row policies or per-tenant views, with role scopes for internal users (region managers see their region). Cache keys include the tenant, exports are scoped and audited, and tests verify isolation. Never allow arbitrary SQL from the client.

**Q5: How do you handle late or duplicate events in real-time metrics?**
A5: Give each event a unique ID and an event timestamp. In the stream processor, dedupe by ID within a window, use event-time windows with watermarks and an allowed lateness (say, 5 minutes) so late events update the right minute bucket, and emit corrections (upserts) to the OLAP store (ReplacingMergeTree or upsert tables in Pinot). For very late data, rely on periodic batch recomputation from the raw lake to correct historical aggregates. The dashboard labels the latest minute as "provisional".

---

## 🔷 Trade-offs
✅ Real-time OLAP (Pinot/ClickHouse/Druid): sub-second at scale — ❌ another system to operate; schema & rollup design effort.
✅ Pre-aggregated rollups: cheap queries — ❌ less flexibility for ad-hoc dimensions (keep raw table too).
✅ Push via SSE/WS: efficient freshness — ❌ connection management; polling simpler for low-frequency widgets.
✅ Canvas charts: fast with big data — ❌ accessibility requires extra work (data tables, labels).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OLTP vs OLAP | Transactions vs analytics stores | लेन-देन बनाम विश्लेषण DB |
| Columnar storage | Store by column for scans | column के हिसाब से डेटा |
| Rollup | Pre-aggregated summary table | पहले से जोड़ी तालिका |
| Materialized view | Auto-maintained query result | अपने-आप बनती query तालिका |
| Watermark | Event-time progress marker | event समय की प्रगति |
| Late event | Arrives after its window | देर से आया event |
| Downsampling | Reduce points for display | कम points में दिखाना |
| Virtualized grid | Render visible rows only | सिर्फ़ दिखने वाली rows |
| Row-level security | Per-tenant data filtering | हर ग्राहक का अलग डेटा |
| Async export | Background report generation | पीछे से report बनाना |

---

## ⚡ 3-Line Summary
**English:**
1. Events → Kafka → Flink (dedupe, enrich, event-time windows) → real-time OLAP (ClickHouse/Pinot/Druid) rollups + raw tables; warehouse for deep history; never query OLTP for analytics.
2. Query API with RLS from tokens, templates, range limits, timeouts and short caching; live tiles pushed via SSE/WS; heavy exports as async jobs.
3. Frontend: URL-synced filters, React Query, canvas charts with server downsampling and incremental updates, virtualized grids, Web Workers, per-widget error boundaries, ₹ lakh/crore and IST formatting.

**Hindi:**
1. Events → Kafka → Flink → real-time OLAP (rollups + raw); पुराना इतिहास warehouse में; analytics कभी production DB पर नहीं।
2. Query API: token से RLS, templates, सीमाएँ, timeout, छोटा cache; live tiles SSE/WS से; बड़ा export async।
3. Frontend: URL filters, React Query, canvas charts + downsampling, virtualized tables, Web Workers, हर widget का error boundary, ₹ lakh/crore और IST।

---

## ➡️ Next Topic Suggestion
**🎉 Full-Stack Design Problems complete!** Next: **127. LLM Basics** in `10-AI-Engineering/`. Modern system design now includes AI features (chatbots, RAG, agents). Next: what LLMs are, how they work, and how to build reliable AI systems on top of them.
