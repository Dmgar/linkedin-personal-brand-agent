"""
Local OAuth 2.0 Helper for LinkedIn Personal Brand Agent.
Opens the user's browser to authorize their own LinkedIn Developer App
(scopes: openid, profile, w_member_social), captures the callback on
http://localhost:3000/callback, exchanges the code for an access token,
resolves the authenticated member's URN (`urn:li:person:...`), and saves
the token securely in `.mcp_tokens/linkedin_token.json` (gitignored).
"""

import http.server
import json
import os
import secrets
import time
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional

import requests


ROOT_DIR = Path(__file__).resolve().parent.parent
TOKEN_DIR = ROOT_DIR / ".mcp_tokens"
TOKEN_FILE = TOKEN_DIR / "linkedin_token.json"


def load_env() -> Dict[str, str]:
    """Reads variables from the root .env file and merges with os.environ."""
    env: Dict[str, str] = dict(os.environ)
    env_file = ROOT_DIR / ".env"
    if env_file.exists():
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def load_saved_token() -> Optional[Dict[str, Any]]:
    """Loads the locally stored OAuth token if present and not expired."""
    if not TOKEN_FILE.exists():
        return None
    try:
        data = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
        expires_at = data.get("expires_at", 0)
        if expires_at and time.time() > expires_at:
            return None
        return data
    except Exception:
        return None


def fetch_userinfo(access_token: str) -> Dict[str, Any]:
    """Calls LinkedIn OpenID Connect /v2/userinfo to get the member's sub ID and name."""
    resp = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    resp.raise_for_status()
    info = resp.json()
    sub = info.get("sub")
    if sub:
        info["person_urn"] = f"urn:li:person:{sub}"
    return info


def run_interactive_oauth() -> Dict[str, Any]:
    """Starts a temporary local server on port 3000 and completes OAuth 2.0 flow."""
    env = load_env()
    client_id = env.get("LINKEDIN_CLIENT_ID", "")
    client_secret = env.get("LINKEDIN_CLIENT_SECRET", "")
    redirect_uri = env.get("LINKEDIN_REDIRECT_URI", "http://localhost:3000/callback")
    scopes = env.get("LINKEDIN_SCOPES", "openid,profile,w_member_social").replace(",", " ")

    if not client_id or client_id == "tu_client_id_aqui" or not client_secret or client_secret == "tu_client_secret_aqui":
        raise ValueError(
            "Faltan LINKEDIN_CLIENT_ID o LINKEDIN_CLIENT_SECRET en tu archivo .env local.\n"
            "1. Crea una app en https://www.linkedin.com/developers/apps\n"
            "2. Activa 'Share on LinkedIn' y 'Sign In with LinkedIn using OpenID Connect'\n"
            "3. Agrega http://localhost:3000/callback en Auth -> Authorized redirect URLs\n"
            "4. Pega tu CLIENT_ID y CLIENT_SECRET en el archivo .env"
        )

    state = secrets.token_urlsafe(16)
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": scopes,
    }
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"

    captured: Dict[str, Optional[str]] = {"code": None, "error": None}

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/callback":
                self.send_response(404)
                self.end_headers()
                return

            qs = urllib.parse.parse_qs(parsed.query)
            if qs.get("state", [None])[0] != state:
                captured["error"] = "Invalid OAuth state parameter."
            elif "error" in qs:
                captured["error"] = qs.get("error_description", qs["error"])[0]
            elif "code" in qs:
                captured["code"] = qs["code"][0]

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if captured["code"]:
                html = (
                    "<html><body style='font-family:sans-serif;text-align:center;padding:40px;'>"
                    "<h2>✅ Autorización con LinkedIn completada</h2>"
                    "<p>Ya puedes cerrar esta pestaña y volver a Google Antigravity.</p>"
                    "</body></html>"
                )
            else:
                html = (
                    f"<html><body style='font-family:sans-serif;text-align:center;padding:40px;'>"
                    f"<h2>❌ Error en la autorización</h2><p>{captured['error']}</p></body></html>"
                )
            self.wfile.write(html.encode("utf-8"))

        def log_message(self, format: str, *args: Any) -> None:
            pass

    parsed_redirect = urllib.parse.urlparse(redirect_uri)
    port = parsed_redirect.port or 3000

    server = http.server.HTTPServer(("127.0.0.1", port), CallbackHandler)
    print(f"\nAbriendo navegador para autorizar en LinkedIn (puerto local {port})...")
    print(f"Si no se abre automáticamente, entra en:\n{auth_url}\n")
    webbrowser.open(auth_url)

    while captured["code"] is None and captured["error"] is None:
        server.handle_request()
    server.server_close()

    if captured["error"]:
        raise RuntimeError(f"Error de autorización OAuth: {captured['error']}")

    token_resp = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "authorization_code",
            "code": captured["code"],
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=20,
    )
    token_resp.raise_for_status()
    token_data = token_resp.json()

    access_token = token_data["access_token"]
    expires_in = int(token_data.get("expires_in", 5184000))
    userinfo = fetch_userinfo(access_token)

    stored_payload = {
        "access_token": access_token,
        "expires_in": expires_in,
        "expires_at": int(time.time()) + expires_in,
        "created_at": int(time.time()),
        "person_urn": userinfo.get("person_urn"),
        "name": userinfo.get("name"),
        "given_name": userinfo.get("given_name"),
        "family_name": userinfo.get("family_name"),
        "picture": userinfo.get("picture"),
    }

    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(stored_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Token guardado localmente en {TOKEN_FILE}")
    print(f"👤 Conectado como: {stored_payload.get('name')} ({stored_payload.get('person_urn')})")
    return stored_payload


if __name__ == "__main__":
    run_interactive_oauth()
