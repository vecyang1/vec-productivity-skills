import importlib.util
import json
import pathlib
import sys
import unittest
from unittest import mock


SCRIPT_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "fluentcrm_ops.py"


def load_module():
    spec = importlib.util.spec_from_file_location("fluentcrm_ops", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["fluentcrm_ops"] = module
    spec.loader.exec_module(module)
    return module


class FluentCrmOpsTests(unittest.TestCase):
    def test_counts_php_is_read_only_and_uses_fluentcrm_tables(self):
        ops = load_module()

        code = ops.build_counts_php()

        self.assertIn("fc_subscribers", code)
        self.assertIn("GROUP BY status", code)
        self.assertIn("COUNT(*)", code)
        self.assertNotIn("INSERT", code.upper())
        self.assertNotIn("UPDATE", code.upper())
        self.assertNotIn("DELETE FROM", code.upper())

    def test_php_runner_routes_through_novamira_execute_php(self):
        ops = load_module()

        with mock.patch.object(ops, "execute_ability", return_value={"ok": True}) as execute:
            result = ops.run_php("return 1;")

        self.assertEqual(result, {"ok": True})
        execute.assert_called_once_with("novamira/execute-php", {"code": "return 1;"})

    def test_execute_ability_unwraps_novamira_return_value(self):
        ops = load_module()
        wrapped = {
            "success": True,
            "data": {
                "success": True,
                "return_value": {"site": "Example", "plugin_surface": {"actions": []}},
                "output": "",
                "errors": [],
            },
        }

        with mock.patch.object(ops, "load_wp_ops") as load_wp_ops:
            load_wp_ops.return_value.execute_ability.return_value = wrapped
            result = ops.execute_ability("novamira/execute-php", {"code": "return array();"})

        self.assertEqual(result["site"], "Example")
        self.assertIn("plugin_surface", result)

    def test_execute_ability_unwraps_fluentcrm_data_payload(self):
        ops = load_module()
        wrapped = {"success": True, "data": {"items": [], "total": 0, "page": 1}}

        with mock.patch.object(ops, "load_wp_ops") as load_wp_ops:
            load_wp_ops.return_value.execute_ability.return_value = wrapped
            result = ops.execute_ability("fluent-crm/list-contacts", {"per_page": 5})

        self.assertEqual(result, {"items": [], "total": 0, "page": 1})

    def test_execute_ability_preserves_error_return_value_envelopes(self):
        ops = load_module()
        error_shapes = [
            {
                "success": False,
                "data": {"success": True, "return_value": {"misleading": True}},
            },
            {
                "success": True,
                "data": {"success": False, "return_value": {"misleading": True}},
            },
            {
                "success": True,
                "data": {
                    "success": True,
                    "return_value": {"misleading": True},
                    "errors": ["PHP warning"],
                },
            },
        ]

        for wrapped in error_shapes:
            with self.subTest(wrapped=wrapped):
                self.assertEqual(ops.unwrap_ability_result(wrapped), wrapped)

    def test_php_command_blocks_mutating_code_without_confirmation(self):
        ops = load_module()

        with mock.patch.object(ops, "execute_ability") as execute:
            with self.assertRaises(SystemExit):
                ops.main(["php", "$wpdb->query('UPDATE wp_fc_subscribers SET status = draft');"])

        execute.assert_not_called()

    def test_ability_command_blocks_write_like_ability_without_confirmation(self):
        ops = load_module()

        with mock.patch.object(ops, "execute_ability") as execute:
            with self.assertRaises(SystemExit):
                ops.main(["ability", "fluent-crm/upsert-contact", "--params", "{}"])

        execute.assert_not_called()

    def test_ability_command_allows_write_like_ability_with_confirmation(self):
        ops = load_module()

        with mock.patch.object(ops, "execute_ability", return_value={"ok": True}) as execute:
            with mock.patch.object(ops, "print_json"):
                ops.main(["ability", "fluent-crm/upsert-contact", "--params", "{}", "--confirm-write"])

        execute.assert_called_once_with("fluent-crm/upsert-contact", {})

    def test_doctor_php_reads_plugin_header_version_when_needed(self):
        ops = load_module()

        code = ops.build_doctor_php()

        self.assertIn("get_plugin_data", code)
        self.assertIn("fluent-crm/fluent-crm.php", code)

    def test_contacts_uses_native_fluentcrm_ability(self):
        ops = load_module()

        with mock.patch.object(ops, "execute_ability", return_value={"items": []}) as execute:
            result = ops.list_contacts(search="ada@example.com", tags=["vip"], limit=25)

        self.assertEqual(result, {"items": []})
        execute.assert_called_once()
        ability, params = execute.call_args.args
        self.assertEqual(ability, "fluent-crm/list-contacts")
        self.assertEqual(params["search"], "ada@example.com")
        self.assertEqual(params["tags"], ["vip"])
        self.assertEqual(params["per_page"], 25)

    def test_refresh_surface_can_write_json_payload(self):
        ops = load_module()
        payload = {"site": "Example", "tables": [{"name": "wp_fc_subscribers"}]}

        with mock.patch.object(ops, "run_php", return_value=payload):
            with mock.patch("pathlib.Path.write_text") as write_text:
                result = ops.refresh_surface(output=pathlib.Path("/tmp/fluentcrm-surface.json"))

        self.assertEqual(result, payload)
        written = json.loads(write_text.call_args.args[0])
        self.assertEqual(written["site"], "Example")
        self.assertEqual(written["tables"][0]["name"], "wp_fc_subscribers")

    def test_surface_php_reads_plugin_header_version_when_needed(self):
        ops = load_module()

        code = ops.build_surface_php()

        self.assertIn("get_plugin_data", code)
        self.assertIn("fluent-crm/fluent-crm.php", code)

    def test_self_test_runs_safe_read_checks_and_write_preview(self):
        ops = load_module()
        doctor = {
            "fluentcrm": {"loaded": True},
            "tables": {
                "subscribers": {"exists": True},
                "subscriber_pivot": {"exists": True},
                "lists": {"exists": True},
                "tags": {"exists": True},
                "funnels": {"exists": True},
                "campaigns": {"exists": True},
            },
        }
        counts = {"contacts": {"total": 0}, "lists": {"total": 3}, "tags": {"total": 3}}
        table_rows = {"exists": True, "rows": []}

        with mock.patch.object(
            ops,
            "run_php",
            side_effect=[doctor, counts, table_rows, table_rows, table_rows],
        ) as run_php:
            with mock.patch.object(ops, "list_contacts", return_value={"items": [], "total": 0}):
                result = ops.run_self_test()

        self.assertTrue(result["ok"])
        self.assertEqual(run_php.call_count, 5)
        self.assertTrue(result["checks"]["write_preview"]["dry_run"])

    def test_self_test_fails_when_write_preview_is_not_dry_run(self):
        ops = load_module()
        doctor = {
            "fluentcrm": {"loaded": True},
            "tables": {
                "subscribers": {"exists": True},
                "subscriber_pivot": {"exists": True},
                "lists": {"exists": True},
                "tags": {"exists": True},
                "funnels": {"exists": True},
                "campaigns": {"exists": True},
            },
        }
        counts = {"contacts": {"total": 0}, "lists": {"total": 3}, "tags": {"total": 3}}
        table_rows = {"exists": True, "rows": []}

        with mock.patch.object(
            ops,
            "run_php",
            side_effect=[doctor, counts, table_rows, table_rows, table_rows],
        ):
            with mock.patch.object(ops, "list_contacts", return_value={"items": [], "total": 0}):
                with mock.patch.object(ops, "upsert_contact", return_value={"dry_run": False}):
                    result = ops.run_self_test()

        self.assertFalse(result["ok"])
        self.assertFalse(result["checks"]["write_preview"]["ok"])


if __name__ == "__main__":
    unittest.main()
