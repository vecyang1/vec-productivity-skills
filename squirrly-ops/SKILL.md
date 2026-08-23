---
name: squirrly-ops
description: Use when working with Squirrly SEO cloud data for any brand — reading SEO health checks, the keyword briefcase, keyword research, focus-page audits, AI-visibility, plan quota and site slots, opening the cloud.squirrly.co dashboard, or researching a topic across blog/wiki/twitter/images. Also use when the user mentions Squirrly, cloud.squirrly.co, api.squirrly.co, the Squirrly briefcase, focus pages, or a Squirrly quota.
---

# Squirrly SEO Operations

## Skill Metadata

- **Origin:** `community`
- **Source:** `https://github.com/vecyang1/vec-productivity-skills/tree/main/squirrly-ops`
- **Author:** Vec Yang
- **Created:** 2026-08-16
- **Updated:** 2026-08-17
- **Review status:** `reviewed`
- **License:** `AGPL-3.0-or-later`

A multi-brand CLI over the Squirrly SEO cloud API (`api.squirrly.co/v2`), built
by reading the vendor's own WordPress plugin source. **Squirrly publishes no API
documentation** — the endpoint map here is the only written description of this
interface I am aware of, and it was derived from the plugin, reconciled against
an independent literal parse, and confirmed against the live server.

## What you get

- 13 subcommands over 76 mapped endpoint/verb pairs
- `references/ENDPOINTS.md` — every endpoint with parameters, response shape,
  standalone usability, and risk
- Writes behind two independent locks; a metered quota that a careless call
  can spend
- A brand registry that stores **pointers to** credentials, never credentials

## Install

```bash
git clone https://github.com/vecyang1/vec-productivity-skills
cp -r vec-productivity-skills/squirrly-ops ~/.claude/skills/
mkdir -p ~/.config/squirrly-ops
cp ~/.claude/skills/squirrly-ops/config.example.json ~/.config/squirrly-ops/sites.json
chmod 600 ~/.config/squirrly-ops/sites.json
```

Then get your token. If the site already runs the Squirrly WordPress plugin it
is already stored there, in `wp_options` → `sq_options.sq_api`:

```bash
wp option get sq_options --format=json | python3 -c 'import json,sys; print(json.load(sys.stdin)["sq_api"])'
```

Put it wherever you keep secrets, export it, and point the registry at it:

```json
{"site_id": "mybrand", "site_url": "https://mybrand.com",
 "credential_ref": "env://SQUIRRLY_TOKEN_MYBRAND",
 "mutation_policy": {"allow_writes": false}}
```

## First move

```bash
python3 ~/.claude/skills/squirrly-ops/scripts/squirrly_ops.py sites
python3 ~/.claude/skills/squirrly-ops/scripts/squirrly_ops.py doctor --site <brand>
```

**`--site` is not optional, ever — not even with one brand configured.** A
Squirrly token is bound to a site by the `USER-URL` header and a plan carries
several site slots, so the day a second brand is registered an implicit default
would silently retarget every existing command. The resolved target is echoed to
stderr before any request:

**The authoritative line is `[squirrly-ops] target: https://<host> (site=<id>)`.**
Read it before trusting any output, and before any write.

## Operation router

| Need | Command |
| --- | --- |
| which brands are configured | `sites` |
| does this brand's credential work | `doctor --site <b>` |
| what plan, how much quota is left, how many site slots | `plan --site <b>` |
| what SEO work is outstanding | `checks --site <b> --todo` |
| what is actually wrong with the pages | `audit --site <b>` |
| audit a page that has never been crawled | `audit --site <b> --crawl <url> --confirm` |
| what keywords am I tracking | `keywords --site <b>` |
| what did keyword research find | `research --site <b> [--all]` |
| how are my focus pages doing | `focus --site <b>` |
| is any traffic coming from AI | `ai-visibility --site <b>` |
| open the cloud dashboard signed in | `dashboard --site <b>` |
| research a topic for content | `inspire "<topic>" --site <b>` |
| register a new site on this account | `add-brand --brand <id> --url <url> --borrow-credential-from <existing> --confirm` |
| what can this API do at all | `ops` (add `--gate serp_quota` etc. to see what is blocked and why) |
| anything else in the API | `raw <op> --site <b> --param k=v` (see `ops`) |

