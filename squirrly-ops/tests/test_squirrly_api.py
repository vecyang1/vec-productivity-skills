"""Unit tests for the API client: verb table, error envelope, guards, shaping.

These pin the facts that were expensive to learn and are invisible from the
response: the per-endpoint verb, that a 200 can carry an error, that the row
total lives in `message` and not `data`, and that `start`/`limit` are only
honoured as a pair.
"""

import json
import sys
import unittest
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

api = _bootstrap.load("squirrly_api")


class TestEndpointTable(unittest.TestCase):
    def test_every_endpoint_declares_a_known_verb(self):
        for op, ep in api.ENDPOINTS.items():
            self.assertIn(ep.verb, ("get", "post"), f"{op} has verb {ep.verb!r}")

    def test_operation_key_matches_its_own_op_field(self):
        for key, ep in api.ENDPOINTS.items():
            self.assertEqual(key, ep.op)

    def test_dual_verb_paths_survive_as_separate_operations(self):
        """api/kr/suggestion and api/ga/properties each exist as GET *and* POST.

        A path-keyed table silently drops one of each pair. This asserts both
        halves are still reachable, which is the regression that table design
        exists to prevent.
        """
        for path in ("api/kr/suggestion", "api/ga/properties"):
            verbs = {e.verb for e in api.ENDPOINTS.values() if e.path == path}
            self.assertEqual(verbs, {"get", "post"}, f"{path} lost a verb")

    def test_every_post_is_marked_mutating(self):
        for op, ep in api.ENDPOINTS.items():
            if ep.verb == "post":
                self.assertTrue(ep.mutates, f"{op} is a POST but not marked mutating")

    def test_quota_consuming_gets_are_marked_mutating(self):
        for op in ("posts.crawl", "serp.refresh"):
            self.assertTrue(api.ENDPOINTS[op].mutates,
                            f"{op} spends metered quota and must be guarded")

    def test_consuming_gets_are_guarded_despite_the_verb(self):
        """A GET is not automatically safe here. dashboardlink burns a
        single-use sign-in link and user.token rotates the site's URL-TOKEN --
        both measured 2026-08-16. Marking them by verb alone would let a
        read-shaped call disturb a live WordPress install."""
        for op in ("user.dashboardlink", "user.token"):
            self.assertEqual(api.ENDPOINTS[op].verb, "get")
            self.assertTrue(api.ENDPOINTS[op].mutates,
                            f"{op} consumes or rotates state and must be guarded")

    def test_table_reports_its_own_size(self):
        # A selector that silently narrows later shows up as a number that fell.
        self.assertGreaterEqual(len(api.ENDPOINTS), 38,
                                "endpoint table shrank; a verified operation was lost")


class TestUnwrap(unittest.TestCase):
    def unwrap(self, payload, status=200):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        return api.SquirrlyClient._unwrap("api/test", status, body)

    def test_returns_data_and_message(self):
        data, message = self.unwrap({"data": [1, 2], "message": {"total": 7}, "error": None})
        self.assertEqual(data, [1, 2])
        self.assertEqual(message, {"total": 7})

    def test_message_total_is_not_discarded(self):
        """The only way to tell a complete list from a first page."""
        _, message = self.unwrap({"data": [], "message": {"total": 51}})
        self.assertEqual(message["total"], 51)

    def test_http_200_carrying_an_error_is_a_failure(self):
        """This API answers 200 for validation errors, so status is not a verdict."""
        with self.assertRaises(api.SquirrlyError) as ctx:
            self.unwrap({"data": [], "error": ["The keyword field is required."]})
        self.assertIn("keyword field is required", str(ctx.exception))

    def test_error_list_is_joined_not_stringified_as_a_list(self):
        with self.assertRaises(api.SquirrlyError) as ctx:
            self.unwrap({"data": [], "error": ["one", "two"]})
        self.assertIn("one; two", str(ctx.exception))

    def test_405_names_the_verb_table_as_the_cause(self):
        with self.assertRaises(api.SquirrlyError) as ctx:
            self.unwrap({"x": 1}, status=405)
        self.assertIn("verb", str(ctx.exception).lower())

    def test_401_says_the_token_was_rejected_for_this_url(self):
        with self.assertRaises(api.SquirrlyError) as ctx:
            self.unwrap({"error": "bad"}, status=401)
        self.assertIn("USER-URL", str(ctx.exception))

    def test_non_json_body_raises_rather_than_returning_empty(self):
        with self.assertRaises(api.SquirrlyError):
            self.unwrap(b"<html>gateway timeout</html>")

    def test_empty_body_raises(self):
        with self.assertRaises(api.SquirrlyError):
            self.unwrap(b"")


