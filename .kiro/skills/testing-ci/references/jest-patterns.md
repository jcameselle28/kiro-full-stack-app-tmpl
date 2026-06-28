# Vitest / Jest Patterns (Web App on RDS)

Test business logic in isolation, the data layer against a **real local database**, and API routes through the app. Mock only auxiliary AWS SDK clients (S3, Secrets Manager).

## Setup

```typescript
// tests/setup.ts
import { mockClient } from "aws-sdk-client-mock";
import { S3Client } from "@aws-sdk/client-s3";
import { SecretsManagerClient } from "@aws-sdk/client-secrets-manager";

export const s3Mock = mockClient(S3Client);
export const secretsMock = mockClient(SecretsManagerClient);

beforeEach(() => {
  s3Mock.reset();
  secretsMock.reset();
});
```

## Service-Layer Unit Tests (no I/O)

```typescript
import { describe, it, expect } from "vitest";
import { InvoiceService } from "../src/services/invoice-service";

describe("InvoiceService", () => {
  const service = new InvoiceService();

  it("calculates total with discount", () => {
    const items = [{ price: 100, quantity: 2 }, { price: 50, quantity: 1 }];
    expect(service.calculateTotal(items, 10)).toBe(225); // (200 + 50) * 0.9
  });

  it("throws on empty items", () => {
    expect(() => service.calculateTotal([], 0)).toThrow("at least one item");
  });
});
```

## Repository Tests (real DB via Prisma)

```typescript
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient({ datasources: { db: { url: process.env.TEST_DATABASE_URL } } });

beforeEach(async () => {
  await prisma.$executeRaw`TRUNCATE TABLE accounts RESTART IDENTITY CASCADE`;
});

describe("AccountRepository", () => {
  it("creates and fetches an account", async () => {
    const repo = new AccountRepository(prisma);
    const created = await repo.create({ name: "Acme", email: "ops@acme.test" });
    const fetched = await repo.get(created.id);
    expect(fetched?.email).toBe("ops@acme.test");
  });

  it("enforces unique email", async () => {
    const repo = new AccountRepository(prisma);
    await repo.create({ name: "A", email: "dup@acme.test" });
    await expect(repo.create({ name: "B", email: "dup@acme.test" })).rejects.toThrow();
  });
});
```

## API Route Tests (supertest)

```typescript
import request from "supertest";
import { app } from "../src/app";

describe("POST /v1/accounts", () => {
  it("creates an account", async () => {
    const res = await request(app)
      .post("/v1/accounts")
      .send({ name: "Acme", email: "ops@acme.test" });
    expect(res.status).toBe(201);
    expect(res.body.email).toBe("ops@acme.test");
  });

  it("returns a validation error envelope", async () => {
    const res = await request(app).post("/v1/accounts").send({ name: "" });
    expect(res.status).toBe(422);
    expect(res.body.error.code).toBe("validation_error");
  });

  it("requires auth", async () => {
    const res = await request(app).get("/v1/accounts");
    expect(res.status).toBe(401);
  });
});
```

## Mocking Auxiliary AWS Clients

```typescript
import { PutObjectCommand } from "@aws-sdk/client-s3";
import { s3Mock } from "./setup";

it("requests a presigned upload URL", async () => {
  s3Mock.on(PutObjectCommand).resolves({});
  const url = await new StorageService("uploads").uploadUrl("docs/a.pdf");
  expect(url).toContain("uploads");
});
```

## Frontend Component Tests (React Testing Library)

```typescript
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AccountForm } from "../src/features/accounts/AccountForm";

it("shows a validation message for an invalid email", async () => {
  render(<AccountForm onSubmit={vi.fn()} />);
  await userEvent.type(screen.getByLabelText(/email/i), "not-an-email");
  await userEvent.click(screen.getByRole("button", { name: /save/i }));
  expect(await screen.findByText(/valid email/i)).toBeInTheDocument();
});
```

## Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",          // "jsdom" for component tests
    setupFiles: ["./tests/setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      include: ["src/**/*.ts", "src/**/*.tsx"],
      exclude: ["src/**/*.d.ts", "src/**/index.ts"],
      thresholds: { lines: 80, functions: 80, branches: 75 },
    },
  },
});
```
Provide `TEST_DATABASE_URL` (a local Postgres/MySQL via docker compose) in CI before running repository/API tests.
