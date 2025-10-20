from rest_framework import viewsets

from .models import Environment
from .serializers import EnvironmentSerializer


class EnvironmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnvironmentSerializer
    queryset = Environment.objects.select_related("project").order_by("project__name", "name")

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def perform_create(self, serializer):
        environment = serializer.save()
        if environment.is_default:
            Environment.objects.filter(project=environment.project).exclude(pk=environment.pk).update(is_default=False)

    def perform_update(self, serializer):
        environment = serializer.save()
        if environment.is_default:
            Environment.objects.filter(project=environment.project).exclude(pk=environment.pk).update(is_default=False)

    def destroy(self, request, *args, **kwargs):
        environment = self.get_object()
        replacement = None
        if environment.is_default:
            replacement = (
                Environment.objects.filter(project=environment.project)
                .exclude(pk=environment.pk)
                .order_by("created_at")
                .first()
            )
        response = super().destroy(request, *args, **kwargs)
        if replacement and not Environment.objects.filter(project=environment.project, is_default=True).exists():
            replacement.is_default = True
            replacement.save(update_fields=["is_default"])
        return response
