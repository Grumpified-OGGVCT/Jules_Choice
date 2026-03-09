#!/usr/bin/env python3
"""Chart generator for Jules_Choice.

Generates SVG charts from repository metrics data.
Supports bar charts, progress charts, and health scorecards.
"""

import os


def generate_health_badge(score: float, output_path: str = "docs/assets/generated/health_badge.svg") -> str:
    """Generate an SVG health score badge."""
    if score >= 80:
        color = "#22c55e"  # green
        label = "healthy"
    elif score >= 50:
        color = "#f59e0b"  # amber
        label = "fair"
    else:
        color = "#ef4444"  # red
        label = "needs work"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="180" height="28" viewBox="0 0 180 28">
  <defs>
    <linearGradient id="bg" x2="0" y2="100%">
      <stop offset="0" stop-color="#555" stop-opacity=".1"/>
      <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
  </defs>
  <rect rx="4" width="180" height="28" fill="#555"/>
  <rect rx="4" x="80" width="100" height="28" fill="{color}"/>
  <rect rx="4" width="180" height="28" fill="url(#bg)"/>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,sans-serif" font-size="11">
    <text x="40" y="19">Health</text>
    <text x="130" y="19">{score:.0f}/100 {label}</text>
  </g>
</svg>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    return output_path


def generate_progress_chart(data: dict, output_path: str = "docs/assets/generated/progress_chart.svg") -> str:
    """Generate an SVG progress bar chart.
    
    Args:
        data: Dict of {label: (current, total)} pairs
    """
    bar_height = 30
    spacing = 10
    margin_left = 120
    bar_width = 250
    height = len(data) * (bar_height + spacing) + 40
    width = margin_left + bar_width + 80

    bars = []
    for i, (label, (current, total)) in enumerate(data.items()):
        y = 30 + i * (bar_height + spacing)
        pct = (current / total * 100) if total > 0 else 0
        fill_width = int(bar_width * pct / 100)
        if pct >= 80:
            fill_color = "#22c55e"
        elif pct >= 50:
            fill_color = "#f59e0b"
        else:
            fill_color = "#3b82f6"
        bars.append(f'  <text x="{margin_left - 10}" y="{y + 20}" text-anchor="end" font-size="12" fill="#e2e8f0">{label}</text>')
        bars.append(f'  <rect x="{margin_left}" y="{y}" width="{bar_width}" height="{bar_height}" rx="4" fill="#334155"/>')
        bars.append(f'  <rect x="{margin_left}" y="{y}" width="{fill_width}" height="{bar_height}" rx="4" fill="{fill_color}"/>')
        bars.append(f'  <text x="{margin_left + bar_width + 10}" y="{y + 20}" font-size="12" fill="#94a3b8">{current}/{total}</text>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" rx="8" fill="#1e293b"/>
  <text x="{width // 2}" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#f1f5f9">Jules Progress</text>
  <g font-family="monospace">
{'\n'.join(bars)}
  </g>
</svg>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    return output_path


def generate_agent_grid(agents: list[str], output_path: str = "docs/assets/generated/agent_grid.svg") -> str:
    """Generate an SVG grid showing all agents."""
    cols = 4
    cell_w = 140
    cell_h = 50
    padding = 8
    rows = (len(agents) + cols - 1) // cols
    width = cols * (cell_w + padding) + padding
    height = rows * (cell_h + padding) + padding + 30

    colors = ["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444",
              "#ec4899", "#6366f1", "#14b8a6", "#f97316", "#84cc16", "#a855f7",
              "#0ea5e9", "#22d3ee"]

    cells = []
    for i, agent in enumerate(agents):
        row = i // cols
        col = i % cols
        x = padding + col * (cell_w + padding)
        y = 30 + padding + row * (cell_h + padding)
        color = colors[i % len(colors)]
        cells.append(f'  <rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" rx="6" fill="{color}" opacity="0.85"/>')
        cells.append(f'  <text x="{x + cell_w // 2}" y="{y + cell_h // 2 + 5}" text-anchor="middle" font-size="11" font-weight="bold" fill="white">{agent}</text>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" rx="8" fill="#0f172a"/>
  <text x="{width // 2}" y="22" text-anchor="middle" font-size="14" font-weight="bold" fill="#f1f5f9">Jules Agent Grid ({len(agents)} agents)</text>
  <g font-family="monospace">
{'\n'.join(cells)}
  </g>
</svg>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    return output_path


def main():
    """Generate all charts."""
    print("Chart Generator")
    print("=" * 40)

    # Health badge
    from tools.repo_health import compute_health
    metrics = compute_health('.')
    badge_path = generate_health_badge(metrics.health_score)
    print(f"  Generated: {badge_path}")

    # Progress chart
    progress = {
        "Agents": (metrics.agent_count, 17),
        "Tools": (metrics.tool_count, 8),
        "Tests": (metrics.test_files, 10),
        "Docs": (metrics.doc_files, 15),
    }
    chart_path = generate_progress_chart(progress)
    print(f"  Generated: {chart_path}")

    # Agent grid
    agents = ["Steward", "Arbiter", "Cove", "Sentinel", "Weaver",
              "Chronicler", "Herald", "Palette", "Scribe", "Consolidator",
              "Oracle", "Catalyst", "Strategist", "Scout"]
    grid_path = generate_agent_grid(agents)
    print(f"  Generated: {grid_path}")


if __name__ == '__main__':
    main()
