import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Post


def serialize(post):
    return {"id": post.id, "author": post.author, "handle": post.handle, "text": post.text, "image": post.image, "likes": post.likes, "created_at": post.created_at.isoformat()}

@require_http_methods(["GET", "POST"])
def posts(request):
    if request.method == "GET":
        return JsonResponse({"posts": [serialize(p) for p in Post.objects.all()[:100]]})
    try:
        data = json.loads(request.body)
        text = data.get("text", "").strip()
        if not text or len(text) > 2000:
            return JsonResponse({"error": "Write between 1 and 2000 characters."}, status=400)
    except (ValueError, AttributeError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse(serialize(Post.objects.create(text=text)), status=201)

@require_http_methods(["GET"])
def csrf(request):
    from django.middleware.csrf import get_token
    return JsonResponse({"token": get_token(request)})
