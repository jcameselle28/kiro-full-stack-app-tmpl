---
inclusion: fileMatch
fileMatchPattern: "**/*.py,**/*.ts,**/*.tsx"
---

# API Conventions

The contract between frontend and backend. Apply these to HTTP APIs unless a project documents an explicit exception.

## Style
- RESTful resource design by default; reserve RPC-style endpoints for genuine actions (`/orders/{id}/cancel`)
- Resource names are **plural nouns**, lowercase, kebab-or-flat (`/ledger-entries`, `/accounts`)
- Nest only one level deep (`/accounts/{id}/transactions`); beyond that, use query filters
- No verbs in resource paths — the HTTP method is the verb

## Methods & Status Codes
- `GET` read · `POST` create · `PUT` full replace · `PATCH` partial update · `DELETE` remove
- Success: `200` OK, `201` Created (+ `Location`), `204` No Content
- Client errors: `400` validation, `401` unauthenticated, `403` unauthorized, `404` not found, `409` conflict, `422` semantic validation, `429` rate limited
- Server errors: `500` (never leak internals), `503` when dependencies are down
- `GET`/`PUT`/`DELETE` are idempotent; support an idempotency key for `POST` where retries are likely

## Request & Response Shape
- JSON only; `Content-Type: application/json`; UTF-8
- Field names: **`snake_case`** on the wire (consistent regardless of backend language)
- Timestamps: ISO-8601 UTC (`2026-01-15T09:30:00Z`)
- Money: integer minor units or decimal strings — never floats
- IDs: string UUIDs in payloads
- Return the created/updated resource in the body (except `204`)

## Errors (consistent envelope)
```json
{
  "error": {
    "code": "validation_error",
    "message": "Human-readable summary",
    "details": [{ "field": "email", "issue": "must be a valid email" }],
    "request_id": "req_01H...."
  }
}
```
- Stable, machine-readable `code`; `message` for humans (no stack traces or internals)
- Always include a `request_id` that correlates to logs

## Pagination, Filtering, Sorting
- Default to **cursor (keyset) pagination** for large collections:
  - Request: `?limit=50&cursor=<opaque>`
  - Response: `{ "data": [...], "page": { "next_cursor": "...", "has_more": true } }`
- Offset pagination only for small, bounded lists
- Filtering via explicit query params (`?status=active`); sorting via `?sort=-created_at`
- Cap and document `limit`; reject oversized values with `400`

## Versioning
- Version in the path: `/v1/...`
- Additive changes (new optional fields, new endpoints) are non-breaking and don't bump the version
- Breaking changes go to a new version; support the old one through a deprecation window
- Never repurpose or change the type of an existing field

## Validation & Security
- Validate every request at the boundary (Pydantic / Zod); reject unknown fields where it matters
- Authorize on the server for every request — see `auth-security`
- Set CORS explicitly for browser clients; never reflect arbitrary origins
- Rate-limit public endpoints; surface `429` with `Retry-After`
- Document endpoints with **OpenAPI**; generate client types from the schema to keep frontend and backend in sync

## Conventions to Keep
- One resource = one canonical representation across endpoints
- Empty collections return `200` with `[]`, not `404`
- Booleans are named affirmatively (`is_active`, not `disabled`)
- Don't break the wire format to match an internal model — map at the boundary
