from datetime import timedelta
from dateutil.relativedelta import relativedelta
from math import pow
from myapp.models import LoanSchedule

# Flat interest schedule
def create_flat_schedule(loan):
    current_date = loan.created_at
    principal = float(loan.principal_amount)
    interest_rate = float(loan.interest_percentage) / 100
    n = loan.total_due_count

    total_interest = principal * interest_rate
    total_payable = principal + total_interest
    installment_total = round(total_payable / n, 2)
    principal_per_installment = round(principal / n, 2)
    interest_per_installment = round(total_interest / n, 2)

    remaining_principal = principal

    for i in range(1, n+1):
        LoanSchedule.objects.create(
            loan=loan,
            installment_no=i,
            due_date=current_date.date(),
            principal_amount=principal_per_installment,
            interest_amount=interest_per_installment,
            total_due=installment_total,
            remaining_principal=round(remaining_principal - principal_per_installment, 2)
        )

        remaining_principal -= principal_per_installment

        if loan.repayment_mode == 'daily':
            current_date += timedelta(days=1)
        elif loan.repayment_mode == 'weekly':
            current_date += timedelta(weeks=1)
        elif loan.repayment_mode == 'monthly':
            current_date += relativedelta(months=1)

# Reducing balance schedule
def create_reducing_schedule(loan):
    current_date = loan.created_at
    principal = float(loan.principal_amount)
    n = loan.total_due_count
    r = float(loan.interest_percentage) / 100 / 12  # monthly interest

    emi = principal * r * pow(1+r, n) / (pow(1+r, n) - 1)
    remaining_principal = principal

    for i in range(1, n+1):
        interest_amount = remaining_principal * r
        principal_amount = emi - interest_amount
        remaining_principal -= principal_amount

        LoanSchedule.objects.create(
            loan=loan,
            installment_no=i,
            due_date=current_date.date(),
            principal_amount=round(principal_amount, 2),
            interest_amount=round(interest_amount, 2),
            total_due=round(emi, 2),
            remaining_principal=round(remaining_principal, 2)
        )

        if loan.repayment_mode == 'daily':
            current_date += timedelta(days=1)
        elif loan.repayment_mode == 'weekly':
            current_date += timedelta(weeks=1)
        elif loan.repayment_mode == 'monthly':
            current_date += relativedelta(months=1)
