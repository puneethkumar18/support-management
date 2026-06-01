from celery import shared_task
from django.core.mail import send_mail
from tickets.models import Ticket


@shared_task(bind=True,max_retries=3)
def send_ticket_assigned_email(self,ticket_id,recipient_email):
    ticket = Ticket.objects.get(pk = ticket_id)
    try:
        send_mail(
            subject=f"Ticket #{ticket.id} Assigend",
            message=(
                f"Your ticket '{ticket.title}' "
                f"has been assigned."
            ),
            from_email=None,
            recipient_list=[recipient_email]
        )
    except Exception as exc:
        raise self.retry(exc=exc,countdown=60)

@shared_task
def test_task():
    print("Celery is working")