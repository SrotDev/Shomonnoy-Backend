
from django.urls import path
from base.api import views
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def api_root(request):
    endpoints = [
        {
            "path": "/api/auth/authority/register/",
            "methods": ["POST"],
            "description": "Register Authority user",
            "input_fields": [
                {"field": "email", "type": "string"},
                {"field": "password", "type": "string"},
                {"field": "name", "type": "string"},
                {"field": "phone_number", "type": "string"},
                {"field": "city", "type": "string"},
                {"field": "designation", "type": "string"},
                {"field": "organization", "type": "string"}
            ],
            "output_fields": [
                {"field": "uuid", "type": "string"},
                {"field": "email", "type": "string"},
                {"field": "name", "type": "string"},
                {"field": "phone_number", "type": "string"},
                {"field": "city", "type": "string"},
                {"field": "designation", "type": "string"},
                {"field": "organization", "type": "string"},
                {"field": "created_at", "type": "datetime"},
                {"field": "updated_at", "type": "datetime"},
                {"field": "is_active", "type": "boolean"}
            ]
        },
        {
            "path": "/api/auth/stakeholder/register/",
            "methods": ["POST"],
            "description": "Register Stakeholder user",
            "input_fields": [
                {"field": "email", "type": "string"},
                {"field": "password", "type": "string"},
                {"field": "name", "type": "string"},
                {"field": "phone_number", "type": "string"},
                {"field": "city", "type": "string"},
                {"field": "designation", "type": "string"},
                {"field": "organization", "type": "string"}
            ],
            "output_fields": [
                {"field": "uuid", "type": "string"},
                {"field": "email", "type": "string"},
                {"field": "name", "type": "string"},
                {"field": "phone_number", "type": "string"},
                {"field": "city", "type": "string"},
                {"field": "designation", "type": "string"},
                {"field": "organization", "type": "string"},
                {"field": "created_at", "type": "datetime"},
                {"field": "updated_at", "type": "datetime"},
                {"field": "is_active", "type": "boolean"}
            ]
        },
        {
            "path": "/api/auth/citizen/register/",
            "methods": ["POST"],
            "description": "Register Citizen user",
            "input_fields": [
                {"field": "email", "type": "string"},
                {"field": "password", "type": "string"},
                {"field": "name", "type": "string"},
                {"field": "phone_number", "type": "string"},
                {"field": "city", "type": "string"},
                {"field": "national_id", "type": "string"}
            ],
            "output_fields": [
                {"field": "uuid", "type": "string"},
                {"field": "email", "type": "string"},
                {"field": "name", "type": "string"},
                {"field": "phone_number", "type": "string"},
                {"field": "city", "type": "string"},
                {"field": "national_id", "type": "string"},
                {"field": "created_at", "type": "datetime"},
                {"field": "updated_at", "type": "datetime"},
                {"field": "is_active", "type": "boolean"}
            ]
        },
        {
            "path": "/api/auth/login/",
            "methods": ["POST"],
            "description": "Login for all user types",
            "input_fields": [
                {"field": "email", "type": "string"},
                {"field": "password", "type": "string"},
                {"field": "user_type", "type": "string", "choices": ["authority", "stakeholder", "citizen"]}
            ],
            "output_fields": [
                {"field": "access", "type": "string"},
                {"field": "refresh", "type": "string"}
            ]
        },
    ]
    return Response({"api_endpoints": endpoints})

urlpatterns = [
    path("", api_root, name="api-root"),
    path("auth/authority/register/", views.AuthorityRegisterView.as_view()),
    path("auth/stakeholder/register/", views.StakeholderRegisterView.as_view()),
    path("auth/citizen/register/", views.CitizenRegisterView.as_view()),
    path("auth/login/", views.LoginView.as_view()),
]
