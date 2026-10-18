# Free-Tier Workflow Guide

This repository is public. Keep actual project handoffs, workbooks, eBook drafts, and any private details in private storage.

## What can run at ₱0 extra

- Scheduled task-status checks using GitHub Actions (subject to GitHub's free allowance and best-effort scheduling).
- Telegram status notifications using the existing repository secrets.
- A private handoff workflow: ask each ORIGINAL Claude conversation to fill in `HANDOFF_TEMPLATE.md` when its rate limit resets, then save the completed copy outside this public repo.
- Local/offline checks and template-based draft creation once the project files are available to the runner.

## What this does not do

- It cannot read or send messages to existing Claude.ai conversations.
- It does not provide unlimited free AI inference.
- It must not log into Claude.ai using saved passwords, cookies, or session tokens, and must not bypass rate limits.
- It must not upload private project data to this public repository.

## Rollout

### Phase 1 — Preserve the source context
1. When each Claude conversation is available, ask it to complete `HANDOFF_TEMPLATE.md`.
2. Save each completed handoff in a private folder or private repository.
3. Keep a copy of the original source files. Never overwrite them during initial automation.

### Phase 2 — Prepare task manifests
For each project, create a private manifest with:
- project ID
- private handoff file path
- authorized input file paths
- next task
- output folder
- status
- approval required (true/false)

Do not put the contents of these private manifests in this public repository.

### Phase 3 — Safe automated work
Start with checks and draft-only outputs:
- Excel: inspect workbook structure and formulas only after the user explicitly supplies an authorized workbook to the worker; save any proposed changes to a new copy.
- eBook: create draft sections in a separate output file; do not publish.
- Validate output files and report results.
- Require approval before overwriting/deleting files, publishing, or taking consequential external actions.

### Phase 4 — Optional AI
If a genuinely free, supported AI endpoint is available and its terms allow this use, configure it explicitly. Otherwise leave AI calls disabled. Never assume a Claude.ai subscription includes API usage.

## Budget and safety rules

- Default AI calls: disabled.
- Maximum AI spend: ₱0.
- If an API key or paid model is configured accidentally, stop rather than call it.
- No secrets in code, commits, logs, handoffs, or Telegram messages.
- Each scheduled run should have a bounded runtime and bounded task count.
- GitHub cron schedules are best-effort, not guaranteed exact-time execution.
