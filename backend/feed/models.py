from django.db import models

class Post(models.Model):
    author = models.CharField(max_length=80, default="Alex Morgan")
    handle = models.CharField(max_length=40, default="alexmorgan")
    text = models.TextField(max_length=2000)
    image = models.URLField(blank=True)
    likes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
