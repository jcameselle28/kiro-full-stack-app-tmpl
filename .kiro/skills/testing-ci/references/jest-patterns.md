# Jest/Vitest Patterns for AWS

## Setup with aws-sdk-client-mock

```typescript
// tests/setup.ts
import { mockClient } from "aws-sdk-client-mock";
import { DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";
import { S3Client } from "@aws-sdk/client-s3";

export const ddbMock = mockClient(DynamoDBDocumentClient);
export const s3Mock = mockClient(S3Client);

beforeEach(() => {
  ddbMock.reset();
  s3Mock.reset();
});
```

## Testing Lambda Handlers

```typescript
import { handler } from "../src/handlers/order";
import { ddbMock } from "./setup";
import { PutCommand, GetCommand } from "@aws-sdk/lib-dynamodb";

describe("Order Handler", () => {
  it("creates an order successfully", async () => {
    ddbMock.on(PutCommand).resolves({});

    const event = {
      body: JSON.stringify({ productId: "prod-123", quantity: 2 }),
      requestContext: { authorizer: { claims: { sub: "user-456" } } },
    };

    const response = await handler(event as any, {} as any);

    expect(response.statusCode).toBe(201);
    expect(JSON.parse(response.body)).toHaveProperty("orderId");
  });

  it("returns 400 on invalid input", async () => {
    const event = { body: JSON.stringify({}) };

    const response = await handler(event as any, {} as any);

    expect(response.statusCode).toBe(400);
  });

  it("returns 500 when DynamoDB fails", async () => {
    ddbMock.on(PutCommand).rejects(new Error("Service unavailable"));

    const event = {
      body: JSON.stringify({ productId: "prod-123", quantity: 1 }),
      requestContext: { authorizer: { claims: { sub: "user-456" } } },
    };

    const response = await handler(event as any, {} as any);

    expect(response.statusCode).toBe(500);
  });
});
```

## Testing Service Layer

```typescript
import { OrderService } from "../src/services/order-service";

describe("OrderService", () => {
  const service = new OrderService();

  describe("calculateTotal", () => {
    it("calculates total with discount", () => {
      const items = [
        { price: 100, quantity: 2 },
        { price: 50, quantity: 1 },
      ];

      const total = service.calculateTotal(items, 10);

      expect(total).toBe(225); // (200 + 50) * 0.9
    });

    it("throws on empty items", () => {
      expect(() => service.calculateTotal([], 0)).toThrow("at least one item");
    });
  });
});
```

## Mocking Specific SDK Responses

```typescript
import { GetCommand } from "@aws-sdk/lib-dynamodb";
import { GetObjectCommand } from "@aws-sdk/client-s3";
import { sdkStreamMixin } from "@smithy/util-stream";
import { Readable } from "stream";

// DynamoDB - item found
ddbMock.on(GetCommand, { TableName: "orders", Key: { PK: "ORDER#123" } }).resolves({
  Item: { PK: "ORDER#123", status: "completed", total: 99.99 },
});

// DynamoDB - item not found
ddbMock.on(GetCommand, { TableName: "orders", Key: { PK: "ORDER#999" } }).resolves({
  Item: undefined,
});

// S3 - file content
const stream = sdkStreamMixin(Readable.from([Buffer.from('{"key": "value"}')]));
s3Mock.on(GetObjectCommand).resolves({ Body: stream });
```

## CDK Testing with Assertions

```typescript
import * as cdk from "aws-cdk-lib";
import { Template, Match } from "aws-cdk-lib/assertions";
import { MyStack } from "../lib/my-stack";

describe("MyStack", () => {
  const app = new cdk.App();
  const stack = new MyStack(app, "TestStack");
  const template = Template.fromStack(stack);

  it("creates a DynamoDB table with PAY_PER_REQUEST", () => {
    template.hasResourceProperties("AWS::DynamoDB::Table", {
      BillingMode: "PAY_PER_REQUEST",
      SSESpecification: { SSEEnabled: true },
    });
  });

  it("creates a Lambda with X-Ray tracing", () => {
    template.hasResourceProperties("AWS::Lambda::Function", {
      TracingConfig: { Mode: "Active" },
      Timeout: Match.anyValue(),
    });
  });

  it("has no public S3 buckets", () => {
    template.hasResourceProperties("AWS::S3::Bucket", {
      PublicAccessBlockConfiguration: {
        BlockPublicAcls: true,
        BlockPublicPolicy: true,
        IgnorePublicAcls: true,
        RestrictPublicBuckets: true,
      },
    });
  });
});
```

## Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    setupFiles: ["./tests/setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      include: ["src/**/*.ts"],
      exclude: ["src/**/*.d.ts", "src/**/index.ts"],
      thresholds: { lines: 80, functions: 80, branches: 75 },
    },
  },
});
```
