#!/usr/bin/env python3
"""Letterly-to-Notion Dashboard Server.
Live HTTP server with auto-refresh, action queue, and full note management.
Zero external dependencies — stdlib only.
"""

import json
import os
import sys
import time
import signal
import shutil
import threading
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(SKILL_DIR, "index.json")
CONFIG_PATH = os.path.join(SKILL_DIR, "config.json")
QUEUE_PATH = os.path.join(SKILL_DIR, "action_queue.json")
BACKUP_DIR = os.path.join(SKILL_DIR, "backups")
MAX_BACKUPS = 10
BACKUP_INTERVAL_SECONDS = 3600  # 1 hour

# --- Data Layer ---

_index_cache = None
_index_mtime = 0

def load_config():
    defaults = {"port": 5588, "refresh_interval_seconds": 10,
                "default_sort": "date", "default_sort_dir": "desc",
                "default_filter_status": "all", "default_filter_tier": "all"}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                defaults.update(cfg)
        except Exception:
            pass
    return defaults

def load_index():
    global _index_cache, _index_mtime
    try:
        mtime = os.path.getmtime(INDEX_PATH)
    except OSError:
        return {"version": 2, "last_sync": None, "notes": {}}
    if _index_cache is not None and mtime == _index_mtime:
        return _index_cache
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            _index_cache = json.load(f)
            _index_mtime = mtime
            return _index_cache
    except Exception:
        return {"version": 2, "last_sync": None, "notes": {}}

def save_index(index):
    global _index_cache, _index_mtime
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    _index_cache = index
    _index_mtime = os.path.getmtime(INDEX_PATH)

def load_queue():
    if not os.path.exists(QUEUE_PATH):
        return {"actions": [], "created": None}
    try:
        with open(QUEUE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"actions": [], "created": None}

def save_queue(queue):
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

def backup_index(label="auto"):
    """Create a timestamped backup of index.json. Prunes old backups beyond MAX_BACKUPS."""
    if not os.path.exists(INDEX_PATH):
        return None
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_name = f"index_{ts}_{label}.json"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    shutil.copy2(INDEX_PATH, backup_path)
    # Prune old backups
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("index_") and f.endswith(".json")])
    while len(backups) > MAX_BACKUPS:
        oldest = backups.pop(0)
        try:
            os.remove(os.path.join(BACKUP_DIR, oldest))
        except OSError:
            pass
    return backup_path

def restore_index(backup_name=None):
    """Restore index.json from the latest or specified backup."""
    if not os.path.exists(BACKUP_DIR):
        return {"ok": False, "error": "No backups directory found"}
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("index_") and f.endswith(".json")])
    if not backups:
        return {"ok": False, "error": "No backups available"}
    if backup_name and backup_name in backups:
        src = os.path.join(BACKUP_DIR, backup_name)
    else:
        src = os.path.join(BACKUP_DIR, backups[-1])  # latest
    # Safety: backup current before restoring
    if os.path.exists(INDEX_PATH):
        backup_index(label="pre_restore")
    shutil.copy2(src, INDEX_PATH)
    global _index_cache, _index_mtime
    _index_cache = None
    _index_mtime = 0
    return {"ok": True, "message": f"Restored from {os.path.basename(src)}", "backup": os.path.basename(src)}

def list_backups():
    if not os.path.exists(BACKUP_DIR):
        return []
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("index_") and f.endswith(".json")])
    result = []
    for b in backups:
        p = os.path.join(BACKUP_DIR, b)
        try:
            size = os.path.getsize(p)
            with open(p, "r") as f:
                data = json.load(f)
                notes_count = len(data.get("notes", {}))
        except Exception:
            size, notes_count = 0, 0
        result.append({"name": b, "size": size, "notes": notes_count})
    return result

def _periodic_backup():
    """Background thread that backs up index.json periodically."""
    while True:
        time.sleep(BACKUP_INTERVAL_SECONDS)
        try:
            backup_index(label="periodic")
        except Exception:
            pass

def compute_tier(char_count):
    if char_count is None or char_count == 0:
        return "unknown"
    if char_count >= 500: return "content"
    if char_count >= 200: return "note"
    if char_count >= 50: return "spark"
    return "snippet"

def compute_stats(notes):
    stats = {"total": 0, "pushed": 0, "skipped": 0, "rejected": 0, "pending": 0, "queued": 0}
    tiers = {"content": 0, "note": 0, "spark": 0, "snippet": 0, "unknown": 0}
    langs = {}
    for n in notes.values():
        stats["total"] += 1
        status = n.get("status", "pending")
        if status.startswith("queued_"):
            stats["queued"] += 1
        else:
            stats[status] = stats.get(status, 0) + 1
        tier = compute_tier(n.get("char_count"))
        tiers[tier] += 1
        lang = n.get("detected_language", "?")
        langs[lang] = langs.get(lang, 0) + 1
    return {"status": stats, "tiers": tiers, "langs": langs}

def format_date(iso_str):
    if not iso_str: return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return iso_str[:10] if len(iso_str) >= 10 else iso_str

def build_notes_list(notes):
    rows = []
    for nid, n in notes.items():
        rows.append({
            "id": nid, "title": n.get("title", ""), "date": format_date(n.get("letterly_created")),
            "chars": n.get("char_count"), "tier": compute_tier(n.get("char_count")),
            "lang": n.get("detected_language", "?"), "status": n.get("status", "pending"),
            "notion_url": n.get("notion_url"), "preview": n.get("preview", ""),
            "processed_date": format_date(n.get("processed_date")),
        })
    rows.sort(key=lambda r: r["date"] or "", reverse=True)
    return rows

