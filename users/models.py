from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    
    class Role(models.TextChoices):
        REQUESTER = "REQUESTER","requester",
        SUPERVISOR = "SUPERVISOR","supervisor",
        AI_AGENT = "AI_AGENT","AI agent"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.REQUESTER
    )

    @property
    def is_supervisor(self):
        return self.role == "SUPERVISOR"
    
    @property
    def is_agent(self):
        return self.role == "AI_AGENT"
    
    @property
    def is_requester(self):
        return self.role == "REQUESTER"
    