**`ops` lists the whole API, including what your account cannot use.** An
endpoint that is entitlement-blocked carries a `gate` and a reason rather than
being dropped from the table, because a missing endpoint and a non-existent
capability look identical to the next reader — that is how a later session
concludes Squirrly "cannot" do rank tracking when the truth is that *this plan*
carries `subscription_max_serps: 0` and a higher tier would work unchanged.
Gates in use: `serp_quota`, `needs_oauth`, `needs_wp_post_id`, `policy`.

## Credential lane

The registry at `~/.config/squirrly-ops/sites.json` (mode `0600`) holds
**pointers only**. `credential_ref` accepts:

- `env://<VAR>` — read from the environment. **Start here**; it is portable and
  needs no extra machinery. Feed it from whatever secret store you already use.
- `op://<vault>/<item>/<field>` — optional. Resolved through a 1Password
  *Service Account* bridge, so a scheduled run never hits an interactive prompt.
  This needs a `bridge_router` module on `SQUIRRLY_OPS_OP_BRIDGE_DIR`; if you
  do not have one, use `env://`.

The `op://` lane deliberately refuses the interactive personal route rather than
silently succeeding while a human happens to be at the keyboard — a biometric
prompt is a lane that does not exist when a cron job fires at 3am, and a
credential path that works only when someone is watching is worse than one that
fails honestly.

### Signed auth, once a brand has run the plugin

A signing brand needs two more registry fields, and the CLI refuses a brand that
has only one of them rather than sending a request that will fail confusingly:

```json
{"site_key_ref": "env://SQUIRRLY_SITE_KEY_MYBRAND", "blog_id": 123456}
```

The site key is `wp_options` → `sq_options.sq_site_key`. **The HMAC key is the
raw 32 bytes** — the plugin runs `hex2bin()` before signing, so passing the
64-character hex string produces a well-formed signature the server rejects.

**Read the slug: the server separates the two faults and they have opposite
remedies.**

| Slug | Meaning | Fix |
| --- | --- | --- |
| `signature_required` | no signature was sent | add `site_key_ref` **and** `blog_id` to the brand |
| `invalid_signature` | a signature was sent and is wrong | re-read the key; do **not** touch the USER-TOKEN |

`invalid_signature` covers three causes that are indistinguishable from the
response — hex-instead-of-raw, the wrong key, and a **stale** key — and the
stale case is the one that arrives without anyone changing anything. Installing
or reconnecting the Squirrly WordPress plugin on a blog the CLI already
registered makes the plugin mint its own key: the blog id survives, so no slot
is spent, but the stored copy dies silently and the Cloud offers no read-back.
**From the moment a blog runs the plugin, WordPress is the authority for its
site key.** The client picks the remedy for you — a 403 here returns what to
change, not just which guard tripped.

### Adding a brand — the plugin is one route, not the only one

The USER-TOKEN is **account-scoped**, and `USER-URL` is what selects the blog, so
a second site needs neither its own token nor the WordPress plugin:

```bash
squirrly_ops.py add-brand --brand second --url https://second.com \
  --borrow-credential-from first --confirm
```

That calls `api/user/connect`, spends one of the account's site slots, and
returns a `user_blog_id`. Cloud-side audits, focus pages and keyword research
then work for the new brand; only the in-WordPress editor assistant and
automatic post syncing need the plugin. **Prefer this route on a site that runs
no SEO plugin today** — activating Squirrly there hands it control of live
titles, meta and the sitemap, which is a change to public SEO output and not
something "connect this brand to the CLI" implies.

