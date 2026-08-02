"""
Spec-derived integration and contract tests for User Auth Login.
Written solely based on specs/user_auth/login/spec.md
"""

import unittest
from user_auth import login

class TestUserAuthLogin(unittest.TestCase):

    def test_login_user_not_found(self):
        # @sds-trace: user_auth.login:AC-1
        response, status_code = login("non_existent_user", "some_password")
        self.assertEqual(status_code, 401)
        self.assertFalse(response["success"])
        self.assertEqual(response["error_code"], "USER_NOT_FOUND")

    def test_login_invalid_credentials(self):
        # @sds-trace: user_auth.login:AC-2
        response, status_code = login("alice", "wrongpassword")
        self.assertEqual(status_code, 401)
        self.assertFalse(response["success"])
        self.assertEqual(response["error_code"], "INVALID_CREDENTIALS")

    def test_login_success(self):
        # @sds-trace: user_auth.login:AC-3
        response, status_code = login("alice", "password123")
        self.assertEqual(status_code, 200)
        self.assertTrue(response["success"])
        self.assertIn("token", response)
        self.assertEqual(response["expires_in"], 3600)

        # Basic JWT format check
        token_parts = response["token"].split(".")
        self.assertEqual(len(token_parts), 2)
        payload = token_parts[0]
        self.assertIn("user_id:user-uuid-1111", payload)

    def test_login_audit_triggered(self):
        # @sds-trace: user_auth.login:AC-4
        # Verify that AC-4 (Audit trail trigger) is invoked on successful login
        from unittest.mock import patch
        with patch("user_auth.send_audit_log") as mock_audit:
            response, status_code = login("alice", "password123")
            self.assertEqual(status_code, 200)
            mock_audit.assert_called_once_with("alice")

    def test_suspended_account_is_denied_without_success_side_effects(self):
        # @sds-trace: user_auth.login:AC-5
        from unittest.mock import patch
        with patch("user_auth.send_audit_log") as mock_audit:
            response, status_code = login("bob", "password456")

        self.assertEqual(status_code, 403)
        self.assertFalse(response["success"])
        self.assertEqual(response["error_code"], "ACCOUNT_SUSPENDED")
        self.assertNotIn("token", response)
        mock_audit.assert_not_called()

if __name__ == "__main__":
    unittest.main()
