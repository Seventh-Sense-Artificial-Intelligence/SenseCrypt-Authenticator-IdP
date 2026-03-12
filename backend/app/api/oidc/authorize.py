from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.config import get_settings
from app.services.product.application_service import get_application_by_client_id
from app.services.oidc.challenge_service import (
    create_challenge,
    build_qr_data,
    generate_qr_svg,
)
from app.services.oidc.templates import render_qr_login_page, render_email_page

router = APIRouter()


def _error_page(message: str) -> HTMLResponse:
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - Sensecrypt</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #131313;
            color: #e0e0e0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .error-box {{
            background-color: #1e1e1e;
            border-radius: 12px;
            padding: 40px;
            max-width: 420px;
            text-align: center;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
        }}
        h1 {{ color: #B3231D; font-size: 20px; margin-bottom: 16px; }}
        p {{ color: #b0b0b0; font-size: 14px; line-height: 1.5; }}
    </style>
</head>
<body>
    <div class="error-box">
        <h1>Authorization Error</h1>
        <p>{message}</p>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html, status_code=400)


@router.get("/authorize", response_class=HTMLResponse)
async def authorize_get(
    response_type: str = Query(default="code"),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    scope: str = Query(default="openid"),
    state: str | None = Query(default=None),
    nonce: str | None = Query(default=None),
    code_challenge: str | None = Query(default=None),
    code_challenge_method: str | None = Query(default=None),
    login_hint: str | None = Query(default=None),
    _from_email: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    # Validate client_id
    app = await get_application_by_client_id(db, client_id)
    if not app or not app.is_active:
        return _error_page("Unknown or inactive application.")

    # Validate redirect_uri
    if redirect_uri not in app.redirect_uris:
        return _error_page("Invalid redirect URI.")

    # Validate response_type
    if response_type != "code":
        return _error_page("Unsupported response_type. Only 'code' is supported.")

    # If no login_hint, ask for email first
    if not login_hint:
        html = render_email_page(
            app_name=app.name,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state,
            nonce=nonce,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            response_type=response_type,
        )
        return HTMLResponse(content=html)

    settings = get_settings()

    # Create challenge
    challenge = await create_challenge(
        db=db,
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
        state=state,
        nonce=nonce,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        response_type=response_type,
        login_hint=login_hint,
        settings=settings,
    )

    # Generate QR code
    qr_data = build_qr_data(challenge, settings)
    qr_svg = generate_qr_svg(qr_data)

    html = render_qr_login_page(
        app_name=app.name,
        challenge_id=challenge.id,
        qr_svg=qr_svg,
        scope=scope,
        expire_seconds=settings.AUTH_CHALLENGE_EXPIRE_MINUTES * 60,
        login_hint=login_hint,
        demo_mode=settings.DEMO_MODE,
        show_app_info=not _from_email,
    )
    return HTMLResponse(content=html)
