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

if __name__ == "__main__":
    unittest.main()
