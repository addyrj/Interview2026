// Cache-aside read path: Redis (ElastiCache) in front of Postgres (RDS).
// npm i pg ioredis
const { Pool } = require("pg");
const Redis = require("ioredis");

const db = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }, // prefer loading the RDS CA bundle in production
  max: 10,
});
const redis = new Redis(process.env.REDIS_URL, { tls: {} }); // rediss:// + in-transit encryption

const TTL_SECONDS = 300;

async function getUser(id) {
  const key = `user:${id}`;

  const hit = await redis.get(key);
  if (hit) return JSON.parse(hit);

  const { rows } = await db.query("SELECT id, name, email FROM users WHERE id = $1", [id]);
  if (rows.length === 0) return null;

  // jitter avoids many keys expiring at the same moment
  const ttl = TTL_SECONDS + Math.floor(Math.random() * 60);
  await redis.set(key, JSON.stringify(rows[0]), "EX", ttl);
  return rows[0];
}

async function updateUser(id, name) {
  await db.query("UPDATE users SET name = $1 WHERE id = $2", [name, id]);
  await redis.del(`user:${id}`); // invalidate on write
}

module.exports = { getUser, updateUser };
