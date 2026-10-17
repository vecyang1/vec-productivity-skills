# Changelog

All notable changes to `post-social-media-with-zernio-api` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to Semantic Versioning.

### [2026-10-17] - Upstream Vendor Capability Expansion (Discovered)
- **Upstream Announcement**: Zernio API Changelog Rollup (30 new features, 7 breaking changes; latest: DELETE /v1/inbox/conversations/{conversationId}, GET /v1/support/runs) (2026-10-15 12:43)
- **Detected Capabilities**: 30 New API Features & 7 Breaking Changes, DELETE /v1/inbox/conversations/{conversationId}, GET /v1/support/runs, GET /v1/ads/targeting/browse, GET /v1/ads/targeting/search
- **Roadmap Candidate**: 💡 在关联技能【post-social-media-with-zernio-api】中核对新增端点 (DELETE /v1/inbox/conversations/{conversationId}, GET /v1/support/runs, GET /v1/ads/targeting/browse) 与 7 项 Breaking Changes，保持 API 客户端契约同步。

### [2026-10-16] - Upstream Vendor Capability Expansion (Discovered)
- **Upstream Announcement**: New: Reddit Ads, Commerce API and support from your code (2026-10-15 15:35)
- **Detected Capabilities**: Reddit Ads API, Commerce API (Shopify & WooCommerce), In-Code Support Agent API
- **Roadmap Candidate**: 💡 在关联技能【post-social-media-with-zernio-api】中评估扩充支持：Reddit Ads API, Commerce API (Shopify & WooCommerce), In-Code Support Agent API；更新 CHANGELOG 并让本地 Agent 保持新能力感知。

### [2026-10-16] - Upstream Vendor Capability Expansion (Discovered)
- **Upstream Announcement**: Zernio API Changelog Rollup (31 new features, 8 breaking changes; latest: DELETE /v1/inbox/conversations/{conversationId}, GET /v1/support/runs) (2026-10-15 12:43)
- **Detected Capabilities**: 31 New API Features & 8 Breaking Changes, DELETE /v1/inbox/conversations/{conversationId}, GET /v1/support/runs, GET /v1/ads/targeting/browse, GET /v1/ads/targeting/search
- **Roadmap Candidate**: 💡 在关联技能【post-social-media-with-zernio-api】中核对新增端点 (DELETE /v1/inbox/conversations/{conversationId}, GET /v1/support/runs, GET /v1/ads/targeting/browse) 与 8 项 Breaking Changes，保持 API 客户端契约同步。

### [2026-10-12] - Upstream Vendor Capability Expansion (Discovered)
- **Upstream Announcement**: New channel: iMessage (2026-09-24 16:19)
- **Detected Capabilities**: Messaging API (SMS/MMS/RCS/iMessage)
- **Roadmap Candidate**: 💡 在关联技能【post-social-media-with-zernio-api】中评估扩充支持：Messaging API (SMS/MMS/RCS/iMessage)；更新 CHANGELOG 并让本地 Agent 保持新能力感知。

### [2026-10-12] - Upstream Vendor Capability Expansion (Discovered)
- **Upstream Announcement**: New: RCS, branded calling, and one API for every ad pixel (2026-10-01 16:21)
- **Detected Capabilities**: Messaging API (SMS/MMS/RCS/iMessage), Unified Ad Pixel API, Branded Calling
- **Roadmap Candidate**: 💡 在关联技能【post-social-media-with-zernio-api】中评估扩充支持：Messaging API (SMS/MMS/RCS/iMessage), Unified Ad Pixel API, Branded Calling；更新 CHANGELOG 并让本地 Agent 保持新能力感知。

### [2026-10-12] - Upstream Vendor Capability Expansion (Discovered)
- **Upstream Announcement**: Meet the new Zernio (2026-10-05 21:31)
- **Detected Capabilities**: General Capability / Feature Update
- **Roadmap Candidate**: 💡 在关联技能【post-social-media-with-zernio-api】中评估扩充支持：General Capability / Feature Update；更新 CHANGELOG 并让本地 Agent 保持新能力感知。

### [2026-10-12] - Upstream Vendor Capability Expansion (Discovered)
- **Upstream Announcement**: New: SMS, MMS, RCS and iMessage in one API (2026-10-06 16:25)
- **Detected Capabilities**: Messaging API (SMS/MMS/RCS/iMessage)
- **Roadmap Candidate**: 💡 在关联技能【post-social-media-with-zernio-api】中评估扩充支持：Messaging API (SMS/MMS/RCS/iMessage)；更新 CHANGELOG 并让本地 Agent 保持新能力感知。

### [2026-10-12] - Upstream Vendor Capability Expansion (Discovered)
- **Upstream Announcement**: Give your agent a phone number to call (2026-10-07 16:10)
- **Detected Capabilities**: Calling API (Voice Inbound/Outbound & AI Phone Calls), AI Agent Integration
- **Roadmap Candidate**: 💡 在关联技能【post-social-media-with-zernio-api】中评估扩充支持：Calling API (Voice Inbound/Outbound & AI Phone Calls), AI Agent Integration；更新 CHANGELOG 并让本地 Agent 保持新能力感知。

## [Unreleased]

### Added
- **Upstream Capability Awareness (Zernio Calling API & AI Voice Agent Integration)**:
  - Detected Zernio's Calling API expansion:
    - **Calling API**: Inbound calls, outbound calls, browser-based calling, and AI agent phone calls from the same phone numbers already provisioned for messaging.
    - Roadmap Candidate: Evaluate `scripts/voice_call.py` or webhook routing for inbound/outbound voice interactions.
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
