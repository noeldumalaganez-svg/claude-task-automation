import unittest

import telegram_control


class TelegramCommandTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "tasks": [
                {"id": "excel-1", "name": "Excel project 1", "status": "waiting_for_integration", "approval_state": "not_requested"},
                {"id": "excel-2", "name": "Excel project 2", "status": "waiting_for_integration", "approval_state": "pending_approval"},
                {"id": "ebook", "name": "eBook project", "status": "waiting_for_integration", "approval_state": "not_requested"},
            ]
        }

    def test_help_lists_commands_and_safety_boundary(self):
        reply, changed = telegram_control.handle_command("/help", self.data)
        self.assertIn("/status", reply)
        self.assertIn("/approve <task-id>", reply)
        self.assertIn("does not execute", reply)
        self.assertFalse(changed)

    def test_status_reports_all_three_projects(self):
        reply, changed = telegram_control.handle_command("/status", self.data)
        self.assertIn("Excel project 1", reply)
        self.assertIn("Excel project 2", reply)
        self.assertIn("eBook project", reply)
        self.assertFalse(changed)

    def test_tasks_lists_approval_state(self):
        reply, changed = telegram_control.handle_command("/tasks", self.data)
        self.assertIn("excel-2", reply)
        self.assertIn("pending_approval", reply)
        self.assertFalse(changed)

    def test_approve_only_records_pending_decision(self):
        reply, changed = telegram_control.handle_command("/approve excel-2", self.data)
        self.assertTrue(changed)
        self.assertEqual(self.data["tasks"][1]["approval_state"], "approved")
        self.assertIn("No task was executed", reply)

    def test_cannot_approve_task_without_pending_request(self):
        reply, changed = telegram_control.handle_command("/approve excel-1", self.data)
        self.assertFalse(changed)
        self.assertEqual(self.data["tasks"][0]["approval_state"], "not_requested")
        self.assertIn("No changes made", reply)

    def test_unknown_task_is_safe(self):
        reply, changed = telegram_control.handle_command("/reject missing", self.data)
        self.assertFalse(changed)
        self.assertIn("Unknown task id", reply)

    def test_reject_records_pending_decision(self):
        reply, changed = telegram_control.handle_command("/reject excel-2", self.data)
        self.assertTrue(changed)
        self.assertEqual(self.data["tasks"][1]["approval_state"], "rejected")
        self.assertIn("No task was executed", reply)


if __name__ == "__main__":
    unittest.main()
