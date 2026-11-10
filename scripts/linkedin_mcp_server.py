"""
Local Model Context Protocol (MCP) Server for LinkedIn Official REST API.
Provides official OAuth 2.0 tools for Google Antigravity and MCP clients:
- `get_profile`: Reads the authenticated member's basic profile & URN.
- `create_post`: Publishes a text post (up to 3,000 characters).
- `create_image_post`: Uploads 1 or more clean screenshots/images via `/rest/images`
  and publishes a post with native single-image or multi-image attachment.
- `create_document_post`: Uploads a PDF via `/rest/documents` and publishes a
  native document/carousel post (for events, papers, or presentations).

All credentials and tokens stay strictly on the user's local machine.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import mimetypes

from mcp.server.mcpserver import MCPServer
import requests

from linkedin_auth import load_env, load_saved_token, fetch_userinfo


mcp = MCPServer("linkedin")


def _get_auth_context() -> Dict[str, Any]:
    """Retrieves valid access token, person_urn, and API version header."""
    token_data = load_saved_token()
    if not token_data or not token_data.get("access_token"):
        raise RuntimeError(
            "No valid LinkedIn OAuth token found locally. "
            "Run `python scripts/linkedin_auth.py` in your terminal after setting LINKEDIN_CLIENT_ID "
            "and LINKEDIN_CLIENT_SECRET in your `.env` file."
        )

    env = load_env()
    api_version = env.get("LINKEDIN_API_VERSION", "202610")
    access_token = token_data["access_token"]
    person_urn = token_data.get("person_urn")

    if not person_urn:
        info = fetch_userinfo(access_token)
        person_urn = info.get("person_urn")

    return {
        "access_token": access_token,
        "person_urn": person_urn,
        "api_version": api_version,
        "profile_snapshot": token_data,
    }


def _rest_headers(access_token: str, api_version: str) -> Dict[str, str]:
    """Standard headers required by LinkedIn's versioned /rest/ endpoints."""
    return {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Linkedin-Version": api_version,
        "Content-Type": "application/json",
    }


def _upload_single_image(image_path: Path, ctx: Dict[str, Any]) -> str:
    """Initializes an image upload on /rest/images and PUTs the binary file."""
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    headers = _rest_headers(ctx["access_token"], ctx["api_version"])
    init_resp = requests.post(
        "https://api.linkedin.com/rest/images?action=initializeUpload",
        headers=headers,
        json={"initializeUploadRequest": {"owner": ctx["person_urn"]}},
        timeout=20,
    )
    init_resp.raise_for_status()
    val = init_resp.json()["value"]
    upload_url = val["uploadUrl"]
    image_urn = val["image"]

    mime_type = mimetypes.guess_type(str(image_path))[0] or "image/png"
    with image_path.open("rb") as f:
        put_resp = requests.put(
            upload_url,
            headers={
                "Authorization": f"Bearer {ctx['access_token']}",
                "Content-Type": mime_type,
            },
            data=f,
            timeout=60,
        )
        put_resp.raise_for_status()

    return image_urn


@mcp.tool()
def get_profile() -> str:
    """
    Retrieves the basic profile information and URN of the authenticated LinkedIn member.
    """
    ctx = _get_auth_context()
    info = fetch_userinfo(ctx["access_token"])
    return json.dumps(info, indent=2, ensure_ascii=False)