# --- HTTP Handler ---

class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default logging

    def _json_response(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html_response(self, html):
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        try:
            if path == "/":
                self._html_response(render_dashboard())
            elif path == "/api/notes":
                index = load_index()
                self._json_response({"ok": True, "data": build_notes_list(index.get("notes", {})),
                                     "last_sync": index.get("last_sync"), "total": len(index.get("notes", {}))})
            elif path == "/api/stats":
                index = load_index()
                self._json_response({"ok": True, "data": compute_stats(index.get("notes", {}))})
            elif path == "/api/config":
                self._json_response({"ok": True, "data": load_config()})
            elif path == "/api/queue":
                self._json_response({"ok": True, "data": load_queue()})
            elif path == "/api/health":
                index = load_index()
                self._json_response({"ok": True, "notes": len(index.get("notes", {})),
                                     "index_exists": os.path.exists(INDEX_PATH),
                                     "uptime": time.time() - SERVER_START})
            elif path == "/api/backups":
                self._json_response({"ok": True, "data": list_backups()})
            elif path.startswith("/api/note/"):
                note_id = path.split("/api/note/")[1].split("/")[0]
                index = load_index()
                note = index.get("notes", {}).get(note_id)
                if note:
                    self._json_response({"ok": True, "data": {**note, "id": note_id}})
                else:
                    self._json_response({"ok": False, "error": "Note not found"}, 404)
            else:
                self._json_response({"ok": False, "error": "Not found"}, 404)
        except Exception as e:
            self._json_response({"ok": False, "error": str(e)}, 500)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length > 0 else {}

            if path == "/api/action":
                result = handle_action(body)
                self._json_response(result)
            elif path.startswith("/api/note/") and path.endswith("/update"):
                note_id = path.split("/api/note/")[1].split("/")[0]
                result = handle_note_update(note_id, body)
                self._json_response(result)
            elif path == "/api/bulk":
                result = handle_bulk(body)
                self._json_response(result)
            elif path == "/api/queue/clear":
                save_queue({"actions": [], "created": None})
                self._json_response({"ok": True, "message": "Queue cleared"})
            elif path == "/api/backup":
                bp = backup_index(label="manual")
                self._json_response({"ok": True, "message": f"Backup created: {os.path.basename(bp)}" if bp else "No index to backup"})
            elif path == "/api/restore":
                name = body.get("backup_name")
                result = restore_index(name)
                self._json_response(result)
            else:
                self._json_response({"ok": False, "error": "Not found"}, 404)
        except Exception as e:
            self._json_response({"ok": False, "error": str(e)}, 500)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

def handle_action(body):
    action = body.get("action")  # push, skip, reject, undo
    note_id = str(body.get("note_id", ""))
    if not action or not note_id:
        return {"ok": False, "error": "Missing action or note_id"}

    index = load_index()
    notes = index.get("notes", {})

    if note_id not in notes:
        return {"ok": False, "error": f"Note {note_id} not in index"}

    if action == "push":
        # Direct push to Notion via API
        result = notion_push_note(note_id)
        return result

    elif action == "skip":
        notes[note_id]["status"] = "skipped"
        notes[note_id]["processed_date"] = datetime.now(timezone.utc).isoformat()
        save_index(index)
        return {"ok": True, "message": f"Note {note_id} skipped"}

    elif action == "reject":
        notes[note_id]["status"] = "rejected"
        notes[note_id]["processed_date"] = datetime.now(timezone.utc).isoformat()
        save_index(index)
        return {"ok": True, "message": f"Note {note_id} rejected"}

    elif action == "undo":
        notes[note_id]["status"] = "pending"
        notes[note_id]["processed_date"] = None
        notes[note_id]["notion_url"] = None
        # Remove from queue if present
        queue = load_queue()
        queue["actions"] = [a for a in queue["actions"] if a.get("note_id") != note_id]
        save_queue(queue)
        save_index(index)
        return {"ok": True, "message": f"Note {note_id} reset to pending"}

    return {"ok": False, "error": f"Unknown action: {action}"}

def handle_note_update(note_id, body):
    index = load_index()
    notes = index.get("notes", {})
    if note_id not in notes:
        return {"ok": False, "error": f"Note {note_id} not found"}
    allowed_fields = {"title", "preview", "detected_language", "tags_override"}
    for key, val in body.items():
        if key in allowed_fields:
            notes[note_id][key] = val
    save_index(index)
    return {"ok": True, "message": f"Note {note_id} updated"}

def handle_bulk(body):
    action = body.get("action")
    note_ids = body.get("note_ids", [])
    if not action or not note_ids:
        return {"ok": False, "error": "Missing action or note_ids"}
    results = []
    for nid in note_ids:
        r = handle_action({"action": action, "note_id": str(nid)})
        results.append({"note_id": nid, "ok": r.get("ok", False)})
    success = sum(1 for r in results if r["ok"])
    return {"ok": True, "message": f"{action}: {success}/{len(note_ids)} notes processed", "results": results}

# --- Direct Notion Push ---

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")  # set via env: export NOTION_TOKEN=ntn_...
NOTION_DB_ID = "22ce1b43239381c1993ecf632dad6d2d"
NOTION_API = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2022-06-28"

LANG_TAG_MAP = {"zh": "China", "vi": "Viet", "ja": "Japan", "th": "Thai"}

def notion_push_note(note_id):
    """Push a note directly to Notion via REST API. Returns page URL or error."""
    index = load_index()
    notes = index.get("notes", {})
    note = notes.get(str(note_id))
    if not note:
        return {"ok": False, "error": f"Note {note_id} not in index"}
    if note.get("status") == "pushed" and note.get("notion_url"):
        return {"ok": False, "error": "Already pushed"}

    title = note.get("title", "Untitled")
    lang = note.get("detected_language", "")
    preview = note.get("preview", "")
    char_count = note.get("char_count", 0)
    created = note.get("letterly_created", "")
    tags_override = note.get("tags_override")

    # Compute date (YYYY-MM-DD)
    pub_date = None
    if created:
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            pub_date = dt.strftime("%Y-%m-%d")
        except Exception:
            pass

    # Compute tags
    if tags_override:
        tags = [t.strip() for t in tags_override.split(",") if t.strip()]
    elif lang in LANG_TAG_MAP:
        tags = [LANG_TAG_MAP[lang]]
    else:
        tags = []

    # Build tier label
    tier = compute_tier(char_count)

    # Build page body
    body_text = f"Source: Letterly voice note #{note_id} | Recorded: {pub_date or 'unknown'}\nChars: {char_count or '?'} | Tier: {tier} | Language: {lang}\n\n---\n\n{preview or '(preview only — full transcript in Letterly)'}"

    # Notion API payload
    payload = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "Status": {"status": {"name": "Idea"}},
            "Media Type": {"multi_select": [{"name": "Audio"}]},
            "Source": {"rich_text": [{"text": {"content": f"Letterly #{note_id}"}}]},
            "Tags": {"multi_select": [{"name": t} for t in tags]},
        },
        "children": [
            {"object": "block", "type": "callout", "callout": {
                "rich_text": [{"text": {"content": f"Source: Letterly voice note #{note_id} | Recorded: {pub_date or 'unknown'}\nChars: {char_count or '?'} | Tier: {tier} | Language: {lang}"}}],
                "icon": {"emoji": "🎙️"},
            }},
            {"object": "block", "type": "divider", "divider": {}},
            {"object": "block", "type": "paragraph", "paragraph": {
                "rich_text": [{"text": {"content": preview[:2000] if preview else "(preview only)"}}]
            }},
        ]
    }

    if pub_date:
        payload["properties"]["Writtern date"] = {"date": {"start": pub_date}}

    # Call Notion API with retry
    last_error = None
    for attempt in range(2):
        try:
            req_body = json.dumps(payload).encode("utf-8")
            req = Request(NOTION_API, data=req_body, method="POST")
            req.add_header("Authorization", f"Bearer {NOTION_TOKEN}")
            req.add_header("Notion-Version", NOTION_VERSION)
            req.add_header("Content-Type", "application/json")

            with urlopen(req, timeout=20) as resp:
                result = json.loads(resp.read())
                page_url = result.get("url", "")

                # Update index
                notes[str(note_id)]["status"] = "pushed"
                notes[str(note_id)]["processed_date"] = datetime.now(timezone.utc).isoformat()
                notes[str(note_id)]["notion_url"] = page_url
                save_index(index)

                # Remove from queue if present
                queue = load_queue()
                queue["actions"] = [a for a in queue["actions"] if str(a.get("note_id")) != str(note_id)]
                save_queue(queue)

                return {"ok": True, "message": f"Pushed to Notion", "notion_url": page_url}

        except HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            last_error = f"Notion API {e.code}: {error_body[:200]}"
            if e.code == 429:  # Rate limited — wait and retry
                time.sleep(1)
                continue
            if e.code >= 500:  # Server error — retry
                time.sleep(0.5)
                continue
            return {"ok": False, "error": last_error}  # Client error — don't retry
        except (URLError, TimeoutError) as e:
            last_error = f"Network error: {str(e)}"
            time.sleep(0.5)
            continue
        except Exception as e:
            return {"ok": False, "error": f"Push failed: {str(e)}"}

    return {"ok": False, "error": last_error or "Push failed after retries"}