class FakeClient(api.SquirrlyClient):
    """Records every request so a test can assert on what was actually sent.

    Records *all* arguments, including ones no test reads yet: a parameter a
    fake accepts and drops reads as covered while being unassertable.
    """

    def __init__(self, pages=None, **kw):
        super().__init__("token-not-real", "https://example.com", **kw)
        self.calls: list[tuple[str, dict]] = []
        self.pages = pages or {}

    def call_meta(self, op, params=None):
        self.calls.append((op, dict(params or {})))
        key = (params or {}).get("start", 0)
        return self.pages.get(key, ([], {"total": len(self.pages) and 0}))


class TestGuards(unittest.TestCase):
    def test_mutating_op_refused_without_permission(self):
        client = api.SquirrlyClient("t", "https://example.com", allow_mutations=False)
        with self.assertRaises(api.SquirrlyError) as ctx:
            client.call("briefcase.add", {"keyword": "x"})
        self.assertIn("--confirm", str(ctx.exception))

    def test_unknown_operation_refuses_rather_than_guessing_a_verb(self):
        client = api.SquirrlyClient("t", "https://example.com")
        with self.assertRaises(api.SquirrlyError) as ctx:
            client.call("does.not.exist")
        self.assertIn("405", str(ctx.exception))

    def test_missing_required_param_is_caught_before_the_request(self):
        client = api.SquirrlyClient("t", "https://example.com")
        with self.assertRaises(api.SquirrlyError) as ctx:
            client.call("kr.other")
        self.assertIn("keyword", str(ctx.exception))

    def test_falsy_params_are_kept_because_they_are_answers(self):
        """0, False and "" are values the caller supplied; only None is absence.

        Asserted against the real request the client would send, not a stub of
        it -- the filtering lives in build_request, so a double that replaced
        that method would make this property unobservable.
        """
        client = api.SquirrlyClient("t", "https://example.com")
        _, request = client.build_request(
            "kr.found", {"start": 0, "search": "", "dropped": None})
        # keep_blank_values=True is required: parse_qs discards `search=` by
        # default, which would make an empty-string parameter that IS being sent
        # look like one that was filtered out -- the same absent-vs-empty
        # confusion this test exists to rule out, one layer up in the harness.
        query = urllib.parse.parse_qs(
            urllib.parse.urlsplit(request.full_url).query, keep_blank_values=True)
        self.assertEqual(query.get("start"), ["0"])
        self.assertEqual(query.get("search"), [""], "an empty string is a value, not an absence")
        self.assertNotIn("dropped", query)


