---
name: post-social-media-with-zernio-api
description: Use when safely validating destinations or publishing an explicitly approved social post through the Zernio API (formerly Late/GetLate), with exact targets, dry runs, and idempotent retry handling.
license: MIT
---

# Publish Social Media with the Zernio API

Use the Zernio API to verify connected social destinations and publish an
explicitly approved post. Zernio is the current name; Late and GetLate are
legacy names. This public package deliberately covers direct publishing only;
it does not automate Inbox messages, workflows, Ads, or account setup.

## Contract

- API base: `https://zernio.com/api/v1`.
- Credential: pass `ZERNIO_API_KEY` through the process environment. Never put
  a key in the repository, a command argument, a log, or a committed `.env`.
- Select destinations with paired `--platforms` and `--account-ids`. A missing
  or mismatched target fails closed; never infer an account from a platform.
- Run a dry run before a live call. A live call additionally requires
  `--confirm-publish`.
- The helper generates an `x-request-id` for one logical post. Preserve it and
  reuse it only when retrying that exact request after a timeout, connection
  error, or server failure.
- Do not alter a reviewed caption with automatic hashtags, tones, or other
  platform-specific copy. The helper sends the exact caption it receives.
- For media, use Zernio's documented presigned-upload flow and pass the
  resulting HTTPS `publicUrl` as a `--media-url`. The helper does not upload a
  local file or print provider response bodies.

## Setup

Create a Zernio API key in the dashboard and inject it only into the current
process. The official API documentation is the authority for keys, endpoints,
platform rules, uploads, errors, and rate limits.

```bash
export ZERNIO_API_KEY='<your-api-key>'
```

## Safe publishing path

1. Read the connected-account inventory. Use `--show-account-ids` only when
   you need to select exact destinations; treat the output as private operator
   data.
2. Validate the exact platform/account pairs intended for the post.
3. Prepare media with the official presigned-upload flow if needed. Confirm
   platform-specific media requirements before publishing.
4. Run `post_content.py --dry-run` with the reviewed caption, media URLs, and
   exact pairs. Confirm the printed payload has no unintended destination.
5. Publish only after the requester approves the exact content and targets.
   Retain the logical request ID and final status receipt.
6. On an uncertain result, do not create a new logical post. Reuse the same
   `--request-id` only for the same request; inspect provider state before any
   other action.

```bash
# Read-only inventory. IDs appear only with this explicit flag.
python3 scripts/verify_connection.py --show-account-ids

# Read-only exact-target preflight.
python3 scripts/verify_connection.py \
  --platforms twitter linkedin \
  --account-ids '<twitter-account-id>' '<linkedin-account-id>'

# Build and inspect the exact payload. No upload or post request is sent.
python3 scripts/post_content.py \
  --caption 'Approved caption' \
  --platforms twitter linkedin \
  --account-ids '<twitter-account-id>' '<linkedin-account-id>' \
  --media-url 'https://media.example/approved-image.jpg' \
  --media-type image \
  --dry-run

# Live publish after explicit approval. Save the emitted request ID as receipt.
python3 scripts/post_content.py \
  --caption 'Approved caption' \
  --platforms twitter linkedin \
  --account-ids '<twitter-account-id>' '<linkedin-account-id>' \
  --confirm-publish
```

## Failure handling

- `401`: missing, invalid, revoked, or expired key. Repair credentials outside
  the repository and retry the preflight, not a blind publish.
- `403`: the key is valid but lacks entitlement or access. Check the account
  and provider plan; do not fall back to another account.
- `409`: Zernio detected recently duplicated content. Inspect the provider's
  existing-post reference instead of sending another post.
- `429`: follow the provider's retry guidance. Keep the same logical request ID
  only for the exact same post.
- `partial` or `failed`: record the returned post ID/status and resolve each
  platform-specific failure before retrying.

## References

- [Safe direct-publishing checklist](references/safe-publishing.md)
- [Zernio Quickstart](https://docs.zernio.com/)
- [Media uploads](https://docs.zernio.com/guides/media-uploads)
- [Idempotency and safe retries](https://docs.zernio.com/guides/idempotency)
- [Error handling](https://docs.zernio.com/guides/error-handling)
