from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "SKILL.md"
TROUBLESHOOTING = ROOT / "references" / "troubleshooting.md"


def test_discord_skill_keeps_its_token_safety_and_agent_reach_contract() -> None:
    text = SKILL.read_text(encoding="utf-8")

    for required in (
        "## Agent Reach Link",
        "`agent-reach`",
        "discord status --yaml",
        "Do not run `discord auth --save`",
        "Do not print or persist raw tokens",
        "explicit user confirmation",
        "[troubleshooting.md](references/troubleshooting.md)",
    ):
        assert required in text


def test_routing_sentences_still_point_at_something_real() -> None:
    """Guard the cross-references, not the judgement around them.

    Each of these is a pointer that fails silently when it rots: the reader
    simply re-derives what the pointer was there to save them.
    """
    skill = SKILL.read_text(encoding="utf-8")
    trouble = TROUBLESHOOTING.read_text(encoding="utf-8")

    # SKILL.md promises a verification script; it must exist and be runnable.
    assert "scripts/e2e_check.py" in skill
    checker = ROOT / "scripts" / "e2e_check.py"
    assert checker.is_file(), "SKILL.md points at a verification script that is missing"
    assert checker.stat().st_mode & 0o111, "e2e_check.py is not executable"

    # SKILL.md promises a forum sweep script; it must exist and be runnable.
    assert "scripts/forum_sweep.py" in skill
    sweeper = ROOT / "scripts" / "forum_sweep.py"
    assert sweeper.is_file(), "SKILL.md points at a forum sweep script that is missing"
    assert sweeper.stat().st_mode & 0o111, "forum_sweep.py is not executable"

    # The forum section is the difference between "unreachable" and "inactive".
    # Losing it silently restores the wrong conclusion, so pin its load-bearing
    # facts rather than only its heading.
    for required in ("type: 15", "dc search", "`fetched: 0`", "not wrapped"):
        assert required in skill, f"forum-channel section lost {required}"

    # troubleshooting.md routes the encrypted-token case to a named section.
    assert "## Credential Lane" in skill
    assert "Credential Lane" in trouble

    # The payload-shape table is why a healthy account can read as failed.
    for required in ("schema_version", '{"fetched"', '"user"'):
        assert required in trouble, f"payload-shape table lost {required}"


if __name__ == "__main__":
    test_discord_skill_keeps_its_token_safety_and_agent_reach_contract()
    test_routing_sentences_still_point_at_something_real()
