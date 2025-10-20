from django.db import models

from projects.models import Project


class Environment(models.Model):
    project = models.ForeignKey(
        Project,
        related_name="environments",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=120)
    base_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    variables = models.JSONField(default=dict, blank=True)
    headers = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("project", "name")
        ordering = ["project__name", "name"]

    def __str__(self) -> str:  # pragma: no cover - debug helper
        return f"{self.project.name}::{self.name}"
