import json
from django.test import Client, TestCase
from django.core.management import call_command
from .models import Post

class FeedTests(TestCase):
    def test_post_persists_and_appears_in_feed(self):
        response = self.client.post('/api/posts/', json.dumps({'text': 'Hello cosmos ✨'}), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.client.get('/api/posts/').json()['posts'][0]['text'], 'Hello cosmos ✨')
        self.assertEqual(Post.objects.count(), 1)

    def test_invalid_posts_are_rejected(self):
        for body in ['{', 'null', '[]', '{"text":" "}', json.dumps({'text': 'x' * 2001})]:
            self.assertEqual(self.client.post('/api/posts/', body, content_type='application/json').status_code, 400)
        self.assertFalse(Post.objects.exists())

    def test_csrf_required_and_token_works(self):
        client = Client(enforce_csrf_checks=True)
        body = json.dumps({'text': 'Protected post'})
        self.assertEqual(client.post('/api/posts/', body, content_type='application/json').status_code, 403)
        token = client.get('/api/csrf/').json()['token']
        self.assertEqual(client.post('/api/posts/', body, content_type='application/json', HTTP_X_CSRFTOKEN=token).status_code, 201)

    def test_seed_is_repeatable(self):
        call_command('seed_demo')
        call_command('seed_demo')
        self.assertEqual(Post.objects.count(), 4)
