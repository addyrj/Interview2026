import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand, GetCommand } from "@aws-sdk/lib-dynamodb";
import { randomUUID } from "node:crypto";

// Created once per execution environment (reused on warm invocations)
const ddb = DynamoDBDocumentClient.from(new DynamoDBClient({}));
const TABLE = process.env.TABLE_NAME;

const json = (statusCode, body) => ({
  statusCode,
  headers: { "content-type": "application/json" },
  body: JSON.stringify(body),
});

export const handler = async (event) => {
  // HTTP API payload format 2.0
  const route = event.routeKey;

  if (route === "POST /items") {
    let data;
    try {
      data = JSON.parse(event.body ?? "{}");
    } catch {
      return json(400, { error: "invalid JSON" });
    }
    const item = { id: randomUUID(), ...data, createdAt: new Date().toISOString() };
    await ddb.send(
      new PutCommand({
        TableName: TABLE,
        Item: item,
        ConditionExpression: "attribute_not_exists(id)",
      })
    );
    return json(201, item);
  }

  if (route === "GET /items/{id}") {
    const res = await ddb.send(
      new GetCommand({ TableName: TABLE, Key: { id: event.pathParameters.id } })
    );
    return res.Item ? json(200, res.Item) : json(404, { error: "not found" });
  }

  return json(404, { error: "no route" });
};
