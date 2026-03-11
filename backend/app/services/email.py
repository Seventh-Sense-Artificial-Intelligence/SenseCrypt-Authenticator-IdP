from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.config import get_settings


def _send(to_email: str, subject: str, html_content: str) -> bool:
    settings = get_settings()
    if not settings.SENDGRID_API_KEY:
        return False
    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
        return True
    except Exception:
        return False


def send_verification_email(to_email: str, verification_url: str) -> bool:
    return _send(
        to_email,
        "Verify your email",
        f"""
        <div style="font-family: 'Inter', sans-serif; max-width: 480px; margin: 0 auto; padding: 2rem;">
            <h2 style="color: #3F4246; margin-bottom: 0.5rem;">Verify your email</h2>
            <p style="color: #666; margin-bottom: 1.5rem;">
                Click the button below to verify your email address and sign in.
            </p>
            <div style="text-align: center; margin: 2rem 0;">
                <a href="{verification_url}"
                   style="display: inline-block; padding: 0.875rem 2.5rem;
                          background: linear-gradient(90deg, #B3231D 0%, #F5A324 100%);
                          color: #fff; font-size: 1rem; font-weight: 700;
                          text-decoration: none; border-radius: 8px;
                          letter-spacing: 0.025em; text-transform: uppercase;">
                    Verify &amp; Sign In
                </a>
            </div>
            <p style="color: #999; font-size: 0.875rem;">
                This link expires in 24 hours. If you didn't create an account, ignore this email.
            </p>
        </div>
        """,
    )


def send_welcome_email(to_email: str, full_name: str) -> bool:
    return _send(
        to_email,
        "Welcome to Seventh Sense",
        f"<p>Hi {full_name},</p><p>Your account has been verified. Welcome aboard!</p>",
    )


def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    return _send(
        to_email,
        "Password Reset Request",
        f"""
        <div style="font-family: 'Inter', sans-serif; max-width: 480px; margin: 0 auto; padding: 2rem;">
            <h2 style="color: #3F4246; margin-bottom: 0.5rem;">Reset your password</h2>
            <p style="color: #666; margin-bottom: 1.5rem;">
                Click the button below to set a new password for your account.
            </p>
            <div style="text-align: center; margin: 2rem 0;">
                <a href="{reset_url}"
                   style="display: inline-block; padding: 0.875rem 2.5rem;
                          background: linear-gradient(90deg, #B3231D 0%, #F5A324 100%);
                          color: #fff; font-size: 1rem; font-weight: 700;
                          text-decoration: none; border-radius: 8px;
                          letter-spacing: 0.025em; text-transform: uppercase;">
                    Reset Password
                </a>
            </div>
            <p style="color: #999; font-size: 0.875rem;">
                This link expires in 1 hour. If you didn't request a password reset, ignore this email.
            </p>
        </div>
        """,
    )