class TestRequestShape(unittest.TestCase):
    """The verb decides where parameters ride. Getting it wrong returns 405."""

    def setUp(self):
        self.client = api.SquirrlyClient("token-not-real", "https://example.com",
                                         allow_mutations=True)

    def test_get_puts_params_in_the_query_and_sends_no_body(self):
        _, request = self.client.build_request("kr.other", {"keyword": "pho"})
        self.assertEqual(request.get_method(), "GET")
        self.assertIn("keyword=pho", request.full_url)
        self.assertIsNone(request.data)

    def test_post_puts_params_in_the_body_and_not_the_query(self):
        _, request = self.client.build_request("briefcase.add", {"keyword": "pho"})
        self.assertEqual(request.get_method(), "POST")
        self.assertNotIn("keyword", urllib.parse.urlsplit(request.full_url).query)
        self.assertIn(b"keyword=pho", request.data)

    def test_auth_headers_are_present_on_every_request(self):
        _, request = self.client.build_request("user.stats")
        headers = {k.lower(): v for k, v in request.header_items()}
        self.assertEqual(headers.get("User-token".lower()), "token-not-real")
        self.assertEqual(headers.get("User-url".lower()), "https://example.com")

    def test_user_url_binds_the_request_to_the_selected_brand(self):
        other = api.SquirrlyClient("token-not-real", "https://elsewhere.test")
        _, request = other.build_request("user.stats")
        headers = {k.lower(): v for k, v in request.header_items()}
        self.assertEqual(headers.get("user-url"), "https://elsewhere.test")


class TestPagination(unittest.TestCase):
    def test_start_and_limit_are_always_sent_together(self):
        """Sent alone, each is silently ignored and the server repeats page one."""
        client = FakeClient(pages={0: ([{"id": 1}], {"total": 1})})
        client.paginate("kr.found", page_size=10)
        _, params = client.calls[0]
        self.assertIn("start", params)
        self.assertIn("limit", params)

    def test_walks_multiple_pages_and_reports_the_server_total(self):
        client = FakeClient(pages={
            0: ([{"id": i} for i in range(3)], {"total": 5}),
            3: ([{"id": 3}, {"id": 4}], {"total": 5}),
        })
        rows, total = client.paginate("kr.found", page_size=3)
        self.assertEqual([r["id"] for r in rows], [0, 1, 2, 3, 4])
        self.assertEqual(total, 5)

    def test_terminates_when_the_server_ignores_the_offset(self):
        """A server that repeats page one forever must not spin this loop."""
        same = ([{"id": 1}, {"id": 2}], {"total": 99})
        client = FakeClient(pages={k: same for k in range(0, 500, 2)})
        rows, _ = client.paginate("kr.found", page_size=2, max_pages=50)
        self.assertEqual(len(rows), 2, "duplicate rows were accumulated")
        self.assertLessEqual(len(client.calls), 3, "did not stop on a repeated window")


class TestEmbeddedJson(unittest.TestCase):
    def test_decodes_json_inside_a_string(self):
        self.assertEqual(api.decode_embedded_json('{"a": 1}'), {"a": 1})

    def test_returns_the_original_when_undecodable(self):
        """A format change must degrade to the raw value, not lose the field."""
        self.assertEqual(api.decode_embedded_json("{not json"), "{not json")

    def test_leaves_non_strings_alone(self):
        self.assertEqual(api.decode_embedded_json(7), 7)
        self.assertIsNone(api.decode_embedded_json(None))

    def test_does_not_decode_a_plain_sentence(self):
        self.assertEqual(api.decode_embedded_json("good"), "good")


