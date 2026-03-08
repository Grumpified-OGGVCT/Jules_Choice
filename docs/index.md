---
layout: home
title: Jules Sandbox — Sprint Preview
---

<p align="center">
  <img src="assets/banner.svg" alt="Jules Sandbox — An Open-Ended Autonomous AI Playground" style="max-width:100%;border-radius:8px;">
</p>

# Jules Sandbox — Live Project Preview

> **⚠️ Jules: You must update this page at the end of every sprint.**
> This is a static GitHub Pages site served from the `/docs` folder.
> It is the canonical public preview of the current project state.
> Replace every section below with accurate, up-to-date information before closing a sprint.

---

## Current Sprint Status

| Field | Value |
|-------|-------|
| **Sprint** | — |
| **Status** | 🟡 In progress |
| **Last updated** | — |
| **Updated by** | Jules (autonomous) |

---


## App Gallery

<!-- APP_GALLERY_START -->

### hello_world
![Screenshot](https://via.placeholder.com/300x200?text=No+Image)

A tiny, self‑contained example that Jules created on its first run.

Running this script prints a friendly greeting.  Jules may replace or extend
this example with something more ambitious later.

**Last Updated:** 2026-03-08 15:06:54 -0500

[Download Zip](app_zips/hello_world.zip)

---

<!-- APP_GALLERY_END -->

## How Jules Works

<p align="center">
  <img src="assets/how-it-works.svg" alt="How Jules Works — Autonomous Cycle Diagram" style="max-width:100%;border-radius:8px;">
</p>

Jules wakes on a schedule (or manual trigger), explores the repository, builds or extends something interesting, tests it, commits the result, and waits for the Eleven Hats review before the next cycle begins. The only hard constraints are the safety rules in `jules_policy.yaml`.

---

## What Jules Has Built So Far

_Jules: replace this section with a concise, human-readable summary of every component,
tool, or module added since the last preview update._

- `examples/hello_world/` — minimal Python entry point (`python examples/hello_world/main.py`)
- `config/personas/` — 15 Sovereign Agentic OS personas + shared universal mandates
- `governance/templates/` — Eleven Hats PR review protocol

---

## Repository Layout

<p align="center">
  <img src="assets/repo-map.svg" alt="Repository Structure — Directory Map" style="max-width:100%;border-radius:8px;">
</p>

```
jules-sandbox/
├── agents/          # Reusable AI-agent classes / notebooks
├── config/
│   └── personas/    # 15 Sovereign OS personas + _shared_mandates.md
├── docs/            # ← YOU ARE HERE (GitHub Pages static site)
├── examples/        # Demonstrators; hello_world is the first
├── governance/
│   └── templates/   # eleven_hats_review.md — mandatory PR review template
├── logs/            # policy_check.log + ethics.log (auto-written by Jules)
├── tests/           # Unit-test scaffolding
├── tools/           # Experimental utilities
├── jules_config.yaml
└── jules_policy.yaml
```

---

## Sovereign Agentic OS — Persona Pack

<p align="center">
  <img src="assets/personas-grid.svg" alt="Sovereign Agentic OS Persona Pack — 14 personas and shared mandates" style="max-width:100%;border-radius:8px;">
</p>

Jules carries a built-in team of 14 specialist AI personas — each with a defined domain, hat colour, and operating temperature. Every persona is governed by the 9 Universal Operating Mandates in `_shared_mandates.md`. Jules can instantiate any combination of them to analyse, plan, review, or build.

---

## Eleven Hats — PR Review Protocol

<p align="center">
  <img src="assets/eleven-hats.svg" alt="Eleven Hats PR Review Protocol" style="max-width:100%;border-radius:8px;">
</p>

Every pull request Jules opens must pass all 11 hat perspectives — 6 core De Bono hats plus 5 Sovereign OS extensions — before it is tagged `Hat-Reviewed` and submitted for human review.

---

## Active Roadmap Items

_Jules: keep this in sync with `docs/roadmap.md`._

- [x] Scaffold repository skeleton
- [x] Embed Sovereign OS persona pack (15 personas)
- [x] Add governance review template (Eleven Hats)
- [ ] Explore a small data-visualisation library
- [ ] Add an interactive REPL tool
- [ ] Build a tiny web-demo (e.g., Flask or FastAPI)
- [ ] Write unit tests for any new component
- [ ] Periodically prune or refactor obsolete code

---

## Sprint History

_Jules: append a new row here at the end of every sprint._

| Sprint | Completed | Key deliverables |
|--------|-----------|-----------------|
| 0 | 2026-03-08 | Repo scaffold, persona pack, governance templates, GitHub Pages setup |

---

## How to Navigate This Site

| Page | Purpose |
|------|---------|
| [Home](index.md) | This page — current project overview |
| [Roadmap](roadmap.md) | Living checklist of planned and completed work |
| [Changelog](CHANGELOG.md) | Full history of every notable change Jules has made |

---

## Jules' Sprint-End Update Protocol

At the end of every sprint Jules **must** update **both** `README.md` and this page:

1. Update the **Current Sprint Status** table in **both files** (sprint number, status, date).
2. Update the **What's Been Built / What Jules Has Built So Far** section in **both files**.
3. Update the **Active Roadmap Items** checklist in **both files** (keep in sync with `docs/roadmap.md`).
4. Append a new row to the **Sprint History** table in **both files**.
5. Commit both files together with the message: `docs: sprint <N> preview update`.

`README.md` is what humans see first on GitHub.  
`docs/index.md` (this page) is the rendered GitHub Pages public preview.  
Both must always reflect the same current state.

This site is **static** — GitHub Pages re-renders it automatically on every push to the branch,
but the content only changes when Jules explicitly edits the Markdown files in `/docs`.
