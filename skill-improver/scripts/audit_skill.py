#!/usr/bin/env python3
import os
import sys
import argparse
import re

def check_file_existence(skill_path, filename):
    filepath = os.path.join(skill_path, filename)
    if os.path.exists(filepath):
        print(f"[OK] Found {filename}")
        return True
    else:
        print(f"[MISSING] {filename} is missing")
        return False

def scan_for_hardcoded_paths(skill_path):
    print("\n--- Scanning for Hardcoded Paths ---")
    suspicious_patterns = [
        r"/Users/[a-zA-Z0-9_-]+/",  # User home directories
        r"/home/[a-zA-Z0-9_-]+/",   # Linux home directories
    ]
    
    found_issues = False
    for root, dirs, files in os.walk(skill_path):
        for file in files:
            if file.endswith(('.py', '.js', '.sh', '.md', '.json')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for pattern in suspicious_patterns:
                            matches = re.findall(pattern, content)
                            if matches:
                                print(f"[WARNING] Potential hardcoded path in {file}: {matches[0]}")
                                found_issues = True
                except Exception as e:
                    print(f"[ERROR] Could not read {file}: {e}")
    
    if not found_issues:
        print("[OK] No obvious hardcoded paths found.")

def check_security_hygiene(skill_path):
    print("\n--- Scanning for Security Hygiene ---")
    
    # Check 1: API Key Hardcoding
    suspicious_patterns = [
        r"API_KEY\s*=\s*['\"]sk-[a-zA-Z0-9]+['\"]",  # OpenAI style
        r"KEY\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]",     # Generic long strings
        r"os\.environ\[['\"][A-Z_]+['\"]\]\s*=\s*['\"][a-zA-Z0-9]+['\"]", # Hardcoded env vars
    ]
    
    found_issues = False
    for root, dirs, files in os.walk(skill_path):
        for file in files:
            if file.endswith(('.py', '.js', '.ts')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for pattern in suspicious_patterns:
                            matches = re.findall(pattern, content)
                            if matches:
                                print(f"[SECURITY WARNING] Potential hardcoded secret in {file}: {matches[0][:20]}...")
                                found_issues = True
                except Exception as e:
                    pass
    
    if not found_issues:
        print("[OK] No obvious hardcoded secrets found.")

    # Check 2: .env usage
    has_env = check_file_existence(skill_path, ".env")
    has_env_example = check_file_existence(skill_path, ".env.example")
    
    if has_env and not has_env_example:
        print("[SUGGESTION] Found .env but missing .env.example. Please add a template.")

def check_runtime_imports(skill_path):
    import importlib.util
    
    print("\n--- Scanning for Runtime Dependencies & Disk Impact ---")
    
    # Heuristics: Lib -> Approx Size (MB)
    HEAVY_LIBS = {
        "torch": 2500,       # ~2.5 GB
        "tensorflow": 1500,  # ~1.5 GB
        "transformers": 500, # ~500 MB (code) + GBs of Model Cache
        "diffusers": 500,    # Similar to transformers
        "scipy": 150,        # ~150 MB
        "playwright": 300,   # ~300 MB + Browsers
        "puppeteer": 300,    # ~300 MB + Browsers
        "pandas": 100,       # ~100 MB
        "numpy": 50,         # ~50 MB
    }
    
    # Map common import names to install names if needed (approximate)
    install_map = {
        "dotenv": "python-dotenv",
        "PIL": "Pillow",
        "google.genai": "google-genai",
        "sklearn": "scikit-learn"
    }

    found_imports = set()
    missing_libs = set()
    
    for root, dirs, files in os.walk(skill_path):
        for file in files:
            if file.endswith(".py"):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for line in lines:
                            # Simple regex to catch top-level imports
                            match = re.match(r"^\s*(?:import|from)\s+([a-zA-Z0-9_]+)", line)
                            if match:
                                lib = match.group(1)
                                if lib in sys.builtin_module_names: continue
                                # Filter output relative imports
                                if lib.startswith("."): continue 
                                
                                found_imports.add(lib)
                except:
                    pass
    
    # Check if installed
    for lib in found_imports:
        # standard libs check (rough)
        try:
            spec = importlib.util.find_spec(lib)
            if spec is None:
                missing_libs.add(lib)
        except (ModuleNotFoundError, ValueError):
            missing_libs.add(lib)
            
    if missing_libs:
        print(f"[MISSING DEPENDENCIES] The following imports are used but not installed:")
        for lib in missing_libs:
            pkg_name = install_map.get(lib, lib)
            size_mb = HEAVY_LIBS.get(lib, 0)
            
            if size_mb > 0:
                print(f"  - ⚠️  [HEAVY] '{lib}': Est. Size ~{size_mb} MB. Think before installing!")
            else:
                print(f"  - [LIGHT] '{lib}': Safe to install ('pip install {pkg_name}').")
    else:
        print("[OK] All runtime dependencies appear to be satisfied.")
        
    # Extra Check: Are we using heavy libs even if installed?
    used_heavy = [lib for lib in found_imports if lib in HEAVY_LIBS]
    if used_heavy:
        print(f"\n[DISK SPACE NOTICE] This skill uses heavy libraries: {', '.join(used_heavy)}")
        print("  -> Ensure you actually need this skill before keeping these libraries.")

import datetime
import shutil
import json

# --- Auto-Fix Logic ---

def get_improver_principles():
    """Extracts principles from the Skill Improver's own SKILL.md."""
    # Assuming the script is at skill-improver/scripts/audit_skill.py
    # We want skill-improver/SKILL.md
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_skill_md = os.path.join(script_dir, "..", "SKILL.md")
    
    default_principles = """
### 🛡️ Systemic Principles (Inherited)
1. **Respect Original Intent**: Do not change *what* the skill does, only *how* well it does it.
2. **Consolidate for Agents**: Future agents prefer clear CLIs over messy scripts.
3. **Traceability**: Always leave breadcrumbs (comments, logs) for the next agent.
4. **Safety First**: backup files if unsure (simple `cp file file.bak`).
5. **Token Economy**: `SKILL.md` is read often. Move static, one-time setup info to subfolders.
6. **Safe Updating (User Wisdom > Source)**: Prioritize user customizations. If the user has heavily iterated, think twice before overwriting with source updates. User's specific wisdom is more valuable than generic upstream changes.
"""
    
    if not os.path.exists(source_skill_md):
        return default_principles

    try:
        with open(source_skill_md, 'r') as f:
            content = f.read()
            # Extract between "## Principles" (or similar) and "## 🧬 Self-Evolution"
            # This is a bit brittle, so fallback to default if regex fails
            match = re.search(r"(##\s*.*?Principles.*?)(?=##\s*.*?Self-Evolution)", content, re.DOTALL | re.IGNORECASE)
            if match:
                # Clean up the header to ensure consistency
                raw_section = match.group(1).strip()
                # Replace the header with our standard sub-header if it's the main one
                # Actually, let's just use the default text for stability unless we need exact syncing.
                # For now, hardcoding the known-good principles is safer than parsing markdown on the fly 
                # to avoid getting partial edits.
                pass
    except Exception as e:
        print(f"[WARN] Could not read source SKILL.md for principles: {e}")

    return default_principles

def get_autopoiesis_section():
    return """
## 🧬 Self-Evolution (Autopoiesis)

**Post-Task Reflection**: 
Before ending the session, the Agent MUST ask: "Did I learn a new pattern, fix a bug, or add a critical feature?"
-   **YES**: Log it in `CHANGELOG.md` and update `SKILL.md` / `references/` immediately.
-   **NO**: Do nothing.
-   **Constraint**: Only log **High-Signal** improvements (e.g., "Added retry logic"). Ignore noise (e.g., "Fixed typo").
-   **Principle Check**: Ensure any changes align with the `## ⚖️ Principles` section.
"""

def fix_missing_changelog(skill_path):
    changelog_path = os.path.join(skill_path, "CHANGELOG.md")
    if os.path.exists(changelog_path):
        return
    
    print(f"[FIX] Creating CHANGELOG.md...")
    today = datetime.date.today().isoformat()
    content = f"""# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.0.0] - {today}
- Initial standardization via Skill Improver.
"""
    try:
        with open(changelog_path, 'w') as f:
            f.write(content)
        print("[FIX] CHANGELOG.md created.")
    except Exception as e:
        print(f"[ERROR] Failed to create CHANGELOG.md: {e}")

def fix_skill_md(skill_path):
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        print("[ERROR] Cannot fix SKILL.md because it does not exist.")
        return

    try:
        with open(skill_md_path, 'r') as f:
            content = f.read()
        
        updated = False
        
        # 1. Principles
        if "## ⚖️ Principles" not in content and "## Principles" not in content:
            print("[FIX] Injecting Systemic Principles...")
            principles = get_improver_principles()
            # If Autopoiesis exists, insert before it, else append
            if "## 🧬 Self-Evolution" in content:
                 content = content.replace("## 🧬 Self-Evolution", f"\n## ⚖️ Principles\n{principles}\n\n## 🧬 Self-Evolution")
            else:
                 content += f"\n\n## ⚖️ Principles\n{principles}"
            updated = True

        # 2. Autopoiesis
        if "## 🧬 Self-Evolution" not in content and "Self-Evolution" not in content:
             print("[FIX] Injecting Autopoiesis Protocol...")
             autopoiesis = get_autopoiesis_section()
             content += f"\n{autopoiesis}"
             updated = True
             
        if updated:
            with open(skill_md_path, 'w') as f:
                f.write(content)
            print("[FIX] SKILL.md updated with missing sections.")
        else:
            print("[INFO] SKILL.md already has required sections.")

    except Exception as e:
        print(f"[ERROR] Failed to update SKILL.md: {e}")

def audit_skill(skill_path, fix_mode=False):
    if not os.path.isdir(skill_path):
        print(f"Error: Directory not found at {skill_path}")
        sys.exit(1)
        
    print(f"Auditing Skill: {os.path.basename(skill_path)}")
    print(f"Path: {skill_path}\n")
    
    # Check structure
    has_skill = check_file_existence(skill_path, "SKILL.md")
    has_changelog = check_file_existence(skill_path, "CHANGELOG.md")
    
    if fix_mode and not has_changelog:
        fix_missing_changelog(skill_path)
    
    # Check Metadata in SKILL.md
    if has_skill:
        try:
            with open(os.path.join(skill_path, "SKILL.md"), 'r') as f:
                content = f.read()
                if "---" in content[:10]: # minimal check for frontmatter
                    print("[OK] SKILL.md seems to have frontmatter")
                else:
                    print("[WARNING] SKILL.md might be missing YAML frontmatter")
                
                if "Source" in content or "Origin" in content or "Author" in content:
                     print("[INFO] Source attribution found in SKILL.md")
                else:
                     print("[SUGGESTION] Consider adding Source/Author to SKILL.md")

                has_principles = "## ⚖️ Principles" in content or "## Principles" in content
                
                if has_principles:
                    print("[OK] Principles section found")
                else:
                    print("[WARNING] SKILL.md is missing '## ⚖️ Principles' section. Inject it to guide Self-Evolution.")
                    
                if fix_mode and not has_principles:
                    fix_skill_md(skill_path) 
                    # Re-read to confirm or just assume success if no error from fix_skill_md

        except Exception as e:
            print(f"[ERROR] Reading SKILL.md: {e}")

    # Scan Code
    scan_for_hardcoded_paths(skill_path)
    check_security_hygiene(skill_path)
    check_runtime_imports(skill_path)
    
    # [SELF-IMPROVEMENT SLOT]
    # Future Agents: If you identify new common bad patterns, add your check functions here.
    # e.g., check_for_api_keys(skill_path)
    
    print("\n--- Audit Complete ---")

# --- Cleaning Functions for Public Sharing ---

def detect_username_from_paths(content):
    """Auto-detect username from common path patterns."""
    patterns = [
        r"/Users/([a-zA-Z0-9_-]+)/",
        r"/home/([a-zA-Z0-9_-]+)/"
    ]
    usernames = set()
    for pattern in patterns:
        matches = re.findall(pattern, content)
        usernames.update(matches)

    # Return most common username if multiple found
    if usernames:
        return max(usernames, key=lambda x: content.count(f"/{x}/"))
    return None

def remove_api_tokens(content, file_ext):
    """Remove/replace API tokens and secrets with placeholders."""
    changes = []

    # Token patterns and their replacements
    patterns = [
        (r'sk-[a-zA-Z0-9]{20,}', '"your_openai_api_key_here"', 'OpenAI API key'),
        (r'ntn_[a-zA-Z0-9]{20,}', '"your_notion_token_here"', 'Notion token'),
        (r'Bearer [a-zA-Z0-9]{20,}', 'Bearer your_token_here', 'Bearer token'),
        (r'(["\'])([a-zA-Z0-9]{40,})\1', r'\1your_api_key_here\1', 'Generic long token'),
    ]

    for pattern, replacement, desc in patterns:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes.append(f"Removed {len(matches)} {desc}(s)")

    return content, changes

def sanitize_paths(content, username=None):
    """Replace personal paths with generic placeholders."""
    changes = []

    if not username:
        username = detect_username_from_paths(content)

    if username:
        # Replace /Users/username/ with /Users/your_username/
        pattern = f"/Users/{re.escape(username)}/"
        if re.search(pattern, content):
            content = re.sub(pattern, "/Users/your_username/", content)
            changes.append(f"Sanitized /Users/{username}/ paths")

        # Replace /home/username/ with /home/your_username/
        pattern = f"/home/{re.escape(username)}/"
        if re.search(pattern, content):
            content = re.sub(pattern, "/home/your_username/", content)
            changes.append(f"Sanitized /home/{username}/ paths")

    return content, changes

def sanitize_database_ids(content):
    """Replace database IDs with placeholders."""
    changes = []

    # Notion-style IDs (32-char hex without hyphens)
    notion_pattern = r'\b[a-f0-9]{32}\b'
    notion_matches = re.findall(notion_pattern, content)
    if notion_matches:
        content = re.sub(notion_pattern, 'your-database-id-here', content)
        changes.append(f"Replaced {len(set(notion_matches))} Notion database ID(s)")

    # UUIDs
    uuid_pattern = r'\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b'
    uuid_matches = re.findall(uuid_pattern, content)
    if uuid_matches:
        content = re.sub(uuid_pattern, 'your-uuid-here', content)
        changes.append(f"Replaced {len(set(uuid_matches))} UUID(s)")

    return content, changes

def sanitize_personal_data(content):
    """Remove email addresses and personal identifiers."""
    changes = []

    # Email addresses (but preserve example.com)
    email_pattern = r'\b[a-zA-Z0-9._%+-]+@(?!example\.com)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    email_matches = re.findall(email_pattern, content)
    if email_matches:
        content = re.sub(email_pattern, 'your-email@example.com', content)
        changes.append(f"Replaced {len(set(email_matches))} email address(es)")

    return content, changes

def should_process_file(filepath, filename):
    """Determine if file should be processed for cleaning."""
    # Skip directories
    skip_dirs = {'.git', 'node_modules', '__pycache__', 'venv', 'env', '.venv'}
    for skip_dir in skip_dirs:
        if skip_dir in filepath:
            return False

    # Skip already template files
    if '.example' in filename or '.template' in filename:
        return False

    # Process these extensions
    process_exts = {'.py', '.js', '.ts', '.sh', '.json', '.yaml', '.yml', '.md', '.mcp.json'}
    return any(filename.endswith(ext) for ext in process_exts)

def clean_file(filepath, dry_run=False):
    """Clean a single file, return changes made."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()

        content = original_content
        all_changes = []

        # Get file extension
        file_ext = os.path.splitext(filepath)[1]

        # Apply cleaning operations
        content, token_changes = remove_api_tokens(content, file_ext)
        all_changes.extend(token_changes)

        content, path_changes = sanitize_paths(content)
        all_changes.extend(path_changes)

        content, id_changes = sanitize_database_ids(content)
        all_changes.extend(id_changes)

        content, data_changes = sanitize_personal_data(content)
        all_changes.extend(data_changes)

        # Write back if changes were made and not dry-run
        if content != original_content:
            if not dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            return all_changes

        return []

    except Exception as e:
        print(f"[ERROR] Failed to clean {filepath}: {e}")
        return []

def create_template_file(source_path, template_path):
    """Create a template version of a config file."""
    try:
        with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Clean the content
        content, _ = remove_api_tokens(content, os.path.splitext(source_path)[1])
        content, _ = sanitize_paths(content)
        content, _ = sanitize_database_ids(content)
        content, _ = sanitize_personal_data(content)

        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"[ERROR] Failed to create template {template_path}: {e}")
        return False

def clean_skill(skill_path, output_path=None, dry_run=False):
    """Main cleaning orchestrator."""
    if not os.path.isdir(skill_path):
        print(f"Error: Directory not found at {skill_path}")
        return False

    # Determine output path
    if output_path is None:
        output_path = f"{skill_path}_cleaned"

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Cleaning Skill: {os.path.basename(skill_path)}")
    print(f"Source: {skill_path}")
    print(f"Output: {output_path}\n")

    if dry_run:
        print("[DRY RUN MODE] No files will be modified. Showing what would be cleaned:\n")

    # Copy skill to output directory (unless dry-run)
    if not dry_run:
        if os.path.exists(output_path):
            print(f"[WARNING] Output directory exists: {output_path}")
            response = input("Overwrite? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return False
            shutil.rmtree(output_path)

        shutil.copytree(skill_path, output_path)
        print(f"[OK] Copied skill to {output_path}")

    # Track all changes
    total_files_processed = 0
    total_changes = {}

    # Process files
    walk_path = output_path if not dry_run else skill_path
    for root, dirs, files in os.walk(walk_path):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', 'venv', 'env', '.venv'}]

        for filename in files:
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, walk_path)

            if should_process_file(filepath, filename):
                changes = clean_file(filepath, dry_run=dry_run)
                if changes:
                    total_files_processed += 1
                    total_changes[rel_path] = changes
                    print(f"{'[DRY RUN] ' if dry_run else ''}[CLEANED] {rel_path}")
                    for change in changes:
                        print(f"  - {change}")

    # Create template files
    if not dry_run:
        template_files = {
            '.env': '.env.example',
            'databases.md': 'databases.md.template',
            'config.json': 'config.example.json'
        }

        for source_name, template_name in template_files.items():
            source_path = os.path.join(output_path, source_name)
            if os.path.exists(source_path):
                template_path = os.path.join(output_path, template_name)
                if create_template_file(source_path, template_path):
                    print(f"[TEMPLATE] Created {template_name}")

    # Summary
    print(f"\n--- Cleaning {'Preview' if dry_run else 'Complete'} ---")
    print(f"Files processed: {total_files_processed}")
    print(f"Total changes: {sum(len(changes) for changes in total_changes.values())}")

    if not dry_run:
        print(f"\nCleaned skill saved to: {output_path}")
        print("Original skill remains untouched.")
    else:
        print("\nThis was a dry run. Use --clean without --dry-run to actually clean the skill.")

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit an Agent Skill for quality issues.")
    parser.add_argument("path", help="Path to the skill directory")
    parser.add_argument("--fix", action="store_true", help="Automatically fix missing standard sections (Principles, Changelog)")
    parser.add_argument("--clean", action="store_true", help="Clean skill for public sharing (removes tokens, personal data)")
    parser.add_argument("--output", type=str, help="Output directory for cleaned skill (default: skill_path_cleaned)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be cleaned without making changes")
    args = parser.parse_args()

    skill_path = os.path.abspath(args.path)

    if args.clean:
        clean_skill(skill_path, output_path=args.output, dry_run=args.dry_run)
    else:
        audit_skill(skill_path, fix_mode=args.fix)
