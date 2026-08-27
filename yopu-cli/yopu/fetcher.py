"""
HTTP Fetcher for Yopu.co score pages.
"""
import re
import urllib.request
import urllib.error
from typing import Tuple


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def extract_score_id(input_str: str) -> str:
    """
    Extracts the Yopu score ID from a URL, path, or raw ID string.
    Example: 'https://yopu.co/view/aPenOOpb' -> 'aPenOOpb'
    """
    input_str = input_str.strip()
    # Match URL patterns like yopu.co/view/XYZ, yopu.co/sheet/XYZ, etc.
    match = re.search(r"yopu\.co/(?:view|sheet)/([a-zA-Z0-9_-]+)", input_str)
    if match:
        return match.group(1)
    
    # If it's already a clean alphanumeric ID
    clean_id = re.sub(r"^https?://[^/]+/", "", input_str).strip("/")
    if re.match(r"^[a-zA-Z0-9_-]+$", clean_id):
        return clean_id
    
    return input_str


def build_score_url(score_id_or_url: str) -> str:
    """Build canonical Yopu URL from ID or URL."""
    score_id = extract_score_id(score_id_or_url)
    return f"https://yopu.co/view/{score_id}"


def fetch_score_html(score_id_or_url: str, timeout: int = 15) -> Tuple[str, str]:
    """
    Fetches raw HTML from Yopu.co.
    Returns (html_content, canonical_url).
    """
    url = build_score_url(score_id_or_url)
    
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": "https://yopu.co/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            encoding = response.headers.get_content_charset() or "utf-8"
            html_content = response.read().decode(encoding, errors="replace")
            return html_content, url
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError(f"Score not found on Yopu.co (HTTP 404): {url}")
        raise ConnectionError(f"Failed to fetch score from Yopu (HTTP {e.code}): {e.reason}")
    except Exception as e:
        raise ConnectionError(f"Network error while connecting to Yopu.co ({url}): {e}")
