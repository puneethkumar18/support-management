from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from comments.serializers import CommentSerializer
from comments.models import Comment

# Create your views here.

class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def perform_create(self,serializer):
        serializer.save(user = self.request.user)

    def get_queryset(self):
        ticket_id = self.request.query_params.get("ticket")
        return Comment.objects.filter(pk = ticket_id)