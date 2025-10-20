from rest_framework import serializers

from .models import (
    APIInterface,
    InterfaceCase,
    Scenario,
    ScenarioStep,
    TestReport,
    TestSuite,
)


class InterfaceSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = APIInterface
        fields = [
            "id",
            "project",
            "project_name",
            "name",
            "method",
            "path",
            "description",
            "request_params",
            "request_body",
            "headers",
            "created_at",
            "updated_at",
        ]


class InterfaceCaseSerializer(serializers.ModelSerializer):
    interface_name = serializers.CharField(source="interface.name", read_only=True)
    project = serializers.PrimaryKeyRelatedField(source="interface.project", read_only=True)
    environment_name = serializers.CharField(source="environment.name", read_only=True)

    class Meta:
        model = InterfaceCase
        fields = [
            "id",
            "interface",
            "interface_name",
            "project",
            "name",
            "description",
            "environment",
            "environment_name",
            "request_payload",
            "assertions",
            "extractions",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ScenarioStepSerializer(serializers.ModelSerializer):
    interface_case_detail = InterfaceCaseSerializer(source="interface_case", read_only=True)
    interface_case = serializers.PrimaryKeyRelatedField(queryset=InterfaceCase.objects.all())

    class Meta:
        model = ScenarioStep
        fields = ["id", "scenario", "interface_case", "interface_case_detail", "order", "config"]
        read_only_fields = ["interface_case_detail"]


class ScenarioSerializer(serializers.ModelSerializer):
    steps = ScenarioStepSerializer(many=True, required=False)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = Scenario
        fields = [
            "id",
            "project",
            "project_name",
            "name",
            "description",
            "steps",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        steps_data = validated_data.pop("steps", [])
        scenario = super().create(validated_data)
        self._sync_steps(scenario, steps_data)
        return scenario

    def update(self, instance, validated_data):
        steps_data = validated_data.pop("steps", None)
        scenario = super().update(instance, validated_data)
        if steps_data is not None:
            scenario.steps.all().delete()
            self._sync_steps(scenario, steps_data)
        return scenario

    def _sync_steps(self, scenario, steps_data):
        for index, step in enumerate(steps_data, start=1):
            ScenarioStep.objects.create(
                scenario=scenario,
                interface_case=step["interface_case"],
                order=step.get("order") or index,
                config=step.get("config", {}),
            )


class TestSuiteSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    case_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=InterfaceCase.objects.all(),
        required=False,
        source="cases",
    )
    case_count = serializers.SerializerMethodField()

    class Meta:
        model = TestSuite
        fields = [
            "id",
            "project",
            "project_name",
            "name",
            "description",
            "case_ids",
            "case_count",
            "created_at",
            "updated_at",
        ]

    def get_case_count(self, obj):
        return obj.cases.count()

    def create(self, validated_data):
        cases = validated_data.pop("cases", [])
        suite = super().create(validated_data)
        if cases:
            suite.cases.set(cases)
        return suite

    def update(self, instance, validated_data):
        cases = validated_data.pop("cases", None)
        suite = super().update(instance, validated_data)
        if cases is not None:
            suite.cases.set(cases)
        return suite


class TestReportSerializer(serializers.ModelSerializer):
    suite_name = serializers.CharField(source="suite.name", read_only=True)
    project = serializers.PrimaryKeyRelatedField(source="suite.project", read_only=True)

    class Meta:
        model = TestReport
        fields = [
            "id",
            "suite",
            "suite_name",
            "project",
            "status",
            "summary",
            "details",
            "created_at",
        ]
        read_only_fields = ["status", "summary", "details", "created_at"]
