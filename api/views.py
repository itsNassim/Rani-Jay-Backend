from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import Complaint, ComplaintStatus
from .serializers import UserSerializer, ComplaintSerializer

User = get_user_model()

class RegisterView(APIView):
    """
    POST /api/register/
    Create a new user account.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Password is write_only, so not returned
            refresh = RefreshToken.for_user(user)
            return Response(   
                {
                    "user": UserSerializer(user).data,
                    "refresh": str(refresh)
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeView(APIView):
    """
    GET /api/me/       -> get current user profile
    PUT/PATCH /api/me/ -> update current user profile
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ComplaintViewSet(viewsets.ModelViewSet):
    """
    /api/complaints/        GET (list), POST (create)
    /api/complaints/{id}/   GET, PUT, PATCH, DELETE
    """
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Complaint.objects.all().order_by("-created_at")
        return Complaint.objects.filter(user=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            status=ComplaintStatus.IN_PROGRESS,
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def set_status(self, request, pk=None):
        """
        POST /api/complaints/{id}/set_status/
        Body: {"status": "IN_PROGRESS"} or "RESOLVED"
        Only staff can update complaint status through this endpoint.
        """
        complaint = self.get_object()
        new_status = request.data.get("status")

        valid_statuses = [choice[0] for choice in ComplaintStatus.choices]
        if new_status not in valid_statuses:
            return Response(
                {"detail": "Invalid status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        complaint.status = new_status
        complaint.save()
        return Response(ComplaintSerializer(complaint).data)
