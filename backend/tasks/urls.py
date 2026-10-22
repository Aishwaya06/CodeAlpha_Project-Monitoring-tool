from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CommentViewSet, dashboard
router = DefaultRouter(); router.register("tasks", TaskViewSet, basename="task"); router.register("comments", CommentViewSet, basename="comment")
urlpatterns = [path("dashboard/", dashboard)] + router.urls
