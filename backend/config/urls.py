from django.contrib import admin
from django.urls import path
from feed import views

urlpatterns = [path("admin/", admin.site.urls), path("api/posts/", views.posts), path("api/csrf/", views.csrf)]
