import json
import os
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
TASKS_FILE = ROOT / "tasks.json"


def load_tasks():
    with TASKS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    tasks = data.get("tasks", [])
    if not isinstance(tasks, list):
        raise ValueError("'tasks' must be a list")
    return tasks


def format_status(tasks):
    lines = ["Scheduled project status"]
    for task in tasks:
        name = str(task.get("name", "Unnamed task"))
        status = str(task.get("status", "unknown"))
        note = str(task.get("note", "")).strip()
        lines.append(f"• {name}: {status}")
        if note:
            lines.append(f"  {note}")
    lines.append("")
    lines.append("Note: this runner reports status only; it does not continue Claude.ai chats.")
    return "\n".join(lines)


def send_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram secrets are not configured; printing status only.")
        print(message)
        return

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": message},
        timeout=20,
    )
    response.raise_for_status()
    if not response.json().get("ok"):
        raise RuntimeError("Telegram API did not confirm the message.")


if __name__ == "__main__":
    task_list = load_tasks()
    if not task_list:
        raise SystemExit("No tasks found in tasks.json")
    send_telegram(format_status(task_list))
