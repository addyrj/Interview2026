// Node.js client for Cosmos DB. npm i @azure/cosmos
// Env: COSMOS_ENDPOINT, COSMOS_KEY (use DefaultAzureCredential + RBAC in production).
const { CosmosClient } = require("@azure/cosmos");

const client = new CosmosClient({
  endpoint: process.env.COSMOS_ENDPOINT,
  key: process.env.COSMOS_KEY,
});
const container = client.database("shop").container("orders");

async function main() {
  // Partition key value must match the /customerId path.
  const { resource } = await container.items.create({
    id: "o-1001",
    customerId: "c-42",
    total: 499,
  });
  console.log("created", resource.id);

  // Point read: cheapest operation (id + partition key).
  const { resource: got } = await container.item("o-1001", "c-42").read();
  console.log("read", got.total);

  // In-partition query: efficient. Cross-partition queries cost more RUs.
  const { resources } = await container.items
    .query({
      query: "SELECT * FROM c WHERE c.customerId = @c",
      parameters: [{ name: "@c", value: "c-42" }],
    })
    .fetchAll();
  console.log("orders for c-42:", resources.length);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
