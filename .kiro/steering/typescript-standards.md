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

## AWS-Specific TypeScript
- Use AWS SDK v3 with modular imports (never import entire SDK)
- Create typed clients with middleware: `const client = new DynamoDBClient({})`
- Use `DynamoDBDocumentClient` for simplified DynamoDB operations
- Handle SDK errors with `try/catch` checking `error.name` or `error.$metadata`
- Use `@aws-lambda-powertools/logger`, `@aws-lambda-powertools/tracer`

## Testing
- Use Vitest (preferred) or Jest as test framework
- Use `aws-sdk-client-mock` for mocking AWS SDK v3 clients
- Structure: `describe` → `it` with clear behavior descriptions
- Mock at the boundary (SDK clients), test business logic in isolation
- Target 80%+ coverage on business logic
