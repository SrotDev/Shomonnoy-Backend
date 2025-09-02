from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from base.api.serializers import (
    AuthoritySerializer,
    StakeholderSerializer,
    CitizenSerializer,
    LoginSerializer,
)

class AuthorityRegisterView(generics.CreateAPIView):
    serializer_class = AuthoritySerializer

class StakeholderRegisterView(generics.CreateAPIView):
    serializer_class = StakeholderSerializer

class CitizenRegisterView(generics.CreateAPIView):
    serializer_class = CitizenSerializer

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
