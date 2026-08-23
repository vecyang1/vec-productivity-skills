#!/usr/bin/env python3
"""FluentCRM operations through the Novamira WordPress MCP bridge."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import sys
from typing import Any


SKILL_ROOT = pathlib.Path(__file__).resolve().parents[1]
WRITE_LIKE_ABILITY_TOKENS = (
    "attach",
    "bulk",
    "create",
    "delete",
    "detach",
    "duplicate",
    "execute",
    "import",
    "pause",
    "resume",
    "schedule",
    "send",
    "sync",
    "unschedule",
    "update",
    "upsert",
)
MUTATING_PHP_SNIPPETS = (
    "$wpdb->delete",
    "$wpdb->insert",
    "$wpdb->query('delete",
    "$wpdb->query('drop",
    "$wpdb->query('insert",
    "$wpdb->query('replace",
    "$wpdb->query('truncate",
    "$wpdb->query('update",
    "$wpdb->replace",
    "$wpdb->update",
    "->create(",
    "->createorupdate(",
    "->delete(",
    "->save(",
    "->update(",
    "alter table",
    "attachlists(",
    "attachtags(",
    "create table",
    "delete from",
    "detachlists(",
    "detachtags(",
    "drop table",
    "fluentcrmapi('contacts')->createorupdate",
    "fluentcrmapi(\"contacts\")->createorupdate",
    "insert into",
    "replace into",
    "truncate table",
    "update ",
    "wp_delete_",
    "wp_insert_",
    "wp_update_",
)


def _json_default(value: Any) -> str:
    return str(value)


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, default=_json_default))


def find_wp_ops_path() -> pathlib.Path:
    env_path = os.getenv("NOVAMIRA_WP_OPS")
    candidates = []
    if env_path:
        candidates.append(pathlib.Path(env_path).expanduser())
    candidates.extend(
        [
            SKILL_ROOT.parent / "novamira-ops" / "scripts" / "wp_ops.py",
            pathlib.Path.home()
            / ".gemini"
            / "antigravity"
            / "skills"
            / "novamira-ops"
            / "scripts"
            / "wp_ops.py",
            pathlib.Path.home()
            / ".agents"
            / "skills"
            / "novamira-ops"
            / "scripts"
            / "wp_ops.py",
            pathlib.Path.home()
            / ".codex"
            / "skills"
            / "novamira-ops"
            / "scripts"
            / "wp_ops.py",
        ]
    )
    for path in candidates:
        if path.exists():
            return path
    searched = "\n".join(f"- {path}" for path in candidates)
    raise FileNotFoundError(
        "Cannot find Novamira wp_ops.py bridge. Set NOVAMIRA_WP_OPS or install novamira-ops.\n"
        f"Searched:\n{searched}"
    )


def load_wp_ops():
    path = find_wp_ops_path()
    spec = importlib.util.spec_from_file_location("novamira_wp_ops", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load Novamira bridge from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def unwrap_ability_result(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    data = value.get("data")
    if isinstance(data, dict) and "return_value" in data:
        if value.get("success") is not True:
            return value
        if data.get("success") is not True:
            return value
        if data.get("errors"):
            return value
        return data["return_value"]
    if not isinstance(data, dict):
        if value.get("success") is True and "data" in value:
            return data
        return value
    if value.get("success") is True and "data" in value:
        return data
    return value


def execute_ability(ability_name: str, parameters: dict[str, Any]) -> Any:
    return unwrap_ability_result(load_wp_ops().execute_ability(ability_name, parameters))


def php_looks_mutating(code: str) -> bool:
    normalized = " ".join(code.lower().split())
    return any(snippet in normalized for snippet in MUTATING_PHP_SNIPPETS)


def ability_looks_mutating(name: str) -> bool:
    action = name.rsplit("/", 1)[-1].replace("_", "-").lower()
    tokens = [token for token in action.split("-") if token]
    return any(token in WRITE_LIKE_ABILITY_TOKENS for token in tokens)


def require_write_confirmation(kind: str, detail: str, confirmed: bool) -> None:
    if confirmed:
        return
    raise SystemExit(
        f"Refusing to run potentially mutating {kind} without --confirm-write: {detail}"
    )


def run_php(code: str) -> Any:
    return execute_ability("novamira/execute-php", {"code": code})


def _php_helpers() -> str:
    return r"""
