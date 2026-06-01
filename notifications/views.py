from rest_framework import viewsets
from notifications.serializers import NotificationSerializer
from notifications.models import Notification
from rest_framework.decorators import action
from rest_framework.response import Response

# Create your views here.
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer

    # MARK AS READ
    @action(detail=True, methods=["post"])
    def mark_read(self,request,pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({
            "message": "Notification marked as read"
        })
    
    # UNREAD COUNT
    @action(detail=False,methods=["get"])
    def unread_count(self,request,pk=None):
        count = Notification.objects.filter(user=self.request.user,is_read = False).count()
        return Response({"count":count},status=200)

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)