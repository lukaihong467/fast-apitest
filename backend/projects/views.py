from django.db.models import Count
from rest_framework import viewsets

from environments.models import Environment
from interfaces.models import APIInterface, InterfaceCase

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("name")
    serializer_class = ProjectSerializer

    def get_queryset(self):  # pragma: no cover - relies on ORM aggregation
        queryset = super().get_queryset()
        return queryset.annotate(
            environment_count=Count("environments", distinct=True),
            interface_count=Count("interfaces", distinct=True),
            case_count=Count("interfaces__cases", distinct=True),
        )

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        data = response.data
        if isinstance(data, list):
            items = data
        else:
            items = data.get("results", [])
        project_ids = [project["id"] for project in items]
        counts = {
            project_id: {
                "environments": Environment.objects.filter(project_id=project_id).count(),
                "interfaces": APIInterface.objects.filter(project_id=project_id).count(),
                "cases": InterfaceCase.objects.filter(interface__project_id=project_id).count(),
            }
            for project_id in project_ids
        }
        for item in items:
            item.update(counts.get(item["id"], {}))
        return response
