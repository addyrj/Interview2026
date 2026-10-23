# P05. Google Docs — Collaborative Editor (End-to-End Design)
# हिंदी में: Google Docs जैसा collaborative editor — कई लोग एक ही document में एक साथ लिखें और सबको तुरंत दिखे: बदलावों को मिलाना (OT या CRDT), दूसरों के cursors, offline editing, version history, comments और sharing permissions

---

## 🔵 Simple Definition (English)
Design a **real-time collaborative document editor** where many users edit the same document concurrently and everyone converges to the **same content**:
- **Client editor** (web first, plus mobile): rich text model (ProseMirror/Tiptap, Lexical, Slate), local edits applied instantly, operations sent to the server, remote operations merged.
- **Concurrency control**: **OT (Operational Transformation)** with a central server ordering operations (Google Docs' approach), or **CRDTs** (Yjs, Automerge), which merge automatically and support offline and peer-to-peer.
- **Presence/awareness**: collaborators' cursors, selections and names in real time (ephemeral).
- **Persistence**: operation log plus periodic **snapshots**, giving **version history** ("See edit history", named versions, restore).
- **Comments & suggestions** anchored to text ranges that move with edits.
- **Sharing & permissions**: owner/editor/commenter/viewer, link sharing, org domain restrictions.
- **Offline editing** with sync on reconnect, and mobile apps.

## 🔵 सरल परिभाषा (Hindi)
Real-time collaborative editor = कई लोग एक ही document में एक साथ लिखें और सबके पास आख़िर में एक जैसा content हो: client editor (rich text model, अपना बदलाव तुरंत दिखे, operations सर्वर को, दूसरों के operations मिलाओ); टकराव सुलझाना — OT (सर्वर क्रम तय करे और बदलावों को transform करे — Google Docs का तरीका) या CRDT (Yjs/Automerge — अपने-आप मिल जाएँ, offline में भी); दूसरों के cursors (अस्थायी); operation log + snapshots से version history; text के साथ खिसकने वाले comments; owner/editor/commenter/viewer permissions; offline editing।

---

## 🔴 Problem it Solves
Before collaborative editors, teams emailed `report_final_v3_REAL.docx` back and forth, with merge conflicts and lost work. Real-time collaboration is hard because:
- Two users type at the **same position at the same time**, and naive "apply in arrival order" corrupts text (characters interleave wrongly, deletions remove the wrong range).
- Network latency means each user's local view is **ahead** of the server. Edits must be applied optimistically and then reconciled.
- Users go **offline** (train, flight) and edit, and changes must merge later without losing work.
- **Large documents** (100+ pages) must stay responsive, and history must be stored efficiently.
- Comments must stay anchored as text moves, and **permissions** must be enforced on every operation.
It's a classic question for **concurrency algorithms, real-time infrastructure and client performance**.

## 🔴 यह क्यों बना? (Hindi)
पहले टीमें `report_final_v3_REAL.docx` email करती थीं — टकराव और खोया काम। Real-time collaboration कठिन है: दो लोग एक ही जगह एक साथ टाइप करें तो सीधे क्रम से लगाने पर text बिगड़ता है; latency की वजह से हर यूज़र का view सर्वर से आगे रहता है — बदलाव पहले local में, फिर मिलाना; offline में किए बदलाव बाद में बिना नुक़सान मिलें; 100+ पन्नों वाले document तेज़ रहें और history कम जगह में; comments text के साथ खिसकें; हर operation पर permission लागू।

---

## 🟢 How it Works — Step by Step

### 1. Requirements

```
Functional: create/edit rich text (headings, lists, tables, images), real-time co-editing (≤ ~100 active
            editors per doc), cursors & selections, comments/suggestions, version history & restore,
            sharing (users, groups, link), offline editing, export (PDF/DOCX), mobile apps
Non-functional: local keystroke latency ~0 (optimistic), remote edits visible < 200–500 ms,
            convergence guaranteed, no data loss, documents up to many MB, high availability
Scale (assume): 100M docs edited/day, 1M concurrent editing sessions, peak 50k ops/s per hot region
```

### 2. Architecture

```
 Web client (React + ProseMirror/Tiptap)      Mobile client (RN: WebView editor or native)
   │ HTTPS (doc metadata, permissions)          │
   │ WSS (ops + presence) ──────────────┐       │
   ▼                                    ▼       ▼
┌──────────────────────────────── Backend ───────────────────────────────────┐
│ API: docs service (metadata, ACLs, sharing) · comments service · export     │
│ Collaboration servers: one AUTHORITATIVE session per document               │
│   (route by doc_id: consistent hashing / session registry → sticky)         │
│   - OT: receive op@rev, transform against ops since rev, apply, broadcast,   │
│     append to op log, ack with new rev                                      │
│   - (or CRDT: merge updates, broadcast, persist)                            │
│   - presence: in-memory per doc, broadcast throttled                        │
│ Storage: op log (Spanner/Postgres/Bigtable, append-only per doc),           │
│          snapshots (object storage, every N ops/minutes), search index      │
│ Pub/sub (Redis/Kafka) for multi-server fan-out & notifications              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3. OT in one picture (server-ordered)

```
Doc "AB" at rev 5. Alice inserts "X" at 1 → op A = ins(1,"X")@5 ; Bob deletes at 1 → op B = del(1)@5
Server receives A first → applies → rev 6 → "AXB" → broadcast A, ack Alice
Server receives B@5 (based on old rev) → TRANSFORM B against A: del(1) becomes del(2) (shifted by A's insert)
   → applies → rev 7 → "AX" → broadcast B' ; Bob's client receives A, transforms its pending ops, converges
Client rule (Jupiter model): at most ONE op in flight; buffer further local ops; on ack, send next;
   on remote op, transform it against in-flight + buffered local ops before applying
Result: all clients converge to identical text with intent preserved
```

### 4. CRDT alternative (Yjs/Automerge)

```
Each character/element gets a unique ID (clientId, clock); inserts reference neighbours by ID, not index
→ concurrent inserts/deletes merge deterministically on every replica without central transform
Server becomes a relay + persistence (y-websocket / Hocuspocus), clients can sync offline or P2P
Pros: offline-first, simpler server, P2P possible; Cons: metadata overhead (tombstones), larger docs,
      harder to enforce schema/permissions per op (validate on server), GC of history
Rule of thumb: central server & strict control → OT; offline/local-first & flexibility → CRDT
```

### 5. Client architecture

```
Editor model (ProseMirror doc tree / Yjs XmlFragment) ⇄ view (contenteditable) ⇄ collaboration plugin
- Local keystroke → transaction → applied instantly (optimistic) → op queued & sent
- Remote ops → transformed/merged → applied without moving local cursor incorrectly
- Undo/redo: per-user undo (only undo YOUR changes) — collaboration-aware undo manager
- Large docs: incremental rendering, virtualize long documents/pages, lazy-load images, Web Workers for
  heavy diff/export; avoid re-rendering entire doc per keystroke
- Offline: persist doc state + pending ops in IndexedDB (y-indexeddb), service worker for app shell;
  on reconnect: send pending (OT: rebase; CRDT: exchange state vectors)
- Mobile: rich-text editing natively is hard → embed web editor in WebView with a bridge (common),
  or native editors with the same CRDT/OT model; handle keyboard, selection handles, IME (Hindi/Indic
  input via keyboards → composition events must not break ops)
```

### 6. Presence & cursors

```
Ephemeral awareness state per client: {user, color, cursor anchor/head (relative positions)}
Throttle broadcasts (e.g., 10–20/s max), drop on disconnect (heartbeat timeout)
Positions stored as RELATIVE positions (attached to text IDs), so they move correctly with edits
```

### 7. Persistence, history & snapshots

```
Append each op (or CRDT update) to the per-doc log with rev number, author, timestamp
Snapshot every N ops / M minutes → fast load = latest snapshot + ops after it
Version history: group ops by author & time windows ("Edited by Asha, 10:42"), named versions = pinned
snapshots; restore = create new ops that transform current → old state (don't rewrite history)
Compaction: old ops folded into snapshots after retention period
```

### 8. Permissions & sharing

```
ACL per doc: owner, editors, commenters, viewers; groups/domains; link sharing (anyone with link: view/comment/edit)
Collaboration server checks role on CONNECT and on every op type (viewer can't send edits, commenter only
comments/suggestions); permission revocation → server closes session/downgrades in real time
Doc load via signed short-lived URLs for snapshots; audit log of sharing changes
```

### 9. Comments & suggestions

```
Comment anchored to a range via relative positions (or marks in the doc model) → moves with text;
if anchored text deleted → comment shown as "orphaned" with original quote
Suggestion mode: edits stored as marked insert/delete ops (tracked changes) until accepted/rejected
Comments service stores threads separately (Postgres), notifies via email/push with deep links
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर document का एक authoritative collaboration session (doc_id से एक ही server पर routing); client हर keystroke तुरंत local में लगाता है और operation (rev के साथ) WebSocket से भेजता है।
2. OT: सर्वर आए हुए op को उसके rev के बाद के ops के हिसाब से transform करता है (जैसे Alice के insert के बाद Bob का delete एक जगह खिसकता है), लगाता है, सबको भेजता है, op log में जोड़ता है; client एक समय में एक op भेजता है, बाक़ी buffer, आने वाले ops को अपने pending ops के हिसाब से transform।
3. CRDT (Yjs): हर अक्षर की अपनी id, बदलाव index नहीं id से जुड़ते हैं — हर replica पर अपने-आप एक जैसा मेल; सर्वर बस relay + persistence; offline/P2P आसान, पर metadata ज़्यादा।
4. Cursors अस्थायी awareness में (relative positions ताकि text के साथ खिसकें, throttle); op log + हर N ops पर snapshot = तेज़ load और version history; restore = नए ops बनाकर पुरानी स्थिति, history नहीं मिटाते।
5. Permissions हर connect और हर op पर (viewer edit नहीं भेज सकता), access हटते ही session बंद; comments relative positions से text के साथ; offline में IndexedDB, फिर sync; mobile पर अक्सर WebView editor, हिंदी/Indic keyboard के composition events का ध्यान।

---

## 🟡 Real World Example

**Google Docs** — uses operational transformation with a central server, inheriting ideas from Google Wave and the Jupiter collaboration model. Every keystroke is an operation, the server orders them, and revision history is built from the op log, letting you browse edit history down to fine granularity.

**Figma** — its multiplayer engine (described in Figma's engineering blog) is server-authoritative with CRDT-inspired structures and last-writer-wins per property on objects. Presence (cursors) is ephemeral, a pattern similar to collaborative docs.

**Notion, Linear and Yjs adopters** — Notion has block-based collaboration with offline support added later. Many products build collaboration on **Yjs** (y-websocket, Hocuspocus, Tiptap collaboration), showing that CRDTs are now mainstream for collaborative apps.

**Zoho Writer (India)** — Chennai-based Zoho's document editor supports real-time collaboration, comments and version history for millions of users, an Indian example of building this at scale.

## 🟡 Real Example Hindi में
Google Docs सर्वर के साथ OT इस्तेमाल करता है (Google Wave और Jupiter model की विरासत) — हर keystroke एक operation, सर्वर क्रम तय करता है, और op log से बारीक edit history।
Figma का multiplayer सर्वर-प्रधान है (CRDT से प्रेरित, हर property पर last-writer-wins); Notion, Linear और बहुत से products Yjs पर collaboration बनाते हैं; चेन्नई की Zoho का **Zoho Writer** भारत का उदाहरण — real-time collaboration, comments, version history।

---

## 🟠 My Stack Example

### Web client: Tiptap (ProseMirror) + Yjs + offline persistence + presence
```tsx
'use client';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Collaboration from '@tiptap/extension-collaboration';
import CollaborationCursor from '@tiptap/extension-collaboration-cursor';
import * as Y from 'yjs';
import { HocuspocusProvider } from '@hocuspocus/provider';
import { IndexeddbPersistence } from 'y-indexeddb';

export function DocEditor({ docId, user, token }: { docId: string; user: { name: string; color: string }; token: string }) {
  const ydoc = useMemo(() => new Y.Doc(), [docId]);
  const provider = useMemo(() => new HocuspocusProvider({ url: 'wss://collab.myapp.com', name: docId, document: ydoc, token }), [docId]);
  useEffect(() => { const local = new IndexeddbPersistence(`doc-${docId}`, ydoc); return () => { local.destroy(); provider.destroy(); }; }, [docId]);

  const editor = useEditor({
    extensions: [
      StarterKit.configure({ history: false }),                 // collaboration-aware undo comes from Yjs
      Collaboration.configure({ document: ydoc }),
      CollaborationCursor.configure({ provider, user }),       // presence: names + colored cursors
    ],
  }, [ydoc]);

  const status = useSyncExternalStore((cb) => { provider.on('status', cb); return () => provider.off('status', cb); }, () => provider.status);
  return (<>
    <div role="status" aria-live="polite">{status === 'connected' ? 'All changes saved' : 'Offline — changes saved on this device'}</div>
    <EditorContent editor={editor} />
  </>);
}
```

### Collaboration server (Node, Hocuspocus): auth per doc, persistence, snapshots
```ts
import { Server } from '@hocuspocus/server';
import { Database } from '@hocuspocus/extension-database';

const server = Server.configure({
  port: 1234,
  async onAuthenticate({ token, documentName, connection }) {
    const user = await verifyJwt(token);
    const role = await acl.roleFor(user.id, documentName);        // owner/editor/commenter/viewer
    if (!role) throw new Error('Forbidden');
    if (role === 'viewer' || role === 'commenter') connection.readOnly = true;   // server rejects edits
    return { user, role };
  },
  extensions: [
    new Database({
      fetch: async ({ documentName }) => (await db.oneOrNone('SELECT state FROM doc_snapshots WHERE doc_id=$1', [documentName]))?.state ?? null,
      store: async ({ documentName, state }) => {                 // debounced by Hocuspocus
        await db.none(`INSERT INTO doc_snapshots (doc_id, state, updated_at) VALUES ($1,$2,now())
                       ON CONFLICT (doc_id) DO UPDATE SET state=EXCLUDED.state, updated_at=now()`, [documentName, state]);
        await maybeCreateHistoryVersion(documentName, state);     // e.g., every 10 min of activity
      },
    }),
  ],
});
server.listen();
// Scale: route all connections for a doc to the same instance (consistent hashing on doc id at the LB),
// or use the Redis extension for cross-instance sync
```

### OT core idea (simplified transform for plain text insert/delete)
```ts
type Op = { type: 'ins'; pos: number; text: string } | { type: 'del'; pos: number; len: number };
// transform op `a` so it applies after `b` (b already applied) — tie-break on site id for equal positions
export function transform(a: Op, b: Op, aWinsTies: boolean): Op {
  if (b.type === 'ins') {
    if (a.pos > b.pos || (a.pos === b.pos && !aWinsTies)) return { ...a, pos: a.pos + b.text.length };
    return a;
  }
  // b is delete
  if (a.pos >= b.pos + b.len) return { ...a, pos: a.pos - b.len };
  if (a.type === 'ins') return a.pos <= b.pos ? a : { ...a, pos: b.pos };
  const start = Math.max(a.pos, b.pos), end = Math.min(a.pos + a.len, b.pos + b.len);   // overlapping deletes
  const overlap = Math.max(0, end - start);
  return { ...a, pos: Math.min(a.pos, b.pos), len: a.len - overlap };
}
```

### Version history API
```sql
CREATE TABLE doc_versions (doc_id TEXT, version_id BIGSERIAL, created_at TIMESTAMPTZ DEFAULT now(),
  authors TEXT[], name TEXT, snapshot_key TEXT, PRIMARY KEY (doc_id, version_id));
-- list: SELECT version_id, created_at, authors, name FROM doc_versions WHERE doc_id=$1 ORDER BY version_id DESC LIMIT 50;
-- restore: load snapshot → compute ops/updates from current → apply as a NEW change (history preserved)
```

### Mobile (React Native): WebView-hosted editor bridge
```tsx
<WebView source={{ uri: `https://docs.myapp.com/embed/${docId}?token=${shortLivedToken}` }}
  onMessage={(e) => handleEditorEvent(JSON.parse(e.nativeEvent.data))}    // title changes, word count, offline state
  injectedJavaScriptBeforeContentLoaded={`window.__PLATFORM__='rn';true;`}
  keyboardDisplayRequiresUserAction={false} hideKeyboardAccessoryView allowsBackForwardNavigationGestures={false} />
// Native shell handles share sheet, file picker, push deep links; the editor reuses the web collaboration stack
```

---

## ⚫ Interview Questions + Answers

**Q1: How do OT and CRDTs differ, and which would you pick?**
A1: OT represents edits as position-based operations and relies on a central server to order them and transform concurrent operations against each other so that intent is preserved. It's compact and well-proven (Google Docs), but needs a central authority and complex transform functions for rich-text structures. CRDTs assign unique IDs to elements so concurrent operations commute and merge deterministically on every replica without central transformation, which enables offline-first and peer-to-peer at the cost of metadata overhead and harder invariant enforcement. Pick OT for a centralized product with strict control; pick CRDTs (Yjs, Automerge) for offline-heavy or local-first apps and faster development with existing libraries.

**Q2: How do you scale collaboration servers?**
A2: Keep each document's live session on one authoritative server process, so ordering and merging happen in one place, by routing connections by document ID (consistent hashing at the load balancer or a session registry). Shard documents across many servers. Persist ops or updates to an append-only log and snapshot periodically, so a server can crash and another can reload the document quickly. Use pub/sub for cross-instance notifications, and rebalance hot documents. Presence is held in memory and is ephemeral.

**Q3: How does offline editing work?**
A3: The client persists document state and unsent changes locally (IndexedDB or SQLite) and keeps editing optimistically. On reconnect, CRDT clients exchange state vectors and send only the missing updates, which merge automatically. OT clients send buffered ops based on their last known revision, and the server transforms them against everything that happened meanwhile (the client also transforms incoming ops against its pending ones). The UI shows offline status, and long offline periods may produce surprising merges, so version history allows recovery.

**Q4: How do comments stay attached to the right text?**
A4: Anchor comments to positions that move with edits: relative positions tied to element IDs (CRDT), or marks or decorations in the document model that are transformed with each operation (OT). When text is inserted before the range, the anchor shifts. When the anchored text is edited, the range adapts, and if it's deleted entirely the comment becomes orphaned with the original quoted text retained. Comment threads live in a separate service with their own permissions and notifications.

**Q5: How do you enforce permissions in a real-time editor?**
A5: Authenticate the WebSocket connection with a short-lived token and look up the user's role for the document before joining the session. Enforce the role on every incoming message: viewers can't send edits, commenters can only send comment and suggestion ops, editors can edit. When permissions change (unshared or downgraded), push the change to the collaboration server to downgrade or close live sessions immediately. Serve snapshots and exports through authorized, short-lived URLs, and audit-log sharing changes and access.

---

## 🔷 Trade-offs
✅ OT: compact, central control, proven — ❌ complex transforms for rich text, central server required.
✅ CRDT: offline/P2P, simpler merging, libraries (Yjs) — ❌ metadata/tombstones, invariant enforcement, GC.
✅ Doc-pinned sessions: simple ordering — ❌ hot documents (100s of editors) concentrate load.
✅ WebView editor on mobile: reuse web stack — ❌ less native feel, keyboard/IME quirks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Operational Transformation | Transform concurrent ops | एक साथ के बदलाव रूपांतरित करना |
| CRDT | Auto-merging replicated data | अपने-आप मिलने वाला डेटा |
| Convergence | All replicas end identical | सब कॉपियाँ एक जैसी |
| Revision (rev) | Server version number of doc | document का version |
| Op log | Append-only list of changes | बदलावों की सूची |
| Snapshot | Full doc state at a point | किसी समय की पूरी स्थिति |
| Awareness / presence | Live cursors & users | live cursors |
| Relative position | Position tied to element IDs | id से जुड़ी जगह |
| Suggestion mode | Tracked changes | सुझाव वाले बदलाव |
| Sticky routing | Same doc → same server | एक doc एक सर्वर पर |

---

## ⚡ 3-Line Summary
**English:**
1. Clients apply edits optimistically and exchange ops (OT with server ordering + transforms) or updates (CRDT/Yjs merging) over WebSockets; one authoritative session per doc.
2. Presence is ephemeral with relative positions; persistence = op log + snapshots for fast load and version history; comments anchored to moving ranges.
3. Enforce ACLs on connect and per op, support offline via IndexedDB/state vectors, optimize large docs, and route by doc ID to scale.

**Hindi:**
1. Client बदलाव तुरंत local में, फिर OT (सर्वर क्रम + transform) या CRDT (Yjs) से WebSocket पर मेल; हर doc का एक session।
2. Cursors अस्थायी (relative positions); op log + snapshots से तेज़ load और history; comments खिसकते range से जुड़े।
3. हर connect और op पर permission, IndexedDB से offline, बड़े docs तेज़, doc id से routing।

---

## ➡️ Next Topic Suggestion
**P06. Search Autocomplete / Typeahead** — From editing to finding: suggestions on every keystroke within ~100 ms. Next: client-side debouncing, caching and accessibility, plus the backend prefix index, ranking and data pipeline.
