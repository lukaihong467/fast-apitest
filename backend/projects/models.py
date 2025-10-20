from django.db import models


class Project(models.Model):
    """High level container for API testing assets."""

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    owner = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - human readable representation
        return self.name
