from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid email or password")


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'role']

    def create(self, validated_data):
        # Extract fields safely
        email = validated_data.get('email')
        username = validated_data.get('username')
        password = validated_data.get('password')
        role = validated_data.get('role', 'user')  # default if role not provided

        user = CustomUser(email=email, username=username, role=role)
        user.set_password(password)
        user.save()
        return user
    
from rest_framework import serializers
from .models import (
    Customer, LoanType, Loan, LoanDue,
    DailyCollection, Attendance, Notification
)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class LoanTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanType
        fields = '__all__'


from rest_framework import serializers
from .models import Loan, LoanSchedule, Customer, LoanType
from .utils.loan_schedule import create_flat_schedule, create_reducing_schedule  # import your functions

class LoanSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    loan_type = LoanTypeSerializer(read_only=True)

    customer_id = serializers.PrimaryKeyRelatedField(
        source='customer', queryset=Customer.objects.all(), write_only=True
    )
    loan_type_id = serializers.PrimaryKeyRelatedField(
        source='loan_type', queryset=LoanType.objects.all(), write_only=True
    )

    class Meta:
        model = Loan
        fields = '__all__'

    def create(self, validated_data):
        # Create the loan instance
        loan = Loan.objects.create(**validated_data)
        
        # Generate repayment schedule automatically
        # Choose either flat or reducing balance
        create_flat_schedule(loan)
        # OR for reducing balance: create_reducing_schedule(loan)

        return loan



class LoanDueSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanDue
        fields = '__all__'


class DailyCollectionSerializer(serializers.ModelSerializer):
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = DailyCollection
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

from rest_framework import serializers
from .models import LoanSchedule, Loan

class LoanScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanSchedule
        fields = [
            'id',
            'loan',
            'installment_no',
            'due_date',
            'principal_amount',
            'interest_amount',
            'total_due',
            'remaining_principal',
        ]
        read_only_fields = ['id', 'loan']
