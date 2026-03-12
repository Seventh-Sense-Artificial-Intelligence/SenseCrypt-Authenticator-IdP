# How to Demo

This guide walks through the Sensecrypt Authenticator OIDC demo end-to-end.

## Prerequisites

- PostgreSQL running locally
- Node.js and Python 3 installed
- Ports 8000 and 9000 available

## 1. Start the demo

From the project root:

```bash
./run-demo.sh
```

This will:
- Reset the database and run migrations
- Build the frontend
- Seed a demo admin user and a pre-configured OAuth application
- Start the IdP on **http://localhost:8000** and the demo client app on **http://localhost:9000**

Once running, you'll see credentials printed in the terminal:

```
IdP admin:  demo-idp@seventhsense.ai / Demo1234!
IdP login:  http://localhost:8000
```

---

## 2. Log in to the IdP admin portal

1. Open **http://localhost:8000** in your browser.
2. Sign in with **demo-idp@seventhsense.ai** / **Demo1234!**
3. Navigate to **Applications** in the left sidebar.

You'll see the pre-configured **OIDC Demo Client** application. Click on it to view its settings.

### What to point out

- **Client ID** — the public identifier the demo app uses to identify itself to the IdP.
- **Application Type** — set to *Web* (server-side app that can store secrets).
- **Redirect URIs** — set to `http://localhost:9000/callback`. After login, the IdP will redirect the user back to this exact URL.
- **Allowed Scopes** — OpenID, Profile, and Email. These control what user information the demo app can request.
- **Grant Types** — Authorization Code and Refresh Token. The standard secure login flow.
- **Token Endpoint Auth Method** — Client Secret (POST). The demo app sends its secret in the request body when exchanging codes for tokens.

This is the trust relationship: the IdP knows about this application and will only redirect authenticated users back to its registered callback URL.

---

## 3. Log in via the demo client app

Now switch to the external application that will use the IdP to authenticate users.

1. Open **http://localhost:9000** in a new tab.
2. Enter an email address (e.g. `demo-idp@seventhsense.ai`) and click **Login with Identity Provider**.

### What happens behind the scenes

The demo app redirects the browser to the IdP's `/authorize` endpoint with:
- its Client ID
- the registered redirect URI
- a PKCE code challenge (for extra security)
- the requested scopes (openid, profile, email)

### 3a. The IdP login page

The browser lands on the IdP's sign-in page showing:
- The name of the requesting application ("OIDC Demo Client")
- The user's email
- The permissions being requested
- A QR code for authentication

**In demo mode:** click the QR code to instantly authenticate. In production, a user would scan this QR code with the Sensecrypt Authenticator mobile app to sign the challenge with their certificate.

### 3b. Redirect back to the demo app

After authentication:
1. The IdP creates a one-time authorization code.
2. The browser is redirected back to `http://localhost:9000/callback?code=...&state=...`
3. The demo app's backend exchanges the code for tokens by calling the IdP's `/token` endpoint (server-to-server, using its Client ID and Client Secret).
4. The demo app calls the IdP's `/userinfo` endpoint with the access token to get the user's profile.

### 3c. The logged-in page

The demo app displays:
- **User Info** — the user's subject ID, email, and name as returned by the IdP.
- **Tokens Received** — the access token, ID token, token type, expiration, and granted scopes.

This confirms the full OIDC Authorization Code flow completed successfully: the external app authenticated the user via the IdP without ever seeing the user's credentials.

---

## Summary of the flow

```
Demo App (localhost:9000)          IdP (localhost:8000)
        |                                  |
        |-- user clicks "Login" ---------->|
        |   (redirect to /authorize)       |
        |                                  |
        |                  IdP shows QR login page
        |                  User clicks QR code (demo)
        |                                  |
        |<-- redirect to /callback --------|
        |    (with authorization code)     |
        |                                  |
        |-- POST /token ------------------>|
        |   (exchange code for tokens)     |
        |<-- access_token, id_token -------|
        |                                  |
        |-- GET /userinfo ---------------->|
        |<-- user profile data ------------|
        |                                  |
        |   Demo app shows logged-in page  |
```
