from tickets.models import Ticket,TicketHistory,TicketAttachment
from rest_framework import serializers
from users.models import User
from notifications.service import create_notification
from notifications.models import Notification
from notifications.service import create_notification
from notifications.tasks import send_ticket_assigned_email

class TicketSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.username",read_only=True)
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),required=False)
    class Meta:
        model = Ticket
        fields = '__all__'
        

    def validate_status(self,value):
        if not self.instance:
            return "OPEN"
        
        current_status = self.instance.status

        if current_status == value:
            return value

        allowed_transactions = {
            "OPEN":["IN_PROGRESS"],
            "IN_PROGRESS":["RESOLVED"],
            "RESOLVED":["CLOSED"],
            "CLOSED":[]
        }

        if value not in allowed_transactions[current_status]:
            raise serializers.ValidationError(
                    f"Current change status from"
                    f"{current_status} to {value} is InValid"
                )
        return value
    

    def update(self, instance, validated_data):
        request = self.context.get('request')
        old_status = instance.status
        old_assignee = instance.assigned_to
        instance = super().update(instance, validated_data)
        if instance.status != old_status :
            TicketHistory.objects.create(
                ticket=instance,
                changed_by=request.user,
                event_type="STATUS_CHANGED",
                old_value=old_status,
                new_value=instance.status
            )
            if instance.status == "RESOLVED":
                create_notification(
                user=instance.created_by,
                message=f"Your ticket #{instance.id} has been resolved."
                )
                send_ticket_assigned_email.delay(
                    ticket_id=instance.id,
                    recipient_email=instance.created_by.email
                )
                

        if old_assignee == None or instance.assigned_to != old_assignee:
            TicketHistory.objects.create(
                ticket=instance,
                changed_by=request.user,
                event_type="ASSIGNED",
                old_value=None,
                new_value=instance.assigned_to.username
            )
            create_notification(
                user = instance.assigned_to,
                message=f"You have been assigned Ticket #{instance.id}"
            )
            
            send_ticket_assigned_email.delay(
                    ticket_id=instance.id,
                    recipient_email=instance.assigned_to.email
            )
            
        return instance




class TicketHistorySerializer(serializers.ModelSerializer):
    changed_by_username = serializers.CharField(source="changed_by.username",read_only = True)
    class Meta:
        model = TicketHistory
        fields = "__all__"





class TicketAttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TicketAttachment
        fields = "__all__"