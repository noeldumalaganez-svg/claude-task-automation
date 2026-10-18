# Claude Task Automation Starter

This repository is a **scheduler and Telegram notification starter** for tracking three workstreams:
- Excel project 1
- Excel project 2
- eBook project

## Important limitation

GitHub Actions cannot automatically continue work inside existing Claude.ai conversations just because this repository exists. This starter does **not** log in to Claude.ai, read your conversations, or send "continue" messages. It avoids storing Claude passwords, browser cookies, or session tokens in GitHub.

Anthropic API usage is separate from a Claude.ai subscription and may cost money. The current free-tier plan keeps AI calls disabled and does not attempt to bypass Claude usage limits.

## What this starter does

- Runs on a schedule and when manually triggered.
- Reads the public task queue file.
- Sends Telegram status messages when Telegram secrets are configured.
- Includes a generic handoff template to preserve context from the original chats.
- Documents a free-tier workflow and safety rules.
- Keeps project data and credentials out of this public repository.

## Preserve your existing Claude work

1. Open `HANDOFF_TEMPLATE.md`.
2. When a project’s original Claude conversation is available again, ask Claude to fill out the template with actual project progress.
3. Save each completed handoff in private storage (not in this public repository).
4. Keep private project files and workbooks in private storage as well.

See `FREE_TIER_WORKFLOW.md` for the planned rollout and limitations.

## Setup

1. In GitHub, open **Settings → Secrets and variables → Actions**.
2. Add repository secrets:
   - `TELEGRAM_BOT_TOKEN`: your Telegram bot token.
   - `TELEGRAM_CHAT_ID`: your Telegram chat ID.
3. Never put either secret in a committed file, issue, or chat message.
4. Open **Actions → Scheduled task status → Run workflow** to test manually.
5. The scheduled run is best-effort; GitHub may delay cron runs.

## Edit the task queue

Edit `tasks.json` to change project labels and notes. Do not put private spreadsheet or eBook contents in this public repository.

## Current status

The current Python runner is **status-only**. It does not modify Excel files, write the eBook, or continue Claude.ai chats. Any future worker must have explicitly authorized private inputs, bounded tasks, safe draft outputs, and approval gates for consequential changes.
