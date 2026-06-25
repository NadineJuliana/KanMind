from django.contrib import admin
from .models import Task, Comment

# Register your models here.


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "board",
        "status",
        "priority",
        "assignee",
        "reviewer",
        "created_by",
        "due_date",
    )

    list_filter = (
        "status",
        "priority",
        "board",
    )

    search_fields = (
        "title",
        "description",
        "board__title",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task",
        "author",
        "created_at",
    )

    search_fields = (
        "content",
        "task__title",
        "author__email",
    )

    list_filter = ("created_at",)
