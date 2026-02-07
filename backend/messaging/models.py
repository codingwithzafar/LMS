from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class MessageThread(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="threads_as_teacher")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="threads_as_student")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("teacher","student")

class Message(models.Model):
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


class ChatGroup(models.Model):
    """Teacher creates a group chat and adds students."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_chat_groups")
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (#{self.id})"


class ChatGroupMember(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_group_memberships")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("group", "user")

    def __str__(self):
        return f"{self.group_id} -> {self.user_id}"


class ChatGroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_messages_sent")
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.group_id} {self.sender_id} {self.created_at}"
