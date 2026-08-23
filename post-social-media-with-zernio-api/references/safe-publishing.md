# Safe Direct-Publishing Checklist

1. Obtain an API key through a secret manager and expose it only as
   `ZERNIO_API_KEY` to the command that needs it.
2. Read connected accounts and pair every requested platform with its explicit
   account ID. Do not treat a platform name as a destination.
3. Check the current platform-specific media constraints in the official Zernio
   documentation. For local media, request a presigned URL, upload directly to
   it, then use its returned `publicUrl` in `mediaItems`.
4. Run the local dry-run command and review its exact payload. This check must
   precede a real publish.
5. Publish only after the requester has approved the caption, media, and every
   destination. Record the generated logical request ID.
6. On a network error, timeout, or 5xx response, retry only that same payload
   with the same request ID. On a `409`, inspect the existing post; do not
   change the request ID to bypass duplicate protection.
7. Treat an API success as a transport receipt, then inspect the returned post
   status. `partial` and `failed` require platform-specific remediation.

The provider's current documentation is authoritative:
[Quickstart](https://docs.zernio.com/),
[media uploads](https://docs.zernio.com/guides/media-uploads),
[idempotency](https://docs.zernio.com/guides/idempotency), and
[error handling](https://docs.zernio.com/guides/error-handling).
