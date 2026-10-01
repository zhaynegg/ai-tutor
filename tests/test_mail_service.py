import json
import unittest
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from unittest.mock import AsyncMock, patch

import httpx

from app.config import settings
from app.services import mail_service


class MailServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.requests = []
        self.response_status = 201

        def handle_request(request):
            self.requests.append(request)
            return httpx.Response(self.response_status, json={"messageId": "test-message"})

        transport = httpx.MockTransport(handle_request)
        async_client = httpx.AsyncClient
        client_patch = patch(
            "app.services.mail_service.httpx.AsyncClient",
            side_effect=lambda **kwargs: async_client(transport=transport, **kwargs),
        )
        client_patch.start()
        self.addCleanup(client_patch.stop)

        settings_patch = patch.multiple(
            settings,
            EMAILJS_SERVICE_ID="",
            EMAILJS_TEMPLATE_ID="",
            EMAILJS_PUBLIC_KEY="",
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

    async def test_brevo_delivers_both_code_emails_to_any_recipient(self):
        username = 'Алия <student> & "friend"'
        for sender in (mail_service.send_verification_email, mail_service.send_reset_email):
            with self.subTest(sender=sender.__name__):
                result = await sender("student@another-provider.example", "123456", username)
                self.assertTrue(result)

                request = self.requests[-1]
                self.assertEqual(str(request.url), "https://api.brevo.com/v3/smtp/email")
                self.assertEqual(request.method, "POST")
                self.assertEqual(request.headers["api-key"], "test-brevo-key")
                payload = json.loads(request.content)
                self.assertEqual(payload["sender"], {"email": "sender@example.com", "name": "Bilim Al Team"})
                self.assertEqual(payload["to"], [{"email": "student@another-provider.example"}])
                self.assertIn("123456", payload["subject"])
                self.assertIn("123456", payload["htmlContent"])
                self.assertIn("Алия &lt;student&gt; &amp; &quot;friend&quot;", payload["htmlContent"])
                self.assertNotIn(username, payload["htmlContent"])

        # Resend is also configured: every captured request must still use Brevo.
        self.assertEqual(len(self.requests), 2)
        self.smtp_send.assert_not_awaited()

    async def test_brevo_uses_app_title_for_a_sender_without_display_name(self):
        with patch.object(settings, "MAIL_FROM", "sender@example.com"):
            self.assertTrue(await mail_service.send_verification_email("student@example.org", "654321", "Student"))
        payload = json.loads(self.requests[0].content)
        self.assertEqual(payload["sender"], {"email": "sender@example.com", "name": "Bilim Al"})

    async def test_brevo_http_error_returns_false_without_another_transport(self):
        self.response_status = 400
        for sender in (mail_service.send_verification_email, mail_service.send_reset_email):
            with self.subTest(sender=sender.__name__):
                self.assertFalse(await sender("student@example.org", "123456", "Student"))

        self.assertEqual(len(self.requests), 2)
        self.assertTrue(all(request.url.host == "api.brevo.com" for request in self.requests))
        self.smtp_send.assert_not_awaited()

    async def test_resend_still_delivers_when_brevo_is_not_configured(self):
        with patch.object(settings, "BREVO_API_KEY", ""):
            self.assertTrue(await mail_service.send_verification_email("student@example.org", "123456", "<Student>"))

        self.assertEqual(len(self.requests), 1)
        request = self.requests[0]
        self.assertEqual(str(request.url), "https://api.resend.com/emails")
        self.assertEqual(request.headers["Authorization"], "Bearer test-resend-key")
        payload = json.loads(request.content)
        self.assertEqual(payload["from"], "Bilim Al Team <sender@example.com>")
        self.assertEqual(payload["to"], ["student@example.org"])
        self.assertIn("&lt;Student&gt;", payload["html"])
        self.smtp_send.assert_not_awaited()

    async def test_local_smtp_still_delivers_when_neither_api_is_configured(self):
        with patch.multiple(settings, BREVO_API_KEY="", RESEND_API_KEY="", IS_RENDER=False):
            self.assertTrue(await mail_service.send_reset_email("student@example.org", "123456", "Алия"))

        self.assertEqual(self.requests, [])
        self.smtp_send.assert_awaited_once()
        args, kwargs = self.smtp_send.call_args
        self.assertEqual(args[0]["To"], "student@example.org")
        self.assertIn("Алия", args[0].get_payload()[0].get_payload(decode=True).decode("utf-8"))
        self.assertEqual(kwargs["hostname"], "smtp.example.com")
        self.assertEqual(kwargs["port"], 587)
        self.assertTrue(kwargs["start_tls"])

    async def test_render_without_an_api_key_rejects_smtp(self):
        message = MIMEMultipart("alternative")
        message.attach(MIMEText("<p>123456</p>", "html"))
        with patch.multiple(settings, BREVO_API_KEY="", RESEND_API_KEY=""):
            with self.assertRaisesRegex(RuntimeError, "(?i)brevo.*resend|resend.*brevo"):
                await mail_service.deliver_email(message)
        self.assertEqual(self.requests, [])
        self.smtp_send.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
