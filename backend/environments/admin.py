from django.contrib import admin

from .models import Environment


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "project",
        "base_url",
        "is_default",
        "updated_at",
    )
    list_filter = ("project", "is_default")
    search_fields = ("name", "project__name")
