from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = (
    ('master_admin', 'Master Admin'),
    ('collection_agent', 'Collection Agent'),
    ('staff', 'Staff'),
)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='collection_agent')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} ({self.role})"


from django.db import models
from django.utils import timezone


# 2. Customers
class Customer(models.Model):
    customer_id = models.BigAutoField(primary_key=True)
    customer_code = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=150)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=120, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    aadhar_number = models.CharField(max_length=20, blank=True, null=True)
    documents_url = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return f"{self.customer_code} - {self.full_name}"


# 3. Loan Types
class LoanType(models.Model):
    loan_type_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'loan_types'
        verbose_name = 'Loan Type'
        verbose_name_plural = 'Loan Types'

    def __str__(self):
        return self.name


# 4. Loans
class Loan(models.Model):
    REPAYMENT_MODES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    LOAN_STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('defaulted', 'Defaulted'),
    ]

    loan_id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.ForeignKey(LoanType, on_delete=models.SET_NULL, null=True)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_due_count = models.IntegerField()
    due_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    repayment_mode = models.CharField(max_length=10, choices=REPAYMENT_MODES)
    loan_status = models.CharField(max_length=10, choices=LOAN_STATUS_CHOICES, default='active')
    created_by = models.BigIntegerField()  # admin id
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loans'
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'

    def __str__(self):
        return f"Loan #{self.loan_id} ({self.customer.full_name})"


# 5. Loan Dues / Payments
class LoanDue(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('card', 'Card'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('skipped', 'Skipped'),
    ]

    due_id = models.BigAutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='dues')
    due_number = models.IntegerField()
    due_date = models.DateField()
    due_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, blank=True, null=True)
    collected_by = models.BigIntegerField(blank=True, null=True)  # agent id
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')
    skip_reason = models.TextField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'loan_dues'
        verbose_name = 'Loan Due'
        verbose_name_plural = 'Loan Dues'

    def __str__(self):
        return f"Due {self.due_number} - Loan #{self.loan_id}"


# 6. Collections Summary
class DailyCollection(models.Model):
    id = models.BigAutoField(primary_key=True)
    collection_date = models.DateField()
    agent_id = models.BigIntegerField()
    cash_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    upi_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    card_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    @property
    def total_amount(self):
        return self.cash_total + self.upi_total + self.card_total

    class Meta:
        db_table = 'daily_collections'
        verbose_name = 'Daily Collection'
        verbose_name_plural = 'Daily Collections'

    def __str__(self):
        return f"{self.collection_date} - Agent {self.agent_id}"


# 7. Attendance
class Attendance(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'attendance'
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance'

    def __str__(self):
        return f"User {self.user_id} - {self.login_time.date()}"


# 8. Notifications
class Notification(models.Model):
    notification_id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    title = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"Notification for User {self.user_id}"
from django.conf import settings
class LoanSchedule(models.Model):
    loan = models.ForeignKey('Loan', on_delete=models.CASCADE, related_name='schedules')
    installment_no = models.PositiveIntegerField()
    due_date = models.DateField()
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_due = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_principal = models.DecimalField(max_digits=12, decimal_places=2)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'collection_agent'},
        related_name='assigned_schedules'
    )

    class Meta:
        db_table = 'loan_schedule'
        ordering = ['installment_no']

    def __str__(self):
        return f"Loan {self.loan.loan_id} - Installment {self.installment_no}"