@mcp.tool()
def create_post(text: str, visibility: str = "PUBLIC") -> str:
    """
    Publishes a text post on the authenticated user's LinkedIn profile via POST /rest/posts.
    IMPORTANT: Only invoke after explicit human approval of the specific draft ID.

    Args:
        text: The full commentary text of the post (maximum 3,000 characters).
        visibility: Either "PUBLIC" or "CONNECTIONS". Defaults to "PUBLIC".
    """
    if len(text) > 3000:
        raise ValueError(f"Post text exceeds LinkedIn's 3,000-character limit ({len(text)} chars).")

    ctx = _get_auth_context()
    payload = {
        "author": ctx["person_urn"],
        "commentary": text,
        "visibility": visibility.upper(),
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    resp = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers=_rest_headers(ctx["access_token"], ctx["api_version"]),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    post_urn = resp.headers.get("x-restli-id", "created")
    return json.dumps(
        {"status": "published", "post_urn": post_urn, "visibility": visibility.upper()},
        indent=2,
        ensure_ascii=False,
    )


@mcp.tool()
def create_image_post(
    text: str,
    image_paths: List[str],
    visibility: str = "PUBLIC",
) -> str:
    """
    Uploads one or more clean local image files (PNG/JPG) to LinkedIn (/rest/images)
    and publishes a post with native single-image or multi-image gallery attachment.
    IMPORTANT: Only invoke after explicit human approval of the specific draft ID.

    Args:
        text: The full commentary text of the post (maximum 3,000 characters).
        image_paths: List of local file paths to PNG/JPG screenshots to attach.
        visibility: Either "PUBLIC" or "CONNECTIONS". Defaults to "PUBLIC".
    """
    if len(text) > 3000:
        raise ValueError(f"Post text exceeds LinkedIn's 3,000-character limit ({len(text)} chars).")
    if not image_paths:
        raise ValueError("Provide at least one image path in `image_paths`.")

    ctx = _get_auth_context()
    uploaded_urns: List[str] = []
    for p_str in image_paths:
        img_urn = _upload_single_image(Path(p_str).expanduser().resolve(), ctx)
        uploaded_urns.append(img_urn)

    if len(uploaded_urns) == 1:
        content_block: Dict[str, Any] = {"media": {"id": uploaded_urns[0]}}
    else:
        content_block = {
            "multiImage": {
                "images": [{"id": urn} for urn in uploaded_urns]
            }
        }

    payload = {
        "author": ctx["person_urn"],
        "commentary": text,
        "visibility": visibility.upper(),
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": content_block,
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    resp = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers=_rest_headers(ctx["access_token"], ctx["api_version"]),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    post_urn = resp.headers.get("x-restli-id", "created")
    return json.dumps(
        {
            "status": "published",
            "post_urn": post_urn,
            "image_urns": uploaded_urns,
            "visibility": visibility.upper(),
        },
        indent=2,
        ensure_ascii=False,
    )


@mcp.tool()
def create_document_post(
    text: str,
    pdf_path: str,
    document_title: str,
    visibility: str = "PUBLIC",
) -> str:
    """
    Uploads a local PDF document via `/rest/documents` and publishes a native
    LinkedIn document/carousel post (reserved for events, papers, or presentations).
    IMPORTANT: Only invoke after explicit human approval of the specific draft ID.

    Args:
        text: The full commentary text of the post (maximum 3,000 characters).
        pdf_path: Local path to the PDF file.
        document_title: Title displayed on the LinkedIn document viewer header.
        visibility: Either "PUBLIC" or "CONNECTIONS". Defaults to "PUBLIC".
    """
    if len(text) > 3000:
        raise ValueError(f"Post text exceeds LinkedIn's 3,000-character limit ({len(text)} chars).")

    doc_file = Path(pdf_path).expanduser().resolve()
    if not doc_file.exists():
        raise FileNotFoundError(f"PDF file not found: {doc_file}")

    ctx = _get_auth_context()
    headers = _rest_headers(ctx["access_token"], ctx["api_version"])

    init_resp = requests.post(
        "https://api.linkedin.com/rest/documents?action=initializeUpload",
        headers=headers,
        json={"initializeUploadRequest": {"owner": ctx["person_urn"]}},
        timeout=20,
    )
    init_resp.raise_for_status()
    val = init_resp.json()["value"]
    upload_url = val["uploadUrl"]
    doc_urn = val["document"]

    with doc_file.open("rb") as f:
        put_resp = requests.put(
            upload_url,
            headers={
                "Authorization": f"Bearer {ctx['access_token']}",
                "Content-Type": "application/pdf",
            },
            data=f,
            timeout=90,
        )
        put_resp.raise_for_status()

    payload = {
        "author": ctx["person_urn"],
        "commentary": text,
        "visibility": visibility.upper(),
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {
            "media": {
                "id": doc_urn,
                "title": document_title,
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    resp = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers=headers,
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    post_urn = resp.headers.get("x-restli-id", "created")
    return json.dumps(
        {
            "status": "published",
            "post_urn": post_urn,
            "document_urn": doc_urn,
            "visibility": visibility.upper(),
        },
        indent=2,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    mcp.run()
