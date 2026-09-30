import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch, Mock

_test_dir = tempfile.TemporaryDirectory()
os.environ['DATABASE_URL'] = f"sqlite:///{Path(_test_dir.name) / 'test.db'}"
os.environ['GROQ_API_KEY'] = ''
os.environ['SECRET_KEY'] = 'test-only-secret-key-which-is-long-enough'
os.environ['ENABLE_CODE_EXECUTION'] = 'false'
from fastapi.testclient import TestClient
from main import app
from app.database import SessionLocal
from app.models.db_models import User, EmailVerification, PasswordResetCode, Course
from app.services.auth_service import verify_password
from app.services.code_runner import code_runner
from app.services.ai_service import ai_service
from app.services.mail_service import send_verification_email
from app.config import settings

class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    def test_pages_and_health(self):
        for url in ['/health', '/login', '/register', '/forgot-password', '/courses', '/coding', '/verify-email']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
    def test_registration_verification_login_and_reset(self):
        payload = dict(username='test_student', email='student@example.com', password='password123', full_name='Test')
        with patch('app.routers.auth.send_verification_email', new=AsyncMock(return_value=True)):
            response = self.client.post('/auth/register', json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        with SessionLocal() as db:
            user = db.query(User).filter_by(username=payload['username']).one()
            self.assertNotEqual(user.hashed_password, payload['password'])
            self.assertTrue(verify_password(payload['password'], user.hashed_password))
            code = db.query(EmailVerification).filter_by(user_id=user.id).one().code
        self.assertEqual(self.client.post('/auth/login', json=payload).status_code, 403)
        self.assertEqual(self.client.post('/auth/verify-email', params={'username':payload['username'], 'code':code}).status_code, 200)
        self.assertEqual(self.client.post('/auth/login', json=payload).status_code, 200)
        for url in ['/', '/dashboard', '/chat', '/quiz', '/admin/']:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        with SessionLocal() as db:
            course = db.query(Course).first()
            lesson_id = course.lessons[0].id
            course_id = course.id
        for url in [f'/courses/{course_id}', f'/courses/{course_id}/lessons/{lesson_id}']:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        with patch('app.routers.password.send_reset_email', new=AsyncMock(return_value=True)):
            self.assertEqual(self.client.post('/forgot-password/send-code',json={'email':payload['email']}).status_code,200)
        with SessionLocal() as db:
            code=db.query(PasswordResetCode).filter_by(user_id=user.id).one().code
        reset={'email':payload['email'],'code':code,'new_password':'newpassword123'}
        self.assertEqual(self.client.post('/forgot-password/reset',json=reset).status_code,200)
        self.assertEqual(self.client.post('/forgot-password/reset',json=reset).status_code,400)
        self.assertEqual(self.client.post('/auth/login',json=payload).status_code,401)
        payload['password']=reset['new_password']
        self.assertEqual(self.client.post('/auth/login',json=payload).status_code,200)
    def test_failed_email_allows_registration_retry(self):
        payload=dict(username='mail_failure',email='failure@example.com',password='password123')
        with patch('app.routers.auth.send_verification_email', new=AsyncMock(return_value=False)):
            self.assertEqual(self.client.post('/auth/register',json=payload).status_code,503)
        with SessionLocal() as db:
            self.assertIsNone(db.query(User).filter_by(username=payload['username']).first())
    def test_model_and_json_mode(self):
        client = Mock()
        client.chat.completions.create.return_value.choices = [Mock(message=Mock(content='{"score":100,"is_correct":true}'))]
        with patch.object(settings, 'GROQ_API_KEY', 'test-key'), patch.object(settings, 'GROQ_MODEL', 'openai/gpt-oss-120b'), patch.object(ai_service, '_client', client):
            result = ai_service.check_code('Print 1', 'print(1)')
        self.assertEqual(result['score'], 100)
        options = client.chat.completions.create.call_args.kwargs
        self.assertEqual(options['model'], 'openai/gpt-oss-120b')
        self.assertEqual(options['response_format'], {'type':'json_object'})

    def test_unavailable_model_returns_503(self):
        from groq import NotFoundError
        import httpx
        from app.services.auth_service import create_token, hash_password
        with SessionLocal() as db:
            user = User(username='model_error', email='modelerror@example.com', hashed_password=hash_password('password123'), is_verified=True)
            db.add(user)
            db.commit()
            course = db.query(Course).first()
            payload = {'course_id':course.id, 'lesson_id':course.lessons[0].id, 'code':'print(1)'}
        self.client.cookies.set('access_token', create_token('model_error'))
        client = Mock()
        response = httpx.Response(404, request=httpx.Request('POST','https://api.groq.com/openai/v1/chat/completions'))
        client.chat.completions.create.side_effect = NotFoundError('model unavailable', response=response, body={'error':{'code':'model_not_found'}})
        with patch.object(settings, 'GROQ_API_KEY', 'test-key'), patch.object(ai_service, '_client', client):
            result = self.client.post('/courses/check_lesson', json=payload)
            self.assertEqual(result.status_code,503)
            self.assertIn('GROQ_MODEL',result.json()['detail'])
            result = self.client.post('/chat/send',json={'message':'hello'})
            self.assertEqual(result.status_code,503)

    def test_no_key_does_not_break_startup(self):
        with self.assertRaisesRegex(RuntimeError,'GROQ_API_KEY'):
            _=ai_service.client
    def test_ai_endpoints_require_login(self):
        requests = {
            '/chat/send': {'message':'hello'},
            '/tasks/generate_task': {'topic':'Python','difficulty':'beginner'},
            '/checker/check_code': {'task_description':'Print 1','student_code':'print(1)'},
            '/explainer/explain_error': {'code':'x','error_message':'NameError'},
            '/courses/check_lesson': {'lesson_id':1,'course_id':1,'code':'print(1)'},
        }
        for url, payload in requests.items():
            with self.subTest(url=url):
                self.assertEqual(self.client.post(url,json=payload).status_code,401)

    def test_public_code_execution_disabled(self):
        self.assertFalse(code_runner.run('raise RuntimeError("should never execute")')[0])
    def test_resend_payload(self):
        response=AsyncMock()
        response.raise_for_status=lambda:None
        transport=AsyncMock()
        transport.post.return_value=response
        with patch.object(settings,'RESEND_API_KEY','test-key'), patch.object(settings,'MAIL_FROM','noreply@example.com'), patch('app.services.mail_service.httpx.AsyncClient') as client:
            client.return_value.__aenter__.return_value=transport
            self.assertTrue(asyncio.run(send_verification_email('student@example.com','123456','<name>')))
        args=transport.post.call_args
        self.assertEqual(args.args[0],'https://api.resend.com/emails')
        self.assertIn('123456',args.kwargs['json']['html'])
        self.assertIn('&lt;name&gt;',args.kwargs['json']['html'])

if __name__=='__main__': unittest.main()
