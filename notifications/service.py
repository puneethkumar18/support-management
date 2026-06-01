from notifications.models import Notification
from django.core.mail import send_mail

def send_ticket_assigned_email(ticket,recipient_email):
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
    except Exception as e:
        print("EMAIL ERROR:", e)



def create_notification(user,message):
    Notification.objects.create(
        user = user,
        message = message
    )