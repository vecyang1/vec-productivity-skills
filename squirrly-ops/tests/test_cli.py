"""CLI shaping: the places where a wrong number would be believed.

The plan view is the sharpest one. `subscription_kr: 298` means 298 *left* of
300, not 298 used -- the vendor's own UI renders it as "%1$s of %2$s left" and
computes used = max - counter. Reading it the other way turns a healthy account
into an exhausted one, and it is exactly the kind of confident wrong number
nobody re-checks.
"""

import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

cli = _bootstrap.load("squirrly_ops")

HEALTHY = {
    "product_name": "Business Lifetime 1Code",
    "product_type": "Business",
    "subscription_status": "active",
    "subscription_onetime": 1,
    "subscription_expires": False,
    "subscription_limits_reset": "2026-09-07",
    "subscription_max_blogs": 5,
    "subscription_kr": 298, "subscription_max_kr": 300,
    "subscription_audit_pages": 299, "subscription_max_audit_pages": 300,
    "subscription_focus_pages": 9, "subscription_max_focus_pages": 10,
    "subscription_serps": 0, "subscription_max_serps": 0,
    "connection_gsc": 1, "connection_ga": 1,
}


def quota_for(payload, resource):
    return next(q for q in payload["quota"] if q["resource"] == resource)


class TestQuotaDirection(unittest.TestCase):
    def test_counter_is_remaining_and_used_is_derived(self):
        row = quota_for(cli._plan_payload(HEALTHY), "keyword research")
        self.assertEqual(row["left"], 298)
        self.assertEqual(row["of"], 300)
        self.assertEqual(row["used"], 2, "counter read as 'used' inverts the whole view")

    def test_a_nearly_exhausted_account_is_reported_as_exhausted(self):
        """The direction has to fail the other way too, or the assertion above
        would pass on a client that just echoed the number back."""
        nearly = dict(HEALTHY, subscription_kr=2, subscription_max_kr=300)
        row = quota_for(cli._plan_payload(nearly), "keyword research")
        self.assertEqual(row["left"], 2)
        self.assertEqual(row["used"], 298)

    def test_serp_absent_from_plan_shows_zero_of_zero(self):
        row = quota_for(cli._plan_payload(HEALTHY), "SERP rank checks")
        self.assertEqual((row["left"], row["of"]), (0, 0))

    def test_used_is_never_negative_when_the_server_disagrees_with_itself(self):
        odd = dict(HEALTHY, subscription_kr=400, subscription_max_kr=300)
        self.assertEqual(quota_for(cli._plan_payload(odd), "keyword research")["used"], 0)


class TestAbsentIsNotZero(unittest.TestCase):
    def test_missing_quota_field_reads_unknown_not_zero(self):
        """'0 researches left' and 'the API stopped sending this field' are
        opposite facts, and only one of them should stop someone working."""
        stripped = {k: v for k, v in HEALTHY.items() if k != "subscription_kr"}
        row = quota_for(cli._plan_payload(stripped), "keyword research")
        self.assertEqual(row["left"], cli.UNKNOWN)
        self.assertEqual(row["used"], cli.UNKNOWN,
                         "used must not be computed from a field that was absent")

    def test_null_quota_field_reads_unknown(self):
        row = quota_for(cli._plan_payload(dict(HEALTHY, subscription_kr=None)), "keyword research")
        self.assertEqual(row["left"], cli.UNKNOWN)

    def test_explicit_zero_is_preserved_as_zero(self):
        row = quota_for(cli._plan_payload(dict(HEALTHY, subscription_kr=0)), "keyword research")
        self.assertEqual(row["left"], 0, "a real zero must not be rewritten as unknown")

    def test_missing_site_slots_reads_unknown(self):
        stripped = {k: v for k, v in HEALTHY.items() if k != "subscription_max_blogs"}
        self.assertEqual(cli._plan_payload(stripped)["site_slots"]["max"], cli.UNKNOWN)

    def test_num_helper_distinguishes_all_three_states(self):
        self.assertEqual(cli._num({}, "x"), cli.UNKNOWN)
        self.assertEqual(cli._num({"x": None}, "x"), cli.UNKNOWN)
        self.assertEqual(cli._num({"x": 0}, "x"), 0)