# --- HTML Dashboard ---

def render_dashboard():
    config = load_config()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Letterly Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{
  --bg:#FEF8FB;--bg-card:#fff;--bg-hover:#F9F0F5;
  --text:#111022;--text-dim:#413B4D;--border:#F9DAE9;
  --accent:#8B7FFF;--accent-hover:#241F37;
  --pink-light:#F9DAE9;--pink-dark:#E2C6D6;
  --radius-lg:1.5rem;--radius-md:0.75rem;--radius-sm:0.5rem;
}}
body{{font-family:'Onest',-apple-system,sans-serif;background:var(--bg);color:var(--text);padding:24px 32px;line-height:1.6;max-width:1400px;margin:0 auto}}
h1{{font-size:1.5rem;font-weight:700;display:flex;align-items:center;gap:8px}}
.header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}}
.subtitle{{color:var(--text-dim);font-size:.82rem;margin-bottom:20px;display:flex;gap:16px;align-items:center}}
.live-dot{{width:8px;height:8px;border-radius:50%;background:#22c55e;display:inline-block;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.pushing{{color:var(--accent);font-size:.8rem;display:flex;align-items:center;gap:6px}}
.pushing::before{{content:'';width:14px;height:14px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .6s linear infinite}}
.banner{{background:#FFF3CD;color:#664D03;padding:10px 16px;border-radius:var(--radius-md);margin-bottom:16px;font-size:.82rem;border:1px solid #FFE69C;display:none}}
.banner.visible{{display:block}}
.stats{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px}}
.stat{{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-md);padding:12px 18px;min-width:100px;text-align:center;box-shadow:0 1px 3px rgba(17,16,34,.04);cursor:pointer;transition:all .2s}}
.stat:hover,.stat.active{{border-color:var(--accent);box-shadow:0 0 0 2px rgba(139,127,255,.15)}}
.stat .num{{font-size:1.5rem;font-weight:700}}
.stat .label{{font-size:.68rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:.5px}}
.stat.pushed .num{{color:#059669}} .stat.skipped .num{{color:#D97706}}
.stat.rejected .num{{color:#DC2626}} .stat.pending .num{{color:var(--accent)}}
.stat.queued .num{{color:#0891B2}}
.controls{{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap;align-items:center}}
.controls input,.controls select{{background:var(--bg-card);border:1px solid var(--border);color:var(--text);padding:8px 12px;border-radius:var(--radius-md);font-size:.82rem;font-family:'Onest',sans-serif;outline:none;transition:border-color .2s}}
.controls input{{flex:1;min-width:200px}}
.controls input:focus,.controls select:focus{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(139,127,255,.12)}}
.controls select{{cursor:pointer}}
.btn{{padding:6px 14px;border-radius:var(--radius-sm);font-size:.75rem;font-weight:600;border:none;cursor:pointer;font-family:'Onest',sans-serif;transition:all .15s}}
.btn-push{{background:#E0E7FF;color:#3730A3}} .btn-push:hover{{background:#C7D2FE}}
.btn-skip{{background:#FEF3C7;color:#92400E}} .btn-skip:hover{{background:#FDE68A}}
.btn-reject{{background:#FEE2E2;color:#991B1B}} .btn-reject:hover{{background:#FECACA}}
.btn-undo{{background:#F3F4F6;color:#374151}} .btn-undo:hover{{background:#E5E7EB}}
.btn-sync{{background:var(--accent);color:#fff;padding:8px 18px;font-size:.82rem}} .btn-sync:hover{{background:var(--accent-hover)}}
table{{width:100%;border-collapse:separate;border-spacing:0;background:var(--bg-card);border-radius:var(--radius-lg);overflow:hidden;border:1px solid var(--border);box-shadow:0 1px 4px rgba(17,16,34,.05)}}
thead{{background:#F9F0F5}}
th{{padding:10px 14px;text-align:left;font-size:.7rem;text-transform:uppercase;letter-spacing:.5px;color:var(--text-dim);cursor:pointer;user-select:none;border-bottom:1px solid var(--border);font-weight:600;white-space:nowrap}}
th:hover{{color:var(--text)}} th .arrow{{margin-left:3px;opacity:.3;font-size:.6rem}}
th.active .arrow{{opacity:1;color:var(--accent)}}
td{{padding:10px 14px;border-bottom:1px solid #F5E8F0;font-size:.82rem;vertical-align:top}}
tr:hover{{background:var(--bg-hover)}} tr:last-child td{{border-bottom:none}}
.badge{{display:inline-block;padding:2px 8px;border-radius:var(--radius-sm);font-size:.7rem;font-weight:600;letter-spacing:.2px}}
.badge.pushed{{background:#D1FAE5;color:#065F46}} .badge.skipped{{background:#FEF3C7;color:#92400E}}
.badge.rejected{{background:#FEE2E2;color:#991B1B}} .badge.pending{{background:#EDE9FE;color:#5B21B6}}
.badge.queued_push{{background:#CFFAFE;color:#155E75}} .badge.content{{background:#E0E7FF;color:#3730A3}}
.badge.note{{background:#EDE9FE;color:#6D28D9}} .badge.spark{{background:#FEF3C7;color:#92400E}}
.badge.snippet{{background:#F3F4F6;color:#6B7280}} .badge.unknown{{background:#F3F4F6;color:#9CA3AF}}
.link{{color:var(--accent);text-decoration:none;font-weight:600}} .link:hover{{color:var(--accent-hover)}}
.preview{{color:var(--text-dim);font-size:.75rem;margin-top:2px;max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.title-cell{{font-weight:500}} .actions-cell{{white-space:nowrap;display:flex;gap:4px}}
.empty{{text-align:center;padding:48px;color:var(--text-dim)}}
.footer{{margin-top:16px;text-align:center;color:var(--text-dim);font-size:.72rem}}
.bulk-bar{{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--accent-hover);color:#fff;
  padding:12px 24px;border-radius:var(--radius-lg);display:none;align-items:center;gap:14px;
  box-shadow:0 8px 24px rgba(0,0,0,.2);z-index:999;font-size:.85rem;font-family:'Onest',sans-serif}}
.bulk-bar.visible{{display:flex}}
.bulk-bar .count{{font-weight:700}} .bulk-bar button{{background:rgba(255,255,255,.15);color:#fff;border:none;padding:6px 14px;
  border-radius:var(--radius-sm);cursor:pointer;font-size:.78rem;font-weight:600;font-family:'Onest',sans-serif}}
.bulk-bar button:hover{{background:rgba(255,255,255,.25)}}
.bulk-bar .bulk-close{{background:none;font-size:1.1rem;padding:4px 8px}}
input[type=checkbox]{{width:16px;height:16px;accent-color:var(--accent);cursor:pointer}}
.modal-overlay{{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(17,16,34,.5);z-index:1000;display:none;justify-content:center;align-items:center;backdrop-filter:blur(4px)}}
.modal-overlay.visible{{display:flex}}
.modal{{background:var(--bg-card);border-radius:var(--radius-lg);width:90%;max-width:700px;max-height:85vh;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.2);display:flex;flex-direction:column}}
.modal-header{{padding:20px 24px 12px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:flex-start}}
.modal-header h2{{font-size:1.2rem;font-weight:600;flex:1}}
.modal-close{{background:none;border:none;font-size:1.4rem;cursor:pointer;color:var(--text-dim);padding:4px 8px}}
.modal-close:hover{{color:var(--text)}}
.modal-body{{padding:20px 24px;overflow-y:auto;flex:1}}
.modal-meta{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}}
.modal-meta .badge{{font-size:.78rem;padding:4px 10px}}
.modal-field{{margin-bottom:14px}}
.modal-field label{{display:block;font-size:.72rem;text-transform:uppercase;letter-spacing:.5px;color:var(--text-dim);margin-bottom:4px;font-weight:600}}
.modal-field input,.modal-field textarea,.modal-field select{{width:100%;padding:8px 12px;border:1px solid var(--border);border-radius:var(--radius-sm);font-family:'Onest',sans-serif;font-size:.85rem;background:var(--bg);color:var(--text);outline:none}}
.modal-field input:focus,.modal-field textarea:focus{{border-color:var(--accent)}}
.modal-field textarea{{min-height:180px;resize:vertical;line-height:1.6}}
.modal-footer{{padding:14px 24px;border-top:1px solid var(--border);display:flex;gap:8px;justify-content:flex-end}}
.modal-footer .btn{{padding:8px 18px;font-size:.82rem}}
.footer code{{background:var(--pink-light);padding:2px 5px;border-radius:3px;font-size:.68rem}}
.toast-container{{position:fixed;top:20px;right:20px;z-index:1000}}
.toast{{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-md);padding:12px 18px;margin-bottom:8px;font-size:.82rem;box-shadow:0 4px 12px rgba(0,0,0,.1);animation:slideIn .3s ease}}
.toast.success{{border-left:4px solid #059669}} .toast.error{{border-left:4px solid #DC2626}}
@keyframes slideIn{{from{{transform:translateX(100%);opacity:0}}to{{transform:translateX(0);opacity:1}}}}
@media(max-width:768px){{body{{padding:12px}} .stats{{gap:6px}} .stat{{padding:8px 12px;min-width:70px}} .stat .num{{font-size:1.2rem}} td,th{{padding:6px 8px;font-size:.78rem}} .actions-cell{{flex-direction:column}}}}
</style>
</head>
<body>
<div class="header">
  <h1>Letterly Dashboard</h1>
  <button class="btn btn-sync" onclick="queueSync()">Sync All to Notion</button>
</div>
<p class="subtitle">
  <span><span class="live-dot"></span> Auto-refresh: <span id="countdown">{config['refresh_interval_seconds']}</span>s</span>
  <span>Last sync: <span id="lastSync">loading...</span></span>
  <span>Total: <span id="totalCount">0</span></span>
</p>
<div id="queueBanner" class="banner"></div>

<div class="stats" id="statsBar"></div>

<div class="controls">
  <input type="text" id="search" placeholder="Search titles and previews...">
  <select id="filterStatus">
    <option value="all">All Status</option>
    <option value="pending">Pending</option>
    <option value="pushed">Pushed</option>
    <option value="skipped">Skipped</option>
    <option value="rejected">Rejected</option>
    <option value="queued_push">Queued</option>
  </select>
  <select id="filterTier">
    <option value="all">All Tiers</option>
    <option value="content">Content (500+)</option>
    <option value="note">Note (200-499)</option>
    <option value="spark">Spark (50-199)</option>
    <option value="snippet">Snippet (&lt;50)</option>
  </select>
  <select id="filterLang">
    <option value="all">All Languages</option>
  </select>
</div>

<table>
<thead>
<tr>
  <th style="width:30px"><input type="checkbox" id="selectAll" onchange="toggleSelectAll(this.checked)"></th>
  <th data-col="id" style="width:70px">ID<span class="arrow"></span></th>
  <th data-col="title">Title<span class="arrow"></span></th>
  <th data-col="date" class="active">Date<span class="arrow">&#9660;</span></th>
  <th data-col="chars" style="width:60px">Chars<span class="arrow"></span></th>
  <th data-col="tier" style="width:70px">Tier<span class="arrow"></span></th>
  <th data-col="lang" style="width:50px">Lang<span class="arrow"></span></th>
  <th data-col="status" style="width:80px">Status<span class="arrow"></span></th>
  <th style="width:160px">Actions</th>
</tr>
</thead>
<tbody id="tbody"></tbody>
</table>
<div id="emptyMsg" class="empty" style="display:none">No notes match your filters.</div>

<div class="modal-overlay" id="modalOverlay" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <div class="modal-header">
      <h2 id="modalTitle">Note Detail</h2>
      <button class="modal-close" onclick="closeModal()">&#10005;</button>
    </div>
    <div class="modal-body">
      <div class="modal-meta" id="modalMeta"></div>
      <div class="modal-field">
        <label>Title (editable)</label>
        <input type="text" id="modalEditTitle">
      </div>
      <div class="modal-field">
        <label>Tags Override (comma-separated, e.g. China,AI)</label>
        <input type="text" id="modalEditTags" placeholder="Leave empty for auto-detect">
      </div>
      <div class="modal-field">
        <label>Full Transcript</label>
        <textarea id="modalContent" readonly></textarea>
      </div>
    </div>
    <div class="modal-footer" id="modalFooter"></div>
  </div>
</div>
<div class="bulk-bar" id="bulkBar">
  <span class="count" id="bulkCount">0</span> selected
  <button onclick="bulkAction('push')">Push</button>
  <button onclick="bulkAction('skip')">Skip</button>
  <button onclick="bulkAction('reject')">Reject</button>
  <button onclick="bulkAction('undo')">Undo</button>
  <button class="bulk-close" onclick="clearSelection()">&#10005;</button>
</div>
<div class="toast-container" id="toasts"></div>
<div class="footer">Letterly-to-Notion Pipeline &bull; Refresh: <code>ltl</code> &bull; Server: localhost:{config['port']}</div>

<script>
let NOTES=[], sortCol='date', sortDir=-1, refreshInterval={config['refresh_interval_seconds']}*1000;
let countdownVal={config['refresh_interval_seconds']}, countdownTimer=null, activeStatFilter=null;
let selectedIds=new Set();

function esc(s){{return s?s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'):''}}

function toast(msg,type='success'){{
  const c=document.getElementById('toasts');
  const d=document.createElement('div');d.className='toast '+type;d.textContent=msg;c.appendChild(d);
  setTimeout(()=>d.remove(),3000);
}}

async function fetchNotes(){{
  try{{
    const r=await fetch('/api/notes');const d=await r.json();
    if(d.ok){{NOTES=d.data;document.getElementById('lastSync').textContent=d.last_sync?d.last_sync.slice(0,10):'Never';
      document.getElementById('totalCount').textContent=d.total;applyFilters();}}
    const s=await fetch('/api/stats');const sd=await s.json();
    if(sd.ok)renderStats(sd.data);
    const q=await fetch('/api/queue');const qd=await q.json();
    if(qd.ok&&qd.data.actions.length>0){{
      document.getElementById('queueBanner').className='banner visible';
      document.getElementById('queueBanner').innerHTML=qd.data.actions.length+' note(s) queued for push. Run <code>sync letterly</code> in Claude to process.';
    }}else{{document.getElementById('queueBanner').className='banner';}}
  }}catch(e){{console.error('Fetch error:',e)}}
}}

function renderStats(s){{
  const bar=document.getElementById('statsBar');
  const items=[
    ['total',s.status.total,'Total'],['pushed',s.status.pushed,'Pushed'],
    ['pending',s.status.pending,'Pending'],['skipped',s.status.skipped,'Skipped'],
    ['rejected',s.status.rejected,'Rejected'],['queued',s.status.queued||0,'Queued']
  ];
  bar.innerHTML=items.map(([cls,num,lbl])=>
    `<div class="stat ${{cls}} ${{activeStatFilter===cls?'active':''}}" onclick="toggleStatFilter('${{cls}}')">`+
    `<div class="num">${{num}}</div><div class="label">${{lbl}}</div></div>`
  ).join('');
  // Populate language filter
  const langSel=document.getElementById('filterLang');
  const current=langSel.value;
  const langOpts=['<option value="all">All Languages</option>'];
  if(s.langs)Object.entries(s.langs).sort((a,b)=>b[1]-a[1]).forEach(([l,c])=>
    langOpts.push(`<option value="${{l}}">${{l}} (${{c}})</option>`));
  langSel.innerHTML=langOpts.join('');
  langSel.value=current;
}}

function toggleStatFilter(cls){{
  if(activeStatFilter===cls){{activeStatFilter=null;document.getElementById('filterStatus').value='all';}}
  else{{activeStatFilter=cls;
    if(cls==='total')document.getElementById('filterStatus').value='all';
    else if(cls==='queued')document.getElementById('filterStatus').value='queued_push';
    else document.getElementById('filterStatus').value=cls;}}
  applyFilters();fetchNotes();
}}

function applyFilters(){{
  const q=document.getElementById('search').value.toLowerCase();
  const fs=document.getElementById('filterStatus').value;
  const ft=document.getElementById('filterTier').value;
  const fl=document.getElementById('filterLang').value;
  let filtered=NOTES.filter(n=>{{
    if(fs!=='all'&&n.status!==fs)return false;
    if(ft!=='all'&&n.tier!==ft)return false;
    if(fl!=='all'&&n.lang!==fl)return false;
    if(q){{const h=(n.title+' '+(n.preview||'')).toLowerCase();if(!h.includes(q))return false;}}
    return true;
  }});
  filtered.sort((a,b)=>{{
    let va=a[sortCol],vb=b[sortCol];
    if(sortCol==='chars'){{va=va??-1;vb=vb??-1;return(va-vb)*sortDir;}}
    va=va??'';vb=vb??'';return va<vb?-sortDir:va>vb?sortDir:0;
  }});
  renderTable(filtered);
}}

function renderTable(notes){{
  const tbody=document.getElementById('tbody');
  const empty=document.getElementById('emptyMsg');
  if(!notes.length){{tbody.innerHTML='';empty.style.display='block';return;}}
  empty.style.display='none';
  tbody.innerHTML=notes.map(n=>{{
    const isPending=n.status==='pending';
    const isQueued=n.status==='queued_push';
    const isSkipped=n.status==='skipped';
    const isRejected=n.status==='rejected';
    const isPushed=n.status==='pushed';
    let actions='';
    if(isPending)actions+=`<button class="btn btn-push" onclick="doAction('push','${{n.id}}')">Push</button><button class="btn btn-skip" onclick="doAction('skip','${{n.id}}')">Skip</button><button class="btn btn-reject" onclick="doAction('reject','${{n.id}}')">Reject</button>`;
    else if(isSkipped||isRejected)actions+=`<button class="btn btn-undo" onclick="doAction('undo','${{n.id}}')">Undo</button>${{isSkipped?`<button class="btn btn-push" onclick="doAction('push','${{n.id}}')">Push</button>`:''}}`
    else if(isQueued)actions+=`<button class="btn btn-undo" onclick="doAction('undo','${{n.id}}')">Cancel</button>`;
    else if(isPushed&&n.notion_url)actions+=`<a class="link" href="${{esc(n.notion_url)}}" target="_blank">Notion &#8599;</a>`;
    const checked=selectedIds.has(n.id)?'checked':'';
    return `<tr data-id="${{n.id}}">
      <td><input type="checkbox" ${{checked}} onchange="toggleSelect('${{n.id}}',this.checked)"></td>
      <td style="font-size:.75rem;color:var(--text-dim)">${{esc(n.id)}}</td>
      <td style="cursor:pointer" onclick="openModal('${{n.id}}')"><div class="title-cell">${{esc(n.title)}}</div>${{n.preview?`<div class="preview">${{esc(n.preview)}}</div>`:''}}</td>
      <td>${{esc(n.date)}}</td>
      <td>${{n.chars!=null?n.chars:'?'}}</td>
      <td><span class="badge ${{n.tier}}">${{n.tier}}</span></td>
      <td>${{esc(n.lang)}}</td>
      <td><span class="badge ${{n.status}}">${{n.status.replace('queued_push','queued')}}</span></td>
      <td><div class="actions-cell">${{actions}}</div></td>
    </tr>`;
  }}).join('');
}}

async function doAction(action,noteId,retryCount=0){{
  // Instant visual feedback
  const row=document.querySelector(`tr[data-id="${{noteId}}"]`);
  const actionsCell=row?.querySelector('.actions-cell');
  const originalHtml=actionsCell?.innerHTML||'';
  if(actionsCell)actionsCell.innerHTML=`<span class="pushing">${{action==='push'?'Pushing to Notion...':'Processing...'}}</span>`;

  try{{
    const controller=new AbortController();
    const timeout=setTimeout(()=>controller.abort(),20000);
    const r=await fetch('/api/action',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{action,note_id:noteId}}),signal:controller.signal}});
    clearTimeout(timeout);
    const d=await r.json();
    if(d.ok){{
      toast(d.message+(d.notion_url?' ✓':''));
      fetchNotes();
      if(currentModalId===noteId)closeModal();
    }}else{{
      // Retry once on Notion errors
      if(action==='push'&&retryCount<1&&d.error?.includes('Notion')){{
        toast('Retrying push...','error');
        return doAction(action,noteId,retryCount+1);
      }}
      toast(d.error||'Action failed','error');
      if(actionsCell)actionsCell.innerHTML=originalHtml;
    }}
  }}catch(e){{
    if(e.name==='AbortError'){{
      toast('Request timed out — try again','error');
    }}else{{
      // Retry once on network errors
      if(retryCount<1){{toast('Retrying...','error');return doAction(action,noteId,retryCount+1);}}
      toast('Network error — check connection','error');
    }}
    if(actionsCell)actionsCell.innerHTML=originalHtml;
  }}
}}

async function queueSync(){{
  const pending=NOTES.filter(n=>n.status==='pending'&&n.tier==='content');
  if(!pending.length){{toast('No content-tier pending notes to queue','error');return;}}
  if(!confirm(`Queue ${{pending.length}} content-tier notes for push?`))return;
  for(const n of pending)await doAction('push',n.id);
  toast(`${{pending.length}} notes queued for push`);
}}

// Sort headers
document.querySelectorAll('th[data-col]').forEach(th=>{{
  th.addEventListener('click',()=>{{
    const col=th.dataset.col;
    if(sortCol===col)sortDir*=-1;else{{sortCol=col;sortDir=-1;}}
    document.querySelectorAll('th').forEach(t=>{{t.classList.remove('active');const a=t.querySelector('.arrow');if(a)a.textContent='';}});
    th.classList.add('active');th.querySelector('.arrow').textContent=sortDir===-1?'\\u25BC':'\\u25B2';
    applyFilters();
  }});
}});

// Filter listeners
['search','filterStatus','filterTier','filterLang'].forEach(id=>{{
  const el=document.getElementById(id);
  el.addEventListener(id==='search'?'input':'change',()=>{{activeStatFilter=null;applyFilters();}});
}});

// Modal detail/edit
let currentModalId=null;
async function openModal(noteId){{
  currentModalId=noteId;
  const r=await fetch(`/api/note/${{noteId}}`);const d=await r.json();
  if(!d.ok){{toast(d.error||'Failed to load note','error');return;}}
  const n=d.data;
  document.getElementById('modalTitle').textContent=n.title||'Untitled';
  document.getElementById('modalEditTitle').value=n.title||'';
  document.getElementById('modalEditTags').value=n.tags_override||'';
  document.getElementById('modalContent').value=n.preview||'(Full transcript not cached — run get_note in Claude to fetch)';
  const meta=document.getElementById('modalMeta');
  meta.innerHTML=`
    <span class="badge ${{n.status}}">${{n.status}}</span>
    <span class="badge ${{compute_tier_js(n.char_count)}}">${{compute_tier_js(n.char_count)}}</span>
    <span class="badge" style="background:#F3F4F6;color:#374151">${{n.detected_language||'?'}}</span>
    <span style="color:var(--text-dim);font-size:.78rem">${{n.char_count||'?'}} chars &bull; ${{format_date_js(n.letterly_created)}}</span>
    <span style="color:var(--text-dim);font-size:.75rem">Letterly #${{noteId}}</span>
    ${{n.notion_url?`<a class="link" href="${{n.notion_url}}" target="_blank" style="font-size:.78rem">Open in Notion &#8599;</a>`:''}}
  `;
  const footer=document.getElementById('modalFooter');
  let btns=`<button class="btn btn-undo" onclick="closeModal()">Cancel</button>
    <button class="btn btn-skip" onclick="saveAndClose()">Save</button>`;
  if(n.status==='pending'||n.status==='skipped')
    btns+=`<button class="btn btn-push" onclick="saveAndPush()">Save & Push</button>`;
  footer.innerHTML=btns;
  document.getElementById('modalOverlay').className='modal-overlay visible';
}}
function closeModal(){{document.getElementById('modalOverlay').className='modal-overlay';currentModalId=null;}}
function compute_tier_js(c){{if(!c||c===0)return'unknown';if(c>=500)return'content';if(c>=200)return'note';if(c>=50)return'spark';return'snippet';}}
function format_date_js(s){{if(!s)return'';try{{return new Date(s).toISOString().slice(0,10)}}catch{{return s?s.slice(0,10):''}};}}
async function saveModal(){{
  if(!currentModalId)return false;
  const title=document.getElementById('modalEditTitle').value.trim();
  const tags=document.getElementById('modalEditTags').value.trim();
  const body={{title}};
  if(tags)body.tags_override=tags;
  const r=await fetch(`/api/note/${{currentModalId}}/update`,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body)}});
  const d=await r.json();
  if(!d.ok){{toast(d.error||'Save failed','error');return false;}}
  toast('Note updated');fetchNotes();return true;
}}
async function saveAndClose(){{if(await saveModal())closeModal();}}
async function saveAndPush(){{if(await saveModal()){{await doAction('push',currentModalId);closeModal();}}}}

// Selection management
function toggleSelect(id,checked){{
  if(checked)selectedIds.add(id);else selectedIds.delete(id);
  updateBulkBar();
}}
function toggleSelectAll(checked){{
  const visible=document.querySelectorAll('#tbody input[type=checkbox]');
  visible.forEach(cb=>{{cb.checked=checked;const id=cb.closest('tr').querySelector('td:nth-child(2)').textContent.trim();
    if(checked)selectedIds.add(id);else selectedIds.delete(id);}});
  updateBulkBar();
}}
function clearSelection(){{
  selectedIds.clear();document.getElementById('selectAll').checked=false;
  document.querySelectorAll('#tbody input[type=checkbox]').forEach(cb=>cb.checked=false);
  updateBulkBar();
}}
function updateBulkBar(){{
  const bar=document.getElementById('bulkBar');
  document.getElementById('bulkCount').textContent=selectedIds.size;
  bar.className=selectedIds.size>0?'bulk-bar visible':'bulk-bar';
}}
async function bulkAction(action){{
  if(!selectedIds.size)return;
  const ids=[...selectedIds];
  if(!confirm(`${{action}} ${{ids.length}} notes?`))return;
  try{{
    const r=await fetch('/api/bulk',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{action,note_ids:ids}})}});
    const d=await r.json();
    if(d.ok){{toast(d.message);clearSelection();fetchNotes();}}
    else toast(d.error||'Bulk action failed','error');
  }}catch(e){{toast('Network error','error')}}
}}

// Auto-refresh
function startCountdown(){{
  countdownVal=refreshInterval/1000;
  document.getElementById('countdown').textContent=countdownVal;
  if(countdownTimer)clearInterval(countdownTimer);
  countdownTimer=setInterval(()=>{{
    countdownVal--;document.getElementById('countdown').textContent=Math.max(0,countdownVal);
    if(countdownVal<=0){{fetchNotes();countdownVal=refreshInterval/1000;}}
  }},1000);
}}

// Init
fetchNotes();startCountdown();
</script>
</body>
</html>"""

# --- Server Startup ---

SERVER_START = time.time()

def main():
    config = load_config()
    port = int(os.environ.get("LTL_PORT", config["port"]))

    # Startup backup
    index = load_index()
    note_count = len(index.get("notes", {}))
    if note_count > 0:
        bp = backup_index(label="startup")
        print(f"Backup: {os.path.basename(bp) if bp else 'skipped'}")

    # Start periodic backup thread
    backup_thread = threading.Thread(target=_periodic_backup, daemon=True)
    backup_thread.start()

    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    print(f"Letterly Dashboard running on http://localhost:{port}")
    print(f"Index: {INDEX_PATH} ({note_count} notes)")
    print(f"Backups: {BACKUP_DIR} (every {BACKUP_INTERVAL_SECONDS}s, max {MAX_BACKUPS})")
    print(f"Press Ctrl+C to stop")

    def shutdown(sig, frame):
        print("\nShutting down...")
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

if __name__ == "__main__":
    main()
