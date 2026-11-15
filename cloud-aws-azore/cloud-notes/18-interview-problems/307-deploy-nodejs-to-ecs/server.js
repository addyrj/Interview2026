const http = require("node:http");

const port = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "content-type": "application/json" });
    return res.end(JSON.stringify({ status: "ok" }));
  }
  res.writeHead(200, { "content-type": "application/json" });
  res.end(JSON.stringify({ message: "hello from ECS", host: process.env.HOSTNAME }));
});

server.listen(port, () => console.log(`listening on ${port}`));

// ECS sends SIGTERM on deploy/scale-in; stop accepting and drain within stopTimeout
process.on("SIGTERM", () => {
  console.log("SIGTERM, shutting down");
  server.close(() => process.exit(0));
});