global $wpdb;
$prefix = $wpdb->prefix;

$table_exists = function ($table) use ($wpdb) {
    return $wpdb->get_var($wpdb->prepare('SHOW TABLES LIKE %s', $table)) === $table;
};

$columns_for = function ($table) use ($wpdb, $table_exists) {
    if (!$table_exists($table)) {
        return array();
    }
    return array_map(function ($row) {
        return $row['Field'];
    }, $wpdb->get_results('SHOW COLUMNS FROM `' . esc_sql($table) . '`', ARRAY_A));
};

$select_existing = function ($table, $wanted, $limit = 100) use ($wpdb, $columns_for, $table_exists) {
    if (!$table_exists($table)) {
        return array('table' => $table, 'exists' => false, 'rows' => array());
    }
    $columns = $columns_for($table);
    $selected = array_values(array_intersect($wanted, $columns));
    if (!$selected) {
        $selected = array_slice($columns, 0, 12);
    }
    $sql_columns = implode(', ', array_map(function ($column) {
        return '`' . esc_sql($column) . '`';
    }, $selected));
    $limit = max(1, min(500, intval($limit)));
    $rows = $wpdb->get_results("SELECT {$sql_columns} FROM `" . esc_sql($table) . "` LIMIT {$limit}", ARRAY_A);
    return array('table' => $table, 'exists' => true, 'columns' => $columns, 'rows' => $rows);
};
"""


def build_doctor_php() -> str:
    return (
        _php_helpers()
        + r"""
$plugins = (array) get_option('active_plugins', array());
$network_plugins = is_multisite() ? array_keys((array) get_site_option('active_sitewide_plugins', array())) : array();
$active_plugins = array_merge($plugins, $network_plugins);
$fluent_plugins = array_values(array_filter($active_plugins, function ($plugin) {
    return stripos($plugin, 'fluent') !== false;
}));
$fluentcrm_version = defined('FLUENTCRM_VERSION') ? FLUENTCRM_VERSION : null;
if (!$fluentcrm_version && file_exists(WP_PLUGIN_DIR . '/fluent-crm/fluent-crm.php')) {
    if (!function_exists('get_plugin_data')) {
        require_once ABSPATH . 'wp-admin/includes/plugin.php';
    }
    if (function_exists('get_plugin_data')) {
        $plugin_data = get_plugin_data(WP_PLUGIN_DIR . '/fluent-crm/fluent-crm.php', false, false);
        $fluentcrm_version = isset($plugin_data['Version']) ? $plugin_data['Version'] : null;
    }
}
$tables = array(
    'subscribers' => $prefix . 'fc_subscribers',
    'subscriber_pivot' => $prefix . 'fc_subscriber_pivot',
    'lists' => $prefix . 'fc_lists',
    'tags' => $prefix . 'fc_tags',
    'funnels' => $prefix . 'fc_funnels',
    'campaigns' => $prefix . 'fc_campaigns',
);
$table_status = array();
foreach ($tables as $label => $table) {
    $table_status[$label] = array('name' => $table, 'exists' => $table_exists($table));
}
return array(
    'site' => array(
        'name' => get_bloginfo('name'),
        'home_url' => home_url(),
        'wp_version' => get_bloginfo('version'),
        'prefix' => $prefix,
    ),
    'fluentcrm' => array(
        'version' => $fluentcrm_version,
        'loaded' => defined('FLUENTCRM') || class_exists('FluentCrm\\App\\Models\\Subscriber'),
        'active_plugins' => $fluent_plugins,
    ),
    'tables' => $table_status,
);
"""
    )


def build_counts_php() -> str:
    return (
        _php_helpers()
        + r"""
