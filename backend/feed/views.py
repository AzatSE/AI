import json

from django.conf import settings
from django.core.exceptions import RequestDataTooBig
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .models import Post


def serialize(post):
    return {"id": post.id, "author": post.author, "handle": post.handle, "text": post.text,
            "image": post.image, "likes": post.likes, "created_at": post.created_at.isoformat()}


@require_http_methods(["GET", "POST"])
def posts(request):
    if request.method == "GET":
        return JsonResponse({"posts": [serialize(p) for p in Post.objects.all()[:100]]})
    # CSRF alone is not authorization. Production writes require a session.
    demo_allowed = settings.DEBUG and settings.ALLOW_DEMO_POSTS
    if not request.user.is_authenticated and not demo_allowed:
        return JsonResponse({"error": "Sign in before publishing. Anonymous publishing is disabled."}, status=401)
    if request.content_type != "application/json":
        return JsonResponse({"error": "Content-Type must be application/json"}, status=415)
    try:
        data = json.loads(request.body)
    except RequestDataTooBig:
        return JsonResponse({"error": "Request body is too large"}, status=413)
    except (ValueError, RecursionError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get("text"), str):
        return JsonResponse({"error": "text must be a string"}, status=400)
    text = data["text"].strip()
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return JsonResponse({"error": "text must contain valid Unicode"}, status=400)
    if not text or len(text) > 2000:
        return JsonResponse({"error": "Write between 1 and 2000 characters."}, status=400)
    author = {}
    if request.user.is_authenticated:
        author = {
            "author": (request.user.get_full_name() or request.user.get_username())[:80],
            "handle": request.user.get_username()[:40],
        }
    return JsonResponse(serialize(Post.objects.create(text=text, **author)), status=201)


@never_cache
@require_http_methods(["GET"])
def csrf(request):
    from django.middleware.csrf import get_token
    return JsonResponse({"token": get_token(request)})
