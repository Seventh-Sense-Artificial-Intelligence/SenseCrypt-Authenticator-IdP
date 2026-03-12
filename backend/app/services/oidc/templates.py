from html import escape
from urllib.parse import urlencode


def render_email_page(
    app_name: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str | None,
    nonce: str | None,
    code_challenge: str | None,
    code_challenge_method: str | None,
    response_type: str,
) -> str:
    # Build the /authorize URL that the form will redirect to (with login_hint appended via JS)
    params: dict[str, str] = {
        "response_type": response_type,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
    }
    if state:
        params["state"] = state
    if nonce:
        params["nonce"] = nonce
    if code_challenge:
        params["code_challenge"] = code_challenge
    if code_challenge_method:
        params["code_challenge_method"] = code_challenge_method

    base_url = "/authorize?" + urlencode(params)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign In - Sensecrypt</title>
    <style>
        :root {{
            --bg: #ffffff;
            --card-bg: #f5f5f5;
            --text: #1a1a1a;
            --text-secondary: #666666;
            --text-muted: #888888;
            --input-bg: #eeeeee;
            --input-border: #cccccc;
            --brand: #F5A324;
            --accent: #B3231D;
            --accent-hover: #9a1e18;
        }}
        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg: #131313;
                --card-bg: #1e1e1e;
                --text: #e0e0e0;
                --text-secondary: #b0b0b0;
                --text-muted: #888888;
                --input-bg: #2a2a2a;
                --input-border: #444444;
            }}
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                         Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 40px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
        }}
        .brand {{
            text-align: center;
            margin-bottom: 24px;
        }}
        .brand h1 {{
            font-size: 24px;
            font-weight: 700;
            color: var(--brand);
            letter-spacing: 1px;
        }}
        .request-info {{
            text-align: center;
            margin-bottom: 24px;
            color: var(--text-secondary);
            font-size: 14px;
            line-height: 1.5;
        }}
        .request-info strong {{
            color: var(--text);
        }}
        .form-group {{
            margin-bottom: 16px;
        }}
        .form-group label {{
            display: block;
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 6px;
        }}
        .form-group input {{
            width: 100%;
            padding: 12px;
            background-color: var(--input-bg);
            border: 1px solid var(--input-border);
            border-radius: 8px;
            color: var(--text);
            font-size: 15px;
            transition: border-color 0.2s;
        }}
        .form-group input:focus {{
            outline: none;
            border-color: var(--brand);
        }}
        .submit-btn {{
            width: 100%;
            padding: 12px;
            background-color: var(--accent);
            color: #fff;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
            margin-top: 8px;
        }}
        .submit-btn:hover {{
            background-color: var(--accent-hover);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="brand">
            <h1>SENSECRYPT</h1>
        </div>
        <div class="request-info">
            <strong>{escape(app_name)}</strong> is requesting access to your account
        </div>
        <form id="email-form" onsubmit="return submitEmail()">
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required
                       placeholder="you@example.com" autofocus>
            </div>
            <button type="submit" class="submit-btn">Continue</button>
        </form>
    </div>
    <script>
        function submitEmail() {{
            var email = document.getElementById("email").value.trim();
            if (!email) return false;
            var url = "{base_url}" + "&login_hint=" + encodeURIComponent(email) + "&_from_email=1";
            window.location.href = url;
            return false;
        }}
    </script>
</body>
</html>"""


def render_qr_login_page(
    app_name: str,
    challenge_id: str,
    qr_svg: str,
    scope: str,
    expire_seconds: int = 300,
    login_hint: str | None = None,
    demo_mode: bool = True,
    show_app_info: bool = True,
) -> str:
    scope_labels = {
        "openid": "Account access",
        "profile": "Your name",
        "email": "Your email",
    }
    scopes = scope.split() if scope else []
    scope_items = ""
    for s in scopes:
        label = scope_labels.get(s, s)
        scope_items += f'<li>{escape(label)}</li>'

    email_html = ""
    if login_hint:
        email_html = f'<span class="user-email">{escape(login_hint)}</span>'

    demo_hint = ""
    demo_click_attr = ""
    if demo_mode:
        demo_hint = '<p class="demo-hint">(or click the QR code in demo mode)</p>'
        demo_click_attr = f'onclick="demoSubmit()" style="cursor:pointer"'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign In - Sensecrypt</title>
    <style>
        :root {{
            --bg: #ffffff;
            --card-bg: #f5f5f5;
            --text: #1a1a1a;
            --text-secondary: #666666;
            --text-muted: #888888;
            --scope-bg: #eeeeee;
            --brand: #F5A324;
            --accent: #B3231D;
            --qr-fill: #1a1a1a;
            --qr-bg: #ffffff;
        }}
        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg: #131313;
                --card-bg: #1e1e1e;
                --text: #e0e0e0;
                --text-secondary: #b0b0b0;
                --text-muted: #888888;
                --scope-bg: #2a2a2a;
                --qr-fill: #e0e0e0;
                --qr-bg: #1e1e1e;
            }}
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                         Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 40px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
        }}
        .brand {{
            text-align: center;
            margin-bottom: 24px;
        }}
        .brand h1 {{
            font-size: 24px;
            font-weight: 700;
            color: var(--brand);
            letter-spacing: 1px;
        }}
        .request-info {{
            text-align: center;
            margin-bottom: 20px;
            color: var(--text-secondary);
            font-size: 14px;
            line-height: 1.5;
        }}
        .request-info strong {{
            color: var(--text);
        }}
        .request-info .user-email {{
            display: block;
            margin-top: 8px;
            font-size: 16px;
            font-weight: 700;
            color: var(--text);
        }}
        .scopes {{
            background-color: var(--scope-bg);
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 24px;
        }}
        .scopes h3 {{
            font-size: 12px;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 8px;
            letter-spacing: 0.5px;
        }}
        .scopes ul {{
            list-style: none;
            padding: 0;
        }}
        .scopes li {{
            padding: 4px 0;
            font-size: 14px;
            color: var(--text-secondary);
        }}
        .scopes li::before {{
            content: "\\2713";
            color: var(--brand);
            margin-right: 8px;
            font-weight: bold;
        }}
        .qr-wrapper {{
            text-align: center;
            margin-bottom: 16px;
        }}
        .qr-wrapper svg {{
            width: 220px;
            height: 220px;
        }}
        .qr-wrapper svg path {{
            fill: var(--qr-fill) !important;
        }}
        .qr-wrapper svg rect {{
            fill: var(--qr-bg) !important;
        }}
        .scan-text {{
            text-align: center;
            font-size: 14px;
            color: var(--text-secondary);
            margin-bottom: 4px;
        }}
        .demo-hint {{
            text-align: center;
            font-size: 13px;
            color: var(--text-muted);
        }}
        .countdown {{
            text-align: center;
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 12px;
        }}
        .countdown.warning {{
            color: var(--accent);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="brand">
            <h1>SENSECRYPT</h1>
        </div>
        {'<div class="request-info"><strong>' + escape(app_name) + '</strong> is requesting access to your account ' + email_html + '</div><div class="scopes"><h3>Permissions requested</h3><ul>' + scope_items + '</ul></div>' if show_app_info else '<div class="request-info">' + email_html + '</div>'}
        <div class="qr-wrapper" id="qr-container" {demo_click_attr}>
            {qr_svg}
        </div>
        <p class="scan-text">Scan with Sensecrypt Authenticator</p>
        {demo_hint}
        <p class="countdown" id="countdown"></p>
    </div>
    <script>
        let challengeId = "{escape(challenge_id)}";
        let polling = true;
        let secondsLeft = {expire_seconds};
        let countdownTimer = null;

        function updateCountdown() {{
            const el = document.getElementById("countdown");
            if (secondsLeft <= 0) {{
                el.textContent = "Refreshing...";
                el.classList.add("warning");
                clearInterval(countdownTimer);
                refreshChallenge();
                return;
            }}
            const m = Math.floor(secondsLeft / 60);
            const s = secondsLeft % 60;
            el.textContent = "Expires in " + m + ":" + (s < 10 ? "0" : "") + s;
            if (secondsLeft <= 30) {{
                el.classList.add("warning");
            }} else {{
                el.classList.remove("warning");
            }}
            secondsLeft--;
        }}

        function startCountdown(seconds) {{
            if (countdownTimer) clearInterval(countdownTimer);
            secondsLeft = seconds;
            updateCountdown();
            countdownTimer = setInterval(updateCountdown, 1000);
        }}

        async function pollStatus() {{
            while (polling) {{
                try {{
                    const resp = await fetch("/challenge/" + challengeId + "/status");
                    const data = await resp.json();
                    if (data.status === "completed" && data.redirect_url) {{
                        polling = false;
                        if (countdownTimer) clearInterval(countdownTimer);
                        window.location.href = data.redirect_url;
                        return;
                    }}
                }} catch (e) {{
                    console.error("Poll error:", e);
                }}
                await new Promise(r => setTimeout(r, 2000));
            }}
        }}

        async function refreshChallenge() {{
            try {{
                const resp = await fetch("/challenge/" + challengeId + "/refresh", {{
                    method: "POST"
                }});
                const data = await resp.json();
                if (data.challenge_id && data.qr_svg) {{
                    challengeId = data.challenge_id;
                    document.getElementById("qr-container").innerHTML = data.qr_svg;
                    startCountdown(data.expire_seconds || {expire_seconds});
                }}
            }} catch (e) {{
                console.error("Refresh error:", e);
            }}
        }}

        async function demoSubmit() {{
            polling = false;
            if (countdownTimer) clearInterval(countdownTimer);
            try {{
                const resp = await fetch("/challenge/" + challengeId + "/demo-submit", {{
                    method: "POST"
                }});
                const data = await resp.json();
                if (data.redirect_url) {{
                    window.location.href = data.redirect_url;
                }}
            }} catch (e) {{
                console.error("Demo submit error:", e);
                polling = true;
                startCountdown(secondsLeft);
                pollStatus();
            }}
        }}

        startCountdown({expire_seconds});
        pollStatus();
    </script>
</body>
</html>"""
