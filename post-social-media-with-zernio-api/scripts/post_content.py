#!/usr/bin/env python3
"""Publish an explicitly approved Zernio post with a durable request ID."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from typing import Any

from zernio_client import APIError, request_json


MEDIA_TYPES = {"image", "video", "document"}


def build_payload(*, caption: str, platforms: list[str], account_ids: list[str], media_items: list[dict[str, str]]) -> dict[str, Any]:
    if not caption.strip():
        raise ValueError("caption must not be empty")
    if not platforms or not account_ids or len(platforms) != len(account_ids):
        raise ValueError("--platforms and --account-ids must be non-empty and paired")
    return {
        "content": caption,
        "mediaItems": media_items,
        "platforms": [
            {"platform": platform, "accountId": account_id}
            for platform, account_id in zip(platforms, account_ids, strict=True)
        ],
        "publishNow": True,
    }


def build_media_items(urls: list[str], media_types: list[str]) -> list[dict[str, str]]:
    if not urls:
        return []
    if len(media_types) == 1:
        media_types = media_types * len(urls)
    if len(urls) != len(media_types):
        raise ValueError("provide one --media-type or one type per --media-url")
    media_items: list[dict[str, str]] = []
    for url, media_type in zip(urls, media_types, strict=True):
        if not url.startswith("https://"):
            raise ValueError("media URLs must use HTTPS")
        if media_type not in MEDIA_TYPES:
            raise ValueError(f"unsupported media type: {media_type}")
        media_items.append({"url": url, "type": media_type})
    return media_items


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caption", required=True, help="exact approved caption")
    parser.add_argument("--platforms", required=True, nargs="+", help="exact destination platform values")
    parser.add_argument("--account-ids", required=True, nargs="+", help="exact destination account IDs")
    parser.add_argument("--media-url", action="append", default=[], help="already-uploaded HTTPS media URL; may repeat")
    parser.add_argument("--media-type", action="append", default=[], choices=sorted(MEDIA_TYPES), help="image, video, or document")
    parser.add_argument("--request-id", help="reuse only for a retry of the same logical post")
    parser.add_argument("--dry-run", action="store_true", help="print the payload without a network write")
    parser.add_argument("--confirm-publish", action="store_true", help="explicitly allow immediate publishing")
    args = parser.parse_args()
    try:
        media_items = build_media_items(args.media_url, args.media_type or ["image"])
        payload = build_payload(
            caption=args.caption,
            platforms=args.platforms,
            account_ids=args.account_ids,
            media_items=media_items,
        )
    except ValueError as exc:
        parser.error(str(exc))

    request_id = args.request_id or str(uuid.uuid4())
    print(f"logical request ID: {request_id}")
    if args.dry_run:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("DRY RUN: no media upload or post request was sent")
        return 0
    if not args.confirm_publish:
        parser.error("refusing to publish without --confirm-publish; use --dry-run first")
    try:
        status, response = request_json("POST", "/posts", payload=payload, request_id=request_id)
    except APIError as exc:
        print(f"FAIL: {exc}; retain the logical request ID before deciding whether to retry", file=sys.stderr)
        return 1
    post = response.get("post", response.get("existingPost", response))
    post_id = post.get("_id", "unknown") if isinstance(post, dict) else "unknown"
    post_status = post.get("status", "unknown") if isinstance(post, dict) else "unknown"
    print(f"PASS: HTTP {status}; post ID {post_id}; status {post_status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
