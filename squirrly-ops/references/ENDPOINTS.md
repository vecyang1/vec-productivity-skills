# Squirrly Cloud API — endpoint reference

Derived from the vendor's own open-source WordPress plugin, `squirrly-seo`
v14.2.2 (`classes/RemoteController.php`), cross-checked against live probes
on 2026-08-16. There is no public API documentation; the plugin is the contract.


> **The HTTP verb is per-endpoint and is not discoverable from the response.**
> Each PHP method assigns `self::$apimethod` as its first statement. Sending the
> wrong verb returns `405` with no hint. Reads are GET, writes are POST — but do
> not infer safety from the verb: `api/user/token` and `api/user/dashboardlink`
> are GETs that consume or rotate state.


**76 distinct (path, verb) pairs.**


## Inventory

| Path | Verb | Mutates | Standalone | Purpose |
|---|---|---|---|---|
| `api/audits/ai-visibility` | GET | no | yes | Return AI-engine traffic (ChatGPT, Perplexity, Gemini, Copilot, Bing, ...) computed by the Cloud from the site's connected GA4 property. |
| `api/audits/audit` | GET | no | yes | Fetch one site audit — either the latest one, or a specific historical audit by its Cloud audit id. |
| `api/audits/focus` | GET | no | yes | Fetch the audit + stats payload for the site's Focus Pages, to be merged onto the getFocusPages rows by user_post_id. |
| `api/audits/notifications` | GET | no | yes | Fetch the Cloud's SEO-goal notification/task set for the current blog, which is then merged over the locally computed task list. |
| `api/briefcase/add` | POST | yes | yes | Adds a single keyword to the Briefcase, optionally queueing it for a SERP rank check and/or creating it hidden. |
| `api/briefcase/get` | GET | no | yes | Lists the account's Briefcase keywords with their labels, rank, research data and the posts each keyword is used in; the main paginated Briefcase tabl |
| `api/briefcase/hide` | POST | yes | yes | Removes (server-side 'hide') a single keyword from the Briefcase — the UI labels this action Delete. |
| `api/briefcase/hide/keywords` | POST | yes | yes | Bulk variant of api/briefcase/hide — removes many Briefcase keywords in one call from the table's bulk-action selector. |
| `api/briefcase/import` | POST | yes | yes | Bulk-imports a batch of keyword strings into the Briefcase, used to restore a previously exported Briefcase backup file. |
| `api/briefcase/label/add` | POST | yes | yes | Creates a new Briefcase label with a name and a colour. |
| `api/briefcase/label/delete` | POST | yes | yes | Deletes a Briefcase label. Serves both the single-label delete and the Labels-table bulk delete. |
| `api/briefcase/label/get` | GET | no | yes | Lists the account's Briefcase labels (id, name, colour), used both for the Labels admin table and to populate label pickers. |
| `api/briefcase/label/keyword` | POST | yes | yes | Sets the full label set on ONE Briefcase keyword (replace semantics — the caller always sends the complete list, and sends an empty string to clear al |
| `api/briefcase/label/keywords` | POST | yes | yes | Bulk variant of api/briefcase/label/keyword — applies one label set to many selected keywords at once. |
| `api/briefcase/label/save` | POST | yes | yes | Updates an existing Briefcase label's name and colour. |
| `api/briefcase/main` | POST | yes | needs_wp_post_id | Marks a Briefcase keyword as the main (focus) keyword for a specific WordPress post. |
| `api/briefcase/optimize/add` | GET | yes | needs_wp_post_id | Attach a Briefcase keyword to a post as an active optimization (the 'optimize with this keyword' action in the Briefcase panel). |
| `api/briefcase/optimize/delete` | GET | yes | yes | Remove one Briefcase optimization record (the delete action on a Briefcase list item). |
| `api/briefcase/optimize/get` | GET | no | needs_wp_post_id | List Briefcase keywords available for optimizing a given post, optionally filtered by search text and label IDs, rendered for the Briefcase panel. |
| `api/briefcase/optimize/save` | GET | yes | needs_wp_post_id | Persist the full set of keyword optimizations for a post (bulk replace of what the Briefcase panel currently has selected). |
| `api/briefcase/serp` | POST | yes | yes | Adds a single keyword to the Rank Checker / SERP tracking queue. |
| `api/briefcase/serp-delete` | POST | yes | yes | Delete one keyword from the Rank Checker so it is no longer tracked. |
| `api/briefcase/serp/keywords` | POST | yes | yes | Bulk-add a list of Briefcase keywords into the Rank Checker (SERP tracking) queue. |
| `api/briefcase/stats` | GET | no | yes | Returns aggregate counters for the account's Briefcase (how many keywords, labels, labelled keywords, keywords queued for SERP checking). |
| `api/ga/properties` | GET | no | needs_oauth | List the Google Analytics properties available to the connected Google account and report which one is currently selected for this site. |
| `api/ga/properties` | POST | yes | needs_oauth | Select/persist which Google Analytics property this site is bound to in the Cloud. |
| `api/ga/revoke` | GET | yes | needs_oauth | Disconnect the site's Google Analytics account from the Squirrly Cloud. |
| `api/ga/token` | GET | no | needs_oauth | Fetch the Google Analytics website tracking code (GA measurement snippet/ID) for the connected GA property. |
| `api/gsc/index` | POST | yes | needs_oauth | Submit URLs to the Google Indexing API via the Cloud (the GSC leg of the plugin's IndexNow auto-submit on post save). |
| `api/gsc/revoke` | GET | yes | needs_oauth | Disconnect the site's Google Search Console account from the Squirrly Cloud. |
| `api/gsc/sync/kr` | GET | no | needs_oauth | Pull suggested keywords from the connected Google Search Console account (keyword-research sync) so they can be added to the Rank Checker. |
| `api/gsc/token` | GET | no | needs_oauth | Fetch the Google Search Console site-verification code for the connected GSC account. |
| `api/kr/countries` | GET | no | yes | Returns the list of countries available for Keyword Research, used to populate the country dropdown on the Research screen. |
| `api/kr/found` | GET | no | yes | Returns the 'Suggested / found' keywords Squirrly discovered for the site (the Briefcase > Suggested tab), paginated. |
| `api/kr/found/delete` | POST | yes | yes | Removes / ignores one discovered keyword from the Suggested list on the Squirrly side. |
| `api/kr/history` | GET | no | yes | Returns past keyword-research runs — either a paginated list of runs, or the full keyword payload of one run when called with an id. |
| `api/kr/languages` | GET | no | yes | Returns the list of languages Squirrly supports for keyword research, used to populate the language <select> on the Research page. |
| `api/kr/other` | GET | no | yes | Returns related/suggested keyword strings for a seed keyword (step 1 of the Find New Keywords wizard, before the paid research is started). |
| `api/kr/suggestion` | GET | no | yes | Polls a previously started research job by id and returns the finished keyword rows; an empty result means the job is still running. |
| `api/kr/suggestion` | POST | yes | yes | Starts an asynchronous keyword-research job on the Squirrly cloud for a set of keywords and returns the job id to poll. |
| `api/posts/audits` | GET | no | yes | List every page registered for the GEO/AEO site audit, with its per-page audit status and score. |
| `api/posts/crawl` | GET | no | yes | Ask the Cloud to fetch/crawl one page of the site and return a rendered HTML 'Inspect URL' report shown in a modal. |
| `api/posts/delete-innelink` | POST | yes | needs_wp_post_id | Tell the cloud an inner link was removed from the site. |
| `api/posts/focus` | GET | no | yes | List every Focus Page registered for this site in the Squirrly cloud. |
| `api/posts/innelinks` | GET | no | needs_wp_post_id | Get the inner-link opportunities the cloud found pointing at a given Focus Page (note the misspelled 'innelinks' path segment). |
| `api/posts/keyword` | GET | no | needs_wp_post_id | Read back the keyword the Cloud has recorded for a given WordPress post, so the Live Assistant can prefill the keyword box (null means first-time / no |
| `api/posts/optimizations` | GET | no | needs_wp_post_id | Fetches the cloud-side optimization percentage and focus keyword for one or many WordPress posts, to fill the Squirrly column in the posts list. |
| `api/posts/remove-audit/{user_post_id}` | POST | yes | yes | Remove one page from the GEO/AEO audit. |
| `api/posts/remove-focus/{user_post_id}` | POST | yes | needs_wp_post_id | Stop monitoring a Focus Page and remove it from the cloud. |
| `api/posts/seo/tasks` | GET | no | yes | Fetch the Live Assistant's SEO task checklist, returned as a ready-to-inject HTML fragment for the assistant panel. |
| `api/posts/set-audit` | POST | yes | needs_wp_post_id | Register a new page of the site for the GEO/AEO audit. |
| `api/posts/set-focus` | POST | yes | needs_wp_post_id | Register a published WordPress post/page as a monitored Focus Page and trigger its first audit. |
| `api/posts/set-innelink` | POST | yes | needs_wp_post_id | Report to the cloud that an inner link from one post to another using a given keyword now exists (or was re-validated). |
| `api/posts/update` | POST | yes | needs_wp_post_id | Pushes a WordPress post's SEO state (keyword, chosen SEO tasks, status, permalink, author) to the Squirrly cloud; also used as a lightweight status pi |
| `api/posts/update-audit` | POST | yes | yes | Request a re-audit — of one registered audit page, or of every audit page when called with no arguments. |
| `api/posts/update-focus` | POST | yes | needs_wp_post_id | Request a re-audit of an already-registered Focus Page (also refreshes its hash/permalink). |
| `api/research/ib/blog` | GET | no | yes | Inspiration Box blog/news article search used to insert references and quote boxes. Shares the single dynamic call site at line 1140. |
| `api/research/ib/gimages` | GET | no | yes | Inspiration Box general (non-license-filtered) image search — the default image path when the 'no licence' checkbox is unchecked. Shares the single dy |
| `api/research/ib/images` | GET | no | yes | Inspiration Box image search restricted to license-free results (the 'no licence' checkbox path). |
| `api/research/ib/preview` | GET | no | yes | Server-side fetch of a remote article's readable preview (title + body) so the Inspiration Box can show a blog result inline instead of navigating awa |
| `api/research/ib/twitter` | GET | no | yes | Inspiration Box social/tweet search for quotable content. Shares the single dynamic call site at line 1140. |
| `api/research/ib/wiki` | GET | no | yes | Inspiration Box Wikipedia search; the JS builds the final article link itself from `<lang>.wikipedia.org/wiki/<title>`. Shares the single dynamic call |
| `api/research/ib/{images\|gimages\|twitter\|blog\|wiki} (variable $url, not a literal)` | GET | no | yes | Generic passthrough used only by the SEO Assistant's Inspiration Box: forwards a caller-supplied endpoint path plus query params to the Cloud and echo |
| `api/serp/get-ranks` | GET | no | yes | List the tracked keywords with their current rank rows for the Rankings table. |
| `api/serp/refresh` | GET | yes | yes | Queue a fresh SERP rank check for one keyword. |
| `api/serp/stats` | GET | no | yes | Fetch the aggregate ranking dashboard numbers (average-position trend line, top-10 count, new keywords, positive changes) for the site. |
| `api/tools/facebook` | GET | no | yes | Resolve a Facebook profile name/URL fragment into the numeric Facebook admin code used for the fb:admins meta tag. |
| `api/user/checkin` | GET | no | yes | The account/plan heartbeat: returns connection state and the whole subscription snapshot (limits, quotas, expiry, product) — the single most useful re |
| `api/user/connect` | POST | yes | no | Binds this WordPress install's generated site identity (site_key + site_uuid) to the account behind USER-TOKEN, creating or confirming the Cloud-side  |
| `api/user/dashboardlink` | GET | yes | yes | Mints a ONE-TIME sign-in URL into the Squirrly Cloud dashboard for the current account, so an admin can jump from wp-admin to the Cloud already logged |
| `api/user/feedback` | POST | yes | yes | POST a user feedback payload to Squirrly (the only POST-verb endpoint in this whole range). |
| `api/user/login` | POST | no | no | Exchanges a Squirrly.co email + password for the account's USER-TOKEN (the api token every other call depends on). |
| `api/user/register` | POST | yes | no | Creates a brand-new Squirrly.co account from an email address and returns its USER-TOKEN. |
| `api/user/settings` | POST | yes | yes | Push account-level settings from the plugin up to the Cloud user profile. |
| `api/user/stats` | GET | no | yes | Fetch account-level usage stats for the connected blog; cached in the sq_stats transient for 60s and used to decide whether keyword-research and artic |
| `api/user/token` | GET | yes | yes | Issues a fresh URL-TOKEN (the per-site cloud token) for the site identified by the USER-URL header, telling the Cloud where this site's REST API lives |

## Detail


### `api/audits/ai-visibility` — GET

*PHP:* `getAiVisibility` (RemoteController.php:2305)  
*Standalone:* `yes`  |  *Mutating:* False

Return AI-engine traffic (ChatGPT, Perplexity, Gemini, Copilot, Bing, ...) computed by the Cloud from the site's connected GA4 property.


| Param | Required | Note |
|---|---|---|
| `days_back` | no | Integer lookback window; defaults to 30 in the plugin (getValue('days_back', 30)). |

*Args evidence:* controllers/Audits.php:190-191 ($days_back = (int) getValue('days_back', 30); getAiVisibility( array( 'days_back' => $days_back ) );) inside setAiVisibility().

*Response:* $json->data is an object with ->total_visits (int), ->ai_percent (float), ->conversions (int), ->days_back (int) and ->sources (array of rows, each with ->label or ->source and ->visits). Evidence: view/Audits/Aivisibility.php:69-146 and view/Audits/AuditStats.php:267.

> **Risk:** None (read-only), but it silently returns nothing when the site has no GA4 connection — an empty result must be reported as 'GA not connected / no AI traffic', never as zero AI traffic.


### `api/audits/audit` — GET

*PHP:* `getAudit` (RemoteController.php:2277)  
*Standalone:* `yes`  |  *Mutating:* False

Fetch one site audit — either the latest one, or a specific historical audit by its Cloud audit id.


| Param | Required | Note |
|---|---|---|
| `id` | no | The CLOUD-side audit id, NOT a WordPress post ID. It originates from $audit->id in the audit list (view/Audits/AuditStats.php:393 builds the link as 'sid=' . (int) $audit->id) and  |
| `days_back` | no | Integer window for the trend data, defaulting to 30 in the plugin. |

*Args evidence:* controllers/Audits.php:115 (array('id' => $sid, 'days_back' => $days_back)), controllers/Audits.php:209 (array('days_back' => $days_back)), controllers/Audits.php:359 (array('id' => $sid)); also called with NO args at models/CheckSeo.php:2438, models/CheckSeo.php:2462, models/Assistant.php:575 and m

*Response:* $json->data is an audit object. Fields read: ->id, ->audit (map of group => array of task rows, each row having ->audit_task and ->value, merged into SQ_Models_Domain_AuditTask with ->complete), ->audit_datetime, ->next_audit_datetime, ->groups, ->urls, ->onpage, ->score, ->stats, ->error. Evidence: models/Audits.php:609-660 (prepareAudit) and view/Audits/Audit.php + view/Audits/AuditStats.php.

> **Risk:** None (read-only). Only the id-less form is used by the SEO-assistant code paths, so a CLI can call it with no arguments safely.


### `api/audits/focus` — GET

*PHP:* `getFocusAudits` (RemoteController.php:1888)  
*Standalone:* `yes`  |  *Mutating:* False

Fetch the audit + stats payload for the site's Focus Pages, to be merged onto the getFocusPages rows by user_post_id.


| Param | Required | Note |
|---|---|---|
| `post_id` | no | MISLEADING NAME: this is the CLOUD user_post_id, not a WordPress post ID. It comes from the ?sid query param, which is rendered as $view->focuspage->id, and getId() returns _user_p |
| `days_back` | no | Int, default 90 (note: a different default from the Rankings pages' 30). |

*Args evidence:* controllers/FocusPages.php:206-209 (array('post_id' => $sid, 'days_back' => $days_back), with $sid/$days_back read at :193-194). The second caller, models/CheckSeo.php:2013, passes NO args at all - so both keys are optional.

*Response:* $json->data is an array of audit objects. Fields read: user_post_id (join key), audit (a JSON STRING that the plugin json_decode()s into an object exposing ->properties and ->data->sq_seo_keywords->value), stats (also a JSON string, json_decode()d), visibility (numeric, >= 0 check). Evidence: controllers/FocusPages.php:216-225, models/CheckSeo.php:2017-2028, models/FocusPages.php:93-96.


### `api/audits/notifications` — GET

*PHP:* `getNotifications` (RemoteController.php:934)  
*Standalone:* `yes`  |  *Mutating:* False

Fetch the Cloud's SEO-goal notification/task set for the current blog, which is then merged over the locally computed task list.


*Args evidence:* classes/RemoteController.php:934 — args are the literal `array()` inline at the call site. Caller models/CheckSeo.php:1376 invokes getNotifications() with no arguments.

*Response:* RemoteController returns $json->data verbatim (checks only $json->error and isset($json->data)). The consumer at models/CheckSeo.php:1376-1416 json_decodes it to an associative array keyed by task-function name, and per key reads ['completed'] (and array_filter()s the rest); the merged local task definitions carry ['priority'], ['positive'], ['tools'] (values seen: 'Audits', 'Rankings', 'Focus Pag

> **Risk:** None — pure read. Result is written into the WP option SQ_TASKS by the caller, not by this method.


### `api/briefcase/add` — POST

*PHP:* `addBriefcaseKeyword` (RemoteController.php:1250)  
*Standalone:* `yes`  |  *Mutating:* True

Adds a single keyword to the Briefcase, optionally queueing it for a SERP rank check and/or creating it hidden.


| Param | Required | Note |
|---|---|---|
| `keyword` | yes | Non-empty string; the caller refuses the call when it is ''. |
| `do_serp` | yes | Int 0/1. Onboarding always sends 1; the Research screen sends the 'doserp' request value, default 0. When 1 the UI promises 'the rank check will be ready in a minute'. |
| `is_hidden` | yes | Int 0/1, from the 'hidden' request value; Onboarding hardcodes 0. |

*Args evidence:* controllers/Research.php:392-394 (called at :395); second, independent build at controllers/Onboarding.php:189-191 (called at :192).

*Response:* $json->data is checked and returned, but both callers ignore the return value and print a canned 'Keyword Saved!' message. No fields are read.

> **Risk:** do_serp=1 queues a SERP rank check, which consumes the account's rank-check quota. A CLI should default do_serp to 0 and require an explicit flag to spend quota. Also clears the sq_briefcase_stats transient.


### `api/briefcase/get` — GET

*PHP:* `getBriefcase` (RemoteController.php:1175)  
*Standalone:* `yes`  |  *Mutating:* False

Lists the account's Briefcase keywords with their labels, rank, research data and the posts each keyword is used in; the main paginated Briefcase table.


| Param | Required | Note |
|---|---|---|
| `start` | no | Offset, computed as (page-1)*limit. Omitted entirely by the two bare getBriefcase() calls. |
| `limit` | no | Page size, from the sq_posts_per_page option. Research.php:585 passes limit = -1 to mean 'everything' for the backup export. |
| `sort` | no | From the ssort query param, default 'rank'. |
| `order` | no | From the sorder query param, default 'asc'. |
| `search` | no | Free-text keyword filter. models/focuspages/Strategy.php:35 passes ONLY this key. |

*Args evidence:* controllers/Research.php:135-141 builds $this->args = array('start','limit','sort','order','search') and passes it at controllers/Research.php:144. Two other shapes exist: controllers/Research.php:585 ($args['limit'] = -1, called at :586) and models/focuspages/Strategy.php:35 ($args['search'] = keyw

*Response:* $json->data->results is read as the total-row count and pushed into the sq_total_records filter (RemoteController.php:1186-1188). $json->data->keywords is the row array; per-row fields consumed in view/Research/Briefcase.php: row->id, row->keyword, row->labels (array of label objects), row->count, row->posts (map of post_id => permalink), row->rank, row->do_serp, row->research->sv->absolute, row->

> **Risk:** limit = -1 pulls the entire Briefcase in one request; this is the only call site in the file that overrides the HTTP timeout (['timeout' => 60]), which is a hint the Cloud is slow on large accounts. A CLI should default to a bounded limit.


### `api/briefcase/hide` — POST

*PHP:* `removeBriefcaseKeyword` (RemoteController.php:1269)  
*Standalone:* `yes`  |  *Mutating:* True

Removes (server-side 'hide') a single keyword from the Briefcase — the UI labels this action Delete.


| Param | Required | Note |
|---|---|---|
| `keyword` | yes | The keyword STRING, not an id, passed through stripslashes(). |

*Args evidence:* controllers/Research.php:431 ($args['keyword'] = stripslashes($keyword)), called at controllers/Research.php:432.

*Response:* UNLIKE its neighbours this method does NOT unwrap ->data and does NOT check ->error: it returns the whole json_decode() result if truthy, else false (RemoteController.php:1269-1273). The caller reads nothing and always prints 'Deleted!', so a server-side failure is invisible in the UI.

> **Risk:** Destructive. Removes a keyword from the live Briefcase, and because the method swallows the error field the caller cannot tell success from failure — a CLI must read the raw envelope itself and verify with a follow-up api/briefcase/get rather than trusting the return.


### `api/briefcase/hide/keywords` — POST

*PHP:* `removeBriefcaseKeywords` (RemoteController.php:1280)  
*Standalone:* `yes`  |  *Mutating:* True

Bulk variant of api/briefcase/hide — removes many Briefcase keywords in one call from the table's bulk-action selector.


| Param | Required | Note |
|---|---|---|
| `keywords` | yes | A PHP ARRAY of keyword strings taken straight from the 'inputs' request value (checkbox values are the keyword strings, per view/Research/Briefcase.php:172). Unlike api/briefcase/i |

*Args evidence:* controllers/Research.php:928 ($args['keywords'] = $keywords, where $keywords = getValue('inputs', array()) at :925), called at controllers/Research.php:929.

*Response:* Same as api/briefcase/hide: the whole decoded JSON is returned with no ->data unwrap and no ->error check (RemoteController.php:1280-1284). The caller reads nothing and unconditionally prints 'Deleted!'.

> **Risk:** Destructive and bulk — one call can empty a large part of the Briefcase, with no error surfaced. Note the encoding difference from api/briefcase/import (raw array here, JSON string there); getting it wrong is the difference between deleting everything you named and deleting nothing.


### `api/briefcase/import` — POST

*PHP:* `importBriefcaseKeywords` (RemoteController.php:1228)  
*Standalone:* `yes`  |  *Mutating:* True

Bulk-imports a batch of keyword strings into the Briefcase, used to restore a previously exported Briefcase backup file.


| Param | Required | Note |
|---|---|---|
| `keywords` | yes | A JSON-ENCODED array of keyword strings (json_encode of a PHP array), not a plain array. The importer chunks the file into groups of 20 and fires one request per chunk. |

*Args evidence:* controllers/Research.php:672 — array('keywords' => json_encode($chunk)) built inline at the call; $chunk comes from array_chunk($keywords, 20) at controllers/Research.php:669.

*Response:* Only $json->data is checked for non-emptiness and returned; the caller at controllers/Research.php:672 discards the return value entirely and just prints a success notice. No individual fields are read.

> **Risk:** Bulk write. Deletes nothing but creates keywords in the live account, and the plugin fires it once per 20-keyword chunk with no per-chunk error handling — a bad file half-imports. Also clears the local sq_briefcase_stats transient. A CLI must confirm before running and should keep to the 20-per-request chunk size.


### `api/briefcase/label/add` — POST

*PHP:* `addBriefcaseLabel` (RemoteController.php:1338)  
*Standalone:* `yes`  |  *Mutating:* True

Creates a new Briefcase label with a name and a colour.


| Param | Required | Note |
|---|---|---|
| `name` | yes | Non-empty string; the caller refuses '' . |
| `color` | yes | Hex colour, defaults to '#ffffff' when the form omits it. |

*Args evidence:* controllers/Research.php:478-479 ($args['name'], $args['color']), called at controllers/Research.php:480.

*Response:* $json->data is returned. This is the one label caller that inspects the result: controllers/Research.php:482-486 only tests is_wp_error() and, on failure, prints $json->get_error_message() — it never reads a field (so the new label's id is not consumed by the plugin).

> **Risk:** Creates account-level state. Repeated runs will create duplicate labels — the Cloud is not asked to dedupe and the plugin does not check for an existing name. Clears the sq_briefcase_stats transient.


### `api/briefcase/label/delete` — POST

*PHP:* `removeBriefcaseLabel` (RemoteController.php:1379)  
*Standalone:* `yes`  |  *Mutating:* True

Deletes a Briefcase label. Serves both the single-label delete and the Labels-table bulk delete.


| Param | Required | Note |
|---|---|---|
| `id` | yes | POLYMORPHIC. controllers/Research.php:536 sends a single int label id; controllers/Research.php:1004 sends an ARRAY of ids under the same 'id' key for the bulk action. Both are Clo |

*Args evidence:* controllers/Research.php:536 ($args['id'] = $id, int) called at :537; and controllers/Research.php:1004 ($args['id'] = $inputs, array from getValue('inputs', array())) called at :1005.

*Response:* $json->data is checked and returned; both callers discard it and print 'Deleted!'. No fields read.

> **Risk:** Destructive, and the single/bulk overload on one key is easy to get wrong — passing an array where a scalar is expected (or vice versa) could delete more or less than intended with no error surfaced to the caller. Unlike its siblings this method does NOT clear the sq_briefcase_stats transient, so cached counters stay stale for up to 60s after a delete.


### `api/briefcase/label/get` — GET

*PHP:* `getBriefcaseLabels` (RemoteController.php:1200)  
*Standalone:* `yes`  |  *Mutating:* False

Lists the account's Briefcase labels (id, name, colour), used both for the Labels admin table and to populate label pickers.


| Param | Required | Note |
|---|---|---|
| `start` | no | Offset = (page-1)*limit. |
| `limit` | no | Page size from sq_posts_per_page. |
| `search` | no | Always sent as an empty string by the plugin; never populated. |

*Args evidence:* controllers/Research.php:181-185 builds $this->args = array('start','limit','search') and passes it at controllers/Research.php:188. Three other call sites pass nothing: controllers/Research.php:245, :791, :880.

*Response:* $json->data is returned directly and treated as an ARRAY of label objects (controllers/Research.php:196 does count($response)). Per-label fields consumed in view/Research/Labels.php: row->id, row->name, row->color. NOTE the total count is read from $json->message->total, NOT from data (RemoteController.php:1210-1212) — this endpoint puts pagination metadata on 'message' while api/briefcase/get put

> **Risk:** None; read-only.


### `api/briefcase/label/keyword` — POST

*PHP:* `saveBriefcaseKeywordLabel` (RemoteController.php:1294)  
*Standalone:* `yes`  |  *Mutating:* True

Sets the full label set on ONE Briefcase keyword (replace semantics — the caller always sends the complete list, and sends an empty string to clear all labels).


| Param | Required | Note |
|---|---|---|
| `keyword` | yes | The keyword string, not an id. |
| `labels` | yes | Comma-joined label IDs via join(',', $labels). Explicitly initialised to '' first, so an empty string is the documented 'remove all labels' value. |

*Args evidence:* controllers/Research.php:562-566 ($args['keyword'], then $args['labels'] = '' then join(',', $labels)), called at controllers/Research.php:569.

*Response:* $json->data is checked and returned; the caller discards it and prints 'Saved!'. No fields read.

> **Risk:** Full-replace on the keyword's label set — omitting a label removes it. A CLI must read the current labels (api/briefcase/get) and merge before writing, or it will silently strip labels nobody asked it to touch. Clears the sq_briefcase_stats transient.


### `api/briefcase/label/keywords` — POST

*PHP:* `saveBriefcaseKeywordsLabel` (RemoteController.php:1316)  
*Standalone:* `yes`  |  *Mutating:* True

Bulk variant of api/briefcase/label/keyword — applies one label set to many selected keywords at once.


| Param | Required | Note |
|---|---|---|
| `keywords` | yes | PHP array of keyword strings from the 'inputs' request value (bulk checkboxes). |
| `labels` | yes | Comma-joined label IDs. NOTE the join only happens when the incoming value is a non-empty array (controllers/Research.php:952-954); if no labels are selected the raw array() is pas |

*Args evidence:* controllers/Research.php:957-958 ($args['keywords'], $args['labels']), called at controllers/Research.php:959.

*Response:* $json->data is checked and returned; the caller discards it and prints 'Saved!'. No fields read.

> **Risk:** Same full-replace hazard as the singular version, multiplied across every selected keyword. The labels argument has two possible shapes in the plugin's own code (comma string vs empty array) — a CLI should always send an explicit comma string. Clears the sq_briefcase_stats transient.


### `api/briefcase/label/save` — POST

*PHP:* `saveBriefcaseLabel` (RemoteController.php:1360)  
*Standalone:* `yes`  |  *Mutating:* True

Updates an existing Briefcase label's name and colour.


| Param | Required | Note |
|---|---|---|
| `id` | yes | Squirrly label ID (int), > 0 enforced by the caller. This is a Cloud-side label id, NOT a WordPress id. |
| `name` | yes | Non-empty string. |
| `color` | yes | Hex colour, default '#ffffff'. |

*Args evidence:* controllers/Research.php:510-512 ($args['id'], $args['name'], $args['color']), called at controllers/Research.php:513.

*Response:* $json->data is checked and returned; the caller discards it and prints 'Saved!'. No fields read.

> **Risk:** Full replace of both fields — sending only a name would blank the colour, so a CLI must read the label first (api/briefcase/label/get) and resend both. Clears the sq_briefcase_stats transient.


### `api/briefcase/main` — POST

*PHP:* `saveBriefcaseMainKeyword` (RemoteController.php:1398)  
*Standalone:* `needs_wp_post_id`  |  *Mutating:* True

Marks a Briefcase keyword as the main (focus) keyword for a specific WordPress post.


| Param | Required | Note |
|---|---|---|
| `post_id` | yes | WORDPRESS post ID (int, > 0 enforced), taken from the 'post_id' request value. Meaningless without the WP install it refers to. |
| `keyword` | yes | Non-empty keyword string. |

*Args evidence:* controllers/Research.php:702-703 ($args['post_id'], $args['keyword']), called at controllers/Research.php:704.

*Response:* $json->data is checked and returned; the caller discards it and prints 'Saved!'. No fields read.

> **Risk:** Writes a post-to-keyword binding in the Cloud keyed on a WordPress post ID. From a standalone CLI the post_id is only meaningful if it matches the real site behind USER-URL — sending an arbitrary id would bind a keyword to a post that does not exist, or worse, to the wrong one.


### `api/briefcase/optimize/add` — GET

*PHP:* `addSLABriefcase` (RemoteController.php:1083)  
*Standalone:* `needs_wp_post_id`  |  *Mutating:* True

Attach a Briefcase keyword to a post as an active optimization (the 'optimize with this keyword' action in the Briefcase panel).


| Param | Required | Note |
|---|---|---|
| `post_id` | yes | WordPress post ID (JS sends $.sq_config.postID). |
| `keyword` | yes | The Briefcase keyword string being attached. |

*Args evidence:* controllers/Post.php:608-613 (ajax action `sla_briefcase_add`); browser side view/assets/js/assistant/sq_briefcase.min.js optimize(keyword) sends post_id and keyword.

*Response:* Returns $json->data verbatim if non-empty, else false; only $json->error / isset($json->data) are checked. The JS ignores the payload entirely and simply re-runs sla_briefcase_get, so no field of data is read anywhere.

> **Risk:** WRITES server-side state over an HTTP GET (self::$apimethod = 'get' at line 1081). A CLI must not treat GET as safe here — this creates a post↔keyword optimization record in the Squirrly Cloud.


### `api/briefcase/optimize/delete` — GET

*PHP:* `deleteSLABriefcase` (RemoteController.php:1121)  
*Standalone:* `yes`  |  *Mutating:* True

Remove one Briefcase optimization record (the delete action on a Briefcase list item).


| Param | Required | Note |
|---|---|---|
| `id` | yes | Cloud-side Briefcase/optimization record ID — NOT a WordPress post ID. It comes from the markup returned by api/briefcase/optimize/get, so a CLI must list first to learn valid ids. |

*Args evidence:* controllers/Post.php:631-635 (ajax action `sla_briefcase_delete`); browser side view/assets/js/assistant/sq_briefcase.min.js delete(id) sends only id.

*Response:* Returns $json->data verbatim if non-empty, else false; only $json->error / isset($json->data) are checked. The JS ignores the payload and re-runs sla_briefcase_get, so no data field is read.

> **Risk:** DESTRUCTIVE delete performed over an HTTP GET (self::$apimethod = 'get' at line 1119) with a single opaque numeric id and no confirmation parameter. This is the highest-risk endpoint in the range for a CLI: any retry, prefetch, or link-follow of the URL deletes the record. Guard it behind an explicit --yes and resolve ids from a fresh list call.


### `api/briefcase/optimize/get` — GET

*PHP:* `getSLABriefcase` (RemoteController.php:1064)  
*Standalone:* `needs_wp_post_id`  |  *Mutating:* False

List Briefcase keywords available for optimizing a given post, optionally filtered by search text and label IDs, rendered for the Briefcase panel.


| Param | Required | Note |
|---|---|---|
| `post_id` | yes | WordPress post ID (JS sends $.sq_config.postID). |
| `search` | no | Free-text keyword filter typed into the Briefcase search box; sent as '' when empty. |
| `label` | no | Comma-joined list of Briefcase label IDs collected from the active label circles (labels.join(',')); '' when no label filter. |
| `return` | no | Output format selector. The JS always sends the literal 'html', which is why the response is markup rather than a keyword array. |

*Args evidence:* controllers/Post.php:583-590 (ajax action `sla_briefcase_get`); browser side view/assets/js/assistant/sq_briefcase.min.js sends post_id, search, label, return:'html'.

*Response:* Returns $json->data verbatim. JS reads response.data.briefcase and passes it to loadList() — with return=html this is an HTML fragment. Absence of data.briefcase is treated as 'no briefcase keywords'.

> **Risk:** Read-only, but note the GET verb is misleading only for its siblings — this one really is a read. A CLI should try omitting `return` (or sending a non-html value) to see whether the Cloud will emit structured JSON instead of markup; the plugin never exercises that.


### `api/briefcase/optimize/save` — GET

*PHP:* `saveSLABriefcase` (RemoteController.php:1102)  
*Standalone:* `needs_wp_post_id`  |  *Mutating:* True

Persist the full set of keyword optimizations for a post (bulk replace of what the Briefcase panel currently has selected).


| Param | Required | Note |
|---|---|---|
| `post_id` | yes | Cast to (int) at the call site: (int)SQ_Classes_Helpers_Tools::getValue('post_id'). WordPress post ID. |
| `optimizations` | yes | JSON-encoded array — the JS sends JSON.stringify(settings.optimizations). Sent as a single string parameter, not as nested form fields. |

*Args evidence:* controllers/Post.php:653-662 (ajax action `sla_briefcase_save`); browser side view/assets/js/assistant/sq_briefcase.min.js sends post_id and optimizations:JSON.stringify(settings.optimizations).

*Response:* Returns $json->data verbatim if non-empty, else false; only $json->error / isset($json->data) are inspected. The JS .done() handler is empty — no field of data is ever read.

> **Risk:** Destructive full-replace over an HTTP GET. It also has a WordPress-side side effect the CLI cannot reproduce and must be aware of: immediately BEFORE the API call the caller runs delete_post_meta($post_id, '_sq_keywords') and delete_post_meta($post_id, 'sq_keyword') (controllers/Post.php:659-660), wiping the predefined local keywords. Calling this endpoint from a CLI changes Cloud state while leaving the WP post meta out of sync.


### `api/briefcase/serp` — POST

*PHP:* `addSerpKeyword` (RemoteController.php:1702)  
*Standalone:* `yes`  |  *Mutating:* True

Adds a single keyword to the Rank Checker / SERP tracking queue.


| Param | Required | Note |
|---|---|---|
| `keyword` | yes | Raw request value (not stripslashed on this path). The handler refuses an empty string with 'Invalid parameters.' |

*Args evidence:* controllers/Research.php:727 (`$args['keyword'] = $keyword;`), call at controllers/Research.php:728, under the sq_ajax_briefcase_doserp AJAX action; fired by `.sq_research_doserp` in view/assets/js/briefcase.min.js.

*Response:* Only truthiness is consumed: the caller tests `=== false` and turns that into 'Could not add the keyword to SERP Check.', otherwise 'The keyword is added to SERP Check.' (controllers/Research.php:728-732). No field of `$json->data` is read anywhere, so the payload shape is unverified by any consumer.

> **Risk:** Consumes plan quota — each keyword added to SERP tracking is a billable tracked keyword, and the plugin exposes no matching remove-from-SERP call in this range. Treat as an irreversible spend from a CLI and require confirmation.


### `api/briefcase/serp-delete` — POST

*PHP:* `deleteSerpKeyword` (RemoteController.php:1752)  
*Standalone:* `yes`  |  *Mutating:* True

Delete one keyword from the Rank Checker so it is no longer tracked.


| Param | Required | Note |
|---|---|---|
| `keyword` | yes | A single keyword string. Bulk delete loops this call one keyword at a time (Ranking.php:257-262) - there is no array form. |

*Args evidence:* controllers/Ranking.php:234 (inline array('keyword' => $keyword)); bulk variant builds the same single key at controllers/Ranking.php:259-261

*Response:* Returns $json->data; the caller only runs is_wp_error() on it to pick a success vs failure notice. No fields are read.

> **Risk:** Destructive - permanently removes the keyword and (presumably) its rank history from the Rank Checker. A CLI must confirm before calling.


### `api/briefcase/serp/keywords` — POST

*PHP:* `addSerpKeywords` (RemoteController.php:1727)  
*Standalone:* `yes`  |  *Mutating:* True

Bulk-add a list of Briefcase keywords into the Rank Checker (SERP tracking) queue.


| Param | Required | Note |
|---|---|---|
| `keywords` | yes | An ARRAY of keyword strings, taken straight from the AJAX `inputs` field. Sent as a POST body array, so WP form-encodes it as keywords[0]=…&keywords[1]=… |

*Args evidence:* controllers/Research.php:980-982 (case 'sq_ajax_briefcase_bulk_doserp': $args['keywords'] = $keywords)

*Response:* Returns $json->data verbatim; the single caller discards it and just prints "The keywords are added to SERP Check!". Only truthiness matters. Non-empty $json->error -> WP_Error; missing data -> WP_Error('no_data').

> **Risk:** Consumes SERP-check credits and enrols each keyword in recurring daily rank checks against the account quota.


### `api/briefcase/stats` — GET

*PHP:* `getBriefcaseStats` (RemoteController.php:1155)  
*Standalone:* `yes`  |  *Mutating:* False

Returns aggregate counters for the account's Briefcase (how many keywords, labels, labelled keywords, keywords queued for SERP checking).


*Args evidence:* models/Assistant.php:389 — every caller invokes SQ_Classes_RemoteController::getBriefcaseStats() with NO arguments (also 401, 413, 426). The $args param defaults to array() and no caller ever builds one.

*Response:* $json->data is an object of counters. Fields actually read: data->keywords, data->labels, data->keywords_labeled, data->keywords_doserp (all compared with > 0 in models/Assistant.php:392,404,416,429). The whole data object is cached in the WP transient sq_briefcase_stats for 60 seconds before being returned.

> **Risk:** None. Read-only, and the plugin short-circuits on a 60s transient, so a CLI hitting it in a loop is only rate-limited by the Cloud, not by the plugin.


### `api/ga/properties` — GET

*PHP:* `getGAProperties` (RemoteController.php:2116)  
*Standalone:* `needs_oauth`  |  *Mutating:* False

List the Google Analytics properties available to the connected Google account and report which one is currently selected for this site.


*Args evidence:* view/SeoSettings/Webmaster.php:76 and view/Connect/GoogleAnalytics.php:33 — both call getGAProperties() with no arguments.

*Response:* $json->data is an object: ->properties (array of property objects, each with ->property_id, ->website_url, ->ga_id) and ->property_id (the currently-selected property id, falsy when none chosen). Read at view/SeoSettings/Webmaster.php:77-118 and view/Connect/GoogleAnalytics.php:34-66.

> **Risk:** None (read-only).


### `api/ga/properties` — POST

*PHP:* `saveGAProperties` (RemoteController.php:2136)  
*Standalone:* `needs_oauth`  |  *Mutating:* True

Select/persist which Google Analytics property this site is bound to in the Cloud.


| Param | Required | Note |
|---|---|---|
| `property_id` | yes | Taken verbatim from the submitted form field 'property_id'; its values come from the ->property_id of the entries returned by GET api/ga/properties. |

*Args evidence:* controllers/SeoSettings.php:180-184 ($args = array(); $args['property_id'] = $property_id; then saveGAProperties($args)) in case 'sq_seosettings_ga_save'.

*Response:* Return value is discarded at the only call site (controllers/SeoSettings.php:184 immediately wp_redirect()s). The method itself would return $json->data; no fields are read anywhere.

> **Risk:** Changes which GA property feeds the site's analytics and AI-Visibility data; a wrong property_id silently repoints the reporting. Requires an existing GA OAuth connection.


### `api/ga/revoke` — GET

*PHP:* `revokeGaConnection` (RemoteController.php:2074)  
*Standalone:* `needs_oauth`  |  *Mutating:* True

Disconnect the site's Google Analytics account from the Squirrly Cloud.


*Args evidence:* controllers/SeoSettings.php:129 — called with no arguments at all (case 'sq_seosettings_ga_revoke'); the method signature takes no $args either.

*Response:* $json->data is returned as-is; the caller only tests is_wp_error() (controllers/SeoSettings.php:130) and never reads any field. The method also deletes the 'sq_checkin' transient locally on success.

> **Risk:** DESTRUCTIVE and irreversible from a CLI: it tears down the site's GA connection, and re-establishing it requires a browser Google OAuth handshake that a token-only CLI cannot perform. A CLI must guard this behind an explicit confirmation. Note the inline comment says '//post call' but the assignment is 'get'.


### `api/ga/token` — GET

*PHP:* `getGAToken` (RemoteController.php:2096)  
*Standalone:* `needs_oauth`  |  *Mutating:* False

Fetch the Google Analytics website tracking code (GA measurement snippet/ID) for the connected GA property.


*Args evidence:* controllers/SeoSettings.php:597 — called as getGAToken() with no arguments (case 'sq_ajax_ga_code'). The $args parameter defaults to array() and no caller populates it.

*Response:* $json->data is a scalar tracking code; the caller assigns it straight to $response['code'] (controllers/SeoSettings.php:600). No sub-fields.

> **Risk:** None (read-only). Returns an error / empty unless the site has an active GA connection.


### `api/gsc/index` — POST

*PHP:* `sendGSCIndex` (RemoteController.php:2226)  
*Standalone:* `needs_oauth`  |  *Mutating:* True

Submit URLs to the Google Indexing API via the Cloud (the GSC leg of the plugin's IndexNow auto-submit on post save).


| Param | Required | Note |
|---|---|---|
| `urls` | yes | Array of absolute URLs. Set as $args['urls'] = $urls in submitUrl(). Note $args is never initialised as an array first — it is created implicitly by this assignment. |

*Args evidence:* models/Indexnow.php:25-26 ($args['urls'] = $urls; SQ_Classes_RemoteController::sendGSCIndex( $args );) inside submitUrl().

*Response:* None usable. The call passes ['blocking' => false], so no body is ever read back; json_decode('') yields null and the method always falls through to WP_Error('api_error','no_data'). The single caller (models/Indexnow.php:26) discards the return value entirely.

> **Risk:** Consumes Google Indexing API quota per URL and is fire-and-forget — a CLI gets NO confirmation of success or failure and must not report success from this call. Requires an active GSC connection.


### `api/gsc/revoke` — GET

*PHP:* `revokeGscConnection` (RemoteController.php:2161)  
*Standalone:* `needs_oauth`  |  *Mutating:* True

Disconnect the site's Google Search Console account from the Squirrly Cloud.


*Args evidence:* controllers/SeoSettings.php:146 — called with no arguments (case 'sq_seosettings_gsc_revoke'); the method takes no $args parameter.

*Response:* $json->data returned as-is; the caller only tests is_wp_error() (controllers/SeoSettings.php:147). The method also deletes the 'sq_checkin' transient locally.

> **Risk:** DESTRUCTIVE and irreversible from a CLI: kills the GSC connection, and reconnecting requires a browser Google OAuth handshake. Also breaks api/gsc/sync/kr, api/gsc/token and api/gsc/index until reconnected. Guard behind explicit confirmation. Inline comment says '//post call' but the assignment is 'get'.


### `api/gsc/sync/kr` — GET

*PHP:* `syncGSC` (RemoteController.php:2184)  
*Standalone:* `needs_oauth`  |  *Mutating:* False

Pull suggested keywords from the connected Google Search Console account (keyword-research sync) so they can be added to the Rank Checker.


| Param | Required | Note |
|---|---|---|
| `max_results` | no | Hardcoded to the string '100' at the only call site. |
| `max_position` | no | Hardcoded to the string '100' at the only call site; upper bound on average SERP position of returned keywords. |

*Args evidence:* controllers/Ranking.php:129-133 ($args['max_results'] = '100'; $args['max_position'] = '100'; then syncGSC($args)) inside gscsync(), guarded by $this->checkin->connection_gsc.

*Response:* $json->data is an array of row objects, each with ->keywords, ->clicks, ->impressions, ->ctr, ->position and ->do_serp (bool: already in Rank Checker). Read at view/Ranking/Gscsync.php:57-99 and view/Research/Suggested.php:88.

> **Risk:** Read-only, but can return the WP_Error code 'token_expired' when the GSC OAuth token has lapsed (controllers/Ranking.php:135) — a CLI should surface that as 'reconnect GSC', not as a generic failure.


### `api/gsc/token` — GET

*PHP:* `getGSCToken` (RemoteController.php:2204)  
*Standalone:* `needs_oauth`  |  *Mutating:* False

Fetch the Google Search Console site-verification code for the connected GSC account.


*Args evidence:* controllers/SeoSettings.php:575 — called as getGSCToken() with no arguments (case 'sq_ajax_gsc_code'). No caller populates the optional $args.

*Response:* $json->data is a scalar code string, passed straight into SQ_Classes_Helpers_Sanitize::checkGoogleWTCode() (controllers/SeoSettings.php:578), which extracts the google-site-verification content value. No sub-fields.

> **Risk:** None (read-only).


### `api/kr/countries` — GET

*PHP:* `getKrCountries` (RemoteController.php:1429)  
*Standalone:* `yes`  |  *Mutating:* False

Returns the list of countries available for Keyword Research, used to populate the country dropdown on the Research screen.


*Args evidence:* controllers/Research.php:110 — SQ_Classes_RemoteController::getKrCountries() is called with NO arguments and is the only caller in the plugin. The $args param defaults to array().

*Response:* $json->data is returned and iterated as an ASSOCIATIVE map: view/Research/Research.php:63 does foreach ($view->countries as $key => $country) where $key is the country code used as the <option value> (matching the 'country' param elsewhere, default 'com') and $country is the display name.

> **Risk:** None; read-only reference data, a good candidate for a CLI-side cache since it is effectively static.


### `api/kr/found` — GET

*PHP:* `getKrFound` (RemoteController.php:1581)  
*Standalone:* `yes`  |  *Mutating:* False

Returns the 'Suggested / found' keywords Squirrly discovered for the site (the Briefcase > Suggested tab), paginated.


| Param | Required | Note |
|---|---|---|
| `start` | no | Offset, (spage-1)*snum. |
| `limit` | no | Page size from 'snum', defaulting to the sq_posts_per_page option. |
| `search` | no | Hardcoded '' on the default path; set from 'skeyword' if the sq_research_search action ran first. |
| `sort` | no | Only via the sq_research_search pre-population path (controllers/Research.php:358). |
| `order` | no | Only via the sq_research_search pre-population path (controllers/Research.php:359). |
| `label` | no | Comma-joined label ids, only when labels were selected (controllers/Research.php:365). |

*Args evidence:* controllers/Research.php:217-221 (args array built in suggested()), call at controllers/Research.php:225. Optional sort/order/label keys come from controllers/Research.php:356-366.

*Response:* `$json->data` is an array of rows. Fields read by view/Research/Suggested.php: `id`, `keyword`, `country`, `data`, `questions`, `labels`, `in_briefcase`, `in_innerlinks`, `from_post_id`, `to_post_id`, `user_post_id`. Pagination total again arrives as `$json->message->total` and is exposed via the `sq_total_records` filter (RemoteController.php:1591-1593).

> **Risk:** Read-only. Rows carry WordPress-side ids (`from_post_id`, `to_post_id`, `user_post_id`) that are only meaningful next to the site itself; a standalone CLI can still list them but cannot resolve them to content.


### `api/kr/found/delete` — POST

*PHP:* `removeKrFound` (RemoteController.php:1612)  
*Standalone:* `yes`  |  *Mutating:* True

Removes / ignores one discovered keyword from the Suggested list on the Squirrly side.


| Param | Required | Note |
|---|---|---|
| `keyword` | yes | Passed through stripslashes(). The handler refuses an empty string with 'Invalid params!'. |

*Args evidence:* controllers/Research.php:454 (`$args['keyword'] = stripslashes( $keyword );`), call at controllers/Research.php:455. Triggered by the sq_briefcase_deletefound AJAX action, which the UI fires from `.sq_delete_found` in view/assets/js/briefcase.min.js.

*Response:* The return value is discarded — the caller ignores it entirely and unconditionally echoes `{message:'Deleted!'}` (controllers/Research.php:457). RemoteController still returns `$json->data` when non-empty, so the payload shape is unverified by any consumer.

> **Risk:** Destructive and identified only by keyword text, with no confirmation in the API layer and no undo path exposed anywhere in the plugin. A CLI must gate this behind explicit confirmation, and must not treat a successful HTTP call as proof of deletion — nothing in the plugin reads the response back.


### `api/kr/history` — GET

*PHP:* `getKRHistory` (RemoteController.php:1551)  
*Standalone:* `yes`  |  *Mutating:* False

Returns past keyword-research runs — either a paginated list of runs, or the full keyword payload of one run when called with an id.


| Param | Required | Note |
|---|---|---|
| `start` | no | List mode. Offset computed as (spage-1)*snum. |
| `limit` | no | List mode. Page size, from the 'snum' request value defaulting to the sq_posts_per_page option. |
| `search` | no | List mode. Hardcoded to '' on the default path; populated from the 'skeyword' request value when the sq_research_search action ran first. |
| `sort` | no | Only present when the sq_research_search action pre-populated $this->args (controllers/Research.php:358). |
| `order` | no | Same conditional path as 'sort' (controllers/Research.php:359). |
| `label` | no | Comma-joined label ids; only when labels were selected in the search action (controllers/Research.php:365). |
| `id` | no | Detail mode — mutually exclusive with the pagination keys. A research-run id, not a WP post id. |

*Args evidence:* List mode: controllers/Research.php:261-265 (args array), call at controllers/Research.php:268. Detail mode: controllers/Research.php:891 (`$args['id'] = $id;`), call at controllers/Research.php:892. The extra sort/order/label keys are injected at controllers/Research.php:356-366 and survive because

*Response:* `$json->data` is an array of run rows. List fields read by view/Research/History.php: `id`, `keyword` (comma-joined seed list), `country`, `datetime`. In detail mode the caller takes `current($krHistory)` and view/Research/HistoryDetails.php reads `keyword` (exploded on ',') and `data` — a JSON *string* that decodes to an array of keyword rows with `keyword`, `in_briefcase` and the same `stats->sc

> **Risk:** Read-only. Note the pagination total lives on `$json->message->total`, not inside `data` — a CLI that only reads `data` will under-report the record count.


### `api/kr/languages` — GET

*PHP:* `getKrLanguages` (RemoteController.php:1454)  
*Standalone:* `yes`  |  *Mutating:* False

Returns the list of languages Squirrly supports for keyword research, used to populate the language <select> on the Research page.


*Args evidence:* controllers/Research.php:111 — `SQ_Classes_RemoteController::getKrLanguages();` called with NO arguments at the only call site in the plugin; $args defaults to array().

*Response:* RemoteController returns `$json->data` verbatim. The view iterates it as an associative map `$key => $language` (language code => display name) — view/Research/Research.php:74-80. Error branches read `$json->error`; missing `$json->data` becomes WP_Error('api_error','no_data').

> **Risk:** None. Pure read of a static reference list; the cheapest endpoint to use as a token/connectivity smoke test.


### `api/kr/other` — GET

*PHP:* `getKROthers` (RemoteController.php:1473)  
*Standalone:* `yes`  |  *Mutating:* False

Returns related/suggested keyword strings for a seed keyword (step 1 of the Find New Keywords wizard, before the paid research is started).


| Param | Required | Note |
|---|---|---|
| `keyword` | yes | Seed keyword. Caller aborts with 'Invalid params!' if falsy. |
| `country` | no | Google TLD-style country code; the AJAX handler defaults it to 'com'. |
| `lang` | no | Language code; the AJAX handler defaults it to 'en'. |

*Args evidence:* controllers/Research.php:756-758 (args built), call at controllers/Research.php:759; upstream values read at controllers/Research.php:744-746 with defaults country='com', lang='en'.

*Response:* `$json->data` is an object exposing `keywords` — an array of plain keyword strings. Read at controllers/Research.php:762-764 (`isset($json->keywords)` on the returned data) and consumed by view/assets/js/research.min.js as `response.keywords[i]`. The JS also branches on error values 'limit_exceeded' and 'no_data'.

> **Risk:** Can return the error code `limit_exceeded` — this suggestion lookup is metered against the plan even though it does not create anything.


### `api/kr/suggestion` — GET

*PHP:* `getKRSuggestion` (RemoteController.php:1521)  
*Standalone:* `yes`  |  *Mutating:* False

Polls a previously started research job by id and returns the finished keyword rows; an empty result means the job is still running.


| Param | Required | Note |
|---|---|---|
| `id` | yes | The Squirrly-side research job id returned by the POST to the same path. NOT a WordPress post id — the caller casts SQ_Classes_Helpers_Tools::getValue('id', 0) to int and only call |

*Args evidence:* controllers/Research.php:800 (`$args['id'] = $id;`), call at controllers/Research.php:801.

*Response:* `$json->data` is an array of keyword rows. Fields read by view/Research/ResearchDetails.php: `keyword`, `initial` (bool, the seed keyword), `in_briefcase` (bool), `labels`, and `stats` — a nested object with `stats->sc->{value,text,color}` (competition), `stats->sv->absolute` (search volume), `stats->tw->{value,text}` (recent discussions). An empty (but non-error) data array is the 'still processi

> **Risk:** Polling only. The plugin's own JS polls every 5s and gives up after ~50 attempts; a CLI should keep the same backoff rather than tight-looping.


### `api/kr/suggestion` — POST

*PHP:* `setKRSuggestion` (RemoteController.php:1502)  
*Standalone:* `yes`  |  *Mutating:* True

Starts an asynchronous keyword-research job on the Squirrly cloud for a set of keywords and returns the job id to poll.


| Param | Required | Note |
|---|---|---|
| `q` | yes | Comma-joined keyword list. In the UI it is the seed keyword plus each checked suggestion (research.min.js builds `$keywords += ',' + value`). |
| `country` | no | Defaults to 'com' at controllers/Research.php:832. |
| `lang` | no | Defaults to 'en' at controllers/Research.php:831. |
| `count` | no | Cast to int; the AJAX handler defaults to 10 and the JS defaults to 10. |

*Args evidence:* controllers/Research.php:841-844 (args built), call at controllers/Research.php:845.

*Response:* `$json->data` is an object whose only field the plugin reads is `id` — the research job id (controllers/Research.php:847-850, echoed to the browser as `{done:false, id:...}`). The method also deletes the `sq_stats` and `sq_briefcase_stats` transients before the call (RemoteController.php:1499-1500).

> **Risk:** Consumes paid keyword-research credits. The caller explicitly handles the error code `limit_exceeded` (controllers/Research.php:854). A CLI must rate-limit this and must not loop it — each call spends plan quota.


### `api/posts/audits` — GET

*PHP:* `getAuditPages` (RemoteController.php:2251)  
*Standalone:* `yes`  |  *Mutating:* False

List every page registered for the GEO/AEO site audit, with its per-page audit status and score.


*Args evidence:* controllers/Audits.php:93, controllers/Audits.php:117, controllers/Audits.php:213 — all three call sites invoke getAuditPages() with no arguments; the optional $args is never populated anywhere in the plugin.

*Response:* $json->data is an array of row objects hydrated into SQ_Models_Domain_AuditPage (controllers/Audits.php:127,222), whose fields are: id, user_post_id, post_id, hash, permalink, audit, stats, incomplete, score, indexed, audit_datetime, audit_error, datetime (models/domain/AuditPage.php:6-21).

> **Risk:** None (read-only).


### `api/posts/crawl` — GET

*PHP:* `getInspectURL` (RemoteController.php:2047)  
*Standalone:* `yes`  |  *Mutating:* False

Ask the Cloud to fetch/crawl one page of the site and return a rendered HTML 'Inspect URL' report shown in a modal.


| Param | Required | Note |
|---|---|---|
| `post_id` | yes | Despite the name this is the CLOUD-side user_post_id, not a WordPress post ID — the view sets data-post_id from $view->focuspage->user_post_id / $view->auditpage->user_post_id (vie |
| `url` | no | Optional. Added only when a 'url' request value is present, so the Cloud can inspect ANY page of the site, not just a registered focus/audit page. Passed through esc_url_raw(). |

*Args evidence:* controllers/FocusPages.php:429-437 (case 'sq_focuspages_inspecturl')

*Response:* $json->data is returned whole and used directly as an HTML string ($json['html'] in controllers/FocusPages.php:438). No sub-fields are read.

> **Risk:** Timeout is raised to 60s (['timeout' => 60]); the Cloud performs a live crawl of the URL, so it is slow and may be rate-limited. Read-only.


### `api/posts/delete-innelink` — POST

*PHP:* `deleteFocusPageInnerlink` (RemoteController.php:1950)  
*Standalone:* `needs_wp_post_id`  |  *Mutating:* True

Tell the cloud an inner link was removed from the site.


| Param | Required | Note |
|---|---|---|
| `from_post_id` | yes | WordPress post ID; falls back to the request's from_post_id when the stored record lacks it. |
| `to_post_id` | yes | WordPress post ID; defaults to 0 when the stored record lacks it. |
| `keyword` | yes | Defaults to '' when the stored record lacks it. |

*Args evidence:* controllers/FocusPages.php:811-815 (case 'sq_focuspages_deleteinnerlink')

*Response:* Returns $json->data; the caller discards it and prints "Inner Link Removed". No fields read.

> **Risk:** Destructive - drops the cloud's record of the inner link. Note this endpoint takes NO `found` key, unlike its set- counterpart.


### `api/posts/focus` — GET

*PHP:* `getFocusPages` (RemoteController.php:1863)  
*Standalone:* `yes`  |  *Mutating:* False

List every Focus Page registered for this site in the Squirrly cloud.


*Args evidence:* NO CALLER PASSES ARGS. All four call sites invoke it with an empty argument list: controllers/FocusPages.php:103, controllers/FocusPages.php:199, controllers/Onboarding.php:55, models/CheckSeo.php:2009. The $args parameter exists but is always the empty default.

*Response:* $json->data is an array of focus page objects hydrated into SQ_Models_Domain_FocusPage. Fields consumed: user_post_id (the cloud-side ID - this is what ?sid and every later focus-page call keys on), id, post_id, hash, permalink, audit, stats, visibility, incomplete, indexed, audit_datetime, audit_error, datetime. Evidence: models/domain/FocusPage.php:6-22 and controllers/FocusPages.php:211-252.


### `api/posts/innelinks` — GET

*PHP:* `getFocusPageInnerlinks` (RemoteController.php:1912)  
*Standalone:* `needs_wp_post_id`  |  *Mutating:* False

Get the inner-link opportunities the cloud found pointing at a given Focus Page (note the misspelled 'innelinks' path segment).


| Param | Required | Note |
|---|---|---|
| `post_id` | yes | The cloud user_post_id in the domain-model path ($this->id -> _user_post_id), models/domain/FocusPage.php:62. The AJAX path takes it from a raw request value that the minified JS s |
| `found` | no | Only the AJAX path sends it, hardcoded to 0 (apparently "return links not yet marked as found"). The domain-model path omits it. |

*Args evidence:* models/domain/FocusPage.php:61-63 (post_id only); controllers/FocusPages.php:487-490 (post_id + found = 0)

*Response:* $json->data is an array of inner-link objects hydrated into SQ_Models_Domain_Innerlink. Fields read: from_post_id, to_post_id, keyword (the array_intersect_key allowlist at controllers/FocusPages.php:503-512), plus found at :523. Domain also declares id, nofollow, blank, valid (models/domain/Innerlink.php:6-13).


### `api/posts/keyword` — GET

*PHP:* `getSLAKeywords` (RemoteController.php:1007)  
*Standalone:* `needs_wp_post_id`  |  *Mutating:* False

Read back the keyword the Cloud has recorded for a given WordPress post, so the Live Assistant can prefill the keyword box (null means first-time / no keyword set).


| Param | Required | Note |
|---|---|---|
| `post_id` | yes | WordPress post ID. Built as SQ_Classes_Helpers_Tools::getValue('post_id'); the JS sends $.sq_config.postID. |

*Args evidence:* controllers/Post.php:520-524 (ajax action `sla_keywords`); browser side view/assets/js/assistant/sq_blocksearch.min.js sends action:'sla_keywords', post_id:$.sq_config.postID.

*Response:* Returns $json->data verbatim. JS reads response.data.keyword (URI-encoded string, or null when no keyword is set for that post).

> **Risk:** None — pure read, gated in WP by the sq_manage_snippet capability check (controllers/Post.php:514).


### `api/posts/optimizations` — GET

*PHP:* `getPostOptimization` (RemoteController.php:1671)  
*Standalone:* `needs_wp_post_id`  |  *Mutating:* False

Fetches the cloud-side optimization percentage and focus keyword for one or many WordPress posts, to fill the Squirrly column in the posts list.


| Param | Required | Note |
|---|---|---|
| `posts` | yes | WordPress post IDs. A single bare id on the per-row AJAX path (controllers/PostsList.php:134) and a comma-joined list on the bulk path (controllers/PostsList.php:312). |

*Args evidence:* controllers/PostsList.php:134 (`$args['posts'] = $post_id;`) with the call at controllers/PostsList.php:136; and controllers/PostsList.php:312 (`$args['posts'] = join(',', ...)`) with the call at controllers/PostsList.php:314.

*Response:* `$json->data` is an object with a `posts` map keyed by post id. Each row's fields, read in models/PostsList.php::processPost (lines 15-42): `error_message` (string; when non-empty it replaces the row with an upgrade link), `keyword` (string, may be empty), `optimized` (int percentage 0-100). The caller also special-cases the WP_Error messages 'no_data' and 'maintenance' (controllers/PostsList.php:

> **Risk:** Read-only, but the request and the entire response are keyed by WordPress post IDs, so results are meaningless without the site's ID space. Bulk lists are unbounded in the plugin — a CLI should chunk them.


### `api/posts/remove-audit/{user_post_id}` — POST

*PHP:* `deleteAuditPage` (RemoteController.php:2378)  
*Standalone:* `yes`  |  *Mutating:* True

Remove one page from the GEO/AEO audit.


| Param | Required | Note |
|---|---|---|
| `user_post_id` | yes | PATH parameter, not a body/query parameter — it is concatenated into the URL ('api/posts/remove-audit/' . $args['user_post_id']) and the request body is empty. It is the CLOUD-side |

*Args evidence:* controllers/Audits.php:436 (array('user_post_id' => $post_id) where $post_id = getValue('id')) and controllers/Audits.php:458 (same, from the bulk 'inputs' array). Value origin proven at view/Audits/AuditPageRow.php:36,92.

*Response:* $json->data is returned but the return value is DISCARDED at both call sites (controllers/Audits.php:436, 458) — the UI prints a success message unconditionally. No fields are read.

> **Risk:** DESTRUCTIVE and unverified: it deletes the page's audit registration (and its audit history) in the Cloud, the plugin ignores the response, and the UI claims success even on failure. Re-adding requires api/posts/set-audit, which needs the WordPress-side hash. A CLI must confirm before calling and must read the response itself rather than copying the plugin's behaviour.


### `api/posts/remove-focus/{user_post_id}` — POST

*PHP:* `deleteFocusPage` (RemoteController.php:2020)  
*Standalone:* `needs_wp_post_id`  |  *Mutating:* True

Stop monitoring a Focus Page and remove it from the cloud.


| Param | Required | Note |
|---|---|---|
| `user_post_id` | yes | PATH SEGMENT, NOT A BODY FIELD. It is concatenated into the URL ('api/posts/remove-focus/' . $args['user_post_id']) and apiCall() is invoked with NO $args, so the POST body is empt |

*Args evidence:* controllers/FocusPages.php:251 (array('user_post_id' => $focuspage->user_post_id)) and controllers/FocusPages.php:948 (array('user_post_id' => $id))

*Response:* Returns $json->data; both callers discard it. Note the method returns false for the whole no-id branch, so 'deleted' and 'never attempted' are indistinguishable to the caller.

> **Risk:** Destructive and partly AUTOMATIC: controllers/FocusPages.php:249-251 fires this on its own whenever a focus page's local WP post can no longer be resolved. Removing the page presumably discards its audit history. A CLI must never call this speculatively.


### `api/posts/seo/tasks` — GET

*PHP:* `getSLATasks` (RemoteController.php:1045)  
*Standalone:* `yes`  |  *Mutating:* False

Fetch the Live Assistant's SEO task checklist, returned as a ready-to-inject HTML fragment for the assistant panel.


*Args evidence:* controllers/Post.php:565 — the sole caller is `SQ_Classes_RemoteController::getSLATasks();` with NO arguments, so $args falls through to its `array()` default and apiCall() appends no query string (apiCall line 102 only builds a query when !empty($args)). Note the path implies a post context but no 

*Response:* Returns $json->data verbatim. JS reads response.data.tasks and appends it directly as HTML into `.sq_tasks` (view/assets/js/assistant/sq_blockseo.min.js), i.e. data.tasks is an HTML string, not structured data.

> **Risk:** None — pure read. Response is raw HTML injected into the admin DOM by the plugin, so a CLI should treat data.tasks as untrusted markup rather than data.


### `api/posts/set-audit` — POST

*PHP:* `addAuditPage` (RemoteController.php:2331)  
*Standalone:* `needs_wp_post_id`  |  *Mutating:* True

Register a new page of the site for the GEO/AEO audit.


| Param | Required | Note |
|---|---|---|
| `post_id` | yes | The real WordPress post ID ($post->ID) of the page being registered. |
| `hash` | yes | Squirrly's local per-post hash ($post->hash), produced by SQ_Models_Snippet::getCurrentSnippet()/savePost(); it is the key the Cloud later uses to match rows back to local posts. |
| `permalink` | yes | The page URL ($post->url). |

*Args evidence:* controllers/Audits.php:382-386 ($args['post_id'] = $post->ID; $args['hash'] = $post->hash; $args['permalink'] = $post->url; then addAuditPage($args)) in case 'sq_audits_addnew'.

*Response:* $json->data is returned but no field is read — the caller only checks truthiness and is_wp_error(), and inspects get_error_message() for the sentinel 'limit_exceed' (controllers/Audits.php:386-392).

> **Risk:** Consumes the account's audit-page quota — the Cloud answers 'limit_exceed' when the plan maximum is reached. Requires a valid WP post ID plus the Squirrly-local hash, which a standalone CLI cannot compute without the WordPress side.


### `api/posts/set-focus` — POST

*PHP:* `addFocusPage` (RemoteController.php:1975)  
*Standalone:* `needs_wp_post_id`  |  *Mutating:* True

Register a published WordPress post/page as a monitored Focus Page and trigger its first audit.


| Param | Required | Note |
|---|---|---|
| `post_id` | yes | A real WordPress post ID ($post->ID). Guarded by post_status == 'publish' and $post->ID == $post_id before sending. |
| `hash` | yes | The plugin's local snippet hash for that post (an md5 of post type / dates / etc., see models/Snippet.php:466-558). A CLI cannot invent this; it is the key the cloud uses to correl |
| `permalink` | yes | $post->url. |

*Args evidence:* controllers/FocusPages.php:837-841 (case 'sq_focuspages_addnew')

*Response:* $json->data is an object; the caller reads ->user_post_id and caches a transient keyed on it (controllers/FocusPages.php:844-845). Error path: $json->error == 'limit_exceed' is special-cased and the plugin then re-reads checkin()->subscription_focus_pages / subscription_max_focus_pages / subscription_max_focus_pages_all to build the message.

> **Risk:** Consumes a Focus Page slot against both the per-site and per-account plan limits; returns 'limit_exceed' when full. Also queues a cloud audit.


### `api/posts/set-innelink` — POST

*PHP:* `setFocusPageInnerlink` (RemoteController.php:1931)  
*Standalone:* `needs_wp_post_id`  |  *Mutating:* True

Report to the cloud that an inner link from one post to another using a given keyword now exists (or was re-validated).


| Param | Required | Note |
|---|---|---|
| `from_post_id` | yes | WordPress post ID of the linking page. Cast to (int) in one lane, passed raw in the other. |
| `to_post_id` | yes | WordPress post ID of the target Focus Page. |
| `keyword` | yes | Anchor keyword. |
| `found` | yes | Result of SQ_Models_Post::checkInnerLink() - whether the keyword actually appears in the source post content. |

*Args evidence:* controllers/FocusPages.php:665-671 (add-new lane); identical 4 keys at controllers/FocusPages.php:711-717 (edit lane) and controllers/FocusPages.php:755-761 (re-check lane)

*Response:* Returns $json->data; all three callers discard the return value entirely and immediately emit "Inner link is saved." No fields read.


### `api/posts/update` — POST

*PHP:* `savePost` (RemoteController.php:1645)  
*Standalone:* `needs_wp_post_id`  |  *Mutating:* True

Pushes a WordPress post's SEO state (keyword, chosen SEO tasks, status, permalink, author) to the Squirrly cloud; also used as a lightweight status ping when a post is published, trashed or deleted.


| Param | Required | Note |
|---|---|---|
| `post_id` | yes | WordPress post ID. Present in both callers. |
| `status` | yes | WP post status; the PostsList caller substitutes the literal 'deleted' when get_post_status() returns falsy. |
| `referer` | yes | 'edit' from the post-editor path (controllers/Post.php:344), 'posts' from the post-list status hook (models/PostsList.php:137). |
| `keyword` | no | Editor path only — the sq_keyword request value, may be ''. |
| `permalink` | no | Editor path only. It is also the guard: the call is skipped entirely when permalink is falsy (controllers/Post.php:346). |
| `author` | no | Editor path only — $post->post_author (a WP user ID). |
| `seo` | no | Editor path only, and only when the sq_seo request value is a non-empty array; imploded with commas at controllers/Post.php:336. |

*Args evidence:* Fullest caller: controllers/Post.php:336-344 (args built in sendSeo()), call at controllers/Post.php:347. Minimal caller: models/PostsList.php:135-137 (status/post_id/referer), call at models/PostsList.php:139.

*Response:* Effectively none. The call passes `['timeout' => 5, 'blocking' => false]` (RemoteController.php:1645), so no body is ever returned — json_decode('') yields null and every branch below it (`$json->error`, `$json->data`) is dead code. The comment at RemoteController.php:1643-1644 states outright that no caller uses the response. Side effect: deletes the `sq_stats` transient (RemoteController.php:164

> **Risk:** Writes server-side state keyed to a WordPress post ID that a standalone CLI cannot verify, and gives back nothing to verify with — the fire-and-forget flag makes success indistinguishable from failure at the call site. Sending a wrong post_id/status pair (e.g. status='deleted') could mark live content as gone in the cloud with no read-back available from this endpoint.


### `api/posts/update-audit` — POST

*PHP:* `updateAudit` (RemoteController.php:2351)  
*Standalone:* `yes`  |  *Mutating:* True

Request a re-audit — of one registered audit page, or of every audit page when called with no arguments.


| Param | Required | Note |
|---|---|---|
| `post_id` | no | MISLEADING NAME: the value actually sent is the CLOUD-side user_post_id, not a WordPress post ID — view/Audits/AuditPageRow.php:77 renders <input name="post_id" value="<?php echo ( |

*Args evidence:* controllers/Audits.php:405-409 (array built as $args['post_id'] = (int) getValue('post_id')), controllers/Audits.php:483 (array('post_id' => $post_id) from bulk inputs), controllers/Audits.php:424 (updateAudit() with NO args = re-audit everything). Value origin proven at view/Audits/AuditPageRow.php

*Response:* $json->data is returned but no field is read — the caller checks is_wp_error() and matches get_error_message() against the sentinel 'too_many_attempts' (controllers/Audits.php:410-414, 425-428).

> **Risk:** Rate-limited and quota-consuming: the Cloud returns 'too_many_attempts' — one audit per page per hour, and the all-pages form once per hour. The no-argument form fans out across every registered page, so a CLI must not send it casually or in a loop.


### `api/posts/update-focus` — POST

*PHP:* `updateFocusPage` (RemoteController.php:1994)  
*Standalone:* `needs_wp_post_id`  |  *Mutating:* True

Request a re-audit of an already-registered Focus Page (also refreshes its hash/permalink).


| Param | Required | Note |
|---|---|---|
| `post_id` | yes | TRAP: unlike api/posts/set-focus, this `post_id` is the CLOUD user_post_id, not a WordPress post ID. Both callers assign $args['post_id'] = $id where $id is the request 'id' value, |
| `hash` | yes | Local snippet hash of the resolved WP post. |
| `permalink` | yes |  |

*Args evidence:* controllers/FocusPages.php:888-893 (case 'sq_ajax_focuspages_reaudit'); identical 3 keys at controllers/FocusPages.php:922-926 (case 'sq_focuspages_update')

*Response:* Returns $json->data; callers only test truthiness and is_wp_error(). Error path: $json->error == 'too_many_attempts' is special-cased into "You've made too many requests, please wait a few minutes." On success a transient sq_auditpage_<id> is set to time().

> **Risk:** Triggers a paid cloud re-audit and is server-side rate limited ('too_many_attempts'). The UI additionally blocks the button for 300s between attempts (controllers/FocusPages.php via $call_timestamp, view/FocusPages/FocusPageRow.php:119) - a CLI should honour the same 5-minute cooldown.


### `api/research/ib/blog` — GET

*PHP:* `getCustomCall` (RemoteController.php:1140)  
*Standalone:* `yes`  |  *Mutating:* False

Inspiration Box blog/news article search used to insert references and quote boxes. Shares the single dynamic call site at line 1140.


| Param | Required | Note |
|---|---|---|
| `page` | yes | RAW OFFSET — the JS passes `start` directly, same as gimages. |
| `rpp` | yes | Results per page. |
| `hl` | yes | Language. |
| `q` | yes | Search keyword wrapped in literal double quotes by the JS. |

*Args evidence:* view/assets/js/assistant/sq_blocksearch.min.js — getSearch() case 'blog'; params="page="+start+"&rpp="+nrb+"&hl="+language+'&q="'+keyword+'"'. Dispatched through controllers/Post.php:696-698.

*Response:* Raw passthrough — no $json->data access in PHP. JS reads response.data.results[] with url, visibleUrl, titleNoFormatting, content.

> **Risk:** Read-only; consumes research credits. Result urls are the natural input to api/research/ib/preview (getSLAPreview), which is the pairing a CLI would use.


### `api/research/ib/gimages` — GET

*PHP:* `getCustomCall` (RemoteController.php:1140)  
*Standalone:* `yes`  |  *Mutating:* False

Inspiration Box general (non-license-filtered) image search — the default image path when the 'no licence' checkbox is unchecked. Shares the single dynamic call site with the other four research endpoints.


| Param | Required | Note |
|---|---|---|
| `page` | yes | RAW OFFSET, not a page number — the JS passes `start` directly here (unlike images/twitter/wiki which send start/nrb+1). |
| `rpp` | yes | Results per page. |
| `hl` | yes | Language. |
| `q` | yes | Search keyword wrapped in literal double quotes by the JS: '&q="'+keyword+'"'. |

*Args evidence:* view/assets/js/assistant/sq_blocksearch.min.js — getSearch() case 'img' else-branch; params="page="+start+"&rpp="+nrb+"&hl="+language+'&q="'+keyword+'"'. Dispatched through controllers/Post.php:696-698.

*Response:* Raw passthrough — PHP never touches $json->data. JS reads response.data.responseData.results[] with url, tbUrl, width, height, attribute, detail, contentNoFormatting (same renderer as api/research/ib/images).

> **Risk:** Read-only; consumes research credits. Same allowlist note as the other ib endpoints. The page-parameter semantics differ from its sibling — a CLI that assumes 1-based paging here will silently re-fetch page 1.


### `api/research/ib/images` — GET

*PHP:* `getCustomCall` (RemoteController.php:1140)  
*Standalone:* `yes`  |  *Mutating:* False

Inspiration Box image search restricted to license-free results (the 'no licence' checkbox path).


| Param | Required | Note |
|---|---|---|
| `page` | yes | 1-based page number, computed as start/nrb + 1. |
| `nrb` | yes | Results per page. NOTE this endpoint uses `nrb` while its four siblings use `rpp` — do not normalise. |
| `hl` | yes | Language, from $.sq_config.language. |
| `q` | yes | Search keyword, sent unquoted for this endpoint. |

*Args evidence:* view/assets/js/assistant/sq_blocksearch.min.js — getSearch() case 'img' builds params="page="+(start/nrb+1)+"&nrb="+nrb+"&hl="+language+"&q="+keyword and posts {action:'sla_customcall', url, params}; PHP then does parse_str(getValue('params'), $args) at controllers/Post.php:696 before controllers/Po

*Response:* getCustomCall does NOT decode JSON at all — it returns the raw body string, echoed straight to the browser (controllers/Post.php:698), so no $json->data access exists in PHP. The JS reads response.data.responseData.results[] with per-item fields: url, tbUrl, width, height, attribute, detail, contentNoFormatting.

> **Risk:** Read-only but consumes Squirrly research credits and proxies third-party image sources. The dynamic $url is gated by a hard allowlist (controllers/Post.php:684-694) of exactly these five api/research/ib/* paths; anything else returns {"error":"invalid_endpoint"} — that gate is WP-side only and does not constrain a direct CLI.


### `api/research/ib/preview` — GET

*PHP:* `getSLAPreview` (RemoteController.php:1026)  
*Standalone:* `yes`  |  *Mutating:* False

Server-side fetch of a remote article's readable preview (title + body) so the Inspiration Box can show a blog result inline instead of navigating away.


| Param | Required | Note |
|---|---|---|
| `filter` | yes | On/off switch for content filtering. The JS literally sends the string '&filter=1' or '&filter=0' as the VALUE of the `filter` key (sq_blocksearch.min.js: filter:filter?"&filter=1" |
| `link` | yes | Absolute URL of the page to preview; JS takes it from the clicked anchor's href. |

*Args evidence:* controllers/Post.php:542-547 (ajax action `sla_preview`); browser side view/assets/js/assistant/sq_blocksearch.min.js previewBlog() sends filter and link.

*Response:* Returns $json->data verbatim. JS reads response.data.title and response.data.content (and treats content === '' as a failure). Note the JS also reads a top-level response.link, but that field is produced by the WP ajax wrapper's echo shape, not by $json->data.

> **Risk:** Server-side fetch of an arbitrary caller-supplied URL through Squirrly's infrastructure (SSRF-ish surface on the vendor side) and it consumes research quota. Read-only.


### `api/research/ib/twitter` — GET

*PHP:* `getCustomCall` (RemoteController.php:1140)  
*Standalone:* `yes`  |  *Mutating:* False

Inspiration Box social/tweet search for quotable content. Shares the single dynamic call site at line 1140.


| Param | Required | Note |
|---|---|---|
| `page` | yes | 1-based page number (start/nrb + 1). |
| `rpp` | yes | Results per page. |
| `hl` | yes | Language. |
| `q` | yes | Search keyword, unquoted. |

*Args evidence:* view/assets/js/assistant/sq_blocksearch.min.js — getSearch() case 'twitter'; params="page="+(start/nrb+1)+"&rpp="+nrb+"&hl="+language+"&q="+keyword. Dispatched through controllers/Post.php:696-698.

*Response:* Raw passthrough — no $json->data access in PHP. JS treats response.data as a FLAT ARRAY (response.data.length) whose items carry id, created_at, from_user, text, profile_image_url. Note this differs from blog/wiki which nest under data.results.

> **Risk:** Read-only; consumes research credits and depends on a third-party social source that may be long-dead — worth a live probe before documenting as working.


### `api/research/ib/wiki` — GET

*PHP:* `getCustomCall` (RemoteController.php:1140)  
*Standalone:* `yes`  |  *Mutating:* False

Inspiration Box Wikipedia search; the JS builds the final article link itself from `<lang>.wikipedia.org/wiki/<title>`. Shares the single dynamic call site at line 1140.


| Param | Required | Note |
|---|---|---|
| `page` | yes | 1-based page number (start/nrb + 1). The JS params string for this case begins with a stray leading '&' ('&page=...'), which parse_str() tolerates. |
| `rpp` | yes | Results per page. |
| `hl` | yes | Language; the JS also uses its first two chars as the Wikipedia subdomain. |
| `q` | yes | Search keyword, unquoted. |

*Args evidence:* view/assets/js/assistant/sq_blocksearch.min.js — getSearch() case 'wiki'; params="&page="+(start/nrb+1)+"&rpp="+nrb+"&hl="+language+"&q="+keyword. Dispatched through controllers/Post.php:696-698.

*Response:* Raw passthrough — no $json->data access in PHP. JS reads response.data.results[] with title, snippet, timestamp.

> **Risk:** Read-only; consumes research credits.


### `api/research/ib/{images|gimages|twitter|blog|wiki} (variable $url, not a literal)` — GET

*PHP:* `getCustomCall` (RemoteController.php:1140)  
*Standalone:* `yes`  |  *Mutating:* False

Generic passthrough used only by the SEO Assistant's Inspiration Box: forwards a caller-supplied endpoint path plus query params to the Cloud and echoes the raw body back to the browser.


| Param | Required | Note |
|---|---|---|
| `url` | yes | The endpoint path itself — the first parameter of getCustomCall, not part of the $args array. controllers/Post.php:684-693 restricts it to a hard allowlist of exactly five paths: a |
| `q` | yes | Search term. For the blog and wiki lanes the JS wraps it in literal double quotes. |
| `page` | yes | Page number. Computed inconsistently by the JS: (start/nrb + 1) for images/gimages/twitter/wiki, but raw start for blog. |
| `rpp` | no | Results per page — used by gimages, twitter, blog and wiki. |
| `nrb` | no | Results per page under a DIFFERENT key, used only by the no-licence images lane (api/research/ib/images). |
| `hl` | yes | Interface/content language from $.sq_config.language. |

*Args evidence:* controllers/Post.php:696 — the $args array is not built literally in PHP; it is produced by parse_str() over the raw 'params' query string supplied by the browser, then passed at controllers/Post.php:698. The actual keys are constructed client-side in view/assets/js/assistant/sq_blocksearch.min.js (

*Response:* NONE parsed. getCustomCall returns the raw response string straight from apiCall() with no json_decode, no ->error check and no ->data unwrap (RemoteController.php:1140), and controllers/Post.php:698 echoes that string verbatim to the browser. The plugin's PHP never reads a single field; the JS caches the body by url+params and hands it to showResults(). A CLI must define the shape empirically per

> **Risk:** Read-only, but it is the plugin's one generic proxy: before the allowlist added at controllers/Post.php:684-693 (called out in readme.txt:184 as a security fix) any authenticated editor could aim it at any Cloud endpoint. A CLI reimplementation should keep the same allowlist rather than exposing an arbitrary-path passthrough. Note the enclosing method sets $apimethod = 'get', so a POST endpoint cannot be reached through it.


### `api/serp/get-ranks` — GET

*PHP:* `getRanks` (RemoteController.php:1802)  
*Standalone:* `yes`  |  *Mutating:* False

List the tracked keywords with their current rank rows for the Rankings table.


| Param | Required | Note |
|---|---|---|
| `start` | no | Offset = ($page - 1) * $num. |
| `limit` | no | Page size. Also used locally to compute max_num_pages. |
| `sort` | no |  |
| `order` | no |  |
| `keyword` | no | Search filter. |
| `strict` | no |  |
| `days_back` | no |  |
| `has_change` | no |  |
| `has_ranks` | no |  |
| `page` | no | SECOND, INCOMPATIBLE ARG VOCABULARY. models/Assistant.php:594 and :611 call this endpoint with ONLY array('page' => 1) - no start/limit. So the server accepts either page-based or  |

*Args evidence:* controllers/Ranking.php:85-95 consumed at :105 (start/limit vocabulary); models/Assistant.php:594 and models/Assistant.php:609-611 (page vocabulary)

*Response:* $json->data is an array of rank row objects. Fields read by view/Ranking/Rankings.php: keyword, rank, best, change, average_position, clicks, impressions, country, datetime, permalink, optimized, facebook, pinterest, reddit. models/Assistant.php:619 additionally reads rank and average_position. SEPARATELY, $json->message->total (not ->data) carries the total record count and is published through t


### `api/serp/refresh` — GET

*PHP:* `checkPostRank` (RemoteController.php:1832)  
*Standalone:* `yes`  |  *Mutating:* True

Queue a fresh SERP rank check for one keyword.


| Param | Required | Note |
|---|---|---|
| `keyword` | yes | Single keyword string. The bulk-refresh action loops one call per keyword (Ranking.php:283-288). |

*Args evidence:* controllers/Ranking.php:215-217 (case 'sq_serp_refresh_post'); bulk variant at controllers/Ranking.php:285-287

*Response:* Returns $json->data; the caller only tests `=== false` to decide between an error notice and "<keyword> is queued and the rank will be checked soon." No fields read.

> **Risk:** State-changing despite being a GET - it queues a paid rank check. The plugin's own failure message tells the user to "check your SERP credits", so this burns account credit on every call. A CLI must rate-limit and not loop this blindly.


### `api/serp/stats` — GET

*PHP:* `getRanksStats` (RemoteController.php:1777)  
*Standalone:* `yes`  |  *Mutating:* False

Fetch the aggregate ranking dashboard numbers (average-position trend line, top-10 count, new keywords, positive changes) for the site.


| Param | Required | Note |
|---|---|---|
| `start` | no | Offset, computed as ($page - 1) * $num. |
| `limit` | no | Page size, defaults to the sq_posts_per_page option. |
| `sort` | no | From the ssort request value, default 'rank'. |
| `order` | no | From the sorder request value, default 'asc'. |
| `keyword` | no | Search filter; empty string on the default listing, populated by the sq_rankings_search action. |
| `strict` | no | Cast to int in the default path, kept as string in the search path (Ranking.php:187) - the plugin is inconsistent here. |
| `days_back` | no | Int, default 30. |
| `has_change` | no | Int, from the 'schanges' request value. |
| `has_ranks` | no | Int, from the 'ranked' request value. |

*Args evidence:* controllers/Ranking.php:85-95 (the $this->args array), consumed at controllers/Ranking.php:98; the search variant rebuilds the identical 9 keys at controllers/Ranking.php:194-204

*Response:* $json->data is stored as $view->info. The Rankings view reads: ->average (array of [date, position] pairs, index 0 appears to be a header row since the loop starts at key>0), ->topten (int), ->new (int), ->positive_changes (int). Evidence: view/Ranking/Rankings.php:66-180.


### `api/tools/facebook` — GET

*PHP:* `getFacebookApi` (RemoteController.php:2415)  
*Standalone:* `yes`  |  *Mutating:* False

Resolve a Facebook profile name/URL fragment into the numeric Facebook admin code used for the fb:admins meta tag.


| Param | Required | Note |
|---|---|---|
| `profile` | yes | Either the path fragment captured from a facebook.com/<profile> URL, or the raw non-numeric value the user typed into the Facebook admin-code setting. |

*Args evidence:* classes/helpers/Sanitize.php:727 (getFacebookApi( array( 'profile' => $result[1] ) ) — from the facebook.com/<x> regex capture) and classes/helpers/Sanitize.php:736 (getFacebookApi( array( 'profile' => $code ) ) — the raw setting value), both inside checkFacebookAdminCode().

*Response:* $json->data is an object; only ->code is read (classes/helpers/Sanitize.php:728-729 and 737-738), and it is returned as the Facebook admin code. Anything without a ->code is treated as an invalid code.

> **Risk:** None (read-only). It is a lookup helper against Facebook via the Cloud, so it may fail for reasons unrelated to the Squirrly account.


### `api/user/checkin` — GET

*PHP:* `checkin` (RemoteController.php:656)  
*Standalone:* `yes`  |  *Mutating:* False

The account/plan heartbeat: returns connection state and the whole subscription snapshot (limits, quotas, expiry, product) — the single most useful read-only endpoint in this range.


*Args evidence:* No caller supplies any. Verified across all 17 call sites: models/CheckSeo.php:1368, controllers/Ranking.php:33, controllers/Post.php:502, controllers/CheckSeo.php:39, controllers/Account.php:97, controllers/Account.php:125, controllers/SeoSettings.php:131, :148, :166, :620, controllers/Audits.php:4

*Response:* Inside checkin() it reads $json->error (special-cased: too_many_requests, maintenance, and the clone family signature_required / clone_detected / url_change_pending / site_key_already_set / site_key_reused), then $json->data->connected, $json->data->connection_gsc, $json->data->connection_ga (saved into the 'connect' option) and $json->data->subscription_devkit (saved as sq_auto_devkit). $json->da

> **Risk:** Read-only and safe, but rate-limited: the Cloud answers too_many_requests and the plugin defends with a 60-second sq_checkin transient plus a 2-minute sq_checkin_down backoff on 5xx — a CLI should cache identically rather than poll. One standalone caveat that applies to this whole range: attachSignedHeaders() only signs when option sq_user_blog_id is set AND sq_legacy_auth is falsy AND a 64-hex sq_site_key exists (classes/RemoteController.php:154-161). A CLI holding only USER-TOKEN + USER-URL ha


### `api/user/connect` — POST

*PHP:* `connect` (RemoteController.php:429)  
*Standalone:* `no`  |  *Mutating:* True

Binds this WordPress install's generated site identity (site_key + site_uuid) to the account behind USER-TOKEN, creating or confirming the Cloud-side site row and returning its user_blog_id.


| Param | Required | Note |
|---|---|---|
| `site_key` | yes | Built inside connect() itself, not by a caller. 64-char hex of a locally generated 32-byte HMAC key (SQ_Classes_Helpers_SiteAuth::getSiteKeyHex(), stored in wp_option sq_site_key). |
| `site_uuid` | yes | SQ_Classes_Helpers_SiteAuth::getSiteUuid(), from wp_option sq_site_uuid, minted by ensureSiteKey(). |

*Args evidence:* classes/RemoteController.php:424-427 (array_merge inside connect()); every caller passes NO args — classes/RemoteController.php:691, :709, :726, :787 and controllers/Account.php:82 all call connect() with an empty argument list, so site_key/site_uuid are the complete parameter set.

*Response:* Reads $json->error first (values handled explicitly: invalid_token, disconnected, banned → plugin clears sq_api + sq_cloud_token; site_key_already_set, site_key_reused → clears the local site key). On success reads $json->data->user_blog_id (saved to option sq_user_blog_id, and sq_legacy_auth set to 0). Returns the whole decoded $json object to the caller.

> **Risk:** Registration/identity call — it writes server-side site state. Calling it from a CLI with a site_key the real WordPress install does not hold can bind the account's site row to a foreign key and make the live site fail checkin with site_key_already_set / site_key_reused / signature_required, i.e. it can disconnect a working site. Also note: if the Cloud answers invalid_token/disconnected/banned the plugin destroys its stored credentials.


### `api/user/dashboardlink` — GET

*PHP:* `getDashboardLink` (RemoteController.php:558)  
*Standalone:* `yes`  |  *Mutating:* True

Mints a ONE-TIME sign-in URL into the Squirrly Cloud dashboard for the current account, so an admin can jump from wp-admin to the Cloud already logged in.


| Param | Required | Note |
|---|---|---|
| `redirect` | no | A bare relative Cloud path. The caller sanitises it with preg_replace('#[^A-Za-z0-9/_-]#','',...) then ltrim('/'), defaulting to 'dashboard'. The Cloud feeds it to admin_url() on i |

*Args evidence:* controllers/Account.php:37-38 (path sanitisation) and controllers/Account.php:44 — array('redirect' => $path). Only caller.

*Response:* Reads $json->error; then requires $json->data->url (non-empty) — validated to start with _SQ_DASH_URL_ or rejected as invalid_url. Optionally reads $json->data->redirect (appended as ?redirect=) and $json->data->blog_id (appended as &blog=). Returns the assembled absolute URL string.

> **Risk:** The returned link is SINGLE-USE — the plugin's own docblock says minting one per rendered link would leave every link but the first dead (classes/RemoteController.php:546-548). A CLI that calls this to 'test' the endpoint burns a live sign-in link. DevKit (Business/Agency) accounts are excluded by the Cloud and always error. Never log or print the returned URL: it is a bearer sign-in credential.


### `api/user/feedback` — POST

*PHP:* `saveFeedback` (RemoteController.php:984)  
*Standalone:* `yes`  |  *Mutating:* True

POST a user feedback payload to Squirrly (the only POST-verb endpoint in this whole range).


*Args evidence:* NO CALLER FOUND. `grep -rn "saveFeedback\\|user/feedback\\|sq_feedback" /tmp/sq-plugin/squirrly-seo --exclude-dir=.git` returns only the two definition lines classes/RemoteController.php:980 and :984. The method is dead code in this build, so the parameter keys are genuinely unknown and are reported

*Response:* Returns $json->data verbatim if non-empty, else false; only $json->error and isset($json->data) are inspected. No field of $json->data is accessed anywhere, because nothing calls this method.

> **Risk:** Mutating (POST) and unexercised by the plugin — a CLI would be sending a payload of unverified shape to Squirrly support/feedback storage. Because self::$apimethod = 'post', apiCall() puts $args in the request body and the HMAC signature (attachSignedHeaders, line 166-168) is computed over http_build_query($body), so a standalone signer must sign the encoded body, not the query string.


### `api/user/login` — POST

*PHP:* `login` (RemoteController.php:478)  
*Standalone:* `no`  |  *Mutating:* False

Exchanges a Squirrly.co email + password for the account's USER-TOKEN (the api token every other call depends on).


| Param | Required | Note |
|---|---|---|
| `user` | yes | The account email. Read from the login form via SQ_Classes_Helpers_Tools::getValue('email'). |
| `password` | yes | Taken raw from $_POST['password'] — not run through getValue(). |

*Args evidence:* core/Blocklogin.php:112-113 ($args['user'], $args['password']), passed at core/Blocklogin.php:117. Only caller in the plugin.

*Response:* Reads $json->error (handled codes seen at the call site: badlogin, multisite, disconnected; plus synthesized server_unavailable and no_data). On success returns $json->data; the caller then reads $response->token and stores it as option sq_api (core/Blocklogin.php:147-148). No other data field is touched.

> **Risk:** Bootstrap credential exchange — needs an email/password, not a token, so it is the wrong shape for a token-only CLI. It is one of only three modules apiCall() will send without sq_api (classes/RemoteController.php:79). Repeated attempts are a credential-stuffing surface and the Cloud may throttle.


### `api/user/register` — POST

*PHP:* `register` (RemoteController.php:517)  
*Standalone:* `no`  |  *Mutating:* True

Creates a brand-new Squirrly.co account from an email address and returns its USER-TOKEN.


| Param | Required | Note |
|---|---|---|
| `name` | yes | Always sent, always the EMPTY STRING — the plugin hardcodes $args['name'] = '' and never collects a name. |
| `user` | yes | The email to register. From SQ_Classes_Helpers_Tools::getValue('email'). |

*Args evidence:* core/Blocklogin.php:56-58 ($args = array(); $args['name'] = ''; $args['user'] = ...), passed at core/Blocklogin.php:62. Only caller in the plugin.

*Response:* Reads $json->error (handled codes at the call site: alreadyregistered, invalidemail; plus server_unavailable and no_data). On success returns $json->data; caller reads $response->token and saves it as option sq_api (core/Blocklogin.php:82-83).

> **Risk:** Creates a real account on the vendor's system and is callable WITHOUT any token (classes/RemoteController.php:79 whitelists it alongside login and checkin). A CLI must never call this speculatively — it is account creation, not a read.


### `api/user/settings` — POST

*PHP:* `saveSettings` (RemoteController.php:2402)  
*Standalone:* `yes`  |  *Mutating:* True

Push account-level settings from the plugin up to the Cloud user profile.


| Param | Required | Note |
|---|---|---|
| `settings` | yes | A single JSON-ENCODED string: the method wraps whatever the caller passed as array('settings' => wp_json_encode($args)). The inner keys observed in callers are: 'audit_email' (cont |

*Args evidence:* controllers/Audits.php:301-304 ($args['audit_email'] = $email; saveSettings($args)) and controllers/Ranking.php:168-172 ($args['sq_google_country'], $args['sq_google_language'], $args['sq_google_device']; saveSettings($args)). Wrapping into 'settings' happens at classes/RemoteController.php:2402.

*Response:* None. This is the only apiCall in the range whose result is not json_decode()d or assigned — classes/RemoteController.php:2402 calls apiCall() as a bare statement and the method returns void.

> **Risk:** Overwrites Cloud-side account settings with no read-back and no error reporting whatsoever — a failure is completely invisible. It is unknown from this file whether the Cloud merges or replaces the settings blob, so a CLI should treat it as a potential full replace and read the settings back (e.g. via api/user/checkin) before and after.


### `api/user/stats` — GET

*PHP:* `getStats` (RemoteController.php:963)  
*Standalone:* `yes`  |  *Mutating:* False

Fetch account-level usage stats for the connected blog; cached in the sq_stats transient for 60s and used to decide whether keyword-research and article-optimization goals are already satisfied.


*Args evidence:* classes/RemoteController.php:962 — `$args = array();` is built inline in the method itself, immediately above the call. Callers models/Assistant.php:375 and models/Assistant.php:443 call getStats() with no arguments.

*Response:* Returns $json->data verbatim and caches it (set_transient('sq_stats', $json->data, 60)). Fields actually read downstream: $data->kr_research (models/Assistant.php:379) and $data->optimized_articles (models/Assistant.php:447).

> **Risk:** None — pure read. Note the 60s transient means repeated plugin calls are throttled; a CLI has no such cache and can hammer it.


### `api/user/token` — GET

*PHP:* `getCloudToken` (RemoteController.php:611)  
*Standalone:* `yes`  |  *Mutating:* True

Issues a fresh URL-TOKEN (the per-site cloud token) for the site identified by the USER-URL header, telling the Cloud where this site's REST API lives so it can call back.


| Param | Required | Note |
|---|---|---|
| `wp-json` | yes | The site's REST URL prefix, computed inside getCloudToken() from rest_get_url_prefix() (or parsed out of rest_url()), trimmed of slashes. Note the literal hyphen in the key name. I |

*Args evidence:* classes/RemoteController.php:603-609 (array_merge inside getCloudToken()); all four callers pass NO args — core/Blocklogin.php:85, core/Blocklogin.php:150, classes/RemoteController.php:711 and controllers/Account.php:84 all call getCloudToken() bare, so 'wp-json' is the complete parameter set.

*Response:* Reads $json->error, then requires $json->data. Returns $json->data; every caller then reads ->token and stores it as option sq_cloud_token with sq_cloud_connect = 1 (core/Blocklogin.php:86-88, core/Blocklogin.php:151-153, classes/RemoteController.php:712-714, controllers/Account.php:85-87).

> **Risk:** Its own docblock reads 'Get a NEW token for the current URL' — treat it as a rotation, not a read. Calling it from a CLI can invalidate the URL-TOKEN the live WordPress install has stored in sq_cloud_token, silently breaking the site's Cloud connection until the next reconnect. The returned value is a secret; never print it. The wp-json value it sends also tells the Cloud a callback address, so a wrong value mis-points the Cloud at a non-existent REST root.