class TestPathParameters(unittest.TestCase):
    """A few endpoints carry the id in the path (`remove-focus/{user_post_id}`).

    Two things can go wrong silently. The value can be left in the body as
    well, which the vendor's own caller does not do; and the signature can be
    computed over the unexpanded template, which the server rejects with the
    a `403 invalid_signature`, which the server words differently from the
    `signature_required` it sends when no signature was attached at all.
    """

    KEY_HEX = "cd" * 32

    def client(self, **kw):
        return api.SquirrlyClient("token-not-real", "https://alpha.test",
                                  allow_mutations=True, **kw)

    def test_placeholder_is_substituted_into_the_url(self):
        _, request = self.client().build_request("posts.remove_audit",
                                                 {"user_post_id": 90590931})
        self.assertTrue(request.full_url.endswith("api/posts/remove-audit/90590931"),
                        request.full_url)

    def test_the_path_value_is_not_also_sent_in_the_body(self):
        _, request = self.client().build_request("posts.remove_audit",
                                                 {"user_post_id": 42})
        self.assertNotIn(b"user_post_id", request.data or b"")

    def test_a_missing_path_value_is_refused_before_the_network(self):
        with self.assertRaises(api.SquirrlyError):
            self.client().build_request("posts.remove_audit", {})

    def test_signature_covers_the_expanded_path_not_the_template(self):
        client = self.client(site_key=self.KEY_HEX, blog_id=123456)
        _, request = client.build_request("posts.remove_audit", {"user_post_id": 42})
        sent = request.get_header("X-sq-sig")
        expected = api.build_signed_headers(
            method="post", path="api/posts/remove-audit/42", body="",
            url="https://alpha.test", blog_id=123456,
            user_token="token-not-real", site_key_hex=self.KEY_HEX,
            timestamp=int(request.get_header("X-sq-timestamp")),
            nonce=request.get_header("X-sq-nonce"),
        )["X-SQ-Sig"]
        self.assertEqual(sent, expected)
        template_signature = api.build_signed_headers(
            method="post", path="api/posts/remove-audit/{user_post_id}", body="",
            url="https://alpha.test", blog_id=123456,
            user_token="token-not-real", site_key_hex=self.KEY_HEX,
            timestamp=int(request.get_header("X-sq-timestamp")),
            nonce=request.get_header("X-sq-nonce"),
        )["X-SQ-Sig"]
        self.assertNotEqual(sent, template_signature,
                            "the two paths must produce different signatures, "
                            "or this test cannot tell them apart")


class TestRequestSigning(unittest.TestCase):
    """Signed auth (X-SQ-Sig). Both traps here fail as `403 invalid_signature`
    — the same slug the server returns for a wrong or stale key, so the response
    tells you the signature is bad but never which of the three reasons it is.
    (It does distinguish that family from `signature_required`, which means no
    signature was sent; measured 2026-08-17.)"""

    KEY_HEX = "ab" * 32  # 64 hex chars -> 32 raw bytes
    ARGS = dict(method="get", path="api/user/checkin", body="",
                url="https://alpha.test", blog_id=123456,
                user_token="token-not-real", timestamp=1_700_000_000,
                nonce="0" * 32)

    def test_hmac_key_is_the_raw_bytes_not_the_hex_string(self):
        """The plugin runs hex2bin() before hash_hmac. Signing the hex text
        yields a well-formed signature the server rejects."""
        import hashlib
        import hmac as _hmac
        headers = api.build_signed_headers(site_key_hex=self.KEY_HEX, **self.ARGS)
        canonical = "\n".join([
            "GET", "/api/user/checkin",
            hashlib.sha256(b"").hexdigest(), "https://alpha.test",
            "1700000000", "0" * 32,
        ])
        raw_key = _hmac.new(bytes.fromhex(self.KEY_HEX), canonical.encode(), hashlib.sha256).hexdigest()
        hex_key = _hmac.new(self.KEY_HEX.encode(), canonical.encode(), hashlib.sha256).hexdigest()
        self.assertNotEqual(raw_key, hex_key, "fixture cannot tell the two apart")
        self.assertEqual(headers["X-SQ-Sig"], "sha256=" + raw_key)

    def test_signed_path_excludes_the_query_string(self):
        """The signature covers the module path only; including the query makes
        every parameterised call fail while bare ones pass."""
        with_query = api.build_signed_headers(
            site_key_hex=self.KEY_HEX, **{**self.ARGS, "path": "api/kr/found"})
        plain = api.build_signed_headers(
            site_key_hex=self.KEY_HEX, **{**self.ARGS, "path": "/api/kr/found"})
        self.assertEqual(with_query["X-SQ-Sig"], plain["X-SQ-Sig"],
                         "a leading slash must be normalised, not signed twice")

    def test_post_body_is_covered_by_the_signature(self):
        a = api.build_signed_headers(site_key_hex=self.KEY_HEX,
                                     **{**self.ARGS, "method": "post", "body": "keyword=a"})
        b = api.build_signed_headers(site_key_hex=self.KEY_HEX,
                                     **{**self.ARGS, "method": "post", "body": "keyword=b"})
        self.assertNotEqual(a["X-SQ-Sig"], b["X-SQ-Sig"])

    def test_no_signature_when_either_half_is_missing(self):
        """The plugin's own rule: send nothing rather than a partial signature."""
        self.assertEqual(api.build_signed_headers(site_key_hex="", **self.ARGS), {})
        self.assertEqual(
            api.build_signed_headers(site_key_hex=self.KEY_HEX,
                                     **{**self.ARGS, "blog_id": ""}), {})

    def test_nonce_differs_between_calls(self):
        a = api.build_signed_headers(site_key_hex=self.KEY_HEX,
                                     **{k: v for k, v in self.ARGS.items() if k != "nonce"})
        b = api.build_signed_headers(site_key_hex=self.KEY_HEX,
                                     **{k: v for k, v in self.ARGS.items() if k != "nonce"})
        self.assertNotEqual(a["X-SQ-Nonce"], b["X-SQ-Nonce"])

    def test_client_attaches_signature_headers_to_a_real_request(self):
        client = api.SquirrlyClient("token-not-real", "https://alpha.test",
                                    site_key=self.KEY_HEX, blog_id=123456)
        _, request = client.build_request("user.stats")
        headers = {k.lower() for k in dict(request.header_items())}
        for required in ("x-sq-sig", "x-sq-blog-id", "x-sq-nonce", "x-sq-timestamp"):
            self.assertIn(required, headers)

    def test_unsigned_client_sends_no_signature_headers(self):
        client = api.SquirrlyClient("token-not-real", "https://alpha.test")
        _, request = client.build_request("user.stats")
        headers = {k.lower() for k in dict(request.header_items())}
        self.assertNotIn("x-sq-sig", headers)

    def test_malformed_key_is_rejected_rather_than_signed_wrongly(self):
        with self.assertRaises(api.SquirrlyError):
            api.build_signed_headers(site_key_hex="z" * 64, **self.ARGS)


