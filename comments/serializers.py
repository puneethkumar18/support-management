from comments.models import Comment
from rest_framework import serializers
from users.serializers import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    def get_user(self,obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
        }
    ticket = serializers.PrimaryKeyRelatedField(source="ticket.title",read_only=True)
    class Meta:
        model = Comment
        fields = "__all__"
