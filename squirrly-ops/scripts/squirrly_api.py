"""Squirrly Cloud API client, brand registry, and credential resolution.

Three things live here, deliberately apart from the CLI in ``squirrly_ops.py``:

* ``Registry``  - the non-secret map of brands to site URLs and credential
  *pointers*. It never holds a secret.
* ``resolve_credential`` - turns one pointer into a token in memory, through
  the 1Password Service Account bridge (no interactive prompt) or the environment.
* ``SquirrlyClient`` - the HTTP surface. It knows the per-endpoint verb, which
  is the one thing about this API that cannot be guessed.

Endpoint truth is derived from the vendor's own open-source WordPress plugin
(``classes/RemoteController.php``); see ``references/ENDPOINTS.md``.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

API_BASE = "https://api.squirrly.co/v2/"
DASHBOARD_BASE = "https://cloud.squirrly.co/"
DEFAULT_CONFIG = Path.home() / ".config" / "squirrly-ops" / "sites.json"
# Optional: directory holding a ``bridge_router`` module that resolves op:// refs
# through a 1Password Service Account (no interactive prompt). Only needed if you
# use op:// refs; env:// works with no extra machinery. Override with
# SQUIRRLY_OPS_OP_BRIDGE_DIR.
ONEPASSWORD_SCRIPTS = Path(
    os.environ.get("SQUIRRLY_OPS_OP_BRIDGE_DIR")
    or Path.home() / ".claude" / "skills" / "1password" / "scripts"
)

# The plugin advertises its own version in a VERSQ header. The server has been
# observed to accept any integer; this mirrors plugin 14.2.2, so requests look
# like the official client rather than an unknown one.
CLIENT_VERSION = "1422"

USER_AGENT = "squirrly-ops/1.0 (+local agent CLI)"


class SquirrlyError(RuntimeError):
    """Any failure that should stop the command with a readable message."""


# --------------------------------------------------------------------------
# Endpoint table
# --------------------------------------------------------------------------
# The verb is NOT uniform across this API and is NOT discoverable from the
# response: `self::$apimethod` is assigned per PHP method in RemoteController,
# 40 GET and 31 POST. Sending the wrong one returns 405 with no hint, so the
# verb is pinned here rather than defaulted. `mutates` drives the write guard.

@dataclass(frozen=True)
class Endpoint:
    op: str
    path: str
    verb: str
    mutates: bool = False
    required: tuple[str, ...] = ()
    # Why this endpoint may return nothing useful on a given account. Reaching
    # an endpoint and getting an empty answer is the most misleading result an
    # API can give, because it looks identical whether the account lacks the
    # entitlement, lacks an OAuth connection, or genuinely owns no rows. The
    # gate is carried here so `ops` can say which of those it is *before* the
    # call, instead of the caller inferring absence from emptiness.
    #   ""                 nothing blocks it
    #   "serp_quota"       needs SERP credits; this account has 0 of 0
    #   "needs_oauth"      needs the Google account connected in the Cloud
    #   "needs_wp_post_id" keyed on a Squirrly user_post_id, so a page must
    #                      already be registered (normally by the WP plugin)
    #   "policy"           deliberately not transmitted by this CLI -- see note
    gate: str = ""
    note: str = ""


def _ep(op: str, path: str, verb: str, mutates: bool = False, *req: str,
        gate: str = "", note: str = "") -> tuple[str, Endpoint]:
    return op, Endpoint(op, path, verb, mutates, tuple(req), gate, note)


# Keyed by operation, NOT by path: two paths carry both verbs with different
# meanings -- `api/kr/suggestion` is a read as GET and a write as POST, and
# `api/ga/properties` likewise. A path-keyed table silently loses one of each
# pair, so the operation name is the key and the path is data.
ENDPOINTS: dict[str, Endpoint] = dict(
    [
        # --- account / plan (read) ---
        _ep("user.stats", "api/user/stats", "get"),
        _ep("user.checkin", "api/user/checkin", "get"),
        # Both of these are GETs that CONSUME something, which is why they are
        # marked mutating despite the verb. Measured 2026-08-16:
        #  - dashboardlink mints a SINGLE-USE sign-in link; a second GET of the
        #    same URL no longer authenticates (verified against a bogus-token
        #    control). Calling it to "test the endpoint" burns a live link.
        #  - user.token ROTATES the site's URL-TOKEN. The plugin's own docblock
        #    says "get a NEW token for the current URL". Probing it left the
        #    live install's stored sq_cloud_token behaving exactly like a bogus
        #    one (checkin returned connected:0 for both, connected:1 with none).
        #    The plugin self-heals on its next checkin, but a CLI must never
        #    call this casually. It is deliberately not exposed as a command.
        _ep("user.dashboardlink", "api/user/dashboardlink", "get", True),
        _ep("user.token", "api/user/token", "get", True),
        # --- audits (read) ---
        _ep("audits.notifications", "api/audits/notifications", "get"),
        _ep("audits.audit", "api/audits/audit", "get"),
        _ep("audits.focus", "api/audits/focus", "get"),
        _ep("audits.ai_visibility", "api/audits/ai-visibility", "get"),
        # --- briefcase / keywords (read) ---
        _ep("briefcase.get", "api/briefcase/get", "get"),
        _ep("briefcase.stats", "api/briefcase/stats", "get"),
        _ep("briefcase.labels", "api/briefcase/label/get", "get"),
        _ep("briefcase.optimize_get", "api/briefcase/optimize/get", "get"),
        # --- keyword research (read) ---
        _ep("kr.countries", "api/kr/countries", "get"),
        _ep("kr.languages", "api/kr/languages", "get"),
        _ep("kr.found", "api/kr/found", "get"),
        _ep("kr.history", "api/kr/history", "get"),
        _ep("kr.other", "api/kr/other", "get", False, "keyword"),
        _ep("kr.suggestion", "api/kr/suggestion", "get", False, "id"),
        # --- posts / pages (read) ---
        _ep("posts.audits", "api/posts/audits", "get"),
        _ep("posts.focus", "api/posts/focus", "get"),
        _ep("posts.keyword", "api/posts/keyword", "get"),
        _ep("posts.optimizations", "api/posts/optimizations", "get", False, "posts"),
        _ep("posts.innerlinks", "api/posts/innelinks", "get"),
        _ep("research.preview", "api/research/ib/preview", "get", False, "link"),
        # The "Inspiration Box" research endpoints. They are reachable in the
        # plugin only through getCustomCall($url, ...) with a *variable* path
        # (controllers/Post.php:685-689), so a literal grep for apiCall('...')
        # never finds them -- they were recovered by tracing the caller.
        # All four verified live 2026-08-16 with q=<topic>.
        _ep("inspire.blog", "api/research/ib/blog", "get", False, "q"),
        _ep("inspire.wiki", "api/research/ib/wiki", "get", False, "q"),
        _ep("inspire.twitter", "api/research/ib/twitter", "get", False, "q"),
        _ep("inspire.images", "api/research/ib/gimages", "get", False, "q"),
        # Sibling of inspire.images (gimages). The plugin builds both names from
        # a variable path, so both are kept rather than guessed away. Its extra
        # required fields were recovered from the server's own error envelope,
        # which names one missing field per reply -- free parameter discovery on
        # an API with no documentation. Verified live: q + page + nrb returns an
        # Unsplash-backed `responseData.results` array.
        _ep("inspire.images_alt", "api/research/ib/images", "get", False,
            "q", "page", "nrb"),
        _ep("tools.facebook", "api/tools/facebook", "get",
            note="Answers HTTP 200 with an EMPTY body on this account. Empty is "
                 "not proof of absence here -- the plugin passes caller args this "
                 "CLI has never had a reason to construct."),
        _ep("posts.seo_tasks", "api/posts/seo/tasks", "get"),
        # --- serp (read) ---
        # These are wired and correct. They return nothing on this account
        # because the plan carries `subscription_max_serps: 0` -- an
        # entitlement of zero, not an exhausted allowance. Kept and labelled
        # so an account that does have SERP credits can use them unchanged.
        _ep("serp.stats", "api/serp/stats", "get", gate="serp_quota"),
        _ep("serp.ranks", "api/serp/get-ranks", "get", gate="serp_quota"),
        # --- google connections (read) ---
        _ep("ga.properties", "api/ga/properties", "get", gate="needs_oauth"),
        _ep("ga.token", "api/ga/token", "get", gate="needs_oauth",
            note="Returns the GA measurement snippet, not an OAuth token."),
        _ep("gsc.token", "api/gsc/token", "get", gate="needs_oauth",
            note="Returns the Search Console site-verification code."),
        _ep("gsc.sync_kr", "api/gsc/sync/kr", "get", gate="needs_oauth",
            note="Pulls keyword suggestions out of the connected GSC property. "
                 "This is the one endpoint that turns real Search Console "
                 "queries into Briefcase candidates without spending KR quota."),
        # --- quota-consuming reads ---
        _ep("posts.crawl", "api/posts/crawl", "get", True, "url"),
        _ep("serp.refresh", "api/serp/refresh", "get", True, gate="serp_quota"),
        # --- writes ---
        _ep("kr.set_suggestion", "api/kr/suggestion", "post", True),
        _ep("ga.save_properties", "api/ga/properties", "post", True, gate="needs_oauth"),
        _ep("briefcase.add", "api/briefcase/add", "post", True, "keyword"),
        _ep("briefcase.hide", "api/briefcase/hide", "post", True, "id"),
        _ep("briefcase.hide_many", "api/briefcase/hide/keywords", "post", True, "ids"),
        _ep("briefcase.import", "api/briefcase/import", "post", True),
        _ep("briefcase.label_add", "api/briefcase/label/add", "post", True, "name"),
        _ep("briefcase.label_save", "api/briefcase/label/save", "post", True, "id"),
        _ep("briefcase.label_delete", "api/briefcase/label/delete", "post", True, "id"),
        # Replace semantics, not append: the caller sends the COMPLETE label set
        # for the keyword, and an empty string clears every label. Read the
        # current set first or a partial payload silently deletes labels.
        _ep("briefcase.label_keyword", "api/briefcase/label/keyword", "post", True, "id"),
        _ep("briefcase.label_keywords", "api/briefcase/label/keywords", "post", True, "ids"),
        _ep("briefcase.set_main", "api/briefcase/main", "post", True),
        # The optimize/* family are GETs that write. The verb says read; the
        # PHP method says `$apimethod = 'get'` while the handler adds, saves or
        # deletes an optimization record.
        _ep("briefcase.optimize_add", "api/briefcase/optimize/add", "get", True,
            gate="needs_wp_post_id"),
        _ep("briefcase.optimize_save", "api/briefcase/optimize/save", "get", True,
            gate="needs_wp_post_id"),
        _ep("briefcase.optimize_delete", "api/briefcase/optimize/delete", "get", True, "id"),
        _ep("briefcase.serp_add", "api/briefcase/serp", "post", True, gate="serp_quota"),
        _ep("briefcase.serp_add_many", "api/briefcase/serp/keywords", "post", True,
            gate="serp_quota"),
        _ep("briefcase.serp_delete", "api/briefcase/serp-delete", "post", True,
            gate="serp_quota"),
        _ep("kr.delete_found", "api/kr/found/delete", "post", True, "id"),
        _ep("posts.set_focus", "api/posts/set-focus", "post", True),
        _ep("posts.update_focus", "api/posts/update-focus", "post", True,
            gate="needs_wp_post_id"),
        _ep("posts.remove_focus", "api/posts/remove-focus/{user_post_id}", "post", True,
            "user_post_id", gate="needs_wp_post_id"),
        _ep("posts.set_audit", "api/posts/set-audit", "post", True),
        _ep("posts.update_audit", "api/posts/update-audit", "post", True),
        _ep("posts.remove_audit", "api/posts/remove-audit/{user_post_id}", "post", True,
            "user_post_id"),
        _ep("posts.set_innerlink", "api/posts/set-innelink", "post", True,
            gate="needs_wp_post_id",
            note="Vendor spelling: 'innelink', not 'innerlink'."),
        _ep("posts.delete_innerlink", "api/posts/delete-innelink", "post", True,
            gate="needs_wp_post_id"),
        _ep("posts.update", "api/posts/update", "post", True, gate="needs_wp_post_id",
            note="How the WordPress plugin pushes a saved post's SEO state to the "
                 "Cloud. Sending it by hand can overwrite what the plugin knows."),
        _ep("gsc.index", "api/gsc/index", "post", True, "urls", gate="needs_oauth",
            note="Submits URLs to Google's Indexing API through the Cloud."),
        _ep("user.save_settings", "api/user/settings", "post", True),
        _ep("user.feedback", "api/user/feedback", "post", True),
        # Registers a URL as a blog under this account and returns its
        # user_blog_id. Generate the site key yourself and STORE IT FIRST: the
        # Cloud never returns it, and every later request for that blog has to
        # be signed with it.
        _ep("user.connect", "api/user/connect", "post", True, "site_key", "site_uuid"),
        # Disconnects the Google account from the Cloud for this blog. Verb is
        # GET; effect is destructive and account-wide for the integration.
        _ep("ga.revoke", "api/ga/revoke", "get", True, gate="needs_oauth"),
        _ep("gsc.revoke", "api/gsc/revoke", "get", True, gate="needs_oauth"),
        # --- present in the contract, deliberately not transmitted ---
        # These two POST an account password (login) or create an account
        # (register). They are listed so `ops` is a complete map of the API
        # rather than a map of what happened to be convenient, and refused at
        # build_request so no code path here can put a password on the wire.
        _ep("user.login", "api/user/login", "post", True, gate="policy",
            note="Posts the account password. Use the Squirrly dashboard; this "
                 "CLI reads its token from 1Password and never handles one."),
        _ep("user.register", "api/user/register", "post", True, gate="policy",
            note="Creates a Squirrly account. Account creation is a human step."),
    ]
)

#: Gates whose endpoints are wired and correct but cannot return useful data on
#: an account that lacks the entitlement or connection. Kept separate from the
#: table so a caller can explain an empty answer without re-deriving why.
GATE_REASONS = {
    "serp_quota": "needs SERP credits (this plan reports subscription_max_serps: 0)",
    "needs_oauth": "needs the Google account connected to this blog in the Squirrly Cloud",
    "needs_wp_post_id": "needs a Squirrly user_post_id, so the page must be registered first",
    "policy": "not transmitted by this CLI",
}


# --------------------------------------------------------------------------
# Brand registry
# --------------------------------------------------------------------------

@dataclass
class Site:
    site_id: str
    site_url: str
    credential_ref: str
    label: str = ""
    notes: str = ""
    mutation_policy: dict[str, Any] = field(default_factory=dict)
    # Signed auth. Once the site's WordPress plugin completes its handshake the
    # server sets a blog id and then *requires* an X-SQ-Sig on every call,
    # answering 403 `signature_required` without one. Both fields are needed
    # together: the plugin itself skips signing when either is missing.
    site_key_ref: str = ""
    blog_id: int | str = ""
    origin: str = ""

    @property
    def host(self) -> str:
        return urllib.parse.urlsplit(self.site_url).netloc or self.site_url

    def may_write(self) -> bool:
        return bool(self.mutation_policy.get("allow_writes", False))


class Registry:
    """The non-secret brand map. Holds pointers to credentials, never values."""

    def __init__(self, path: Path, sites: dict[str, Site], defaults: dict[str, Any]):
        self.path = path
        self.sites = sites
        self.defaults = defaults

    @classmethod
    def load(cls, explicit: str | None = None) -> "Registry":
        raw_path = explicit or os.environ.get("SQUIRRLY_OPS_CONFIG") or str(DEFAULT_CONFIG)
        path = Path(raw_path).expanduser()
        if not path.is_file():
            raise SquirrlyError(
                f"No brand registry at {path}.\n"
                f"Create one from the template:\n"
                f"  mkdir -p {path.parent}\n"
                f"  cp {Path(__file__).resolve().parent.parent / 'config.example.json'} {path}\n"
                f"  chmod 600 {path}\n"
                f"Then edit it, or point --config / $SQUIRRLY_OPS_CONFIG elsewhere."
            )
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SquirrlyError(f"{path} is not valid JSON: {exc}") from exc

        sites: dict[str, Site] = {}
        for entry in doc.get("sites", []):
            missing = [k for k in ("site_id", "site_url", "credential_ref") if not entry.get(k)]
            if missing:
                raise SquirrlyError(
                    f"{path}: a site entry is missing {', '.join(missing)}. "
                    "Every brand needs an id, a URL, and a credential pointer."
                )
            site = Site(
                site_id=entry["site_id"],
                site_url=entry["site_url"].rstrip("/"),
                credential_ref=entry["credential_ref"],
                label=entry.get("label", ""),
                notes=entry.get("notes", ""),
                mutation_policy=entry.get("mutation_policy", {}),
                site_key_ref=entry.get("site_key_ref", ""),
                blog_id=entry.get("blog_id", ""),
                origin=entry.get("origin", ""),
            )
            if site.site_id in sites:
                raise SquirrlyError(f"{path}: duplicate site_id {site.site_id!r}.")
            sites[site.site_id] = site
        return cls(path, sites, doc.get("defaults", {}))

    def select(self, selector: str | None) -> Site:
        """Resolve --site. Fails closed and enumerates; never guesses.

        Naming a site is the strongest signal available, so an explicit
        selection wins outright. There is deliberately no implicit default even
        when only one brand is configured -- a registry grows, and a command
        that silently picked "the only one" keeps working against the wrong
        brand on the day a second is added.
        """
        if not self.sites:
            raise SquirrlyError(f"{self.path} defines no sites.")
        if not selector:
            listed = ", ".join(sorted(self.sites))
            raise SquirrlyError(
                f"--site is required. Configured brands: {listed}. "
                "(There is no default even with one brand configured, so that "
                "adding a second cannot silently retarget existing commands.)"
            )
        if selector in self.sites:
            return self.sites[selector]
        # accept a bare host as a convenience, but only on an exact match
        for site in self.sites.values():
            if selector == site.host or selector.rstrip("/") == site.site_url:
                return site
        listed = ", ".join(sorted(self.sites))
        raise SquirrlyError(
            f"Unknown --site {selector!r}. Configured brands: {listed}. "
            "Names are matched exactly so a typo cannot silently target another brand."
        )


# --------------------------------------------------------------------------
# Credential resolution
# --------------------------------------------------------------------------

_OP_REF = re.compile(r"^op://[^/]+/[^/]+/[^/]+$")


def resolve_credential(ref: str) -> str:
    """Resolve one credential pointer to a token, in memory.

    ``env://NAME``  - read from the environment. This is the portable lane and
                      the one to start with: export the token from whatever
                      secret store you already use, and nothing else is needed.
    ``op://v/i/f``  - read through the Service Account bridge. Never bare ``op``:
                      that runs in personal mode and raises an interactive
                      biometric prompt, which is exactly the lane that does not
                      exist when a scheduled job fires. Requires a
                      ``bridge_router`` module on SQUIRRLY_OPS_OP_BRIDGE_DIR.
    """
    if ref.startswith("env://"):
        name = ref[len("env://"):]
        value = os.environ.get(name, "")
        if not value:
            raise SquirrlyError(
                f"credential_ref points at ${name} but that variable is empty. "
                "Export it before running, or declare it in your scheduler's "
                "environment spec."
            )
        return value

    if not _OP_REF.match(ref):
        raise SquirrlyError(
            f"Unsupported credential_ref {ref!r}. "
            "Use 'op://<vault>/<item>/<field>' or 'env://<VAR>'."
        )

    if str(ONEPASSWORD_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(ONEPASSWORD_SCRIPTS))
    try:
        import bridge_router  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise SquirrlyError(
            f"credential_ref {ref!r} needs a 1Password Service Account bridge, but no "
            f"'bridge_router' module was found in {ONEPASSWORD_SCRIPTS} ({exc}). "
            "Set SQUIRRLY_OPS_OP_BRIDGE_DIR, or use 'env://<VAR>' instead."
        ) from exc

    cmd = ["op", "read", "--no-newline", ref]
    route = bridge_router.route_for_command(cmd, service_bridge_available=True)
    if route != "service_account":
        raise SquirrlyError(
            f"Refusing to resolve {ref} over the {route!r} route: that prompts "
            "interactively and would not exist in a scheduled run. Start your "
            "Service Account bridge first, or use 'env://<VAR>'."
        )
    result = bridge_router.run_command(cmd, timeout=120)
    token = (result.get("stdout") or "").strip()
    if not token:
        err = (result.get("stderr") or "").strip()[:200]
        raise SquirrlyError(f"1Password returned no value for {ref}. Bridge said: {err or '(nothing)'}")
    return token


# --------------------------------------------------------------------------
# HTTP client
# --------------------------------------------------------------------------

SIG_PREFIX = "sha256="


def build_signed_headers(*, method: str, path: str, body: str, url: str,
                         blog_id: Any, user_token: str, site_key_hex: str,
                         origin: str = "", timestamp: int | None = None,
                         nonce: str | None = None) -> dict[str, str]:
    """Build the X-SQ-* signature headers, mirroring the vendor plugin.

    Two details are load-bearing and neither is visible from a response:

    * **The HMAC key is the raw 32 bytes, not the 64-char hex string.** The
      plugin runs ``hex2bin()`` before ``hash_hmac``, so signing the hex text
      produces a perfectly well-formed signature the server rejects.
      **Corrected 2026-08-17:** an earlier version of this docstring said that
      rejection is worded identically to sending no signature. It is not -- the
      server separates them cleanly, and the distinction is the whole diagnosis:

        no signature at all  -> 403 ``signature_required``
        any wrong signature  -> 403 ``invalid_signature``
          (hex-instead-of-raw, wrong key, and a stale key all land here)

      That claim was written from inference rather than from a run: once signing
      worked, the failure modes theorised along the way were never exercised, and
      the theory got recorded with the confidence of an observation. Measured
      against the live API on 2026-08-17 with three deliberate variants.
    * **The signed path excludes the query string** and is the module path with
      a single leading slash (``/api/user/checkin``), not the full URL.

    Returns ``{}`` when either the key or the blog id is missing, which is the
    plugin's own rule -- an account that has not completed the handshake must
    send no signature rather than a partial one.
    """
    key_hex = (site_key_hex or "").strip()
    if not blog_id or len(key_hex) != 64:
        return {}
    try:
        key = bytes.fromhex(key_hex)
    except ValueError:
        raise SquirrlyError("site key is not valid hex; expected 64 hex characters.") from None

    stamp = int(time.time()) if timestamp is None else int(timestamp)
    use_nonce = secrets.token_hex(16) if nonce is None else nonce
    canonical = "\n".join([
        method.upper(),
        "/" + path.lstrip("/"),
        hashlib.sha256(body.encode("utf-8")).hexdigest(),
        url,
        str(stamp),
        use_nonce,
    ])
    signature = SIG_PREFIX + hmac.new(key, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
    return {
        "X-SQ-Blog-Id": str(blog_id),
        "X-SQ-User-Token": user_token,
        "X-SQ-Url": url,
        "X-SQ-Origin": origin or url,
        "X-SQ-Timestamp": str(stamp),
        "X-SQ-Nonce": use_nonce,
        "X-SQ-Sig": signature,
    }


class SquirrlyClient:
    def __init__(self, token: str, site_url: str, *, timeout: int = 60,
                 allow_mutations: bool = False, site_key: str = "",
                 blog_id: Any = "", origin: str = ""):
        self._token = token
        self._site_key = site_key
        self.blog_id = blog_id
        self.origin = origin
        self.site_url = site_url.rstrip("/")
        self.timeout = timeout
        self.allow_mutations = allow_mutations
        # Server-reported clock offset, learned from a `clock_skew:<ts>` reply.
        self.time_offset = 0
        # Row total from the most recent call, or None when the server sent
        # none. None means "not reported" and must not be rendered as 0.
        self.last_total: Any = None

    def _headers(self) -> dict[str, str]:
        # USER-URL binds the request to one registered blog. The same token
        # against a different USER-URL is a different account context, which is
        # why the CLI never lets a site be implied.
        return {
            "USER-TOKEN": self._token,
            "USER-URL": self.site_url,
            "LANG": "en-US",
            "VERSQ": CLIENT_VERSION,
            "User-Agent": USER_AGENT,
        }

    def call(self, op: str, params: dict[str, Any] | None = None) -> Any:
        """Return the ``data`` payload. The server's row total, when it sends
        one, is left on ``self.last_total`` rather than discarded."""
        data, meta = self.call_meta(op, params)
        self.last_total = meta.get("total") if isinstance(meta, dict) else None
        return data

    def paginate(self, op: str, params: dict[str, Any] | None = None,
                 *, page_size: int = 100, max_pages: int = 50) -> tuple[list[Any], Any]:
        """Walk a list endpoint using the vendor's own ``start``/``limit`` pair.

        The two parameters are only honoured **together** -- sent alone, each is
        silently ignored and the server returns the same first window, which is
        indistinguishable from a complete answer. Stops when a window returns
        nothing new, so a server that starts ignoring the offset cannot spin
        this into an infinite loop.
        """
        collected: list[Any] = []
        seen: set[Any] = set()
        total: Any = None
        for page in range(max_pages):
            window = dict(params or {})
            window.update(start=page * page_size, limit=page_size, search=window.get("search", ""))
            data, meta = self.call_meta(op, window)
            if isinstance(meta, dict) and meta.get("total") is not None:
                total = meta["total"]
            rows = data if isinstance(data, list) else []
            fresh = [r for r in rows
                     if not isinstance(r, dict) or r.get("id") not in seen]
            for row in rows:
                if isinstance(row, dict) and row.get("id") is not None:
                    seen.add(row["id"])
            if not fresh:
                break
            collected.extend(fresh)
            if len(rows) < page_size:
                break
        self.last_total = total
        return collected, total

    def build_request(self, op: str, params: dict[str, Any] | None = None
                      ) -> tuple[Endpoint, urllib.request.Request]:
        """Validate, guard, and construct the request.

        This is a seam on purpose. Request *shape* is where every expensive fact
        about this API lives -- the verb, whether params ride in the query or the
        body, which values survive filtering -- so it has to be assertable
        without a network call. A test that stubbed the transport instead would
        replace this logic and could not observe any of it.
        """
        endpoint = ENDPOINTS.get(op)
        if endpoint is None:
            raise SquirrlyError(
                f"Unknown operation {op!r}. It is not in the verified table; "
                "the HTTP verb would have to be guessed, and guessing returns 405."
            )
        if endpoint.gate == "policy":
            raise SquirrlyError(
                f"{op} ({endpoint.path}) is in the endpoint map but this CLI will "
                f"not send it. {endpoint.note}"
            )
        path = endpoint.path
        # `is not None` deliberately, not truthiness: 0, False and "" are answers
        # the caller supplied, and dropping them would silently change the query.
        params = {k: v for k, v in (params or {}).items() if v is not None}

        missing = [k for k in endpoint.required if k not in params]
        if missing:
            raise SquirrlyError(f"{op} ({path}) requires {', '.join(missing)}.")

        # A few paths carry the id in the path rather than the payload. Consume
        # the value out of params so it is not ALSO sent in the body, which the
        # vendor's own caller does not do.
        for placeholder in re.findall(r"\{(\w+)\}", path):
            value = params.pop(placeholder, None)
            if value is None:
                raise SquirrlyError(f"{op} ({path}) requires {placeholder} in the path.")
            path = path.replace("{" + placeholder + "}", urllib.parse.quote(str(value), safe=""))

        if endpoint.mutates and not self.allow_mutations:
            raise SquirrlyError(
                f"{op} ({path}) changes server state or spends quota; "
                "pass --confirm to allow it."
            )

        url = API_BASE + path
        data = None
        body = ""
        if endpoint.verb == "get":
            if params:
                url += "?" + urllib.parse.urlencode(params, doseq=True)
        else:
            body = urllib.parse.urlencode(params, doseq=True)
            data = body.encode("utf-8")

        request = urllib.request.Request(url, data=data, method=endpoint.verb.upper())
        for key, value in self._headers().items():
            request.add_header(key, value)
        if data is not None:
            request.add_header("Content-Type", "application/x-www-form-urlencoded")

        # The signature covers the *body*, so it is built here rather than in
        # _headers(): only this function knows whether params became a query
        # string or a body, and signing the wrong one is silently rejected.
        for key, value in self._signed_headers(endpoint.verb, path, body).items():
            request.add_header(key, value)
        return endpoint, request

    def _signed_headers(self, verb: str, path: str, body: str) -> dict[str, str]:
        if not self._site_key or not self.blog_id:
            return {}
        return build_signed_headers(
            method=verb, path=path, body=body, url=self.site_url,
            blog_id=self.blog_id, user_token=self._token,
            site_key_hex=self._site_key, origin=self.origin,
            timestamp=int(time.time()) + self.time_offset,
        )

    def call_meta(self, op: str, params: dict[str, Any] | None = None) -> tuple[Any, Any]:
        endpoint, request = self.build_request(op, params)
        path = endpoint.path
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                status, body = response.status, response.read()
        except urllib.error.HTTPError as exc:
            status, body = exc.code, exc.read()
        except urllib.error.URLError as exc:
            raise SquirrlyError(f"{path}: network error contacting api.squirrly.co ({exc.reason}).") from exc

        # Read it off the request that was actually sent, not off the client's
        # configuration: whether a signature went out is what separates a stale
        # key from an unconfigured brand, and the two have opposite remedies.
        return self._unwrap(path, status, body,
                            signed=request.get_header("X-sq-sig") is not None)

    @staticmethod
    def _unwrap(path: str, status: int, body: bytes, *, signed: bool = False) -> tuple[Any, Any]:
        """Return ``(data, message)``, or raise.

        A 200 carrying an ``error`` field is a failure: this API answers 200 for
        validation errors, so status alone is not a verdict -- treating it as one
        is how a caller ends up reporting an empty result as a real answer.

        ``message`` is returned rather than dropped because the authoritative row
        total lives there (``message.total``), and without it a caller cannot
        tell a complete list from the first page of a longer one.

        The 403 branch carries the remedy rather than the diagnosis. The server
        says `signature_required` for three different faults and words them
        identically -- no signature sent, a signature made with the hex string
        instead of the raw bytes, and a signature made with a *stale* key. Only
        the caller knows which one it just did, so it is the only place the right
        remedy can be chosen. Getting this wrong is expensive in a specific way:
        the obvious reading is "the token is bad", and re-checking or rotating a
        token that was fine the whole time is the one action that cannot help.
        """
        text = body.decode("utf-8", "replace").strip()
        if status == 401 or status == 403:
            slug = ""
            try:
                parsed = json.loads(text) if text else {}
                slug = str(parsed.get("error") or "") if isinstance(parsed, dict) else ""
            except json.JSONDecodeError:
                slug = text[:80]
            if "signature" in slug.lower():
                if signed:
                    raise SquirrlyError(
                        f"{path}: HTTP {status} {slug} - a signature WAS sent, so the "
                        "site key is wrong, not missing. The usual cause is that this "
                        "blog's WordPress plugin reconnected and minted a new key: the "
                        "Cloud signs against whatever the plugin last sent and offers no "
                        "read-back, so the stored copy goes stale silently.\n"
                        "Fix: re-read wp_options -> sq_options.sq_site_key from the site "
                        "and overwrite the 1Password item named in site_key_ref. "
                        "(Second possibility: the key was signed as the 64-char hex "
                        "string; it must be the raw 32 bytes, bytes.fromhex(...).)\n"
                        "Re-checking the USER-TOKEN will not help - it is a different "
                        "credential and this error does not implicate it."
                    )
                raise SquirrlyError(
                    f"{path}: HTTP {status} {slug} - this blog requires a signed "
                    "request and none was sent. Its registry entry needs BOTH "
                    "site_key_ref and blog_id; holding one without the other is the "
                    "state that produces this error."
                )
            raise SquirrlyError(
                f"{path}: HTTP {status} - the token was rejected for this USER-URL"
                + (f" ({slug})" if slug else "") + ". "
                "Check that the credential belongs to this brand."
            )
        if status == 405:
            raise SquirrlyError(
                f"{path}: HTTP 405 - wrong HTTP verb for this endpoint. "
                "The verb table in squirrly_api.ENDPOINTS is out of date."
            )
        if not text:
            raise SquirrlyError(f"{path}: HTTP {status} with an empty body.")
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            raise SquirrlyError(f"{path}: HTTP {status} returned non-JSON ({len(body)} bytes).") from None
        if status >= 400:
            raise SquirrlyError(f"{path}: HTTP {status} - {str(payload)[:200]}")

        if isinstance(payload, dict):
            error = payload.get("error")
            if error:
                if isinstance(error, list):
                    error = "; ".join(str(item) for item in error)
                raise SquirrlyError(f"{path}: {error}")
            if "data" in payload:
                return payload["data"], payload.get("message")
        return payload, None


def decode_embedded_json(value: Any) -> Any:
    """Several fields arrive as JSON *inside* a JSON string (``audit``, ``data``,
    ``related``). Decode when possible; return the original when not, so a
    format change degrades to the raw string instead of losing the field."""
    if not isinstance(value, str) or not value.strip().startswith(("{", "[")):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value
