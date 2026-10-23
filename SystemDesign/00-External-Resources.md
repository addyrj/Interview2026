# External Resources for System Design

This file lists the best free resources to go deeper on any topic in this guide.
Read the topic file here first → then use these links for real-world depth.

---

## 📺 YouTube Channels (Watch in this order)

### 1. ByteByteGo (Alex Xu) — ⭐ Best for system design visuals
Channel: **ByteByteGo** on YouTube
- System design fundamentals with animated diagrams
- Every major design problem (URL shortener, Twitter, YouTube, Uber)
- Matches "System Design Interview Vol 1 & 2" books

### 2. Gaurav Sen — ⭐ Best for distributed systems concepts
Channel: **Gaurav Sen** on YouTube
- Consistent hashing, load balancing, message queues
- Deep dives with clear whiteboard explanations
- Great for understanding WHY, not just WHAT

### 3. Tech Dummies (Narendra L) — Good for real-world design problems
Channel: **Tech Dummies Narendra L** on YouTube
- End-to-end design walkthroughs (WhatsApp, Instagram, Netflix)
- 45-minute mock interview style

### 4. Hussein Nasser — Best for networking and protocol depth
Channel: **Hussein Nasser** on YouTube
- HTTP/2, WebSockets, gRPC, proxies, TCP
- Great if networking topics feel shallow

### 5. Martin Kleppmann talks — Best for distributed systems depth
Search: **"Martin Kleppmann distributed systems"** on YouTube
- Author of "Designing Data-Intensive Applications"
- Consensus, CRDTs, event sourcing — advanced

---

## 📚 Articles / Websites

### System Design Fundamentals
- **High Scalability** → highscalability.com
  Real architecture case studies: how Netflix, WhatsApp, Instagram actually work
- **ByteByteGo Newsletter** → blog.bytebytego.com
  Weekly deep dives, free tier available
- **The System Design Handbook** → systemdesignhandbook.com
  Structured guides on key problems (mentioned in your own notes)
- **Hello Interview** → hellointerview.com/learn/system-design
  Interview-focused, practical framework (also in your notes)

### Database & Distributed Systems
- **Use The Index, Luke** → use-the-index-luke.com
  Deep SQL indexing guide — best free resource for DB indexes
- **Martin Fowler's Blog** → martinfowler.com
  Patterns: Saga, CQRS, Event Sourcing, Strangler Fig (original source)
- **Designing Data-Intensive Applications** (DDIA) — most recommended book
  Read chapter summaries free at: ddia.rocks

### Company Engineering Blogs (Real production systems)
- **Netflix Tech Blog** → netflixtechblog.com
- **Uber Engineering** → eng.uber.com
- **Airbnb Engineering** → medium.com/airbnb-engineering
- **Meta Engineering** → engineering.fb.com
- **AWS Architecture Blog** → aws.amazon.com/blogs/architecture

### Frontend System Design
- **web.dev** → web.dev (Google's guide for web performance)
- **Frontend System Design by Greatfrontend** → greatfrontend.com/system-design

### Mobile System Design
- **React Native Performance** → reactnative.dev/docs/performance
- **Expo Documentation** → docs.expo.dev

### AI Engineering
- **LangChain Docs** → python.langchain.com
- **LlamaIndex Docs** → docs.llamaindex.ai
- **Anthropic Cookbook** → github.com/anthropics/anthropic-cookbook

---

## 🐙 GitHub Repositories

### Must-read (free, comprehensive)
1. **System Design Primer** — donnemartin
   github.com/donnemartin/system-design-primer
   ⭐ 280k+ stars — the most complete free system design resource
   Covers every topic with diagrams, examples, and interview prep

2. **System Design 101** — ByteByteGo
   github.com/ByteByteGoHq/system-design-101
   ⭐ 65k+ stars — visual, diagram-heavy explanations

3. **Awesome System Design Resources** — ashishps1
   github.com/ashishps1/awesome-system-design-resources
   Curated list of the best videos, articles, books per topic

4. **Awesome Scalability** — binhnguyennus
   github.com/binhnguyennus/awesome-scalability
   Real architecture patterns from production systems

### For distributed systems (advanced)
5. **Patterns of Distributed Systems** — unmesh-joshi
   github.com/unmesh-joshi/patterns-of-distributed-systems
   Every distributed pattern with code: Paxos, Raft, 2PC, etc.

---

## 📖 Books (if you want to go deep)

| Book | Best for | Priority |
|---|---|---|
| Designing Data-Intensive Applications (DDIA) — Martin Kleppmann | Distributed systems, databases | ⭐⭐⭐⭐⭐ |
| System Design Interview Vol 1 & 2 — Alex Xu | Interview prep, design problems | ⭐⭐⭐⭐⭐ |
| Building Microservices — Sam Newman | Microservices in depth | ⭐⭐⭐⭐ |
| Clean Architecture — Robert Martin | Service/module design | ⭐⭐⭐ |
| The Phoenix Project | DevOps culture (easy read) | ⭐⭐⭐ |

---

## 🗺️ Suggested Study Path per Role

### Backend / Full-stack (5yr+)
```
Week 1: DDIA chapters 1-4 (data models, storage, encoding)
Week 2: ByteByteGo — URL shortener, Twitter, WhatsApp
Week 3: Gaurav Sen — consistent hashing, load balancing
Week 4: Mock designs (2/week, timed 45 min each)
```

### Frontend (5yr+)
```
ByteByteGo — CDN, caching, rendering strategies
greatfrontend.com system design section
web.dev performance guides
Mock: design Google Docs editor, Facebook feed, YouTube player
```

### Mobile (React Native, 5yr+)
```
Expo docs — background tasks, offline storage
ByteByteGo — notification systems, offline sync
Mock: design WhatsApp mobile, Uber rider app, Instagram reels
```

### AI Engineering
```
Anthropic Cookbook — RAG, tool use, agents
LangChain docs — chains, retrieval, agents
Mock: design a RAG chatbot, an AI coding assistant
```

---

## 🔗 Topic → Best Resource Quick Map

| Topic from guide | Best deep-dive resource |
|---|---|
| Consistent Hashing | Gaurav Sen YouTube |
| Kafka / Messaging | confluent.io/learn/kafka |
| CAP Theorem | Martin Kleppmann DDIA ch.9 |
| Redis internals | redis.io/docs |
| Kubernetes | kubernetes.io/docs/tutorials |
| Database indexes | use-the-index-luke.com |
| ETL/ELT / dbt | docs.getdbt.com |
| OAuth / OIDC | auth0.com/docs |
| Microservices patterns | martinfowler.com/articles/microservices |
| React performance | web.dev/react |
| React Native offline | expo.dev docs |
| LLM / RAG | Anthropic Cookbook GitHub |
