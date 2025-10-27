from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from .serializers import LoginSerializer, ChangePasswordSerializer, SignupSerializer
from .models import CustomUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

# -------------------- LOGIN --------------------
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {
                    'email': user.email,
                    'username': user.username,
                    'role': user.role
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------- LOGOUT --------------------
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()  # delete token
        except Exception:
            pass
        logout(request)
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)


# -------------------- CHANGE PASSWORD --------------------
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            if not user.check_password(old_password):
                return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------- SIGNUP --------------------
class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # create new user
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "User registered successfully",
                "token": token.key,
                "user": {
                    "email": user.email,
                    "username": user.username,
                    "role": user.role
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import viewsets
from .models import (
    Customer, LoanType, Loan, LoanDue,
    DailyCollection, Attendance, Notification
)
from .serializers import (
    CustomerSerializer, LoanTypeSerializer, LoanSerializer,
    LoanDueSerializer, DailyCollectionSerializer,
    AttendanceSerializer, NotificationSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('-created_at')
    serializer_class = CustomerSerializer


class LoanTypeViewSet(viewsets.ModelViewSet):
    queryset = LoanType.objects.all()
    serializer_class = LoanTypeSerializer


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.select_related('customer', 'loan_type').all()
    serializer_class = LoanSerializer

    @action(detail=True, methods=["get"], url_path="details")
    def details(self, request, pk=None):
        """
        Returns full loan details including all related schedules.
        """
        loan = self.get_object()
        schedules = LoanSchedule.objects.filter(loan=loan)
        schedule_serializer = LoanScheduleSerializer(schedules, many=True)
        loan_serializer = self.get_serializer(loan)
        return Response({
            "loan": loan_serializer.data,
            "schedules": schedule_serializer.data
        }, status=status.HTTP_200_OK)


class LoanDueViewSet(viewsets.ModelViewSet):
    queryset = LoanDue.objects.select_related('loan').all()
    serializer_class = LoanDueSerializer


class DailyCollectionViewSet(viewsets.ModelViewSet):
    queryset = DailyCollection.objects.all().order_by('-collection_date')
    serializer_class = DailyCollectionSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().order_by('-login_time')
    serializer_class = AttendanceSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
from rest_framework import generics
from .models import LoanSchedule
from .serializers import LoanScheduleSerializer

# Fetch schedules for all loans
class LoanScheduleListAPIView(generics.ListAPIView):
    queryset = LoanSchedule.objects.all()
    serializer_class = LoanScheduleSerializer

# Fetch schedules for a specific loan
class LoanScheduleByLoanAPIView(generics.ListAPIView):
    serializer_class = LoanScheduleSerializer

    def get_queryset(self):
        loan_id = self.kwargs['loan_id']
        return LoanSchedule.objects.filter(loan_id=loan_id).order_by('installment_no')

# views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CustomUser
from .serializers import UserSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_collection_agents(request):
    """
    API: /api/auth/agents/
    Returns a list of all users with role='collection_agent'
    """
    agents = CustomUser.objects.filter(role='collection_agent')
    serializer = UserSerializer(agents, many=True)
    return Response(serializer.data)

# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LoanSchedule
from .serializers import LoanScheduleSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class LoanScheduleViewSet(viewsets.ModelViewSet):
    queryset = LoanSchedule.objects.all()
    serializer_class = LoanScheduleSerializer

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        try:
            schedule = self.get_object()
            assigned_to_id = request.data.get('assigned_to')

            if not assigned_to_id:
                return Response({"error": "assigned_to field is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                assigned_user = User.objects.get(id=assigned_to_id)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            schedule.assigned_to = assigned_user
            schedule.save()

            return Response(
                {"message": f"Loan schedule {pk} successfully assigned to {assigned_user.email}"},
                status=status.HTTP_200_OK,
            )

        except LoanSchedule.DoesNotExist:
            return Response({"error": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .models import LoanSchedule
from .serializers import LoanScheduleAssignSerializer

User = get_user_model()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_loan_schedule(request, pk):
    """
    Assign a loan schedule to a collection agent.
    Example JSON body: {"assigned_to": 5}
    """
    try:
        schedule = LoanSchedule.objects.get(pk=pk)
    except LoanSchedule.DoesNotExist:
        return Response(
            {"error": "Loan schedule not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    assigned_to_id = request.data.get("assigned_to")
    if not assigned_to_id:
        return Response(
            {"error": "assigned_to field is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ✅ Validate that the user exists and is a collection agent
    try:
        assigned_user = User.objects.get(pk=assigned_to_id)
        if assigned_user.role != "collection_agent":
            return Response(
                {"error": "User must be a collection agent."},
                status=status.HTTP_400_BAD_REQUEST
            )
    except User.DoesNotExist:
        return Response(
            {"error": "Assigned user not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # ✅ Perform assignment
    serializer = LoanScheduleAssignSerializer(
        schedule,
        data={"assigned_to": assigned_user.id},
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": f"Loan schedule {pk} assigned successfully.",
                "loan_schedule_id": schedule.id,
                "assigned_to": {
                    "id": assigned_user.id,
                    "email": assigned_user.email,
                    "username": assigned_user.username,
                    "role": assigned_user.role,
                },
            },
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# views.py
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import LoanSchedule
from .serializers import LoanScheduleSerializer

class LoanScheduleUpdateView(APIView):
    def patch(self, request, pk):
        try:
            schedule = LoanSchedule.objects.get(pk=pk)
        except LoanSchedule.DoesNotExist:
            return Response({"error": "Loan schedule not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LoanScheduleSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import LoanSchedule
from .serializers import LoanScheduleSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_loan_schedule(request, pk):
    """
    Assign a loan schedule to an agent using serializer itself.
    """
    try:
        schedule = LoanSchedule.objects.get(pk=pk)
    except LoanSchedule.DoesNotExist:
        return Response(
            {"error": "Loan schedule not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = LoanScheduleSerializer(
        schedule,
        data=request.data,
        partial=True  # ✅ allows updating only 'assigned_to'
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                **serializer.data,
                "message": "Agent successfully assigned to loan schedule."
            },
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
