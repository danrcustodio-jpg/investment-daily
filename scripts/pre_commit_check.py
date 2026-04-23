#!/usr/bin/env python3
"""
Pre-commit code quality checks for InvestmentDaily.
Run automatically by .git/hooks/pre-commit on every commit.
Can also be run manually: python scripts/pre_commit_check.py
"""

import subprocess
import sys
import json
import os

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"

def get_staged_files():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True
    )
    return [f for f in result.stdout.strip().splitlines() if f]

def get_staged_content(filepath):
    result = subprocess.run(
        ["git", "show", f":{filepath}"],
        capture_output=True, text=True, errors="replace"
    )
    return result.stdout if result.returncode == 0 else ""

def check_merge_conflicts(files):
    """Block commits that contain unresolved merge conflict markers."""
    bad = []
    for f in files:
        content = get_staged_content(f)
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("<<<<<<< ") or stripped.startswith(">>>>>>> ") or stripped == "=======":
                bad.append(f)
                break
    if bad:
        print(f"  {FAIL} Merge conflict markers found in: {', '.join(bad)}")
        return False
    print(f"  {PASS} No merge conflict markers")
    return True

def check_large_files(files, max_kb=300):
    """Block files larger than max_kb kilobytes."""
    bad = []
    for f in files:
        if os.path.exists(f):
            size_kb = os.path.getsize(f) / 1024
            if size_kb > max_kb:
                bad.append(f"{f} ({size_kb:.0f} KB)")
    if bad:
        print(f"  {FAIL} Files exceed {max_kb} KB limit: {', '.join(bad)}")
        return False
    print(f"  {PASS} All files under {max_kb} KB")
    return True

def check_json_valid(files):
    """Block commits with malformed JSON files."""
    json_files = [f for f in files if f.endswith(".json")]
    bad = []
    for f in json_files:
        content = get_staged_content(f)
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            bad.append(f"{f}: {e}")
    if bad:
        for b in bad:
            print(f"  {FAIL} Invalid JSON — {b}")
        return False
    if json_files:
        print(f"  {PASS} JSON files are valid ({len(json_files)} checked)")
    else:
        print(f"  {PASS} No JSON files staged")
    return True

def check_no_secrets(files):
    """Warn if .env or files containing passwords/keys are staged."""
    risky_names = {".env", ".env.local", ".env.production"}
    risky_patterns = ["PASSWORD", "SECRET_KEY", "API_KEY", "AUTH_TOKEN", "PRIVATE_KEY"]
    bad = []
    for f in files:
        if os.path.basename(f) in risky_names:
            bad.append(f"{f} (credentials file)")
            continue
        content = get_staged_content(f)
        for line in content.splitlines():
            stripped = line.strip()
            for p in risky_patterns:
                if p in stripped.upper() and "=" in stripped and not stripped.startswith("#"):
                    val = stripped.split("=", 1)[-1].strip().strip('"').strip("'")
                    # Skip: empty values, env lookups, list/dict literals, comments
                    if (val and val not in ("", '""', "''")
                            and not val.startswith("os.")
                            and not val.startswith("[")
                            and not val.startswith("{")
                            and "getenv" not in val
                            and len(val) > 6):
                        bad.append(f"{f}: possible hardcoded secret ({p})")
                        break
    if bad:
        for b in bad:
            print(f"  {FAIL} Secret risk — {b}")
        return False
    print(f"  {PASS} No hardcoded secrets detected")
    return True

def check_ruff(files):
    """Run ruff linter on staged Python files."""
    py_files = [f for f in files if f.endswith(".py") and os.path.exists(f)]
    if not py_files:
        print(f"  {PASS} No Python files staged")
        return True

    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check"] + py_files,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  {FAIL} Ruff found issues:")
        for line in result.stdout.strip().splitlines():
            print(f"       {line}")
        print("\n  Tip: run  python -m ruff check --fix  to auto-fix many of these.")
        return False
    print(f"  {PASS} Ruff: no issues ({len(py_files)} file(s) checked)")
    return True

def check_trailing_whitespace(files):
    """Block files with trailing whitespace on any line."""
    text_exts = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".ps1", ".html", ".css", ".js"}
    bad = []
    for f in files:
        if not any(f.endswith(ext) for ext in text_exts):
            continue
        content = get_staged_content(f)
        for i, line in enumerate(content.splitlines(), 1):
            if line != line.rstrip():
                bad.append(f"{f}:{i}")
                break
    if bad:
        print(f"  {FAIL} Trailing whitespace in: {', '.join(bad)}")
        return False
    print(f"  {PASS} No trailing whitespace")
    return True

def main():
    print("\n-- Pre-commit checks ------------------------------------------")
    staged = get_staged_files()

    if not staged:
        print("  No staged files — nothing to check.")
        print("───────────────────────────────────────────────────\n")
        sys.exit(0)

    print(f"  Checking {len(staged)} staged file(s)...\n")

    results = [
        check_merge_conflicts(staged),
        check_large_files(staged),
        check_json_valid(staged),
        check_no_secrets(staged),
        check_trailing_whitespace(staged),
        check_ruff(staged),
    ]

    print("\n---------------------------------------------------------------")
    if all(results):
        print(f"  {PASS} All checks passed -- committing.\n")
        sys.exit(0)
    else:
        failed = results.count(False)
        print(f"  {FAIL} {failed} check(s) failed -- commit blocked.")
        print("  Fix the issues above, then stage the fixes and try again.")
        print("  To bypass in an emergency: git commit --no-verify\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
