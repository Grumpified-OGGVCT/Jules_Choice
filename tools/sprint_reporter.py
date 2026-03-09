#!/usr/bin/env python3
"""Sprint reporter for Jules_Choice."""

import os
import sys
import subprocess
from datetime import datetime


def get_recent_commits(since: str = "1 week ago", limit: int = 50) -> list[dict]:
    try:
        result = subprocess.run(
            ['git', 'log', f'--since={since}', f'-n{limit}',
             '--format=%H|||%ai|||%s|||%an'],
            capture_output=True, text=True, check=True
        )
        commits = []
        for line in result.stdout.strip().splitlines():
            parts = line.split('|||')
            if len(parts) == 4:
                commits.append({'sha': parts[0][:8], 'date': parts[1], 'message': parts[2], 'author': parts[3]})
        return commits
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def get_file_stats() -> dict:
    stats = {'agents': 0, 'tools': 0, 'tests': 0, 'docs': 0, 'config': 0}
    mappings = {'agents/': 'agents', 'tools/': 'tools', 'tests/': 'tests', 'docs/': 'docs', 'config/': 'config'}
    for dirpath, _, filenames in os.walk('.'):
        if '.git' in dirpath:
            continue
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            for prefix, category in mappings.items():
                if prefix in filepath:
                    stats[category] += 1
                    break
    return stats


def generate_report(since: str = "1 week ago") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    commits = get_recent_commits(since)
    stats = get_file_stats()
    report = [f"# Sprint Report -- {now}", "", "## Summary"]
    report.append(f"- **Commits:** {len(commits)}")
    for k, v in stats.items():
        report.append(f"- **{k.capitalize()}:** {v}")
    if commits:
        report.extend(["", "## Recent Commits", "", "| SHA | Date | Message | Author |", "|-----|------|---------|--------|" ])
        for c in commits[:20]:
            report.append(f"| `{c['sha']}` | {c['date'][:10]} | {c['message'][:60]} | {c['author']} |")
    return '\n'.join(report)


def main():
    since = sys.argv[1] if len(sys.argv) > 1 else "1 week ago"
    report = generate_report(since)
    print(report)
    if '--save' in sys.argv:
        output_path = f"logs/sprint_report_{datetime.now().strftime('%Y%m%d')}.md"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nSaved to {output_path}")


if __name__ == '__main__':
    main()
