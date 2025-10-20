from django.db import models

from environments.models import Environment
from projects.models import Project


HTTP_METHODS = (
    ("GET", "GET"),
    ("POST", "POST"),
    ("PUT", "PUT"),
    ("PATCH", "PATCH"),
    ("DELETE", "DELETE"),
    ("HEAD", "HEAD"),
    ("OPTIONS", "OPTIONS"),
)


class APIInterface(models.Model):
    project = models.ForeignKey(
        Project,
        related_name="interfaces",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=160)
    method = models.CharField(max_length=10, choices=HTTP_METHODS, default="GET")
    path = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    request_params = models.JSONField(default=dict, blank=True)
    request_body = models.JSONField(default=dict, blank=True)
    headers = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("project", "method", "path")
        ordering = ["project__name", "name"]

    def __str__(self) -> str:  # pragma: no cover - debugging helper
        return f"{self.project.name} {self.method} {self.path}"


class InterfaceCase(models.Model):
    interface = models.ForeignKey(
        APIInterface,
        related_name="cases",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    environment = models.ForeignKey(
        Environment,
        null=True,
        blank=True,
        related_name="interface_cases",
        on_delete=models.SET_NULL,
    )
    request_payload = models.JSONField(default=dict, blank=True)
    assertions = models.JSONField(default=list, blank=True)
    extractions = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["interface__project__name", "name"]

    def __str__(self) -> str:  # pragma: no cover - debugging helper
        return f"{self.interface.name}::{self.name}"


class Scenario(models.Model):
    project = models.ForeignKey(
        Project,
        related_name="scenarios",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("project", "name")
        ordering = ["project__name", "name"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.project.name}::{self.name}"


class ScenarioStep(models.Model):
    scenario = models.ForeignKey(
        Scenario,
        related_name="steps",
        on_delete=models.CASCADE,
    )
    interface_case = models.ForeignKey(
        InterfaceCase,
        related_name="scenario_steps",
        on_delete=models.CASCADE,
    )
    order = models.PositiveIntegerField(default=1)
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["scenario", "order"]
        unique_together = ("scenario", "order")

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.scenario}::{self.order}"


class TestSuite(models.Model):
    project = models.ForeignKey(
        Project,
        related_name="test_suites",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    cases = models.ManyToManyField(InterfaceCase, related_name="test_suites", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("project", "name")
        ordering = ["project__name", "name"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.project.name}::{self.name}"


class TestReport(models.Model):
    STATUS_CHOICES = (
        ("success", "Success"),
        ("failed", "Failed"),
        ("running", "Running"),
    )

    suite = models.ForeignKey(
        TestSuite,
        related_name="reports",
        on_delete=models.CASCADE,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="running")
    summary = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.suite}::{self.created_at:%Y-%m-%d %H:%M}"