$subscribers = $prefix . 'fc_subscribers';
$lists = $prefix . 'fc_lists';
$tags = $prefix . 'fc_tags';
$result = array(
    'site' => home_url(),
    'contacts' => array('total' => 0, 'by_status' => array()),
    'lists' => array('total' => 0),
    'tags' => array('total' => 0),
);
if ($table_exists($subscribers)) {
    $result['contacts']['total'] = intval($wpdb->get_var("SELECT COUNT(*) FROM `" . esc_sql($subscribers) . "`"));
    $result['contacts']['by_status'] = $wpdb->get_results(
        "SELECT COALESCE(status, '') AS status, COUNT(*) AS count FROM `" . esc_sql($subscribers) . "` GROUP BY status ORDER BY count DESC",
        ARRAY_A
    );
}
if ($table_exists($lists)) {
    $result['lists']['total'] = intval($wpdb->get_var("SELECT COUNT(*) FROM `" . esc_sql($lists) . "`"));
}
if ($table_exists($tags)) {
    $result['tags']['total'] = intval($wpdb->get_var("SELECT COUNT(*) FROM `" . esc_sql($tags) . "`"));
}
return $result;
"""
    )


def build_taxonomy_php(kind: str, limit: int) -> str:
    if kind not in {"lists", "tags"}:
        raise ValueError("kind must be lists or tags")
    table_name = "fc_lists" if kind == "lists" else "fc_tags"
    return (
        _php_helpers()
        + f"""
$table = $prefix . '{table_name}';
return $select_existing($table, array('id', 'title', 'slug', 'description', 'created_at', 'updated_at'), {int(limit)});
"""
    )


def build_funnels_php(limit: int) -> str:
    return (
        _php_helpers()
        + f"""
$table = $prefix . 'fc_funnels';
return $select_existing($table, array('id', 'title', 'trigger_name', 'type', 'status', 'created_at', 'updated_at'), {int(limit)});
"""
    )


def build_surface_php() -> str:
    return (
        _php_helpers()
        + r"""
