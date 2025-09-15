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
from rest_framework.exceptions import APIException
from base.api.serializers import UserSerializer
from django.db.models import Prefetch



from typing import List, Tuple

from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Q


from .shortest_path_utils import routeProbSolver

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
        Prefetch('conflicts', queryset=Work.objects.exclude(status__in=['Declined', 'Done']))
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



class ShortRoutesAPIView(APIView):
    """
    POST /api/work-rects/
    Body JSON:
      {
        "statuses": ["Ongoing", "Planned"] or "Ongoing,Planned",
        "city": "Dhaka",
        "distinct": true,
        "orig_str": "23.7767759,90.3996056",
        "dest_str": "23.8104016,90.4125185"
      }

    Returns JSON:
      {
        "route": {...}   # GeoJSON geometry + summary
      }
    """
    def post(self, request):
        # Base queryset: works with location
        qs = Work.objects.select_related("location").filter(location__isnull=False)

        # --- Optional filters ---
        statuses = request.data.get("statuses")
        if statuses:
            if isinstance(statuses, str):
                status_list = [s.strip() for s in statuses.split(",") if s.strip()]
            elif isinstance(statuses, list):
                status_list = [str(s).strip() for s in statuses if s]
            else:
                status_list = ["Ongoing", "Planned"]
            if status_list:
                qs = qs.filter(status__in=status_list)

        city = request.data.get("city")
        if city:
            qs = qs.filter(location__city__iexact=city)

        dedup = request.data.get("distinct", True)
        if isinstance(dedup, str):
            dedup = dedup.lower() not in ("0", "false", "no")

        rect_specs: List[List[float]] = []
        seen: set = set()

        for work in qs:
            loc = getattr(work, "location", None)
            if not loc:
                continue
            geom = getattr(loc, "geom", None)
            if geom is None:
                continue

            # Convert to 4326 safely
            try:
                geom_4326 = geom if geom.srid == 4326 else geom.clone().transform(4326)
            except Exception:
                geom_4326 = geom

            try:
                xmin, ymin, xmax, ymax = geom_4326.extent
            except Exception:
                continue

            rect = [round(float(xmin), 8), round(float(ymin), 8),
                    round(float(xmax), 8), round(float(ymax), 8)]
            tup = tuple(rect)

            if dedup and tup in seen:
                continue
            seen.add(tup)

            rect_specs.append(rect)

        # --- Validate start/end ---
        orig_str = request.data.get("orig_str")
        dest_str = request.data.get("dest_str")
        if not orig_str or not dest_str:
            return Response(
                {"error": "orig_str and dest_str are required, format 'lat,lon'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            resdata = routeProbSolver(rect_specs=rect_specs, orig_str=orig_str, dest_str=dest_str)
        except Exception as e:
            raise APIException(f"Routing failed: {e}")

        return Response(
            {"route": resdata},
            status=status.HTTP_200_OK
        )