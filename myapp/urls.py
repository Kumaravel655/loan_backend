from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SignupView, LoginView, LogoutView, ChangePasswordView,
    CustomerViewSet, LoanTypeViewSet, LoanViewSet,
    LoanDueViewSet, DailyCollectionViewSet,
    AttendanceViewSet, NotificationViewSet,assign_loan_schedule,list_collection_agents,LoanScheduleUpdateView, LoanScheduleViewSet
)
from .views import LoanScheduleListAPIView, LoanScheduleByLoanAPIView
# Initialize router
router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'loan-types', LoanTypeViewSet)
router.register(r'loans', LoanViewSet)
router.register(r'loan-dues', LoanDueViewSet)
router.register(r'daily-collections', DailyCollectionViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'loan-schedules', LoanScheduleViewSet, basename='loan-schedules')


# Combine all URL patterns
urlpatterns = [
    # Authentication endpoints
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('loan-schedules/', LoanScheduleListAPIView.as_view(), name='loan-schedules'),
    path('loan-schedules/<int:loan_id>/', LoanScheduleByLoanAPIView.as_view(), name='loan-schedules-by-loan'), 
    path('loan-schedules/<int:pk>/', LoanScheduleUpdateView.as_view(), name='update-loan-schedule'),
    path('loan-schedules/<int:pk>/assign/', assign_loan_schedule, name='assign-loan-schedule'),


     path('agents/', list_collection_agents, name='list_collection_agents'),
    # API routes
    path('', include(router.urls)),
]
