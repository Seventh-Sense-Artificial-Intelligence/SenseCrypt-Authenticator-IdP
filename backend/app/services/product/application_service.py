import secrets
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product.oauth_application import OAuthApplication
from app.schemas.product.oauth_application import (
    OAuthApplicationCreate,
    OAuthApplicationUpdate,
)


def _hash_secret(secret: str) -> str:
    return bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()


def _verify_secret(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


async def _check_redirect_uri_uniqueness(
    db: AsyncSession,
    redirect_uris: list[str],
    exclude_app_id: str | None = None,
) -> None:
    """Ensure no other application uses any of the given redirect_uris."""
    if not redirect_uris:
        return
    result = await db.execute(select(OAuthApplication))
    all_apps = list(result.scalars().all())
    for app in all_apps:
        if exclude_app_id and app.id == exclude_app_id:
            continue
        existing_uris = set(app.redirect_uris or [])
        for uri in redirect_uris:
            if uri in existing_uris:
                raise ValueError(
                    f"Redirect URI '{uri}' is already registered by application '{app.name}'"
                )


async def create_application(
    db: AsyncSession, user_id: str, data: OAuthApplicationCreate
) -> tuple[OAuthApplication, str]:
    await _check_redirect_uri_uniqueness(db, data.redirect_uris)

    client_id = secrets.token_urlsafe(32)
    client_secret = secrets.token_urlsafe(48)
    client_secret_hash = _hash_secret(client_secret)

    app = OAuthApplication(
        user_id=user_id,
        name=data.name,
        client_id=client_id,
        client_secret_hash=client_secret_hash,
        application_type=data.application_type,
        redirect_uris=data.redirect_uris,
        post_logout_redirect_uris=data.post_logout_redirect_uris,
        allowed_scopes=data.allowed_scopes,
        grant_types=data.grant_types,
        token_endpoint_auth_method=data.token_endpoint_auth_method,
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app, client_secret


async def list_applications(
    db: AsyncSession, user_id: str
) -> list[OAuthApplication]:
    result = await db.execute(
        select(OAuthApplication).where(OAuthApplication.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_application(
    db: AsyncSession, user_id: str, app_id: str
) -> OAuthApplication | None:
    result = await db.execute(
        select(OAuthApplication).where(
            OAuthApplication.id == app_id,
            OAuthApplication.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def get_application_by_client_id(
    db: AsyncSession, client_id: str
) -> OAuthApplication | None:
    result = await db.execute(
        select(OAuthApplication).where(OAuthApplication.client_id == client_id)
    )
    return result.scalar_one_or_none()


async def update_application(
    db: AsyncSession, user_id: str, app_id: str, data: OAuthApplicationUpdate
) -> OAuthApplication | None:
    app = await get_application(db, user_id, app_id)
    if not app:
        return None
    update_data = data.model_dump(exclude_unset=True)
    if "redirect_uris" in update_data:
        await _check_redirect_uri_uniqueness(
            db, update_data["redirect_uris"], exclude_app_id=app_id
        )
    for field, value in update_data.items():
        setattr(app, field, value)
    await db.commit()
    await db.refresh(app)
    return app


async def delete_application(
    db: AsyncSession, user_id: str, app_id: str
) -> bool:
    app = await get_application(db, user_id, app_id)
    if not app:
        return False
    await db.delete(app)
    await db.commit()
    return True


async def rotate_secret(
    db: AsyncSession, user_id: str, app_id: str
) -> tuple[OAuthApplication, str] | None:
    app = await get_application(db, user_id, app_id)
    if not app:
        return None
    new_secret = secrets.token_urlsafe(48)
    app.client_secret_hash = _hash_secret(new_secret)
    await db.commit()
    await db.refresh(app)
    return app, new_secret


async def verify_client_credentials(
    db: AsyncSession, client_id: str, client_secret: str
) -> OAuthApplication | None:
    app = await get_application_by_client_id(db, client_id)
    if not app:
        return None
    if not app.is_active:
        return None
    if not _verify_secret(client_secret, app.client_secret_hash):
        return None
    return app
