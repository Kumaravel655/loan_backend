from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import LoanSchedule, LoanDue

@receiver(post_save, sender=LoanSchedule)
def create_or_update_loan_due(sender, instance, created, **kwargs):
    """
    Whenever a LoanSchedule is created or updated,
    ensure a matching LoanDue exists or is updated.
    """
    LoanDue.objects.update_or_create(
        loan=instance.loan,
        due_number=instance.installment_no,
        defaults={
            'due_date': instance.due_date,
            'due_amount': instance.total_due,
            'payment_status': 'pending',  # default
        }
    )


@receiver(post_delete, sender=LoanSchedule)
def delete_loan_due(sender, instance, **kwargs):
    """
    If a LoanSchedule is deleted, delete the matching LoanDue.
    """
    LoanDue.objects.filter(loan=instance.loan, due_number=instance.installment_no).delete()
