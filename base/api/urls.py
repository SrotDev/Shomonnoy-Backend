
from django.urls import path
from base.api import views
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def api_root(request):
    endpoints = [
        {"path": "/api/auth/authority/register/", "methods": ["POST"], "description": "Register Authority user"},
        {"path": "/api/auth/stakeholder/register/", "methods": ["POST"], "description": "Register Stakeholder user"},
        {"path": "/api/auth/citizen/register/", "methods": ["POST"], "description": "Register Citizen user"},
        {"path": "/api/auth/login/", "methods": ["POST"], "description": "Login for all user types"},
    ]
    return Response({"api_endpoints": endpoints})

urlpatterns = [
    path("", api_root, name="api-root"),
    path("auth/authority/register/", views.AuthorityRegisterView.as_view()),
    path("auth/stakeholder/register/", views.StakeholderRegisterView.as_view()),
    path("auth/citizen/register/", views.CitizenRegisterView.as_view()),
    path("auth/login/", views.LoginView.as_view()),
]
