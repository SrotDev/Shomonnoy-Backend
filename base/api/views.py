from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from base.api.serializers import (
    UserSerializer,
    LoginSerializer,
    LocationSerializer,
    WorkSerializer,
    NoticeSerializer,
    NotificationSerializer,
    FeedbackSerializer,
    ReportSerializer,
)
from base.models import User, Location, Work, Notice, Notification, Feedback, Report
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from base.api.serializers import UserSerializer
from django.db.models import Prefetch



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["role"]
    permission_classes = [IsAuthenticated]



# Registration view (for POST only)
class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer



class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]


class WorkViewSet(viewsets.ModelViewSet):
    queryset = Work.objects.all()
    serializer_class = WorkSerializer
    permission_classes = [IsAuthenticated]

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def conflict_detection_view(request):
    works = Work.objects.prefetch_related(
        Prefetch('conflicts', queryset=Work.objects.exclude(status__iexact='Declined'))
    ).filter(status__iexact='ProposedByStakeholder')
    
    visited = set()
    conflict_groups = []

    for work in works:
        if work.pk in visited:
            continue
        group = set([work])
        stack = [work]
        while stack:
            current = stack.pop()
            for conflicted in current.conflicts.all():
                if conflicted.pk not in visited and conflicted not in group:
                    group.add(conflicted)
                    stack.append(conflicted)
        if len(group) > 1:
            for w in group:
                visited.add(w.pk)
            # conflict_groups.append([WorkSerializer(w).data for w in group])
            conflict_groups.append(WorkSerializer(group, many=True).data)

    return Response(conflict_groups, status=status.HTTP_200_OK)



class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [IsAuthenticated]


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)