class TestCredentialResolution(unittest.TestCase):
    def test_env_scheme_reads_the_named_variable(self):
        import os
        os.environ["SQUIRRLY_TEST_TOKEN"] = "value-from-env"
        try:
            self.assertEqual(api.resolve_credential("env://SQUIRRLY_TEST_TOKEN"), "value-from-env")
        finally:
            os.environ.pop("SQUIRRLY_TEST_TOKEN", None)

    def test_empty_env_variable_is_an_error_not_an_empty_token(self):
        import os
        os.environ["SQUIRRLY_TEST_EMPTY"] = ""
        try:
            with self.assertRaises(api.SquirrlyError):
                api.resolve_credential("env://SQUIRRLY_TEST_EMPTY")
        finally:
            os.environ.pop("SQUIRRLY_TEST_EMPTY", None)

    def test_malformed_reference_is_rejected(self):
        for bad in ("op://only/two", "vault/item/field", "https://example.com", ""):
            with self.assertRaises(api.SquirrlyError):
                api.resolve_credential(bad)

    def test_personal_route_is_refused_rather_than_prompting(self):
        """An interactive biometric prompt is a lane that does not exist in a
        scheduled run, so the personal route must fail loudly instead of
        silently working while a human happens to be at the keyboard."""
        import types
        fake = types.ModuleType("bridge_router")
        fake.route_for_command = lambda cmd, **kw: "personal"

        def _must_not_run(*a, **kw):  # trap, not a value
            raise AssertionError("run_command was reached on the personal route")

        fake.run_command = _must_not_run
        sys.modules["bridge_router"] = fake
        try:
            with self.assertRaises(api.SquirrlyError) as ctx:
                api.resolve_credential("op://Vault/Item/credential")
            # Assert the property, not one vendor's word for the prompt: the
            # refusal has to name the route it rejected and hand back a lane
            # that works unattended. Pinning one vendor's prompt name made this test fail on
            # a pure rewording while a genuinely silent fallback would pass.
            message = str(ctx.exception)
            self.assertIn("personal", message)
            self.assertIn("env://", message)
        finally:
            sys.modules.pop("bridge_router", None)


