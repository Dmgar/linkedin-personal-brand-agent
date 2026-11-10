"""
Live App Screenshot Engine for LinkedIn Personal Brand Agent.
Launches a local web application (Streamlit, Dash, or custom URL/command),
navigates across its interactive tabs using Playwright, and stores clean,
unmodified high-DPI screenshots in content/assets/<POST_ID>/.

Reads LOCAL_REPOS_DIR from the local .env file so no user-specific paths
are hardcoded in the public repository.
"""

import argparse
import os
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

from playwright.sync_api import sync_playwright


REPO_AGENT_ROOT = Path(__file__).resolve().parents[4]


def load_local_env() -> Dict[str, str]:
    """Loads key-value pairs from the root .env file if present."""
    env_vars: Dict[str, str] = {}
    env_path = REPO_AGENT_ROOT / ".env"
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env_vars[k.strip()] = v.strip().strip('"').strip("'")
    return env_vars


def resolve_app_dir(app_dir_arg: str) -> Path:
    """Resolves either an absolute path or a repository name inside LOCAL_REPOS_DIR."""
    candidate = Path(app_dir_arg)
    if candidate.is_absolute() and candidate.exists():
        return candidate

    env_vars = load_local_env()
    repos_root = env_vars.get("LOCAL_REPOS_DIR") or os.environ.get("LOCAL_REPOS_DIR")
    if repos_root:
        resolved = Path(repos_root) / app_dir_arg
        if resolved.exists():
            return resolved

    # Fallback: sibling directory next to linkedin-personal-brand-agent
    sibling = REPO_AGENT_ROOT.parent / app_dir_arg
    if sibling.exists():
        return sibling

    raise FileNotFoundError(
        f"Could not find repository '{app_dir_arg}'. Configure LOCAL_REPOS_DIR in .env or pass an absolute --app-dir."
    )


def find_project_python(app_dir: Path) -> str:
    """Finds the virtual environment Python executable inside the target project."""
    for venv_name in [".venv", "venv", "env"]:
        win_py = app_dir / venv_name / "Scripts" / "python.exe"
        if win_py.exists():
            return str(win_py)
        unix_py = app_dir / venv_name / "bin" / "python"
        if unix_py.exists():
            return str(unix_py)
    return "python"


def wait_for_server(url: str, timeout: int = 40) -> bool:
    """Polls the target HTTP URL until the server responds with HTTP 200."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.8)
    return False


def find_system_browser() -> Optional[str]:
    """Detects local Chrome or Edge installation on Windows if Playwright browser cache is absent."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def capture_streamlit_app(
    app_dir: Path,
    post_id: str,
    entrypoint: str = "app.py",
    port: int = 8519,
) -> List[Path]:
    """
    Launches a Streamlit application, navigates through its top-level tabs and
    subtabs automatically, and saves clean high-resolution PNG screenshots.
    """
    out_dir = REPO_AGENT_ROOT / "content" / "assets" / post_id
    out_dir.mkdir(parents=True, exist_ok=True)

    py_exec = find_project_python(app_dir)
    url = f"http://localhost:{port}"

    cmd = [
        py_exec,
        "-m",
        "streamlit",
        "run",
        entrypoint,
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--theme.base=light",
        "--theme.backgroundColor=#FFFFFF",
        "--theme.secondaryBackgroundColor=#F8FAFC",
        "--theme.textColor=#0F172A",
    ]

    print(f"[1/2] Starting live app ({app_dir.name}) on {url}...")
    proc = subprocess.Popen(
        cmd,
        cwd=str(app_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    saved_files: List[Path] = []
    try:
        if not wait_for_server(url, timeout=45):
            raise RuntimeError(f"Server did not become ready on {url} within timeout.")

        print("[2/2] Capturing clean screenshots via headless browser...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path=find_system_browser())
            context = browser.new_context(
                viewport={"width": 1680, "height": 1120},
                device_scale_factor=2,
            )
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Wait for Streamlit main container and charts/metrics to settle
            page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=45000)
            time.sleep(6.0)

            # Hide developer chrome (top bar / deploy toolbar) while keeping the app UI untouched
            page.evaluate(
                """
                () => {
                    const header = document.querySelector('header[data-testid="stHeader"]');
                    if (header) header.style.display = 'none';
                    const toolbar = document.querySelector('div[data-testid="stToolbar"]');
                    if (toolbar) toolbar.style.display = 'none';
                    const deco = document.querySelector('div[data-testid="stDecoration"]');
                    if (deco) deco.style.display = 'none';
                    const mainBlock = document.querySelector('.block-container');
                    if (mainBlock) {
                        mainBlock.style.paddingTop = '1.5rem';
                        mainBlock.style.paddingBottom = '2rem';
                    }
                }
                """
            )
            time.sleep(0.8)

            # Capture 01: Initial overview with sidebar
            shot_01 = out_dir / "01_overview.png"
            page.screenshot(path=str(shot_01), full_page=False)
            saved_files.append(shot_01)
            print(f"  -> Saved {shot_01.name}")

            # Hide sidebar for subsequent analytical tabs to maximize chart width
            page.evaluate(
                """
                () => {
                    const sb = document.querySelector('[data-testid="stSidebar"]');
                    if (sb) sb.style.display = 'none';
                }
                """
            )
            time.sleep(0.6)

            # Discover top-level tabs if present
            tabs = page.locator('[data-baseweb="tab-list"]').first.locator('button[role="tab"]')
            tab_count = tabs.count()

            shot_index = 2
            for idx in range(1, tab_count):
                tab_btn = tabs.nth(idx)
                tab_label = (tab_btn.inner_text() or f"tab_{idx}").strip()
                slug = "".join(c if c.isalnum() else "_" for c in tab_label.lower()).strip("_")[:28]
                tab_btn.click()
                time.sleep(4.0)

                shot_path = out_dir / f"{shot_index:02d}_{slug}.png"
                page.screenshot(path=str(shot_path), full_page=False)
                saved_files.append(shot_path)
                print(f"  -> Saved {shot_path.name}")
                shot_index += 1

            browser.close()

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    return saved_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture clean live screenshots of a local project.")
    parser.add_argument("--post-id", default="LI-001", help="Draft ID folder under content/assets/ (e.g. LI-001)")
    parser.add_argument("--app-dir", required=True, help="Repository folder name in LOCAL_REPOS_DIR or absolute path")
    parser.add_argument("--entrypoint", default="app.py", help="Entrypoint file for Streamlit (default: app.py)")
    parser.add_argument("--port", type=int, default=8519, help="Local port to run the server on")
    args = parser.parse_args()

    target_dir = resolve_app_dir(args.app_dir)
    capture_streamlit_app(target_dir, post_id=args.post_id, entrypoint=args.entrypoint, port=args.port)


if __name__ == "__main__":
    main()
