from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import MessageThread, Message, ChatGroup, ChatGroupMember, ChatGroupMessage
from .serializers import ThreadSerializer, MessageSerializer, ContactSerializer, ChatGroupSerializer, ChatGroupMessageSerializer


def _ensure_member(thread: MessageThread, user):
    if thread.teacher_id != user.id and thread.student_id != user.id:
        raise PermissionDenied("You are not a member of this thread.")


class ThreadListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ThreadSerializer

    def get_queryset(self):
        u = self.request.user
        # prefetch messages to compute last_message cheaply
        return (
            MessageThread.objects
            .filter(Q(teacher=u) | Q(student=u))
            .prefetch_related("messages")
            .order_by("-created_at")
        )


class ThreadStartView(APIView):
    """Create (or get) a thread between current user and other user.
    Teacher starts with student_id, Student starts with teacher_id.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        other_id = request.data.get("other_user_id")
        if not other_id:
            raise ValidationError({"other_user_id": "This field is required."})

        u = request.user
        # roles
        if u.role == "TEACHER":
            teacher_id = u.id
            student_id = int(other_id)
        elif u.role == "STUDENT":
            teacher_id = int(other_id)
            student_id = u.id
        else:
            raise PermissionDenied("Only TEACHER or STUDENT can start chats.")

        thread, _ = MessageThread.objects.get_or_create(
            teacher_id=teacher_id,
            student_id=student_id,
        )
        return Response(ThreadSerializer(thread, context={"request": request}).data)


class MessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def _get_thread(self):
        thread_id = self.kwargs["thread_id"]
        try:
            return MessageThread.objects.get(id=thread_id)
        except MessageThread.DoesNotExist:
            raise ValidationError({"thread_id": "Thread not found"})

    def get_queryset(self):
        thread = self._get_thread()
        _ensure_member(thread, self.request.user)
        return Message.objects.filter(thread=thread).select_related("sender").order_by("created_at")

    def perform_create(self, serializer):
        thread = self._get_thread()
        _ensure_member(thread, self.request.user)
        serializer.save(thread=thread, sender=self.request.user)


from academics.models import GroupStudent
from rest_framework.exceptions import PermissionDenied


class TeacherContactsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        if u.role != "TEACHER":
            raise PermissionDenied("Only TEACHER can access contacts.")
        student_ids = (
            GroupStudent.objects
            .filter(group__teacher=u, is_active=True)
            .values_list("student_id", flat=True)
            .distinct()
        )
        qs = User.objects.filter(id__in=student_ids).order_by("full_name", "username")
        return Response(ContactSerializer(qs, many=True, context={"request": request}).data)


def _ensure_group_member(group: ChatGroup, user):
    if not ChatGroupMember.objects.filter(group=group, user=user).exists():
        raise PermissionDenied("You are not a member of this group.")


class ChatGroupListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        group_ids = ChatGroupMember.objects.filter(user=u).values_list("group_id", flat=True)
        qs = ChatGroup.objects.filter(id__in=group_ids).prefetch_related("members", "messages").order_by("-created_at")
        return Response(ChatGroupSerializer(qs, many=True, context={"request": request}).data)

    def post(self, request):
        u = request.user
        if u.role != "TEACHER":
            raise PermissionDenied("Only TEACHER can create groups.")
        name = (request.data.get("name") or "").strip()
        member_ids = request.data.get("member_ids") or []
        if not name:
            raise ValidationError({"name": "Group name is required."})

        allowed_ids = set(
            GroupStudent.objects.filter(group__teacher=u, is_active=True).values_list("student_id", flat=True)
        )
        member_ids = [int(x) for x in member_ids]
        for sid in member_ids:
            if sid not in allowed_ids:
                raise PermissionDenied("You can only add your own students.")

        group = ChatGroup.objects.create(owner=u, name=name)
        ChatGroupMember.objects.get_or_create(group=group, user=u)
        for sid in member_ids:
            ChatGroupMember.objects.get_or_create(group=group, user_id=sid)

        return Response(ChatGroupSerializer(group, context={"request": request}).data, status=201)


class ChatGroupAddMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        u = request.user
        try:
            group = ChatGroup.objects.get(id=group_id)
        except ChatGroup.DoesNotExist:
            raise ValidationError({"group_id": "Group not found"})

        if u.role != "TEACHER" or group.owner_id != u.id:
            raise PermissionDenied("Only group owner teacher can add members.")

        member_ids = request.data.get("member_ids") or []
        member_ids = [int(x) for x in member_ids]

        allowed_ids = set(
            GroupStudent.objects.filter(group__teacher=u, is_active=True).values_list("student_id", flat=True)
        )
        for sid in member_ids:
            if sid not in allowed_ids:
                raise PermissionDenied("You can only add your own students.")
            ChatGroupMember.objects.get_or_create(group=group, user_id=sid)

        return Response({"ok": True, "added": member_ids})


class ChatGroupMessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        try:
            group = ChatGroup.objects.get(id=group_id)
        except ChatGroup.DoesNotExist:
            raise ValidationError({"group_id": "Group not found"})
        _ensure_group_member(group, request.user)
        qs = ChatGroupMessage.objects.filter(group=group).select_related("sender").order_by("created_at")
        return Response(ChatGroupMessageSerializer(qs, many=True, context={"request": request}).data)

    def post(self, request, group_id):
        try:
            group = ChatGroup.objects.get(id=group_id)
        except ChatGroup.DoesNotExist:
            raise ValidationError({"group_id": "Group not found"})
        _ensure_group_member(group, request.user)

        text = (request.data.get("text") or "").strip()
        if not text:
            raise ValidationError({"text": "Message text is required."})

        msg = ChatGroupMessage.objects.create(group=group, sender=request.user, text=text)
        return Response(ChatGroupMessageSerializer(msg, context={"request": request}).data, status=201)