$all_tables = $wpdb->get_col($wpdb->prepare('SHOW TABLES LIKE %s', $prefix . 'fc_%'));
$fluentcrm_version = defined('FLUENTCRM_VERSION') ? FLUENTCRM_VERSION : null;
if (!$fluentcrm_version && file_exists(WP_PLUGIN_DIR . '/fluent-crm/fluent-crm.php')) {
    if (!function_exists('get_plugin_data')) {
        require_once ABSPATH . 'wp-admin/includes/plugin.php';
    }
    if (function_exists('get_plugin_data')) {
        $plugin_data = get_plugin_data(WP_PLUGIN_DIR . '/fluent-crm/fluent-crm.php', false, false);
        $fluentcrm_version = isset($plugin_data['Version']) ? $plugin_data['Version'] : null;
    }
}
$folders = array(
    'actions' => WP_PLUGIN_DIR . '/fluent-crm/app/Services/Funnel/Actions',
    'benchmarks' => WP_PLUGIN_DIR . '/fluent-crm/app/Services/Funnel/Benchmarks',
    'controllers' => WP_PLUGIN_DIR . '/fluent-crm/app/Http/Controllers',
    'models' => WP_PLUGIN_DIR . '/fluent-crm/app/Models',
);
$files = array();
foreach ($folders as $label => $folder) {
    $files[$label] = array(
        'path' => str_replace(ABSPATH, '', $folder),
        'exists' => is_dir($folder),
        'files' => is_dir($folder) ? array_values(array_filter(scandir($folder), function ($file) {
            return substr($file, -4) === '.php';
        })) : array(),
    );
}
return array(
    'captured_at' => gmdate('c'),
    'site' => get_bloginfo('name'),
    'home_url' => home_url(),
    'fluentcrm_version' => $fluentcrm_version,
    'tables' => array_map(function ($table) use ($columns_for) {
        return array('name' => $table, 'columns' => $columns_for($table));
    }, $all_tables),
    'plugin_surface' => $files,
);
"""
    )


def list_contacts(
    search: str | None = None,
    tags: list[str] | None = None,
    lists: list[str] | None = None,
    statuses: list[str] | None = None,
    limit: int = 50,
    include_custom_fields: bool = False,
) -> Any:
    params: dict[str, Any] = {
        "per_page": max(1, min(500, int(limit))),
        "include_custom_fields": include_custom_fields,
    }
    if search:
        params["search"] = search
    if tags:
        params["tags"] = tags
    if lists:
        params["lists"] = lists
    if statuses:
        params["statuses"] = statuses
    return execute_ability("fluent-crm/list-contacts", params)


def upsert_contact(args: argparse.Namespace) -> Any:
    params: dict[str, Any] = {"email": args.email}
    for attr in ("first_name", "last_name", "status"):
        value = getattr(args, attr)
        if value:
            params[attr] = value
    if args.tag:
        params["tags"] = args.tag
    if args.list:
        params["lists"] = args.list
    if not args.confirm_write:
        return {
            "dry_run": True,
            "ability": "fluent-crm/upsert-contact",
            "params": params,
            "next_step": "Re-run with --confirm-write after checking the payload.",
        }
    return execute_ability("fluent-crm/upsert-contact", params)


def refresh_surface(output: pathlib.Path | None = None) -> Any:
    payload = run_php(build_surface_php())
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def run_self_test(refresh_surface_output: pathlib.Path | None = None) -> dict[str, Any]:
    doctor = run_php(build_doctor_php())
    counts = run_php(build_counts_php())
    lists = run_php(build_taxonomy_php("lists", 10))
    tags = run_php(build_taxonomy_php("tags", 10))
    funnels = run_php(build_funnels_php(10))
    contacts = list_contacts(limit=5)
    write_preview = upsert_contact(
        argparse.Namespace(
            email="codex-preview@example.invalid",
            first_name="Codex",
            last_name=None,
            status=None,
            tag=["subscriber"],
            list=None,
            confirm_write=False,
        )
    )

    table_status = doctor.get("tables", {}) if isinstance(doctor, dict) else {}
    expected_tables = (
        "subscribers",
        "subscriber_pivot",
        "lists",
        "tags",
        "funnels",
        "campaigns",
    )
    tables_ok = all(
        table_status.get(table, {}).get("exists") is True
        for table in expected_tables
    )
    write_preview_check = {"ok": False, "payload": write_preview}
    if isinstance(write_preview, dict):
        write_preview_check = {
            "ok": write_preview.get("dry_run") is True,
            **write_preview,
        }

    checks: dict[str, Any] = {
        "doctor": {
            "ok": bool(
                isinstance(doctor, dict)
                and doctor.get("fluentcrm", {}).get("loaded")
                and tables_ok
            ),
            "fluentcrm_version": (
                doctor.get("fluentcrm", {}).get("version")
                if isinstance(doctor, dict)
                else None
            ),
            "tables_ok": tables_ok,
        },
        "counts": {
            "ok": isinstance(counts, dict)
            and isinstance(counts.get("contacts"), dict)
            and isinstance(counts.get("lists"), dict)
            and isinstance(counts.get("tags"), dict),
            "summary": counts,
        },
        "lists": {
            "ok": isinstance(lists, dict) and lists.get("exists") is True,
            "count": len(lists.get("rows", [])) if isinstance(lists, dict) else None,
        },
        "tags": {
            "ok": isinstance(tags, dict) and tags.get("exists") is True,
            "count": len(tags.get("rows", [])) if isinstance(tags, dict) else None,
        },
        "funnels": {
            "ok": isinstance(funnels, dict) and funnels.get("exists") is True,
            "count": len(funnels.get("rows", [])) if isinstance(funnels, dict) else None,
        },
        "contacts": {
            "ok": isinstance(contacts, dict) and "items" in contacts,
            "total": contacts.get("total") if isinstance(contacts, dict) else None,
        },
        "write_preview": write_preview_check,
    }

    if refresh_surface_output is not None:
        surface = refresh_surface(refresh_surface_output)
        checks["surface"] = {
            "ok": isinstance(surface, dict) and "plugin_surface" in surface and "tables" in surface,
            "captured_at": surface.get("captured_at") if isinstance(surface, dict) else None,
            "output": str(refresh_surface_output),
        }

    return {
        "ok": all(check.get("ok", True) is not False for check in checks.values() if isinstance(check, dict)),
        "checks": checks,
    }


def parse_csv(values: list[str] | None) -> list[str] | None:
    if not values:
        return None
    parsed: list[str] = []
    for value in values:
        parsed.extend(item.strip() for item in value.split(",") if item.strip())
    return parsed or None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Operate FluentCRM through Novamira WordPress MCP.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="Check FluentCRM plugin and table availability.")
    subparsers.add_parser("counts", help="Read contact/list/tag counts.")

    contacts = subparsers.add_parser("contacts", help="List contacts through native FluentCRM ability.")
    contacts.add_argument("--search")
    contacts.add_argument("--tag", action="append", help="Tag id/slug. Repeat or comma-separate.")
    contacts.add_argument("--list", action="append", help="List id/slug. Repeat or comma-separate.")
    contacts.add_argument("--status", action="append", help="Status. Repeat or comma-separate.")
    contacts.add_argument("--limit", type=int, default=50)
    contacts.add_argument("--include-custom-fields", action="store_true")

    for name in ("lists", "tags", "funnels"):
        child = subparsers.add_parser(name, help=f"Read FluentCRM {name}.")
        child.add_argument("--limit", type=int, default=100)

    surface = subparsers.add_parser("refresh-surface", help="Introspect live FluentCRM tables/classes.")
    surface.add_argument("--output", type=pathlib.Path)

    self_test = subparsers.add_parser(
        "self-test",
        help="Run safe live read checks and dry-run write preview.",
    )
    self_test.add_argument("--refresh-surface", action="store_true")
    self_test.add_argument(
        "--surface-output",
        type=pathlib.Path,
        default=SKILL_ROOT / "references" / "live-surface.json",
    )

    php = subparsers.add_parser("php", help="Run raw PHP through novamira/execute-php.")
    php.add_argument("code")
    php.add_argument("--confirm-write", action="store_true")

    ability = subparsers.add_parser("ability", help="Call a Novamira/FluentCRM ability.")
    ability.add_argument("name")
    ability.add_argument("--params", default="{}")
    ability.add_argument("--confirm-write", action="store_true")

    upsert = subparsers.add_parser("upsert-contact", help="Create or update a FluentCRM contact.")
    upsert.add_argument("email")
    upsert.add_argument("--first-name")
    upsert.add_argument("--last-name")
    upsert.add_argument("--status")
    upsert.add_argument("--tag", action="append", help="Tag id/slug. Repeat or comma-separate.")
    upsert.add_argument("--list", action="append", help="List id/slug. Repeat or comma-separate.")
    upsert.add_argument("--confirm-write", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "doctor":
        print_json(run_php(build_doctor_php()))
    elif args.command == "counts":
        print_json(run_php(build_counts_php()))
    elif args.command == "contacts":
        print_json(
            list_contacts(
                search=args.search,
                tags=parse_csv(args.tag),
                lists=parse_csv(args.list),
                statuses=parse_csv(args.status),
                limit=args.limit,
                include_custom_fields=args.include_custom_fields,
            )
        )
    elif args.command == "lists":
        print_json(run_php(build_taxonomy_php("lists", args.limit)))
    elif args.command == "tags":
        print_json(run_php(build_taxonomy_php("tags", args.limit)))
    elif args.command == "funnels":
        print_json(run_php(build_funnels_php(args.limit)))
    elif args.command == "refresh-surface":
        print_json(refresh_surface(args.output))
    elif args.command == "self-test":
        output = args.surface_output if args.refresh_surface else None
        print_json(run_self_test(output))
    elif args.command == "php":
        if php_looks_mutating(args.code):
            require_write_confirmation("PHP", args.code, args.confirm_write)
        print_json(run_php(args.code))
    elif args.command == "ability":
        if ability_looks_mutating(args.name):
            require_write_confirmation("ability", args.name, args.confirm_write)
        print_json(execute_ability(args.name, json.loads(args.params)))
    elif args.command == "upsert-contact":
        args.tag = parse_csv(args.tag)
        args.list = parse_csv(args.list)
        print_json(upsert_contact(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
