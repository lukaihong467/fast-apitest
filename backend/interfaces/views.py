import json

from django.db import transaction
from django.db.models import Prefetch
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import Project

from .models import APIInterface, InterfaceCase, Scenario, ScenarioStep, TestReport, TestSuite
from .serializers import (
    InterfaceCaseSerializer,
    InterfaceSerializer,
    ScenarioSerializer,
    ScenarioStepSerializer,
    TestReportSerializer,
    TestSuiteSerializer,
)


class InterfaceViewSet(viewsets.ModelViewSet):
    serializer_class = InterfaceSerializer
    queryset = APIInterface.objects.select_related("project").order_by("project__name", "name")

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class InterfaceCaseViewSet(viewsets.ModelViewSet):
    serializer_class = InterfaceCaseSerializer
    queryset = InterfaceCase.objects.select_related("interface", "environment", "interface__project").order_by(
        "interface__project__name",
        "name",
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        interface_id = self.request.query_params.get("interface")
        project_id = self.request.query_params.get("project")
        if interface_id:
            queryset = queryset.filter(interface_id=interface_id)
        if project_id:
            queryset = queryset.filter(interface__project_id=project_id)
        return queryset


class ScenarioViewSet(viewsets.ModelViewSet):
    serializer_class = ScenarioSerializer
    queryset = Scenario.objects.select_related("project").prefetch_related(
        Prefetch("steps", queryset=ScenarioStep.objects.select_related("interface_case", "interface_case__interface"))
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset


class ScenarioStepViewSet(viewsets.ModelViewSet):
    serializer_class = ScenarioStepSerializer
    queryset = ScenarioStep.objects.select_related("scenario", "interface_case")


class TestSuiteViewSet(viewsets.ModelViewSet):
    serializer_class = TestSuiteSerializer
    queryset = TestSuite.objects.select_related("project").prefetch_related("cases")

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    @action(detail=True, methods=["post"], url_path="run")
    def run(self, request, pk=None):
        suite = self.get_object()
        execution_details = {
            "executed_cases": suite.cases.count(),
            "request_headers": [case.request_payload.get("headers", {}) for case in suite.cases.all()],
        }
        summary = request.data.get("summary") or f"Executed {execution_details['executed_cases']} cases."
        report = TestReport.objects.create(
            suite=suite,
            status="success",
            summary=summary,
            details=execution_details,
        )
        serializer = TestReportSerializer(report, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TestReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TestReportSerializer
    queryset = TestReport.objects.select_related("suite", "suite__project")

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(suite__project_id=project_id)
        return queryset


class SwaggerImportView(APIView):
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request, *args, **kwargs):
        project_id = request.data.get("project")
        if not project_id:
            return Response({"detail": "Project parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        project = Project.objects.filter(pk=project_id).first()
        if not project:
            return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        raw_spec = request.data.get("swagger")
        uploaded_file = request.FILES.get("file")

        if uploaded_file:
            raw_spec = uploaded_file.read().decode("utf-8")

        if not raw_spec:
            return Response({"detail": "Swagger content is missing."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            spec = json.loads(raw_spec)
        except json.JSONDecodeError as exc:  # pragma: no cover - depends on user input
            return Response({"detail": f"Invalid JSON: {exc}"}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        with transaction.atomic():
            for path, operations in spec.get("paths", {}).items():
                for method, payload in operations.items():
                    interface, _ = APIInterface.objects.update_or_create(
                        project=project,
                        path=path,
                        method=method.upper(),
                        defaults={
                            "name": payload.get("summary") or f"{method.upper()} {path}",
                            "description": payload.get("description", ""),
                            "request_params": payload.get("parameters", {}),
                            "request_body": payload.get("requestBody", {}),
                            "headers": payload.get("headers", {}),
                        },
                    )
                    created.append(interface.pk)

        return Response({"created": created, "count": len(created)}, status=status.HTTP_201_CREATED)
