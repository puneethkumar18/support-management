from rest_framework import serializers
from tickets.serializers import TicketSerializer
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    assigned_tickets = TicketSerializer(many=True,read_only=True)
    tickets_created = TicketSerializer(many=True,read_only=True)
    class Meta:
        model = User
        fields = ["username","id","email","assigned_tickets","tickets_created"]