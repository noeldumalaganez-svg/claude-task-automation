# Claude Task Automation Starter

This public repository tracks three workstreams:
- Excel project 1
- Excel project 2
- eBook project

## Important limitations

GitHub Actions cannot automatically continue work inside existing Claude.ai conversations just because this repository exists. This system does **not** log in to Claude.ai, read your conversations, or send "continue" messages. It avoids storing Claude passwords, browser cookies, or session tokens in GitHub.

Anthropic API usage is separate from a Claude.ai subscription and may cost money. AI calls remain disabled; this repository does not bypass Claude usage limits.

## What is implemented

- Existing scheduled Telegram status reports remain in `.github/workflows/scheduler.yml`.
- `tasks.json` is the shared queue for all three projects, with status, next action, and approval state.
- `telegram_control.py` handles read-only status commands and records approval/rejection decisions for tasks explicitly marked `pending_approval`.
- `.github/workflows/telegram-control.yml` checks Telegram commands about every five minutes and can also be run manually.
- Unit tests cover command handling and approval safety.
- `HANDOFF_TEMPLATE.md` helps preserve context from the original Claude conversations.
- `FREE_TIER_WORKFLOW.md` describes the no-extra-cost approach.

**Approval is a record only.** `/approve` does not run code, modify a workbook, publish the eBook, or perform any other project action. A real task worker has not been implemented yet.

## Telegram commands

Send these commands to the configured bot from the chat matching `TELEGRAM_CHAT_ID`:

- `/help` — list commands and safety rules.
- `/status` — show status for all three projects.
- `/tasks` — show task IDs, statuses, and approval states.
- `/approve <task-id>` — record approval only if that task is already marked `pending_approval`.
- `/reject <task-id>` — record rejection only if that task is already marked `pending_approval`.

Commands are checked on a best-effort five-minute schedule, so replies are not instant. Do not configure a Telegram webhook for this bot while using the polling workflow; Telegram polling and webhooks are mutually exclusive. The workflow needs repository Contents write permission only to save approval decisions to `tasks.json`.

To create an approval request, edit the relevant task in `tasks.json` and set `approval_state` to `pending_approval`, with a clear description of the proposed action. Do not include private project data or secrets in that description.

## Preserve your existing Claude work

1. Open `HANDOFF_TEMPLATE.md`.
2. When the original Claude conversation is available again, ask Claude to fill out the template with actual project progress.
3. Save each completed handoff in private storage (not in this public repository).
4. Keep private project files and workbooks in private storage as well.

## Setup and checks

1. In GitHub, open **Settings → Secrets and variables → Actions**.
2. Confirm repository secrets `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are configured. Never put them in committed files, issues, or chat messages.
3. Under **Actions**, confirm workflows are enabled and that the workflow token is allowed to write repository contents.
4. Run **Actions → Telegram task controls → Run workflow** to test the command poller; run **Scheduled task status** to test the existing status report.
5. Check the workflow run logs if a command does not receive a reply. GitHub scheduled runs are best-effort and may be delayed.

## Privacy and safety

This is a **public** repository. Do not commit private spreadsheet/eBook contents, handoffs, credentials, personal data, or client information. Keep AI calls disabled to preserve the ₱0 extra budget. Future workers must use explicitly authorized private inputs, bounded tasks, draft outputs, and approval gates for consequential changes.

## Current status

The system can track tasks and report status, and the Telegram control workflow can record decisions. A reusable, read-only eBook QA/DOCX draft workflow is now available in `.github/workflows/ebook-worker-reusable.yml`, with its helper in `ebook_worker.py`. It must be called by a private manuscript repository; this public repository does not contain the manuscript and does not run the private build itself. The worker checks section count, summarizes scanner flags without printing manuscript excerpts, and creates a draft artifact plus metadata-only report. It does not edit the master, upload to Drive, perform a literary or historical review, or continue Claude.ai chats.


## Important Actions billing clarification

Public repositories can use standard GitHub-hosted runners without consuming the included Actions minutes, subject to GitHub's other limits and policies. However, when a private repository calls this reusable workflow, the Actions minutes are charged to the **private caller repository**. Reusing public workflow code does not make the private build unlimited. Keep the eBook workflow manual or low-frequency, monitor the included allowance, and do not enable paid overages if the budget must remain PHP 0.
