from django.contrib import admin

from .models import APIInterface, InterfaceCase, Scenario, ScenarioStep, TestReport, TestSuite


@admin.register(APIInterface)
class APIInterfaceAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "method", "path", "updated_at")
    list_filter = ("project", "method")
    search_fields = ("name", "path", "project__name")


@admin.register(InterfaceCase)
class InterfaceCaseAdmin(admin.ModelAdmin):
    list_display = ("name", "interface", "environment", "is_active", "updated_at")
    list_filter = ("interface__project", "environment", "is_active")
    search_fields = ("name", "interface__name", "interface__project__name")


class ScenarioStepInline(admin.TabularInline):
    model = ScenarioStep
    extra = 0


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "updated_at")
    list_filter = ("project",)
    search_fields = ("name", "project__name")
    inlines = [ScenarioStepInline]


@admin.register(TestSuite)
class TestSuiteAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "created_at", "updated_at")
    filter_horizontal = ("cases",)
    search_fields = ("name", "project__name")


@admin.register(TestReport)
class TestReportAdmin(admin.ModelAdmin):
    list_display = ("suite", "status", "created_at")
    list_filter = ("status", "suite__project")
    search_fields = ("suite__name", "suite__project__name")