class TestSiteSlotsDoNotInventAnAccountFact(unittest.TestCase):
    """`user.checkin` reports the cap and nothing that counts registered blogs.

    This shipped as a hardcoded `used_here: 1`, which read as an account fact,
    was true on the day it was written, and could never have gone wrong out
    loud -- a constant wearing a predicate's name. The two honest answers are
    'the server does not say' and 'this machine is configured for N'.
    """

    def test_account_side_usage_is_unknown_not_a_number(self):
        slots = cli._plan_payload(HEALTHY)["site_slots"]
        self.assertEqual(slots["used_on_account"], cli.UNKNOWN)

    def test_local_count_tracks_the_registry_rather_than_a_literal(self):
        for count in (0, 1, 2, 7):
            slots = cli._plan_payload(HEALTHY, configured_locally=count)["site_slots"]
            self.assertEqual(slots["configured_locally"], count)

    def test_local_count_is_unknown_when_the_caller_did_not_supply_one(self):
        slots = cli._plan_payload(HEALTHY)["site_slots"]
        self.assertEqual(slots["configured_locally"], cli.UNKNOWN)


class TestPlanMetadata(unittest.TestCase):
    def test_missing_product_name_is_unknown_not_blank(self):
        stripped = {k: v for k, v in HEALTHY.items() if k != "product_name"}
        self.assertEqual(cli._plan_payload(stripped)["product"], cli.UNKNOWN)

    def test_false_expiry_renders_as_never(self):
        self.assertEqual(cli._plan_payload(HEALTHY)["expires"], "never")

    def test_a_real_expiry_date_is_preserved(self):
        payload = cli._plan_payload(dict(HEALTHY, subscription_expires="2027-01-01"))
        self.assertEqual(payload["expires"], "2027-01-01")


class TestOutput(unittest.TestCase):
    def test_json_output_is_parseable(self):
        import json
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.emit({"a": 1, "b": [1, 2]}, "json")
        self.assertEqual(json.loads(buffer.getvalue()), {"a": 1, "b": [1, 2]})

    def test_warnings_go_to_stderr_so_json_stays_a_clean_pipe(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            cli.warn("this must not land on stdout")
        self.assertEqual(out.getvalue(), "")
        self.assertIn("this must not land on stdout", err.getvalue())

    def test_table_renders_empty_values_as_a_dash(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.emit({"present": 5, "absent": None}, "table")
        self.assertIn("-", buffer.getvalue())


class TestParser(unittest.TestCase):
    def test_global_flags_work_before_and_after_the_subcommand(self):
        """argparse accepts them only before the subcommand by default, which is
        the position nobody reaches for."""
        before = cli.parse_args(["--site", "x", "--output", "json", "plan"])
        after = cli.parse_args(["plan", "--site", "x", "--output", "json"])
        for parsed in (before, after):
            self.assertEqual(parsed.site, "x")
            self.assertEqual(parsed.output, "json")

    def test_subparser_does_not_clobber_a_flag_given_earlier(self):
        """The failure this guards against is silent: with `parents=`, a
        subparser re-declaring --site writes its own default over the value the
        user already supplied, so `--site x plan` runs against no brand at all
        rather than erroring."""
        self.assertEqual(cli.parse_args(["--site", "alpha", "doctor"]).site, "alpha")
        self.assertTrue(cli.parse_args(["--confirm", "plan"]).confirm)

    def test_confirm_defaults_off(self):
        self.assertFalse(cli.parse_args(["plan"]).confirm)

    def test_dashboard_does_not_print_the_url_by_default(self):
        """The link is a live one-shot credential and stdout is captured into
        agent transcripts, so printing must be opt-in."""
        self.assertFalse(cli.parse_args(["dashboard"]).print_url)


if __name__ == "__main__":
    unittest.main()
