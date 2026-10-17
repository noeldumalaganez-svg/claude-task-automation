# Claude Task Automation Starter

This repository is a **scheduler and Telegram notification starter** for tracking three workstreams:
- Excel project 1
- Excel project 2
- eBook project

## Important limitation

GitHub Actions cannot automatically continue work inside existing Claude.ai conversations just because this repository exists. This starter does **not** log in to Claude.ai, read your conversations, or send "continue" messages. It avoids storing Claude passwords, browser cookies, or session tokens in GitHub.

To automate actual generation, a supported API integration or a separately designed local browser workflow would be needed. Anthropic API usage is separate from a Claude.ai subscription and may cost money. Do not try to bypass Claude usage limits.

## What this starter does

- Runs on a schedule and when manually triggered.
- Checks the public task queue file.
- Sends a Telegram status message when Telegram secrets are configured.
- Keeps project data and credentials out of this public repository.

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

This is a safe foundation for scheduling and status notifications, **not yet an AI worker**. It does not modify your Excel files or write the eBook automatically.
