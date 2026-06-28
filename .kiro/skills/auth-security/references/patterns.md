# Auth Patterns — Deep Dive

Supporting reference for the `auth-security` skill.

## OIDC Authorization Code + PKCE (browser apps)

Use the authorization-code flow with PKCE — never the implicit flow.

1. App generates a `code_verifier` (random) and `code_challenge = S256(code_verifier)`
2. Redirect the user to the IdP (Cognito) `/authorize` with `response_type=code`, `code_challenge`, `state`, and `nonce`
3. User authenticates at the IdP; IdP redirects back with `code` + `state`
4. **Backend** exchanges `code` + `code_verifier` at `/token` for access/ID/refresh tokens (the exchange happens server-side so the refresh token never touches the browser)
5. Backend sets tokens in httpOnly cookies and redirects into the app

Validate `state` (CSRF) and `nonce` (replay) on return. Reject mismatches.

## Refresh-Token Rotation With Reuse Detection

- Issue a new refresh token on every refresh; invalidate the previous one
- Track a token "family" id. If a **already-used** refresh token is presented again, assume theft → revoke the entire family and force re-login
- Store refresh-token state server-side (hashed) so revocation is real, not just expiry-based
- Keep access tokens short (5–15 min) so revocation latency is bounded

```
login            -> RT1 (family F)
use RT1          -> RT2 (family F), RT1 invalidated
use RT1 again    -> REUSE DETECTED -> revoke family F
```

## Secure Cookie Configuration

| Attribute | Value | Why |
|---|---|---|
| `HttpOnly` | yes | JS can't read it → XSS can't steal it |
| `Secure` | yes | HTTPS only |
| `SameSite` | `Lax` (default) / `Strict` (sensitive) | CSRF mitigation |
| `Path` | `/` or scoped | limit exposure |
| `Domain` | exact app domain | avoid over-broad sharing |
| `Max-Age` | short for access, longer for refresh | bound lifetime |

For `SameSite=Lax` flows that still accept cross-site POSTs, add an explicit CSRF token (double-submit or synchronizer pattern).

## Password Reset Flow (secure)

1. User requests reset by email
2. Generate a high-entropy, single-use token; store only its **hash** with a short expiry (e.g., 30 min)
3. Email a link containing the raw token
4. Always respond with the same generic message whether or not the email exists (no enumeration)
5. On submit: look up by hash, check expiry/unused, set new password (Argon2id), invalidate the token and all existing sessions
6. Notify the user by email that their password changed

Email verification follows the same single-use, hashed, expiring-token pattern.

## Multi-Tenant Authorization

- Every tenant-scoped request resolves a `tenant_id` from the authenticated subject — never from a client-supplied body/param alone
- Verify the subject is a member of the target tenant before any data access
- Scope all queries by `tenant_id`; back it with Postgres Row-Level Security as defense in depth (see `database-rds`)
- For cross-tenant admin, require a distinct elevated role and log every access

## IDOR / Object-Level Authorization

A user being authenticated does not mean they own the object. For every resource fetch/mutation:
```
load resource by id
assert resource.owner_id == subject.id  (or tenant/role check)
otherwise 404 (preferred) or 403
```
Prefer returning **404** for objects the subject may not even know exist, to avoid leaking existence.

## MFA

- TOTP (authenticator apps) as a baseline; **WebAuthn/passkeys** for phishing-resistant MFA
- Require MFA for admin/privileged roles and sensitive operations (step-up auth)
- Provide recovery codes; store only their hashes
- Cognito supports TOTP and SMS MFA natively — prefer TOTP/WebAuthn over SMS

## Rate Limiting & Lockout

- Rate-limit auth endpoints per IP and per account
- Exponential backoff or temporary lockout after repeated failures
- Pair app-level limits with **WAF rate-based rules** on `/login`, `/signup`, `/reset`
- Log auth failures with correlation ids (never log credentials or tokens)

## Logout & Revocation

- Clear cookies and invalidate the server-side session/refresh family
- For Cognito hosted UI, also hit the IdP logout endpoint to end the IdP session
- Provide "log out everywhere" by revoking all refresh families for the user

## What NOT to Do
- Don't store access/refresh tokens in `localStorage` or non-httpOnly cookies
- Don't put authorization decisions only in the frontend
- Don't trust roles/permissions from the request body
- Don't use the implicit OAuth flow
- Don't return different messages for "no such user" vs "wrong password"
- Don't log tokens, passwords, reset tokens, or full session ids
