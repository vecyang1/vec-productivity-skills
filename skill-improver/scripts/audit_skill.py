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

def audit_skill(skill_path):
    if not os.path.isdir(skill_path):
        print(f"Error: Directory not found at {skill_path}")
        sys.exit(1)
        
    print(f"Auditing Skill: {os.path.basename(skill_path)}")
    print(f"Path: {skill_path}\n")
    
    # Check structure
    has_skill = check_file_existence(skill_path, "SKILL.md")
    check_file_existence(skill_path, "CHANGELOG.md")
    
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

                if "## ⚖️ Principles" in content or "## Principles" in content:
                    print("[OK] Principles section found")
                else:
                    print("[WARNING] SKILL.md is missing '## ⚖️ Principles' section. Inject it to guide Self-Evolution.")
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit an Agent Skill for quality issues.")
    parser.add_argument("path", help="Path to the skill directory")
    args = parser.parse_args()
    
    audit_skill(os.path.abspath(args.path))