*Ordering is load-bearing:* the site key is generated locally, the Cloud never
returns it, and every later request for that blog must be signed with it — so
`add-brand` stores the key **before** connecting. A failed connect leaves an
unused item; a successful connect with an unstored key strands the blog.

## Safety rules

- Writes need **two** locks: `--confirm` on the command *and*
  `mutation_policy.allow_writes` in the registry. The flag proves intent; the
  registry proves the brand is meant to be writable at all.
- **A GET is not automatically safe here.** `user.dashboardlink` burns a
  single-use sign-in link and `user.token` rotates the site's URL-TOKEN; both
  are marked mutating despite the verb.
- `user.connect`, `user.login` and `user.register` are deliberately absent from
  the operation table. They create or rebind accounts.
- Quota is metered and resets monthly. `posts.crawl` and `serp.refresh` spend it.
- Never print a token, and treat **any URL this API returns as secret-bearing** —
  the dashboard link is a live credential in a path segment, where a redactor
  keyed on query parameters will not find it.

## Output contract

- `--output json` writes only JSON to stdout; every diagnostic goes to stderr,
  so the pipe stays clean. **Do not use `2>&1` on a JSON run** — merging the
  streams corrupts line 1 and makes this tool look like it emits invalid JSON.
- Missing numbers render as `unknown`, never `0`. "0 researches left" and "the
  API stopped sending this field" are opposite facts.
- List commands report `server_total` alongside the row count, so a truncated
  read cannot be mistaken for a complete one.
- `dashboard` opens the browser and does **not** print the link. `--print-url`
  is an explicit opt-in and warns first.

## Verification

```bash
cd ~/.claude/skills/squirrly-ops
python3 -B -m unittest discover -s tests -p 'test_*.py'   # 105 tests, no network
python3 scripts/e2e_check.py --site <brand>               # 10 stages, live
```

`scripts/e2e_check.py` proves the whole lane, not just auth: registry load →
brand guard → credential resolution → HMAC signing → live authenticate → a GET →
a paginated read reconciled against `server_total` → the verb table checked
against the server → a write refused without `--confirm`. It prints a redacted
receipt and exits non-zero on any failed stage. It was proven red-capable:
mutating one pinned verb turns it to exit 1, restoring it returns exit 0.

The unit suite is hermetic — it points `HOME` at a sandboxed registry, so it
never reads your real `~/.config/squirrly-ops/sites.json` and never touches the
network.

## Gotchas

Each of these cost real debugging time. They are the reason this skill exists.

- **`405` on a call that should work.** The verb is per-endpoint (40 GET reads,
  31 POST writes), assigned in the vendor plugin per PHP method. It is not
  discoverable from the response. Fix the table in `scripts/squirrly_api.py`;
  do not retry with the other verb blindly.
- **A list looks complete but is one page.** `start` and `limit` are honoured
  **only together**; sent alone each is silently ignored and the server returns
  the same first window. The authoritative row count is in `message.total`, not
  in `data`. Use `paginate()`.
- **`checks` hints look broken.** The server returns printf templates
  (`"You ranked on %s ... %s"`) that the plugin fills from local WordPress
  state. Unsubstituted templates are dropped rather than shown.
- **HTTP 200 with an empty result.** This API answers `200` for validation
  errors and names the missing field in `error` (`"The q field is required."`).
  That is free parameter discovery; it is also why status alone is never a
  verdict.
- **`403 signature_required` on calls that worked an hour ago.** Not rate
  limiting and not the token. A brand flips to signed auth the moment its plugin
  handshake sets `sq_user_blog_id`, and the plugin's own self-heal does exactly
  that. To tell "the server changed the rules" from "my client is blocked",
  replay the same credential from a second vantage point — the WordPress site
  itself — in the same minute; the site's reply carries the real error slug.
