"""
URL routes for task and comment endpoints.
"""

from django.urls import path

from .views import (
    AssignedToMeTaskListView,
    ReviewingTaskListView,
    TaskCreateView,
    TaskDetailView,
    CommentDeleteView,
    CommentListCreateView,
)

urlpatterns = [
    path(
        "tasks/assigned-to-me/",
        AssignedToMeTaskListView.as_view(),
        name="assigned-tasks",
    ),
    path(
        "tasks/reviewing/",
        ReviewingTaskListView.as_view(),
        name="reviewing-tasks",
    ),
    path("tasks/", TaskCreateView.as_view(), name="task-create"),
    path(
        "tasks/<int:task_id>/",
        TaskDetailView.as_view(),
        name="task-detail",
    ),
    path(
    "tasks/<int:task_id>/comments/",
    CommentListCreateView.as_view(),
    name="task-comments",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        CommentDeleteView.as_view(),
        name="task-comment-delete",
    ),
]