---
name: Skill Improver
description: A meta-skill for auditing, improving, refactoring, and verifying other Agent Skills. Handles script consolidation, error handling enhancement, and documentation updates.
version: 1.2.0
---

# Skill Improver

A meta-skill designed to elevate the quality, reliability, and maintainability of other Agent Skills. Use this skill when a user asks to "improve", "fix", "optimize", or "standardize" a skill, or immediately after installing a new skill to ensure it meets production standards.

## Usage Verification

**Trigger logic**:
- Explicit: "Improve this skill", "Fix the error in skill X", "Make skill Y more robust".
- Implicit: After `skill-install` finishes, if the user asks to "check if it works" or "make it better".

## Workflow

### Phase 1: Audit & Discovery

1.  **Automated Audit**: Run the included script to check for common issues:
    ```bash
    python3 scripts/audit_skill.py /path/to/skill
    ```
2.  **Manual Review**: Read the `SKILL.md` to understand the skill's purpose and logic.
3.  **Inventory Files**: If the script isn't enough, use `list_dir` to explore further.
4.  **Analyze Scripts**:
    *   Are there multiple loose scripts?
    *   Are dependencies listed?
4.  **Check Metadata**:
    *   Does `SKILL.md` have a frontmatter?
    *   Is there a `CHANGELOG.md`?
    *   Is there source attribution (Where did this skill come from?)?

### Phase 2: Strategy Formulation

Propose a plan to the user if the changes are significant.

*   **Consolidation**: If the skill relies on multiple loose scripts, propose consolidating them into a single CLI tool (using `typer` for Python or `commander` for Node.js) or an MCP server.
*   **Structure**: Ensure the folder adheres to:
    ```
    skill-name/
    ├── SKILL.md
    ├── CHANGELOG.md
    ├── scripts/
    │   └── (Executable scripts)
    ├── references/
    │   └── (Docs, schemas, templates)
    └── assets/
        └── (Images, static files)
    ```
*   **Robustness**: Add try/catch blocks, input validation, and verbose logging to scripts.

### Phase 3: Execution (The Refactor)

1.  **Source Traceability**:
    *   If missing, add a `Source` or `Origin` section to `SKILL.md` noting where it was installed from (URL, Author) and the date.
2.  **Code Improvements**:
    *   **Paths**: Replace hardcoded paths with relative paths or environment variables. Use `os.path.join` or `pathlib`.
    *   **Env Vars**: Move secrets to `.env` or `mcp_config`.
    *   **Dependencies**: Generate/Update `requirements.txt` or `package.json`.
3.  **Consolidation (The Lego Maker)**:
    *   *Python*: Create a `main.py` using `typer` to wrap multiple functions.
    *   *Node*: Create a `index.js` bin.
4.  **Instruction Draft**: Update `SKILL.md` to reflect the new script usage (e.g., `python scripts/main.py command` instead of `python script1.py`).

### Phase 4: Verification

1.  **Test Run**: Execute the skill's core function with a sample input.
2.  **Fix Bugs**: If it fails, debug and fix immediately.
3.  **Self-Correction**: Did the refactor break the logic? Verify against the original behavior.

### Phase 5: Documentation & Logging

1.  **Update CHANGELOG.md**:
    *   Log date, author (Agent), and specific changes (e.g., "Consolidated 3 scripts into CLI", "Added error handling").
2.  **Update Installation Log**:
    *   If applicable, append to `~/.gemini/antigravity/skills/installation_log.md` with "Improved [Skill Name]".
3.  **Final Report**: Summarize the improvements to the user.

### Phase 6: The Inception (Autopoiesis Injection)

**CRITICAL**: To turn the skill into a "Living Form" ($e^x$), you MUST inject the *Self-Evolution Gene*.

1.  **Check Target**: Does the target skill's `SKILL.md` have a "Self-Evolution" or "Contribution" section?
2.  **Inject Protocol**: If not, append the following section to the end of the target's `SKILL.md`:
    ```markdown
    ## 🧬 Self-Evolution (Autopoiesis)
    
    **Post-Task Reflection**: 
    Before ending the session, the Agent MUST ask: "Did I learn a new pattern, fix a bug, or add a critical feature?"
    -   **YES**: Log it in `CHANGELOG.md` and update `SKILL.md` / `references/` immediately.
    -   **NO**: Do nothing.
    -   **Constraint**: Only log **High-Signal** improvements (e.g., "Added retry logic"). Ignore noise (e.g., "Fixed typo").
    ```

### Phase 7: Recursive Evolution (Self-Improvement)

*   **Pattern Recognition**: Did you discover a new common error or a better pattern during this session?
*   **Backport**: If yes, immediately update **this** skill (`skill-improver`).
    *   *New Check*: Add it to `scripts/audit_skill.py`.
    *   *New Step*: Update `SKILL.md` workflow.
*   **Log**: Update `skill-improver/CHANGELOG.md` with the self-improvement.

## Principles

1.  **Respect Original Intent**: Do not change *what* the skill does, only *how* well it does it.
2.  **Consolidate for Agents**: Future agents prefer clear CLIs over messy scripts.
3.  **Traceability**: Always leave breadcrumbs (comments, logs) for the next agent.
4.  **Safety First**: backup files if unsure (simple `cp file file.bak`).
5.  **Token Economy**: `SKILL.md` is read often. Move static, one-time setup info to subfolders.

## 🧬 Self-Evolution (Autopoiesis)

**Post-Task Reflection**: 
Before ending the session, the Agent MUST ask: "Did I learn a new pattern, fix a bug, or add a critical feature?"
-   **YES**: Log it in `CHANGELOG.md` and update `SKILL.md` / `references/` immediately.
-   **NO**: Do nothing.
-   **Constraint**: Only log **High-Signal** improvements (e.g., "Added retry logic"). Ignore noise (e.g., "Fixed typo").
