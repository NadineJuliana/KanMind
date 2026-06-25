from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# Create your models here.


class Board(models.Model):
    """
    Represents a project board that contains tasks and members.
    """

    title = models.CharField(max_length=255)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_boards",
    )

    members = models.ManyToManyField(
        User,
        related_name="boards",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Board"
        verbose_name_plural = "Boards"

    def __str__(self):
        return self.title
