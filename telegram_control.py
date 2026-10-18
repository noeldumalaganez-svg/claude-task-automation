"""Telegram command poller for the project task queue.

Commands: /help, /status, /tasks, /approve <task-id>, /reject <task-id>.
Approval commands only record a decision for a task already marked pending_approval.
They never execute project work, change private files, or call an AI API.
"""
import base64
import json
import os
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
TASKS_FILE = ROOT / "tasks.json"
API_TIMEOUT = 20
TASK_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


def telegram_call(token, method, payload=None):
    response = requests.post(
        f"https://api.telegram.org/bot{token}/{method}",
        json=payload or {},
        timeout=API_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram method {method} failed")
    return data.get("result", [])


def load_queue():
    with TASKS_FILE.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("'tasks' must be a list")
    seen = set()
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str):
            raise ValueError("Every task must be an object with a string id")
        if not TASK_ID_RE.fullmatch(task["id"]) or task["id"] in seen:
            raise ValueError(f"Invalid or duplicate task id: {task.get('id')}")
        seen.add(task["id"])
    return data


def status_message(data):
    lines = ["Project automation status"]
    for task in data["tasks"]:
        lines.append(f"• {task.get('name', task['id'])}: {task.get('status', 'unknown')}")
    pending = sum(t.get("approval_state") == "pending_approval" for t in data["tasks"])
    lines.append(f"Pending approvals: {pending}")
    lines.append("AI calls are disabled. This bot only tracks status and approval decisions.")
    return "\n".join(lines)


def tasks_message(data):
    lines = ["Task queue"]
    for task in data["tasks"]:
        lines.append(
            f"• {task['id']} — {task.get('name', 'Unnamed')} "
            f"[{task.get('status', 'unknown')}; approval: {task.get('approval_state', 'not_requested')}]"
        )
    return "\n".join(lines)


def handle_command(text, data):
    parts = text.strip().split()
    if not parts:
        return "Send /help to see available commands.", False
    command = parts[0].split("@", 1)[0].lower()
    if command in ("/start", "/help"):
        return (
            "Commands:\n/status — project status\n/tasks — list task queue\n"
            "/approve <task-id> — approve a task marked pending_approval\n"
            "/reject <task-id> — reject a task marked pending_approval\n"
            "Approval only records your decision; it does not execute or publish changes."
        ), False
    if command == "/status":
        return status_message(data), False
    if command == "/tasks":
        return tasks_message(data), False
    if command in ("/approve", "/reject"):
        if len(parts) != 2 or not TASK_ID_RE.fullmatch(parts[1]):
            return f"Usage: {command} <task-id>", False
        task = next((item for item in data["tasks"] if item["id"] == parts[1]), None)
        if task is None:
            return f"Unknown task id: {parts[1]}. Use /tasks.", False
        if task.get("approval_state") != "pending_approval":
            return (
                f"No pending approval for {parts[1]}. Current state: "
                f"{task.get('approval_state', 'not_requested')}. No changes made."
            ), False
        decision = "approved" if command == "/approve" else "rejected"
        task["approval_state"] = decision
        task["approval_decision"] = decision
        return f"Recorded {decision} for {parts[1]}. No task was executed and no project files were changed.", True
    return "Unknown command. Send /help.", False


def persist_queue(repo, github_token, data):
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = f"https://api.github.com/repos/{repo}/contents/tasks.json"
    current = requests.get(url, headers=headers, timeout=API_TIMEOUT)
    current.raise_for_status()
    current_data = current.json()
    encoded = base64.b64encode(
        (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    ).decode("ascii")
    response = requests.put(
        url,
        headers=headers,
        json={
            "message": "Record Telegram approval decision",
            "content": encoded,
            "sha": current_data["sha"],
            "branch": os.getenv("GITHUB_REF_NAME", "main"),
        },
        timeout=API_TIMEOUT,
    )
    response.raise_for_status()


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    repo = os.getenv("GITHUB_REPOSITORY")
    github_token = os.getenv("GITHUB_TOKEN")
    if not token or not chat_id:
        raise SystemExit("Telegram secrets are not configured.")
    if not repo or not github_token:
        raise SystemExit("GitHub repository/token environment is missing.")

    data = load_queue()
    updates = telegram_call(token, "getUpdates", {"timeout": 0, "allowed_updates": ["message"]})
    cursor = max((int(u.get("update_id", 0)) for u in updates), default=None)
    allowed_chat = str(chat_id)
    replies = []
    changed_any = False

    for update in sorted(updates, key=lambda u: int(u.get("update_id", 0))):
        message = update.get("message") or {}
        chat = message.get("chat") or {}
        # Ignore messages from every chat except the configured private/group chat.
        if str(chat.get("id", "")) != allowed_chat:
            continue
        command_text = message.get("text", "")
        if not command_text.startswith("/"):
            continue
        reply, changed = handle_command(command_text, data)
        replies.append(reply)
        changed_any = changed_any or changed

    if changed_any:
        # Persist only when this run made a new decision; stale file SHA makes races fail closed.
        persist_queue(repo, github_token, data)

    if replies:
        telegram_call(token, "sendMessage", {"chat_id": allowed_chat, "text": "\n\n".join(replies)})

    # Acknowledge updates after processing. If persistence fails, the run stops before this point.
    if cursor is not None:
        telegram_call(token, "getUpdates", {"offset": cursor + 1, "timeout": 0, "allowed_updates": ["message"]})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Telegram control run failed safely: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
