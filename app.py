from __future__ import annotations

import concurrent.futures
import ipaddress
import socket
from urllib.parse import urlparse

import requests
import streamlit as st

DEFAULT_TIMEOUT = 8
MAX_URLS = 25
USER_AGENT = "Site-Connectivity-Checker/1.0"


def normalize_url(value: str) -> str:
    """Return a normalized HTTP(S) URL or raise ValueError."""
    value = value.strip()
    if not value:
        raise ValueError("URL cannot be empty.")
    if "://" not in value:
        value = f"https://{value}"

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Enter a valid HTTP or HTTPS URL.")
    if parsed.username or parsed.password:
        raise ValueError("Credentials in URLs are not supported.")
    return parsed.geturl()


def is_public_destination(url: str) -> bool:
    """Reject loopback, private, link-local and otherwise non-public targets."""
    hostname = urlparse(url).hostname
    if not hostname:
        return False
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(hostname, None)}
    except socket.gaierror:
        return False

    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            return False
    return bool(addresses)


def check_site_availability(url: str, timeout: int = DEFAULT_TIMEOUT) -> tuple[str, bool, str]:
    """Check a URL exactly once and return URL, availability, and detail."""
    normalized = normalize_url(url)
    if not is_public_destination(normalized):
        return normalized, False, "Blocked non-public or unresolved destination"

    try:
        response = requests.get(
            normalized,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=True,
            stream=True,
        )
        ok = 200 <= response.status_code < 400
        return normalized, ok, f"HTTP {response.status_code}"
    except requests.RequestException as exc:
        return normalized, False, exc.__class__.__name__


def check_many(urls: list[str]) -> list[tuple[str, bool, str]]:
    workers = min(8, len(urls))
    if not workers:
        return []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(check_site_availability, urls))


def main() -> None:
    st.set_page_config(page_title="Website Availability Checker", page_icon="⚡")
    st.title("⚡ Website Availability Checker")
    st.caption("Check up to 25 public HTTP(S) websites concurrently.")

    raw_urls = st.text_area(
        "Websites",
        placeholder="example.com\nhttps://openai.com",
        help="Enter one URL per line. Private and local network addresses are blocked.",
    )

    if st.button("Check websites", type="primary"):
        values = [line.strip() for line in raw_urls.splitlines() if line.strip()]
        if not values:
            st.warning("Enter at least one website.")
            return
        if len(values) > MAX_URLS:
            st.error(f"Please enter no more than {MAX_URLS} websites.")
            return

        normalized: list[str] = []
        for value in values:
            try:
                normalized.append(normalize_url(value))
            except ValueError as exc:
                st.error(f"{value}: {exc}")
        if not normalized:
            return

        with st.spinner("Checking websites..."):
            for url, available, detail in check_many(normalized):
                icon = "✅" if available else "❌"
                st.write(f"{icon} **{url}** — {detail}")


if __name__ == "__main__":
    main()
