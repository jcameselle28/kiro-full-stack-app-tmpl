---
inclusion: fileMatch
fileMatchPattern: "**/*.ts,**/*.tsx"
---

# TypeScript Coding Standards

## Compiler Settings
- Strict mode always (`"strict": true` in tsconfig)
- No implicit any (`"noImplicitAny": true`)
- Target ES2022+ for modern features
- Module resolution: `bundler` or `node16`

## Formatting & Style
- Use ESLint + Prettier for linting and formatting
- Line length: 120 characters max
- Use single quotes for strings
- Semicolons: always
- Trailing commas: always (ES5+)

## Type System
- Prefer `interface` over `type` for object shapes (extendable)
- Use `type` for unions, intersections, and mapped types
- Avoid `any` — use `unknown` when type is truly unknown
- Use generics for reusable utilities
- Export types alongside their implementations
- Use `as const` for literal types and enums alternatives

## Error Handling
- Use typed error classes extending `Error`
- Never catch without handling or re-throwing
- Use Result/Either patterns for expected failures
- Validate external input at boundaries (Zod, io-ts)

## Naming Conventions
- `camelCase` for variables, functions, methods
- `PascalCase` for classes, interfaces, types, enums
- `UPPER_SNAKE_CASE` for constants
- Prefix interfaces with `I` only if team convention requires it (prefer no prefix)
- File names: `kebab-case.ts` for modules, `PascalCase.ts` for classes

## Project Structure
- Barrel exports (`index.ts`) for public API of each module
- Co-locate tests with source: `handler.ts` + `handler.test.ts`
- Separate `src/` from `infrastructure/` (app code vs IaC)
- Use path aliases in tsconfig for clean imports

## Web & AWS Integration (EC2 / RDS)
- Use a Node web framework (Express/Fastify/NestJS) behind the ALB
- Expose dedicated health and readiness endpoints for ALB target group checks
- Access RDS through an ORM/query builder (Prisma/TypeORM) with a managed connection pool; never open a connection per request
- Manage schema changes with migrations (Prisma Migrate / TypeORM migrations) checked into the repo
- Always use parameterized queries / ORM bindings — never string-interpolate SQL
- Use AWS SDK v3 with modular imports (never import the entire SDK)
- Use the default credential provider chain (EC2 instance profile) — never hardcode credentials
- Load secrets and config from Secrets Manager / SSM Parameter Store, not from committed files
- Handle SDK errors with `try/catch` checking `error.name` or `error.$metadata`

## Testing
- Use Vitest (preferred) or Jest as test framework
- Run integration tests against a real local database (Docker Postgres/MySQL); use `aws-sdk-client-mock` for auxiliary AWS service clients (S3, Secrets Manager)
- Structure: `describe` → `it` with clear behavior descriptions
- Test business logic in isolation; mock at the boundary
- Target 80%+ coverage on business logic
