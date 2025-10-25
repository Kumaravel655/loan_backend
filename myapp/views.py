from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from .serializers import LoginSerializer, ChangePasswordSerializer, SignupSerializer
from .models import CustomUser


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

