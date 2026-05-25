#!/usr/bin/env python3
"""
MiMo Code Reviewer — AI code review agent powered by Xiaomi MiMo V2.5 Pro
Usage: python review.py <file_or_dir> [--recursive] [--output report.md]
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path

API_BASE = "https://api.xiaomimimo.com/v1"
MODEL = "mimo-v2.5-pro"

SYSTEM_PROMPT = """You are an expert Python code reviewer. Analyze the code and find:
1. 🐛 Bugs — potential errors, unhandled exceptions, logic issues
2. ⚡ Performance — inefficient patterns, unnecessary allocations
3. 📝 Style — readability, naming, function length, missing docstrings

For each issue, respond in this exact format:
TYPE|LINE|TITLE|SUGGESTION

Where TYPE is Bug, Perf, or Style.
End with a score line: SCORE|X.X

Example:
Bug|23|Unchecked None return|Add null check before .data access
Perf|67|List comprehension in loop|Move filtering outside loop
Style|89|Long function|Extract validation into helper
SCORE|7.2"""


def review_code(code: str, filename: str, api_key: str) -> dict:
    """Send code to MiMo for review."""
    r = requests.post(
        f"{API_BASE}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Review this file ({filename}):\n\n```python\n{code}\n```"},
            ],
            "temperature": 0.3,
            "max_tokens": 2048,
        },
        timeout=60,
    )
    r.raise_for_status()
    response = r.json()["choices"][0]["message"]["content"]
    return parse_review(response)


def parse_review(response: str) -> dict:
    """Parse MiMo review output into structured data."""
    issues = []
    score = 0.0

    for line in response.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split("|")
        if len(parts) == 2 and parts[0] == "SCORE":
            try:
                score = float(parts[1])
            except ValueError:
                pass
        elif len(parts) == 4:
            icon = {"Bug": "🐛", "Perf": "⚡", "Style": "📝"}.get(parts[0], "❓")
            issues.append({
                "type": parts[0],
                "icon": icon,
                "line": parts[1],
                "title": parts[2],
                "suggestion": parts[3],
            })

    return {"issues": issues, "score": score}


def format_report(filename: str, line_count: int, review: dict) -> str:
    """Format review as readable output."""
    lines = [f"\n📁 Reviewing: {filename} ({line_count} lines)\n"]

    if not review["issues"]:
        lines.append("  ✅ No issues found!\n")
    else:
        for issue in review["issues"]:
            lines.append(f"  {issue['icon']} [{issue['type']}] Line {issue['line']}: {issue['title']}")
            lines.append(f"     → {issue['suggestion']}\n")

    lines.append(f"  Score: {review['score']}/10 | Issues: {len(review['issues'])}")
    return "\n".join(lines)


def collect_files(path: Path, recursive: bool) -> list:
    """Collect Python files to review."""
    if path.is_file():
        return [path] if path.suffix == ".py" else []
    if recursive:
        return sorted(path.rglob("*.py"))
    return sorted(path.glob("*.py"))


def main():
    parser = argparse.ArgumentParser(description="MiMo Code Reviewer")
    parser.add_argument("path", help="File or directory to review")
    parser.add_argument("--recursive", "-r", action="store_true", help="Scan subdirectories")
    parser.add_argument("--output", "-o", help="Save report to file")
    args = parser.parse_args()

    api_key = os.environ.get("MIMO_API_KEY", "")
    if not api_key:
        print("[!] Set MIMO_API_KEY environment variable")
        sys.exit(1)

    target = Path(args.path)
    if not target.exists():
        print(f"[!] Not found: {target}")
        sys.exit(1)

    files = collect_files(target, args.recursive)
    if not files:
        print("[!] No Python files found")
        sys.exit(1)

    print(f"🔍 MiMo Code Reviewer — {len(files)} file(s)")
    print(f"   Model: {MODEL}\n")

    full_report = []
    total_issues = 0

    for f in files:
        code = f.read_text(encoding="utf-8", errors="ignore")
        line_count = len(code.splitlines())
        print(f"  Reviewing {f.name}...", end=" ", flush=True)

        try:
            review = review_code(code, f.name, api_key)
            report = format_report(str(f), line_count, review)
            print(f"✓ ({len(review['issues'])} issues)")
            full_report.append(report)
            total_issues += len(review["issues"])
        except Exception as e:
            print(f"✗ Error: {e}")
            full_report.append(f"\n📁 {f}: ❌ Error — {e}")

    # Print results
    output = "\n".join(full_report)
    output += f"\n\n{'='*40}\n  Total: {len(files)} files | {total_issues} issues\n{'='*40}"
    print(output)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"\n  Report saved: {args.output}")


if __name__ == "__main__":
    main()
