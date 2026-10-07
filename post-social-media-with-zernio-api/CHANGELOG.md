# Changelog

All notable changes to `post-social-media-with-zernio-api` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to Semantic Versioning.

## [Unreleased]

### Added
- **Upstream Capability Awareness (Zernio Messaging API & Ad Pixels)**:
  - Detected Zernio's major platform expansion from social posting to unified communication:
    - **Messaging API**: One unified endpoint supporting SMS, MMS, RCS, and iMessage outbound messaging and unified two-way replies.
    - **Unified Ad Pixel API**: One API for cross-platform ad conversion pixels.
    - **Branded Calling**: Verified caller identity integration.
  - Roadmap Candidate: Prepare `send_message.py` and inbound webhook handler functions to allow local agents to trigger SMS/MMS/iMessage customer updates via Zernio.

## [1.0.0] - 2026-08-09

### Added
- Initial public release of `post-social-media-with-zernio-api`.
- Verified multi-platform social media publishing via Zernio API v1.
- Preflight connection check (`scripts/verify_connection.py`) with `--show-account-ids` and dry-run confirmation.
- Safe content publisher (`scripts/post_content.py`) with `--dry-run`, `--confirm-publish`, and idempotent `x-request-id` retry handling.
