from django.urls import path, include
from base.api import views
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

@api_view(["GET"])
def api_root(request):
    endpoints = [
        {
            "path": "/api/auth/register/",
            "methods": ["POST"],
            "description": "Register a new user (Authority, Stakeholder, Citizen)",
            "input_fields": [
                {"field": "email", "type": "string"},
                {"field": "password", "type": "string"},
                {"field": "name", "type": "string"},
                {"field": "phone_number", "type": "string"},
                {"field": "city", "type": "string"},
                {"field": "role", "type": "string", "choices": ["authority", "stakeholder", "citizen"]},
                {"field": "designation", "type": "string", "optional": True},
                {"field": "organization", "type": "string", "optional": True},
                {"field": "national_id", "type": "string", "optional": True}
            ],
            "output_fields": [
                {"field": "uuid", "type": "string"},
                {"field": "email", "type": "string"},
                {"field": "name", "type": "string"},
                {"field": "phone_number", "type": "string"},
                {"field": "city", "type": "string"},
                {"field": "role", "type": "string"},
                {"field": "designation", "type": "string"},
                {"field": "organization", "type": "string"},
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
                {"field": "role", "type": "string", "choices": ["authority", "stakeholder", "citizen"]}
            ],
            "output_fields": [
                {"field": "access", "type": "string"},
                {"field": "refresh", "type": "string"}
            ]
        },
        {
            "path": "/api/locations/",
            "methods": ["GET", "POST"],
            "description": "List all locations or create a new location",
            "input_fields": [
                {"field": "city", "type": "string"},
                {"field": "geom", "type": "GeoJSON/geometry"}
            ],
            "output_fields": [
                {"field": "uuid", "type": "string"},
                {"field": "city", "type": "string"},
                {"field": "geom", "type": "GeoJSON/geometry"}
            ]
        },
        {
            "path": "/api/locations/{uuid}/",
            "methods": ["GET", "PUT", "PATCH", "DELETE"],
            "description": "Retrieve, update, or delete a specific location",
            "input_fields": [
                {"field": "city", "type": "string"},
                {"field": "geom", "type": "GeoJSON/geometry"}
            ],
            "output_fields": [
                {"field": "uuid", "type": "string"},
                {"field": "city", "type": "string"},
                {"field": "geom", "type": "GeoJSON/geometry"}
            ]
        },
        {
            "path": "/api/works/",
            "methods": ["GET", "POST"],
            "description": "List all works or create a new work",
            "input_fields": [
                {"field": "stakeholder", "type": "uuid"},
                {"field": "location", "type": "uuid"},
                {"field": "name", "type": "string"},
                {"field": "details", "type": "string"},
                {"field": "tag", "type": "string", "choices": ["Emergency", "Regular"]},
                {"field": "status", "type": "string", "choices": ["ProposedByAdmin", "ProposedByStaekHolder", "Declined", "Planned", "Ongoing", "Completed"]},
                {"field": "estimated_time", "type": "duration"},
                {"field": "proposed_start_date", "type": "date"},
                {"field": "proposed_end_date", "type": "date"},
                {"field": "start_date", "type": "date"},
                {"field": "end_date", "type": "date"},
                {"field": "budget", "type": "decimal"}
            ],
            "output_fields": [
                {"field": "uuid", "type": "string"},
                {"field": "stakeholder", "type": "uuid"},
                {"field": "location", "type": "uuid"},
                {"field": "name", "type": "string"},
                {"field": "details", "type": "string"},
                {"field": "tag", "type": "string"},
                {"field": "status", "type": "string"},
                {"field": "estimated_time", "type": "duration"},
                {"field": "proposed_start_date", "type": "date"},
                {"field": "proposed_end_date", "type": "date"},
                {"field": "start_date", "type": "date"},
                {"field": "end_date", "type": "date"},
                {"field": "budget", "type": "decimal"}
            ]
        },
            {
                "path": "/api/users/",
                "methods": ["GET", "POST"],
                "description": "List all users, create a new user. Use ?search=role to filter by role.",
                "input_fields": [
                    {"field": "email", "type": "string"},
                    {"field": "password", "type": "string"},
                    {"field": "name", "type": "string"},
                    {"field": "phone_number", "type": "string"},
                    {"field": "city", "type": "string"},
                    {"field": "role", "type": "string", "choices": ["authority", "stakeholder", "citizen"]},
                    {"field": "designation", "type": "string", "optional": True},
                    {"field": "organization", "type": "string", "optional": True},
                    {"field": "national_id", "type": "string", "optional": True}
                ],
                "output_fields": [
                    {"field": "uuid", "type": "string"},
                    {"field": "email", "type": "string"},
                    {"field": "name", "type": "string"},
                    {"field": "phone_number", "type": "string"},
                    {"field": "city", "type": "string"},
                    {"field": "role", "type": "string"},
                    {"field": "designation", "type": "string"},
                    {"field": "organization", "type": "string"},
                    {"field": "national_id", "type": "string"},
                    {"field": "created_at", "type": "datetime"},
                    {"field": "updated_at", "type": "datetime"},
                    {"field": "is_active", "type": "boolean"}
                ]
            },
            {
                "path": "/api/users/{uuid}/",
                "methods": ["GET", "PUT", "PATCH", "DELETE"],
                "description": "Retrieve, update, or delete a specific user.",
                "input_fields": [
                    {"field": "email", "type": "string"},
                    {"field": "password", "type": "string"},
                    {"field": "name", "type": "string"},
                    {"field": "phone_number", "type": "string"},
                    {"field": "city", "type": "string"},
                    {"field": "role", "type": "string", "choices": ["authority", "stakeholder", "citizen"]},
                    {"field": "designation", "type": "string", "optional": True},
                    {"field": "organization", "type": "string", "optional": True},
                    {"field": "national_id", "type": "string", "optional": True}
                ],
                "output_fields": [
                    {"field": "uuid", "type": "string"},
                    {"field": "email", "type": "string"},
                    {"field": "name", "type": "string"},
                    {"field": "phone_number", "type": "string"},
                    {"field": "city", "type": "string"},
                    {"field": "role", "type": "string"},
                    {"field": "designation", "type": "string"},
                    {"field": "organization", "type": "string"},
                    {"field": "national_id", "type": "string"},
                    {"field": "created_at", "type": "datetime"},
                    {"field": "updated_at", "type": "datetime"},
                    {"field": "is_active", "type": "boolean"}
                ]
            },
        {
            "path": "/api/works/{uuid}/",
            "methods": ["GET", "PUT", "PATCH", "DELETE"],
            "description": "Retrieve, update, or delete a specific work entry",
            "input_fields": [
                {"field": "stakeholder", "type": "uuid"},
                {"field": "location", "type": "uuid"},
                {"field": "name", "type": "string"},
                {"field": "details", "type": "string"},
                {"field": "tag", "type": "string", "choices": ["Emergency", "Regular"]},
                {"field": "status", "type": "string", "choices": ["ProposedByAdmin", "ProposedByStaekHolder", "Declined", "Planned", "Ongoing", "Completed"]},
                {"field": "estimated_time", "type": "duration"},
                {"field": "proposed_start_date", "type": "date"},
                {"field": "proposed_end_date", "type": "date"},
                {"field": "start_date", "type": "date"},
                {"field": "end_date", "type": "date"},
                {"field": "budget", "type": "decimal"}
            ],
            "output_fields": [
                {"field": "uuid", "type": "string"},
                {"field": "stakeholder", "type": "uuid"},
                {"field": "location", "type": "uuid"},
                {"field": "name", "type": "string"},
                {"field": "details", "type": "string"},
                {"field": "tag", "type": "string"},
                {"field": "status", "type": "string"},
                {"field": "estimated_time", "type": "duration"},
                {"field": "proposed_start_date", "type": "date"},
                {"field": "proposed_end_date", "type": "date"},
                {"field": "start_date", "type": "date"},
                {"field": "end_date", "type": "date"},
                {"field": "budget", "type": "decimal"}
            ]
        },
        {
            "path": "/api/notices/",
            "methods": ["GET", "POST"],
            "description": "List all notices or create a new notice (PDF upload only)",
            "input_fields": [
                {"field": "title", "type": "string"},
                {"field": "ordinance_no", "type": "string"},
                {"field": "details", "type": "string"},
                {"field": "pdf", "type": "file", "accept": "application/pdf"}
            ],
            "output_fields": [
                {"field": "uuid", "type": "string"},
                {"field": "title", "type": "string"},
                {"field": "ordinance_no", "type": "string"},
                {"field": "details", "type": "string"},
                {"field": "pdf", "type": "url"},
                {"field": "created_at", "type": "datetime"},
                {"field": "updated_at", "type": "datetime"}
            ]
        },
        {
            "path": "/api/notices/{uuid}/",
            "methods": ["GET", "PUT", "PATCH", "DELETE"],
            "description": "Retrieve, update, or delete a specific notice (PDF upload only)",
            "input_fields": [
                {"field": "title", "type": "string"},
                {"field": "ordinance_no", "type": "string"},
                {"field": "details", "type": "string"},
                {"field": "pdf", "type": "file", "accept": "application/pdf"}
            ],
            "output_fields": [
                {"field": "uuid", "type": "string"},
                {"field": "title", "type": "string"},
                {"field": "ordinance_no", "type": "string"},
                {"field": "details", "type": "string"},
                {"field": "pdf", "type": "url"},
                {"field": "created_at", "type": "datetime"},
                {"field": "updated_at", "type": "datetime"}
            ]
        },
        {
            "path": "/api/notifications/",
            "methods": ["GET", "POST"],
            "description": "List all notifications or create a new notification",
            "input_fields": [
                {"field": "title", "type": "string"},
                {"field": "message", "type": "string"},
                {"field": "genre", "type": "string", "choices": ["Info", "Warning", "Alert"]},
                {"field": "created_for", "type": "uuid"},
                {"field": "is_read", "type": "boolean"}
            ],
            "output_fields": [
                {"field": "uuid", "type": "string"},
                {"field": "title", "type": "string"},
                {"field": "message", "type": "string"},
                {"field": "genre", "type": "string"},
                {"field": "created_at", "type": "datetime"},
                {"field": "updated_at", "type": "datetime"}
            ]
        },
        {
            "path": "/api/notifications/{uuid}/",
            "methods": ["GET", "PUT", "PATCH", "DELETE"],
            "description": "Retrieve, update, or delete a specific notification",
            "input_fields": [
                {"field": "title", "type": "string"},
                {"field": "message", "type": "string"},
                {"field": "genre", "type": "string", "choices": ["Info", "Warning", "Alert"]}
            ],
            "output_fields": [
                {"field": "uuid", "type": "string"},
                {"field": "title", "type": "string"},
                {"field": "message", "type": "string"},
                {"field": "genre", "type": "string"},
                {"field": "created_at", "type": "datetime"},
                {"field": "updated_at", "type": "datetime"}
            ]
        }, 
        {
            "path": "/api/conflicts/",
            "methods": ["GET"],
            "description": "Detect and list all works that have spatial conflicts based on their locations",
            "input_fields": [],
            "output_fields": [
                {"field": "work_uuid", "type": "string"},
                {"field": "conflicting_works", "type": "list of strings"}
            ]
        },
        {
            "path": "/api/feedback/",
            "methods": ["GET", "POST"],
            "description": "List all feedback or create a new feedback",
            "input_fields": [
                {"field": "feeling", "type": "string", "choices": ["Excellent", "Good", "Average", "Poor", "Terrible"]},
                {"field": "details", "type": "string"},
                {"field": "related_work", "type": "uuid", "optional": True}
            ],
            "output_fields": [
                {"field": "uuid", "type": "string"},
                {"field": "created_by", "type": "uuid"},
                {"field": "feeling", "type": "string"},
                {"field": "details", "type": "string"},
                {"field": "related_work", "type": "uuid"},
                {"field": "created_at", "type": "datetime"},
                {"field": "updated_at", "type": "datetime"}
            ]
        },
        {
            "path": "/api/reports/",
            "methods": ["GET", "POST"],
            "description": "List all reports or create a new report",
            "input_fields": [
                {"field": "report_type", "type": "string"},
                {"field": "details", "type": "string"},
                {"field": "status", "type": "string", "choices": ["Pending", "In Progress", "Resolved"]},
                {"field": "related_work", "type": "uuid", "optional": True}
            ],
            "output_fields": [
                {"field": "uuid", "type": "string"},
                {"field": "created_by", "type": "uuid"},
                {"field": "report_type", "type": "string"},
                {"field": "details", "type": "string"},
                {"field": "status", "type": "string"},
                {"field": "related_work", "type": "uuid"},
                {"field": "created_at", "type": "datetime"},
                {"field": "updated_at", "type": "datetime"}
            ]
        }
    ]
    return Response({"api_endpoints": endpoints})

router = DefaultRouter()
router.register(r'locations', views.LocationViewSet, basename='location')
router.register(r'works', views.WorkViewSet, basename='work')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'notices', views.NoticeViewSet, basename='notice')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'feedback', views.FeedbackViewSet, basename='feedback')
router.register(r'reports', views.ReportViewSet, basename='report')

urlpatterns = [
    path("", api_root, name="api-root"),
    path("auth/register/", views.UserRegisterView.as_view()),
    path("auth/login/", views.LoginView.as_view()),
    path("conflicts/", views.conflict_detection_view, name="conflict-detection"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("", include(router.urls)),
]
