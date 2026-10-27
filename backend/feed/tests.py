import json
import os
import secrets
import subprocess
import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, SimpleTestCase, TestCase, override_settings

from .models import Post


class FeedTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="stargazer", first_name="Star", last_name="Gazer")
        self.client.force_login(self.user)

    def post(self, body, **kwargs):
        return self.client.post('/api/posts/', body, content_type='application/json', secure=True, **kwargs)

    def test_post_persists_and_cannot_spoof_author(self):
        response = self.post(json.dumps({'text': 'Hello cosmos ✨', 'author': 'NASA', 'handle': 'nasa', 'likes': 999}))
        self.assertEqual(response.status_code, 201)
        post = self.client.get('/api/posts/', secure=True).json()['posts'][0]
        self.assertEqual(post['text'], 'Hello cosmos ✨')
        self.assertEqual(post['author'], 'Star Gazer')
        self.assertEqual(post['handle'], 'stargazer')
        self.assertEqual(post['likes'], 0)
        self.assertEqual(Post.objects.count(), 1)

    def test_invalid_posts_are_rejected(self):
        bodies = ['{', 'null', '[]', '{"text":" "}', json.dumps({'text': 'x' * 2001})]
        bodies += [json.dumps({'text': value}) for value in [None, 1, True, [], {}]]
        for body in bodies:
            with self.subTest(body_type=type(body).__name__):
                self.assertEqual(self.post(body).status_code, 400)
        self.assertEqual(self.post(b'\xff').status_code, 400)
        self.assertEqual(self.post(json.dumps({'text': '\ud800'})).status_code, 400)
        self.assertEqual(self.post('[' * 1500 + '0' + ']' * 1500).status_code, 400)
        self.assertFalse(Post.objects.exists())

    def test_oversized_and_wrong_content_type_rejected(self):
        self.assertEqual(self.post(json.dumps({'text': 'x' * 17000})).status_code, 413)
        response = self.client.post('/api/posts/', 'text=Hello', content_type='text/plain', secure=True)
        self.assertEqual(response.status_code, 415)
        self.assertFalse(Post.objects.exists())

    @override_settings(DEBUG=False, ALLOW_DEMO_POSTS=False)
    def test_anonymous_can_read_but_not_publish(self):
        client = Client()
        self.assertEqual(client.get('/api/posts/', secure=True).status_code, 200)
        self.assertEqual(client.post('/api/posts/', json.dumps({'text': 'Spam'}), content_type='application/json', secure=True).status_code, 401)
        self.assertFalse(Post.objects.exists())

    @override_settings(DEBUG=False, ALLOW_DEMO_POSTS=True)
    def test_demo_flag_cannot_bypass_production_auth(self):
        self.assertEqual(Client().post('/api/posts/', '{}', content_type='application/json', secure=True).status_code, 401)

    @override_settings(DEBUG=True, ALLOW_DEMO_POSTS=True)
    def test_explicit_local_demo_still_works(self):
        response = Client().post('/api/posts/', json.dumps({'text': 'Local demo'}), content_type='application/json', secure=True)
        self.assertEqual(response.status_code, 201)

    def test_csrf_required_and_token_works_for_authenticated_user(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        body = json.dumps({'text': 'Protected post'})
        self.assertEqual(client.post('/api/posts/', body, content_type='application/json', secure=True).status_code, 403)
        token_response = client.get('/api/csrf/', secure=True)
        self.assertIn('no-store', token_response['Cache-Control'])
        token = token_response.json()['token']
        self.assertEqual(client.post('/api/posts/', body, content_type='application/json', HTTP_X_CSRFTOKEN=token, HTTP_ORIGIN='https://evil.example', secure=True).status_code, 403)
        self.assertEqual(client.post('/api/posts/', body, content_type='application/json', HTTP_X_CSRFTOKEN=token, HTTP_ORIGIN='https://testserver', secure=True).status_code, 201)

    def test_untrusted_origin_gets_no_cors_permission(self):
        response = self.client.get('/api/posts/', HTTP_ORIGIN='https://evil.example', secure=True)
        self.assertNotIn('Access-Control-Allow-Origin', response)

    def test_unsupported_methods_rejected(self):
        self.assertEqual(self.client.delete('/api/posts/', secure=True).status_code, 405)

    def test_seed_is_repeatable(self):
        call_command('seed_demo')
        call_command('seed_demo')
        self.assertEqual(Post.objects.count(), 4)


class ProductionSettingsTests(SimpleTestCase):
    def check_settings(self, **overrides):
        env = os.environ.copy()
        env.update({
            'DJANGO_SETTINGS_MODULE': 'config.settings',
            'DJANGO_DEBUG': 'false',
            'DJANGO_SECRET_KEY': secrets.token_urlsafe(64),
            'DJANGO_ALLOWED_HOSTS': 'cosmix.example.com',
            'DJANGO_ALLOW_DEMO_POSTS': 'false',
            'DJANGO_CORS_ALLOWED_ORIGINS': '',
            'DJANGO_CSRF_TRUSTED_ORIGINS': 'https://cosmix.example.com',
            'DJANGO_TRUST_PROXY_SSL_HEADER': 'false',
        })
        env.update(overrides)
        return subprocess.run([sys.executable, '-c', '''
import django
from django.conf import settings
from django.test import Client
django.setup()
assert not settings.DEBUG
assert settings.SECURE_SSL_REDIRECT
assert settings.SESSION_COOKIE_SECURE and settings.CSRF_COOKIE_SECURE
assert settings.SESSION_COOKIE_HTTPONLY
assert settings.SECURE_HSTS_SECONDS >= 31536000
assert not settings.CORS_ALLOWED_ORIGINS
assert settings.DATA_UPLOAD_MAX_MEMORY_SIZE == 16384
assert not hasattr(settings, 'SECURE_PROXY_SSL_HEADER') or settings.SECURE_PROXY_SSL_HEADER is None
client = Client()
assert client.get('/api/posts/', HTTP_HOST='cosmix.example.com').status_code == 301
assert client.get('/api/csrf/', HTTP_HOST='untrusted.example', secure=True).status_code == 400
response = client.get('/api/csrf/', HTTP_HOST='cosmix.example.com', secure=True)
assert response.status_code == 200
assert response.cookies['csrftoken']['secure']
assert response['X-Frame-Options'] == 'DENY'
assert response['X-Content-Type-Options'] == 'nosniff'
assert 'max-age=31536000' in response['Strict-Transport-Security']
'''], env=env, cwd=settings.BASE_DIR, capture_output=True, text=True, timeout=20)

    def test_secure_production_defaults_and_responses(self):
        result = self.check_settings()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_production_refuses_unsafe_configuration(self):
        for values in [
            {'DJANGO_SECRET_KEY': ''},
            {'DJANGO_SECRET_KEY': 'too-short'},
            {'DJANGO_SECRET_KEY': 'django-insecure-' + secrets.token_urlsafe(64)},
            {'DJANGO_ALLOWED_HOSTS': ''},
            {'DJANGO_ALLOWED_HOSTS': '*'},
            {'DJANGO_ALLOW_DEMO_POSTS': 'true'},
            {'DJANGO_CORS_ALLOWED_ORIGINS': 'https://*.example.com'},
            {'DJANGO_CSRF_TRUSTED_ORIGINS': 'http://cosmix.example.com'},
            {'DJANGO_DEBUG': 'yes'},
        ]:
            with self.subTest(variable=next(iter(values))):
                result = self.check_settings(**values)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('ImproperlyConfigured', result.stderr)