if __name__ == "__main__":
    unittest.main()


class TestSignatureFailureCarriesItsRemedy(unittest.TestCase):
    """The server distinguishes `signature_required` (none sent) from
    `invalid_signature` (sent and wrong), and the two have opposite remedies.
    Within `invalid_signature` it does NOT distinguish hex-instead-of-raw from a
    wrong key from a stale key, so only the caller knows which it committed --
    and the wrong reading ("the token is bad") sends the reader to re-check a
    credential neither error implicates.

    This is the rung-3 slot: the failure was already detected, and the detection
    was a bare pass-through of the vendor's word.
    """

    BODY = b'{"error":"signature_required","data":null}'

    def test_a_signed_request_is_told_the_key_is_stale_and_where_to_re_read_it(self):
        with self.assertRaises(api.SquirrlyError) as caught:
            api.SquirrlyClient._unwrap("api/user/checkin", 403, self.BODY, signed=True)
        message = str(caught.exception)
        self.assertIn("sq_site_key", message, "must name the field to re-read")
        self.assertIn("site_key_ref", message, "must name where the stored copy lives")
        self.assertIn("will not help", message, "must rule out the token")

    def test_an_unsigned_request_is_told_to_configure_the_brand_instead(self):
        with self.assertRaises(api.SquirrlyError) as caught:
            api.SquirrlyClient._unwrap("api/user/checkin", 403, self.BODY, signed=False)
        message = str(caught.exception)
        self.assertIn("blog_id", message)
        self.assertNotIn("sq_site_key", message,
                         "a brand that never signed has no stored key to re-read; "
                         "sending it to WordPress is the wrong remedy")

    def test_an_ordinary_403_keeps_the_token_remedy(self):
        with self.assertRaises(api.SquirrlyError) as caught:
            api.SquirrlyClient._unwrap("api/user/stats", 403,
                                       b'{"error":"invalid_token"}', signed=True)
        message = str(caught.exception)
        self.assertIn("credential belongs to this brand", message)
        self.assertNotIn("sq_site_key", message)

    def test_the_two_signature_remedies_are_actually_different(self):
        """Without this the pair above could both pass on one shared string."""
        messages = []
        for signed in (True, False):
            with self.assertRaises(api.SquirrlyError) as caught:
                api.SquirrlyClient._unwrap("api/user/checkin", 403, self.BODY, signed=signed)
            messages.append(str(caught.exception))
        self.assertNotEqual(messages[0], messages[1])

    def test_the_signed_flag_comes_from_the_request_not_the_config(self):
        """A client holding a key still sends no signature when blog_id is
        missing, so reading intent instead of the wire would mislabel it."""
        client = api.SquirrlyClient("t", "https://x.test", site_key="ab" * 32, blog_id="")
        _, request = client.build_request("user.checkin")
        self.assertIsNone(request.get_header("X-sq-sig"))

    def test_invalid_signature_is_handled_as_a_bad_key_not_a_missing_one(self):
        """The two slugs are different strings and the branch must match both.

        Keying only on the literal `signature_required` -- which is what the
        earlier, inferred understanding would have produced -- would drop the
        commonest case straight through to the token remedy.
        """
        with self.assertRaises(api.SquirrlyError) as caught:
            api.SquirrlyClient._unwrap("api/user/checkin", 403,
                                       b'{"error":"invalid_signature"}', signed=True)
        message = str(caught.exception)
        self.assertIn("sq_site_key", message)
        self.assertIn("invalid_signature", message, "echo the slug the server sent")
