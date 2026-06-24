from django.contrib import admin
from .models import Board

# Register your models here.

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "owner", "created_at"]
    search_fields = ["title", "owner__email", "owner__first_name"]
    list_filter = ["created_at"]
    filter_horizontal = ["members"]