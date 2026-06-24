from django.contrib import admin
from .models import Task

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