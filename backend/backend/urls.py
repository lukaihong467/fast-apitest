"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from environments.views import EnvironmentViewSet
from interfaces.views import (
    InterfaceCaseViewSet,
    InterfaceViewSet,
    ScenarioStepViewSet,
    ScenarioViewSet,
    SwaggerImportView,
    TestReportViewSet,
    TestSuiteViewSet,
)
from projects.views import ProjectViewSet

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")
router.register("environments", EnvironmentViewSet, basename="environment")
router.register("interfaces", InterfaceViewSet, basename="interface")
router.register("interface-cases", InterfaceCaseViewSet, basename="interface-case")
router.register("scenarios", ScenarioViewSet, basename="scenario")
router.register("scenario-steps", ScenarioStepViewSet, basename="scenario-step")
router.register("test-suites", TestSuiteViewSet, basename="test-suite")
router.register("test-reports", TestReportViewSet, basename="test-report")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/swagger/import/", SwaggerImportView.as_view(), name="swagger-import"),
]
