from django.db import models
from users.models import User
from tickets.models import Ticket
from django.core.exceptions import ValidationError

# Create your models here.
class Comment(models.Model):
    message = models.CharField(max_length=200)
    user =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="user")
    ticket = models.ForeignKey(Ticket,on_delete=models.CASCADE,related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

    def validate_message(self,value):
        if value.trim() == "":
            raise ValidationError("Message is Empty")

    class Meta:
        ordering = ("-created_at",)

