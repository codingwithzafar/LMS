from django.urls import path
from .views import (
    ThreadListView, ThreadStartView, MessageListCreateView,
    TeacherContactsView,
    ChatGroupListCreateView, ChatGroupAddMembersView, ChatGroupMessageListCreateView,
)

urlpatterns = [
    path("threads/", ThreadListView.as_view(), name="threads_list"),
    path("threads/start/", ThreadStartView.as_view(), name="threads_start"),
    path("threads/<int:thread_id>/messages/", MessageListCreateView.as_view(), name="messages_list_create"),

    path("contacts/", TeacherContactsView.as_view(), name="teacher_contacts"),
    path("groups/", ChatGroupListCreateView.as_view(), name="chat_groups_list_create"),
    path("groups/<int:group_id>/members/", ChatGroupAddMembersView.as_view(), name="chat_groups_add_members"),
    path("groups/<int:group_id>/messages/", ChatGroupMessageListCreateView.as_view(), name="chat_groups_messages"),
]
