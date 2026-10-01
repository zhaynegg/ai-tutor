import json
import unittest
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from unittest.mock import AsyncMock, patch

import httpx

from app.config import settings
from app.services import mail_service


class EmailJSTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.requests = []
        self.response_status = 200
        self.response_text = "OK"

        def handle_request(request):
            self.requests.append(request)
            return httpx.Response(self.response_status, text=self.response_text)

        transport = httpx.MockTransport(handle_request)
        async_client = httpx.AsyncClient
        client_patch = patch(
            "app.services.mail_service.httpx.AsyncClient",
            side_effect=lambda **kwargs: async_client(transport=transport, **kwargs),
        )
        self.client_factory = client_patch.start()
        self.addCleanup(client_patch.stop)

        settings_patch = patch.multiple(
            settings,
            EMAILJS_SERVICE_ID="test-service-id",
            EMAILJS_TEMPLATE_ID="test-template-id",
            EMAILJS_PUBLIC_KEY="test-public-key",
            EMAILJS_PRIVATE_KEY="",
            BREVO_API_KEY="test-brevo-key",
            RESEND_API_KEY="test-resend-key",
            MAIL_FROM="Bilim Al Team <sender@example.com>",
            APP_TITLE="Bilim Al",
            IS_RENDER=True,
            MAIL_USERNAME="test-smtp-user",
            MAIL_PASSWORD="test-smtp-password",
            MAIL_SERVER="smtp.example.com",
            MAIL_PORT=587,
        )
        settings_patch.start()
        self.addCleanup(settings_patch.stop)

        smtp_patch = patch("app.services.mail_service.aiosmtplib.send", new_callable=AsyncMock)
        self.smtp_send = smtp_patch.start()
        self.addCleanup(smtp_patch.stop)

    async def test_both_code_flows_use_emailjs_with_raw_template_values(self):
        username = 'Алия <student> & "friend" 👩‍🎓'
        recipient = "student@another-provider.example"
        messages = []
        flows = (
            (mail_service.send_verification_email, "Подтверждение email", "Подтверждение email"),
            (mail_service.send_reset_email, "Восстановление пароля", "Код восстановления пароля"),
        )
        for sender, title, subject_label in flows:
            with self.subTest(sender=sender.__name__):
                self.assertTrue(await sender(recipient, "123456", username))
                request = self.requests[-1]
                self.assertEqual(request.method, "POST")
                self.assertEqual(str(request.url), "https://api.emailjs.com/api/v1.0/email/send")
                payload = json.loads(request.content)
                self.assertEqual(set(payload), {"service_id", "template_id", "user_id", "template_params"})
                self.assertEqual(payload["service_id"], "test-service-id")
                self.assertEqual(payload["template_id"], "test-template-id")
                self.assertEqual(payload["user_id"], "test-public-key")
                params = payload["template_params"]
                self.assertEqual(
                    set(params),
                    {"to_email", "subject", "username", "code", "title", "message", "expires_minutes"},
                )
                self.assertEqual(params["to_email"], recipient)
                self.assertEqual(params["subject"], f"Bilim Al — {subject_label}: 123456")
                self.assertEqual(params["username"], username)
                self.assertEqual(params["code"], "123456")
                self.assertEqual(params["title"], title)
                self.assertEqual(params["expires_minutes"], 15)
                self.assertIsInstance(params["message"], str)
                self.assertTrue(params["message"].strip())
                messages.append(params["message"])

        self.assertNotEqual(messages[0], messages[1])
        # Brevo, Resend, and SMTP are configured: EmailJS must take precedence.
        self.assertEqual(len(self.requests), 2)
        self.smtp_send.assert_not_awaited()

    async def test_optional_private_key_uses_emailjs_access_token_field(self):
        with patch.object(settings, "EMAILJS_PRIVATE_KEY", "test-private-key"):
            self.assertTrue(await mail_service.send_reset_email("student@example.org", "654321", "Student"))

        payload = json.loads(self.requests[0].content)
        self.assertEqual(payload["accessToken"], "test-private-key")
        self.assertNotIn("access_token", payload)
        self.assertNotIn("EMAILJS_PRIVATE_KEY", payload)
        self.smtp_send.assert_not_awaited()

    async def test_partial_configuration_names_missing_fields_before_network(self):
        fields = ("EMAILJS_SERVICE_ID", "EMAILJS_TEMPLATE_ID", "EMAILJS_PUBLIC_KEY")
        cases = [{field: f"sensitive-{field}"} for field in (*fields, "EMAILJS_PRIVATE_KEY")]
        cases.extend(
            {field: f"sensitive-{field}" for field in fields if field != missing}
            for missing in fields
        )
        message = MIMEMultipart("alternative")
        message["From"] = "sender@example.com"
        message["To"] = "student@example.org"
        message["Subject"] = "Code 123456"
        message.attach(MIMEText("<p>123456</p>", "html", "utf-8"))

        for configured in cases:
            with self.subTest(configured_fields=tuple(configured)):
                values = dict.fromkeys((*fields, "EMAILJS_PRIVATE_KEY"), "")
                values.update(configured)
                missing = set(fields) - set(configured)
                with patch.multiple(settings, **values):
                    with self.assertRaises(mail_service.EmailConfigurationError) as raised:
                        await mail_service.deliver_email(
                            message, code="123456", username="Student", purpose="verification"
                        )
                self.assertIsInstance(raised.exception, RuntimeError)
                error = str(raised.exception)
                for field in missing:
                    self.assertIn(field, error)
                for value in configured.values():
                    self.assertNotIn(value, error)

        self.client_factory.assert_not_called()
        self.assertEqual(self.requests, [])
        self.smtp_send.assert_not_awaited()

    async def test_partial_configuration_returns_false_without_fallback(self):
        with patch.object(settings, "EMAILJS_TEMPLATE_ID", ""):
            with self.assertLogs(mail_service.__name__, level="ERROR") as logs:
                self.assertFalse(await mail_service.send_verification_email("student@example.org", "123456", "Student"))
                self.assertFalse(await mail_service.send_reset_email("student@example.org", "123456", "Student"))

        logged = "\n".join(logs.output)
        self.assertIn("EMAILJS_TEMPLATE_ID", logged)
        for secret in ("test-service-id", "test-public-key", "test-brevo-key", "test-resend-key", "123456"):
            self.assertNotIn(secret, logged)
        self.client_factory.assert_not_called()
        self.assertEqual(self.requests, [])
        self.smtp_send.assert_not_awaited()

    async def test_http_errors_return_false_without_fallback_or_sensitive_logs(self):
        secrets = (
            "test-service-id", "test-template-id", "test-public-key", "test-private-key",
            "test-brevo-key", "test-resend-key", "test-smtp-password", "123456",
        )
        self.response_text = "provider-sensitive-response " + " ".join(secrets)
        with patch.object(settings, "EMAILJS_PRIVATE_KEY", "test-private-key"):
            for status in (403, 429):
                self.response_status = status
                for sender in (mail_service.send_verification_email, mail_service.send_reset_email):
                    with self.subTest(status=status, sender=sender.__name__):
                        before = len(self.requests)
                        with self.assertLogs(mail_service.__name__, level="ERROR") as logs:
                            self.assertFalse(await sender("student@example.org", "123456", "Student"))
                        self.assertEqual(len(self.requests), before + 1)
                        logged = "\n".join(logs.output)
                        self.assertIn("api.emailjs.com", logged)
                        self.assertIn(str(status), logged)
                        self.assertNotIn("provider-sensitive-response", logged)
                        for secret in secrets:
                            self.assertNotIn(secret, logged)

        self.assertEqual(len(self.requests), 4)
        self.assertTrue(all(request.url.host == "api.emailjs.com" for request in self.requests))
        self.smtp_send.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
