#!/usr/bin/env python3
"""Self-evaluation tool for Jules_Choice.

Provides a comprehensive self-assessment by running all health,
security, policy, and goal checks, then producing a report card.
"""

from datetime import datetime


def run_self_eval() -> dict:
    """Run comprehensive self-evaluation."""
    results = {
        'timestamp': datetime.now().isoformat(),
        'checks': {},
        'overall_grade': 'F',
    }

    # Health check
    try:
        from tools.repo_health import compute_health
        health = compute_health('.')
        results['checks']['health'] = {
            'score': health.health_score,
            'status': 'PASS' if health.health_score >= 50 else 'FAIL',
        }
    except ImportError:
        results['checks']['health'] = {'score': 0, 'status': 'ERROR'}

    # Security check
    try:
        from tools.security_scan import scan_directory
        scan = scan_directory('.')
        results['checks']['security'] = {
            'files_scanned': scan.files_scanned,
            'findings': len(scan.findings),
            'critical': scan.critical_count,
            'status': 'PASS' if scan.passed else 'FAIL',
        }
    except ImportError:
        results['checks']['security'] = {'status': 'ERROR'}

    # Policy check
    try:
        from tools.policy_checker import run_policy_check
        policy = run_policy_check()
        results['checks']['policy'] = {
            'checks_run': policy.checks_run,
            'violations': len(policy.violations),
            'status': 'PASS' if policy.passed else 'FAIL',
        }
    except ImportError:
        results['checks']['policy'] = {'status': 'ERROR'}

    # Goal tracking
    try:
        from tools.goal_tracker import track_goals
        goals = track_goals()
        achieved = sum(1 for g in goals if g.achieved)
        results['checks']['goals'] = {
            'achieved': achieved,
            'total': len(goals),
            'completion': f"{(achieved / len(goals) * 100):.0f}%" if goals else "0%",
            'status': 'PASS' if achieved >= len(goals) // 2 else 'NEEDS_WORK',
        }
    except ImportError:
        results['checks']['goals'] = {'status': 'ERROR'}

    # Compute overall grade
    statuses = [c.get('status', 'ERROR') for c in results['checks'].values()]
    pass_count = statuses.count('PASS')
    total = len(statuses)
    if pass_count == total:
        results['overall_grade'] = 'A'
    elif pass_count >= total * 0.75:
        results['overall_grade'] = 'B'
    elif pass_count >= total * 0.5:
        results['overall_grade'] = 'C'
    elif pass_count >= total * 0.25:
        results['overall_grade'] = 'D'
    else:
        results['overall_grade'] = 'F'

    return results


def main():
    """Run and display self-evaluation."""
    print("Jules Self-Evaluation Report")
    print("=" * 50)

    results = run_self_eval()
    print(f"\nTimestamp: {results['timestamp']}")
    print(f"Overall Grade: {results['overall_grade']}")
    print()

    for check_name, check_data in results['checks'].items():
        status = check_data.get('status', 'UNKNOWN')
        icon = {'PASS': 'OK', 'FAIL': 'FAIL', 'NEEDS_WORK': 'WARN', 'ERROR': 'ERR'}.get(status, '?')
        print(f"  [{icon}] {check_name}:")
        for key, value in check_data.items():
            if key != 'status':
                print(f"       {key}: {value}")
        print()


if __name__ == '__main__':
    main()
