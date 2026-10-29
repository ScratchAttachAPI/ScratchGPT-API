#!/usr/bin/env python3
"""Read the active Scratch session cookie from a browser profile.

This tool is intended to be run on the same machine where the Scratch tab is open.
It cannot access a browser tab from inside a remote/dev-container environment.
"""

import argparse
import os
import sqlite3
import sys


def _browser_loader(name):
    try:
        import browser_cookie3
    except Exception as exc:
        raise RuntimeError(
            "browser_cookie3 is not installed. Run: pip install browser_cookie3"
        ) from exc

    mapping = {
        "any": browser_cookie3.load,
        "chrome": browser_cookie3.chrome,
        "chromium": browser_cookie3.chromium,
        "edge": browser_cookie3.edge,
        "firefox": browser_cookie3.firefox,
        "safari": browser_cookie3.safari,
        "vivaldi": browser_cookie3.vivaldi,
    }

    if name is None:
        name = "any"

    loader = mapping.get(name.lower())
    if loader is None:
        raise ValueError(f"Unsupported browser '{name}'. Pick one of: {', '.join(sorted(mapping))}")
    return loader()


def _read_chrome_sqlite(profile_path):
    if not profile_path:
        return []

    path = os.path.expanduser(profile_path)
    cookies_db = os.path.join(path, "Network", "Cookies")
    if not os.path.exists(cookies_db):
        raise FileNotFoundError(f"Chrome cookie database not found at {cookies_db}")

    conn = sqlite3.connect(f"file:{cookies_db}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            "SELECT host_key, name, value FROM cookies WHERE host_key LIKE '%scratch.mit.edu' AND name='scratchsessionsid'"
        ).fetchall()
    finally:
        conn.close()

    return [{"name": name, "value": value, "domain": host_key} for host_key, name, value in rows]


def get_scratch_cookies(browser_name=None, chrome_profile_path=None):
    if chrome_profile_path:
        return _read_chrome_sqlite(chrome_profile_path)

    cookies = _browser_loader(browser_name)
    matches = []
    for cookie in cookies:
        domain = (cookie.domain or "").lower()
        if "scratch.mit.edu" in domain or domain.endswith("scratch.mit.edu"):
            matches.append({
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
            })
    return matches


def main():
    parser = argparse.ArgumentParser(description="Read Scratch browser cookies and print the session id.")
    parser.add_argument("--browser", choices=[
        "any", "chrome", "chromium", "edge", "firefox", "safari", "vivaldi"
    ], default="any", help="Browser profile to inspect")
    parser.add_argument(
        "--chrome-profile",
        help="Direct path to the Chrome/Chromium profile folder, for example ~/.config/google-chrome/Default",
    )
    parser.add_argument("--validate", action="store_true", help="Validate the session id by creating a scratchattach session")
    args = parser.parse_args()

    try:
        cookies = get_scratch_cookies(args.browser, args.chrome_profile)
    except Exception as exc:
        print(f"Could not read browser cookies: {exc}", file=sys.stderr)
        print("If you are in a dev container or remote machine, open Scratch on your local machine and run this script there.")
        raise SystemExit(1)

    scratch_cookies = {c["name"]: c["value"] for c in cookies}
    print("Scratch cookies found:")
    for name in sorted(scratch_cookies):
        print(f"  {name} = {scratch_cookies[name]}")

    session_id = scratch_cookies.get("scratchsessionsid")
    if not session_id:
        print("\nNo 'scratchsessionsid' cookie was found for scratch.mit.edu.", file=sys.stderr)
        print("Open Scratch in a browser tab and try again, then ensure the cookie is not cleared.")
        raise SystemExit(1)

    print(f"\nSession ID: {session_id}")

    if args.validate:
        try:
            import scratchattach
            session = scratchattach.login_by_id(session_id)
            print(f"Validated username: {session.username}")
        except Exception as exc:
            print(f"Validation failed: {exc}", file=sys.stderr)
            raise SystemExit(1)


if __name__ == "__main__":
    main()
