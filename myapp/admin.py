from django.contrib import admin
from .models import CustomUser,Customer,LoanType,Loan,LoanDue,DailyCollection,Attendance,Notification,LoanSchedule
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Customer)
admin.site.register(LoanType)
admin.site.register(Loan)
admin.site.register(LoanDue)
admin.site.register(DailyCollection)
admin.site.register(Attendance)
admin.site.register(Notification)
admin.site.register(LoanSchedule)

 