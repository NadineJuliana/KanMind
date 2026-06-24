from django.db import models
from boards_app.models import Board
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class Task(models.Model):
    """
    Represents a task that belongs to a board.
    """
        
    STATUS_CHOICES = [
        ("to-do", "To Do"),
        ("in-progress", "In Progress"),
        ("review", "Review"),
        ("done", "Done"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="to-do",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
    )

    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        null=True,
        blank=True,
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="review_tasks",
        null=True,
        blank=True,
    )

    due_date = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_tasks",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title
    

class Comment(models.Model):
    """
    Represents a user comment on a task.
    """

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"{self.author} - {self.task}"