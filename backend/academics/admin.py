from django.contrib import admin
from .models import Group, GroupSchedule, GroupStudent, Homework, HomeworkSubmission


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "group_number", "name", "teacher", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "group_number", "teacher__username", "teacher__full_name")


@admin.register(GroupSchedule)
class GroupScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "day_of_week", "start_time", "end_time", "room")
    list_filter = ("day_of_week", "room")
    search_fields = ("group__name",)


@admin.register(GroupStudent)
class GroupStudentAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "student", "is_active", "joined_at")
    list_filter = ("is_active",)
    search_fields = ("group__name", "student__username", "student__full_name")


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "teacher", "title", "created_at", "due_date")
    search_fields = ("title", "group__name", "teacher__username")
    list_filter = ("created_at",)


@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "homework", "student", "submitted_at")
    search_fields = ("homework__title", "student__username", "student__full_name")
    list_filter = ("submitted_at",)
