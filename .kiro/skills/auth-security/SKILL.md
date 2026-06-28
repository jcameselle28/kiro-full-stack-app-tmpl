---
name: auth-security
description: This skill provides authentication and authorization patterns for web apps on AWS — Amazon Cognito, custom JWT, and server sessions; token handling, refresh rotation, RBAC/ABAC, route protection on frontend and backend, OWASP Top 10 mitigations, and WAF tuning for auth endpoints. Covers Python (FastAPI) and TypeScript (Next.js/Express). Triggers on requests about auth, login, signup, sessions, JWT, tokens, permissions, roles, OAuth, or OIDC.
---

# Auth & Security Skill

How to implement authentication and authorization for web applications on AWS. This skill is the **how-to depth** for auth; the broad, always-on rules (secrets, input validation, parameterized queries, TLS, secure headers) live in `security-guardrails.md` and are assumed here.

## Activation Keywords
- auth, authn, authz, authentication, authorization
- login, signup, logout, password, MFA, session
- JWT, token, access token, refresh token, bearer
- OAuth, OIDC, Cognito, SSO, role, permission, RBAC

## Choosing an Auth Strategy

| Option | Use when | Notes |
|---|---|---|
| **Amazon Cognito** (default) | You want managed user pools, hosted UI, MFA, social/SSO, OIDC | Least code to own; integrates with ALB and API auth. Recommended starting point. |
| **Custom JWT** | You need full control, custom claims, or a non-Cognito IdP | You own token issuance, rotation, revocation, and storage. More surface area. |
| **Server sessions** | Classic server-rendered app, single backend | Opaque session id in an httpOnly cookie; state in RDS/ElastiCache. Simple revocation. |

Record the chosen strategy in `project-config.md`. Don't mix strategies for the same surface.

## Token Handling (Cognito / JWT)
- **Short-lived access tokens** (5–15 min) + **refresh tokens** with rotation
- Store tokens in **httpOnly, Secure, SameSite cookies** for browser apps — not `localStorage` (XSS-exfiltratable)
- Rotate refresh tokens on every use; detect reuse of a rotated token → revoke the family
- Always validate on the backend: signature (against the IdP's JWKS), `iss`, `aud`, `exp`, `nbf`
- Cache JWKS and refresh on `kid` miss; never skip signature verification
- Keep tokens out of URLs, logs, and error messages

## Session Management (cookie sessions)
- Opaque, high-entropy session id; server-side session store (RDS/ElastiCache)
- Cookie flags: `HttpOnly`, `Secure`, `SameSite=Lax` (or `Strict` for sensitive apps)
- Regenerate the session id on login and privilege change (prevents fixation)
- Idle + absolute timeouts; server-side invalidation on logout
- Bind sensitive sessions to additional signals where appropriate

## Passwords & Credentials
- Never roll your own hashing — prefer Cognito. If self-managed, use **Argon2id** (or bcrypt) with per-user salt
- Enforce length-first password policy; check against known-breached lists
- Offer **MFA** (TOTP/WebAuthn); require it for admin roles
- Rate-limit and lock out on repeated failures; use generic error messages ("invalid credentials") to avoid user enumeration
- Secure, expiring, single-use tokens for password reset and email verification

## Authorization (RBAC / ABAC)
- **Authenticate once, authorize on every request** — never trust a client-supplied role
- Default **RBAC**: roles carried as verified token claims or looked up server-side; deny by default
- Use **ABAC** (attributes: ownership, tenant, resource state) when row-level/ownership rules matter
- Enforce authorization in the **backend service layer**, not just at the route or in the UI
- For multi-tenant apps, scope every query by `tenant_id` and verify the subject belongs to the tenant (pairs with `database-rds` RLS)
- Frontend route guards are **UX only** — they hide UI, they do not secure data

## Frontend Integration
- Protect routes with a guard that checks auth state, but treat the API as the real gate
- Keep tokens in httpOnly cookies; let the browser send them — the JS never reads them
- Handle 401 (re-auth) vs 403 (insufficient permission) distinctly in the UI
- Refresh access tokens silently via a backend endpoint; on refresh failure, route to login
- Never embed secrets or client secrets in frontend bundles

## AWS Integration
- **Cognito + ALB**: the ALB can authenticate users against a Cognito user pool / OIDC IdP before traffic reaches EC2
- **API authorization**: validate Cognito JWTs in the app, or use an ALB listener auth rule
- **WAF on auth endpoints**: rate-based rules on `/login`, `/signup`, `/reset`; managed rule groups for common attacks; consider bot control / account-takeover prevention on login
- Keep IdP and signing config/secrets in Secrets Manager / SSM

## OWASP Top 10 — Practical Mitigations
- **Broken Access Control**: deny by default; server-side checks; verify object ownership (no IDOR)
- **Cryptographic Failures**: TLS everywhere; hash passwords with Argon2id; encrypt sensitive data at rest
- **Injection**: parameterized queries / ORM bindings (see `security-guardrails.md`)
- **Identification & Auth Failures**: MFA, rotation, lockout, secure session lifecycle
- **SSRF / Security Misconfig**: validate outbound URLs; least-privilege IAM; no verbose errors to clients
- **Vulnerable Components**: pin and scan dependencies in CI

## Code Examples

### Verify a Cognito JWT (Python / FastAPI)
```python
from fastapi import Depends, HTTPException, Request
from jose import jwt
import httpx

JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{POOL_ID}/.well-known/jwks.json"

async def current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "not authenticated")
    jwks = await get_jwks_cached(JWKS_URL)
    try:
        claims = jwt.decode(
            token, jwks, algorithms=["RS256"],
            audience=APP_CLIENT_ID, issuer=ISSUER,
        )
    except Exception:
        raise HTTPException(401, "invalid token")
    return claims

def require_role(role: str):
    def checker(user: dict = Depends(current_user)) -> dict:
        if role not in user.get("cognito:groups", []):
            raise HTTPException(403, "forbidden")
        return user
    return checker
```

### Auth-aware route guard + 401/403 handling (TypeScript / Next.js)
```ts
// middleware.ts — UX gate; the API still enforces authorization
import { NextResponse, type NextRequest } from "next/server";

export function middleware(req: NextRequest) {
  const hasSession = req.cookies.has("access_token");
  if (!hasSession && req.nextUrl.pathname.startsWith("/app")) {
    return NextResponse.redirect(new URL("/login", req.url));
  }
  return NextResponse.next();
}
export const config = { matcher: ["/app/:path*"] };
```

```ts
// lib/api/client.ts — distinguish re-auth from permission errors
if (res.status === 401) { await tryRefreshOrRedirect(); }
if (res.status === 403) { throw new ForbiddenError(); } // show "no access", don't loop login
```

For deeper material (OIDC authorization-code + PKCE flow, refresh-token rotation with reuse detection, secure cookie config, password reset flow, multi-tenant authorization), see `references/patterns.md`.
