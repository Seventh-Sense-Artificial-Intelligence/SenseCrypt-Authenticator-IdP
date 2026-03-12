"""
Seed script: creates a verified test user and a demo OAuth application.
Run from backend/ with: PYTHONPATH=. python seed_demo.py

Prints the credentials needed to configure the demo app.
"""
import asyncio
import secrets
import bcrypt
from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.product.oauth_application import OAuthApplication
from sqlalchemy import select


TEST_EMAIL = "demo@sensecrypt.com"
TEST_PASSWORD = "Demo1234!"
TEST_NAME = "Demo User"

DEMO_APP_NAME = "OIDC Demo Client"
DEMO_REDIRECT_URI = "http://localhost:9000/callback"


async def seed():
    async with AsyncSessionLocal() as db:
        # --- Test user ---
        result = await db.execute(select(User).where(User.email == TEST_EMAIL))
        user = result.scalar_one_or_none()

        if not user:
            password_hash = bcrypt.hashpw(TEST_PASSWORD.encode(), bcrypt.gensalt()).decode()
            user = User(
                email=TEST_EMAIL,
                password_hash=password_hash,
                full_name=TEST_NAME,
                is_verified=True,
                is_active=True,
            )
            db.add(user)
            await db.flush()
            print(f"Created test user: {TEST_EMAIL}")
        else:
            print(f"Test user already exists: {TEST_EMAIL}")

        # --- Demo OAuth application ---
        result = await db.execute(
            select(OAuthApplication).where(
                OAuthApplication.user_id == user.id,
                OAuthApplication.name == DEMO_APP_NAME,
            )
        )
        app = result.scalar_one_or_none()

        if app:
            # Regenerate secret so we can print it
            client_secret = secrets.token_urlsafe(48)
            app.client_secret_hash = bcrypt.hashpw(
                client_secret.encode(), bcrypt.gensalt()
            ).decode()
            app.redirect_uris = [DEMO_REDIRECT_URI]
            app.is_active = True
            await db.commit()
            print(f"Updated existing demo app (rotated secret)")
        else:
            client_id = secrets.token_urlsafe(32)
            client_secret = secrets.token_urlsafe(48)
            client_secret_hash = bcrypt.hashpw(
                client_secret.encode(), bcrypt.gensalt()
            ).decode()
            app = OAuthApplication(
                user_id=user.id,
                name=DEMO_APP_NAME,
                client_id=client_id,
                client_secret_hash=client_secret_hash,
                application_type="web",
                redirect_uris=[DEMO_REDIRECT_URI],
                post_logout_redirect_uris=[],
                allowed_scopes=["openid", "profile", "email"],
                grant_types=["authorization_code", "refresh_token"],
                token_endpoint_auth_method="client_secret_post",
            )
            db.add(app)
            await db.commit()
            print(f"Created demo OAuth application")

        await db.refresh(app)

        print()
        print("=" * 60)
        print("  DEMO CREDENTIALS")
        print("=" * 60)
        print(f"  User email:     {TEST_EMAIL}")
        print(f"  Client ID:      {app.client_id}")
        print(f"  Client Secret:  {client_secret}")
        print(f"  Redirect URI:   {DEMO_REDIRECT_URI}")
        print()
        print("  Login: Click the QR code on the IdP login page")
        print("=" * 60)

        # Write demo/.env automatically
        import os
        demo_env_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "demo", ".env"
        )
        with open(demo_env_path, "w") as f:
            f.write(f"OIDC_ISSUER_URL=http://localhost:8000\n")
            f.write(f"CLIENT_ID={app.client_id}\n")
            f.write(f"CLIENT_SECRET={client_secret}\n")
            f.write(f"REDIRECT_URI={DEMO_REDIRECT_URI}\n")
            f.write(f"SCOPES=openid profile email\n")
        print(f"\n  Wrote {demo_env_path}")


if __name__ == "__main__":
    asyncio.run(seed())
