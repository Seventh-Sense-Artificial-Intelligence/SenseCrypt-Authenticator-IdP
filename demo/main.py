import time
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from config import get_settings
from oidc import (
    generate_state, generate_nonce, generate_pkce_pair,
    build_authorize_url, exchange_code_for_tokens, fetch_userinfo,
)
import httpx

app = FastAPI(title="OIDC Demo Client")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# In-memory storage for pending auth flows (state -> {code_verifier, nonce, login_hint, created_at})
pending_auth: dict[str, dict] = {}

# Cleanup entries older than 10 minutes
def cleanup_stale():
    cutoff = time.time() - 600
    stale = [k for k, v in pending_auth.items() if v.get("created_at", 0) < cutoff]
    for k in stale:
        del pending_auth[k]

@app.get("/")
async def login_page(request: Request):
    settings = get_settings()
    return templates.TemplateResponse("login.html", {
        "request": request,
        "issuer_url": settings.OIDC_ISSUER_URL,
    })

@app.post("/login")
async def login(request: Request, email: str = Form("")):
    cleanup_stale()
    settings = get_settings()
    state = generate_state()
    nonce = generate_nonce()
    code_verifier, code_challenge = generate_pkce_pair()

    pending_auth[state] = {
        "code_verifier": code_verifier,
        "nonce": nonce,
        "login_hint": email,
        "created_at": time.time(),
    }

    authorize_url = build_authorize_url(
        issuer_url=settings.OIDC_ISSUER_URL,
        client_id=settings.CLIENT_ID,
        redirect_uri=settings.REDIRECT_URI,
        scope=settings.SCOPES,
        state=state,
        nonce=nonce,
        code_challenge=code_challenge,
        login_hint=email or None,
    )
    return RedirectResponse(authorize_url, status_code=302)

@app.get("/callback")
async def callback(request: Request):
    error = request.query_params.get("error")
    if error:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": error,
            "error_description": request.query_params.get("error_description", ""),
        })

    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code or not state:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "missing_params",
            "error_description": "Missing code or state parameter",
        })

    auth_data = pending_auth.pop(state, None)
    if not auth_data:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "invalid_state",
            "error_description": "Invalid or expired state parameter. Possible CSRF attack.",
        })

    settings = get_settings()

    try:
        tokens = await exchange_code_for_tokens(
            issuer_url=settings.OIDC_ISSUER_URL,
            code=code,
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            redirect_uri=settings.REDIRECT_URI,
            code_verifier=auth_data["code_verifier"],
        )
    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_detail = e.response.json().get("error_description", e.response.text)
        except Exception:
            error_detail = e.response.text
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "token_exchange_failed",
            "error_description": f"Token exchange failed: {error_detail}",
        })
    except httpx.RequestError as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "connection_error",
            "error_description": f"Could not connect to Identity Provider: {e}",
        })

    try:
        userinfo = await fetch_userinfo(
            issuer_url=settings.OIDC_ISSUER_URL,
            access_token=tokens.get("access_token", ""),
        )
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "userinfo_failed",
            "error_description": f"Failed to fetch user info: {e}",
        })

    return templates.TemplateResponse("logged_in.html", {
        "request": request,
        "userinfo": userinfo,
        "tokens": {
            "access_token": tokens.get("access_token", "")[:50] + "...",
            "id_token": tokens.get("id_token", "")[:50] + "...",
            "token_type": tokens.get("token_type", ""),
            "expires_in": tokens.get("expires_in", ""),
            "scope": tokens.get("scope", ""),
        },
    })

@app.get("/logout")
async def logout():
    return RedirectResponse("/", status_code=302)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