- **`connected: 0` on the WordPress side.** Probing `user.token` rotates the
  site's URL-TOKEN, leaving the stored one behaving like a bogus one. The plugin
  self-heals on its next checkin (`RemoteController.php:703-716`) — but that
  self-heal is what completes the signing handshake above, so it changes the
  auth mode for every other client of the account. Do not hand-write the option;
  do re-check whether signing became required.
- **A plan with zero SERP credits is not a broken install.** `serp.*` returning
  empty is correct when `subscription_max_serps: 0`. Check `plan --site <b>`
  before debugging. Ranking questions belong to Google Search Console, which
  gives you impressions and positions for free.
- **A WordPress SEO plugin cannot see a non-WordPress route.** If part of your
  domain is served by something else — a Worker, a proxied subpath, a headless
  frontend — no Squirrly metas or audits apply there. That is by design. But
  check *where the traffic actually is* before deciding it does not matter: a
  single route outside the plugin's reach can carry the majority of a domain's
  search impressions.

### Three that generalise past Squirrly

- **An auto-generated description can be a confident false statement, and the
  cause can be a hidden block rather than a client-side render.** A shop page
  went live telling Google **"No products found."** while serving 30 products.
  The products were fully server-rendered; the chain was three links, none
  visible from the served page: Squirrly Automation set the page-type pattern to
  `{{excerpt}}`; the page's `post_excerpt` was empty, so WordPress derived an
  auto-excerpt from `post_content`; and `post_content` contained the page
  builder's `product-list-no-products` block — a fallback that *renders* only on
  an empty query but *sits in the markup* unconditionally. So the sentence came
  from stored content that never displays. Any builder with an empty-state block
  (SureCart, WooCommerce blocks, Query Loop's "no results") can do this on a page
  that is working perfectly. It is worse than the blank it replaced: blank
  invites a fix, a sentence looks finished, and audits cannot see it — an
  `EmptyDescription` check counts only absences. **Read the served
  `<meta name="description">` of each commercial route**, because no local state
  distinguishes a good auto description from this one.
- **A purge that "does not work" may be an application-level cache no header
  describes.** After marking pages `noindex` + `nositemap`, the served
  `sitemap-pages.xml` still listed every page. Page cache purged fine, object
  cache flushed fine, `cf-cache-status: DYNAMIC` and `x-proxy-cache: MISS` both
  said no edge cache, and no static `sitemap*.xml` existed in the webroot.
  Evaluating the generator's own loop expression agreed the page should be
  skipped. **What settled it was the payload, not the headers:** the XML carried
  `<!-- generated-on="..." -->` and it was 52 minutes old. Squirrly writes
  rendered sitemaps to `wp-content/cache/squirrly/sitemap/`. Deleting those files
  regenerated it immediately. Generalises: when a purge appears not to work, look
  for a generation timestamp *inside* the artifact before re-purging. Cache
  headers describe the layers that answered; an application's own file cache is
  invisible to all of them.
- **Setting one field can fix five surfaces and miss the sixth.** Writing a
  page's snippet `description` fixed `<meta name="description">`,
  `og:description` and `twitter:description` — while the JSON-LD `description`
  kept the old text, because the JSON-LD builder reads the *pattern-expanded*
  value rather than the snippet. The durable fix was one layer down: set the
  page's `post_excerpt`, since the pattern was literally `{{excerpt}}`. That
  repaired every consumer at once. Verify by grepping the served `<head>` for the
  bad string — not by re-reading the snippet you just wrote.

## References

- `references/ENDPOINTS.md` — all 76 endpoint/verb pairs with params, response
  shape, standalone usability and risk, derived from the plugin source.
- `config.example.json` — brand-registry template.
- `scripts/squirrly_api.py` — client, verb table, pagination, credential lane.
- `scripts/squirrly_ops.py` — CLI surface.
- `scripts/e2e_check.py` — the live 10-stage gate.
- `tests/test_squirrly_api.py` — client and credential-resolution tests.
- `tests/test_contract.py` — pointer and contract gates.

## License

AGPL-3.0-or-later. See the repository `LICENSE`.
