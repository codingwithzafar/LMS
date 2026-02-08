from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MessageThread, Message, ChatGroup, ChatGroupMember, ChatGroupMessage

User = get_user_model()

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","username","full_name","role")

class MessageSerializer(serializers.ModelSerializer):
    sender_info = UserMiniSerializer(source="sender", read_only=True)

    class Meta:
        model = Message
        fields = ("id","sender","sender_info","text","created_at","is_read")
        read_only_fields = ("sender","created_at","is_read")

class ThreadSerializer(serializers.ModelSerializer):
    teacher_info = UserMiniSerializer(source="teacher", read_only=True)
    student_info = UserMiniSerializer(source="student", read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = MessageThread
        fields = ("id","teacher","teacher_info","student","student_info","created_at","last_message")

    def get_last_message(self, obj):
        m = obj.messages.order_by("-created_at").first()
        if not m:
            return None
        return {
            "id": m.id,
            "text": m.text[:120],
            "created_at": m.created_at,
            "sender": m.sender_id,
        }


class ContactSerializer(serializers.ModelSerializer):
    is_online = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "full_name", "last_seen", "role", "is_online")

    def get_is_online(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        if not obj.last_seen:
            return False
        return (timezone.now() - obj.last_seen) <= timedelta(seconds=120)


class ChatGroupSerializer(serializers.ModelSerializer):
    owner_info = UserMiniSerializer(source="owner", read_only=True)
    members_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatGroup
        fields = ("id", "name", "created_at", "owner", "owner_info", "members_count", "last_message")

    def get_members_count(self, obj):
        return obj.members.count()

    def get_last_message(self, obj):
        last = obj.messages.order_by("-created_at").first()
        if not last:
            return None
        return {
            "id": last.id,
            "text": last.text,
            "created_at": last.created_at,
            "sender": last.sender_id,
        }


class ChatGroupMessageSerializer(serializers.ModelSerializer):
    sender_info = UserMiniSerializer(source="sender", read_only=True)

    class Meta:
        model = ChatGroupMessage
        fields = ("id", "group", "sender", "sender_info", "text", "created_at")
        read_only_fields = ("group", "sender", "created_at")
