from django.db import models
from users.models import User

# Create your models here.
class Ticket(models.Model):
    STATUS_CHOICES = [
        ("OPEN",'open'),
        ("IN_PROGRESS",'inprogress'),
        ("RESOLVED",'resolved'),
        ("CLOSED",'closed')
    ]

    PRIORITY_CHOICES = [
        ('LOW','low'),
        ('MEDIUM','medium'),
        ('HIGH','high')
    ]

    title =  models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN'
    )
    priority = models.CharField(max_length=20,choices=PRIORITY_CHOICES,default='LOW',)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="tickets_created")
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="assigned_tickets",blank=True)


    def __str__(self):
        return self.title




class TicketHistory(models.Model):
    EVENT_CHOICES = [
        ("ASSIGNED", "Assigned"),
        ("STATUS_CHANGED", "Status Changed"),
    ]
    ticket = models.ForeignKey(Ticket,on_delete=models.CASCADE,related_name="TicketHistory")
    changed_by = models.ForeignKey(User,on_delete=models.SET_NULL,null= True)
    event_type = models.CharField(max_length=30,choices=EVENT_CHOICES,null=True)
    old_value = models.CharField(max_length=255,null=True,blank=True)
    new_value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["-created_at"]




class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket,on_delete=models.CASCADE,related_name="TicketAttachments")
    uploaded_by = models.ForeignKey(User,on_delete=models.CASCADE)
    file = models.FileField(upload_to="ticket_attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)