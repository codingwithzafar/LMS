from rest_framework import serializers
from django.contrib.auth import get_user_model
from messaging.models import MessageThread

from .models import (
    Group,
    GroupSchedule,
    GroupStudent,
    Homework,
    HomeworkSubmission,
)

User = get_user_model()


class GroupScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupSchedule
        fields = ("id", "day_of_week", "start_time", "end_time", "room")


class TeacherInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "full_name")


class ContactSerializer(serializers.ModelSerializer):
    is_online = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "full_name", "last_seen", "is_online")

    def get_is_online(self, obj):
        # online: last 2 minutes
        last = getattr(obj, "last_seen", None)
        if not last:
            return False
        from django.utils import timezone

        return (timezone.now() - last).total_seconds() <= 120


class GroupSerializer(serializers.ModelSerializer):
    schedules = GroupScheduleSerializer(many=True, read_only=True)
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ("id", "name", "group_number", "teacher", "is_active", "schedules", "students_count")

    def get_students_count(self, obj):
        return obj.members.filter(is_active=True).count()


class GroupForStudentSerializer(serializers.ModelSerializer):
    schedules = GroupScheduleSerializer(many=True, read_only=True)
    teacher_info = TeacherInfoSerializer(source="teacher", read_only=True)

    class Meta:
        model = Group
        fields = ("id", "name", "group_number", "teacher_info", "schedules")


class CreateTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "full_name")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data, role="TEACHER")
        user.set_password(password)
        user.save()
        return user


class CreateStudentSerializer(serializers.ModelSerializer):
    # ✅ endi group_id emas, group_number
    group_number = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "password", "full_name", "group_number")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        group_number = int(validated_data.pop("group_number"))
        password = validated_data.pop("password")

        request = self.context.get("request")
        if not request or not request.user or request.user.role != "TEACHER":
            raise serializers.ValidationError({"detail": "Only TEACHER can create students."})

        group = Group.objects.filter(
            teacher=request.user, group_number=group_number, is_active=True
        ).first()
        if not group:
            raise serializers.ValidationError({"detail": "Group number noto‘g‘ri yoki bu group sizniki emas."})

        if User.objects.filter(username=validated_data.get("username")).exists():
            raise serializers.ValidationError({"detail": "Username already exists"})

        user = User(**validated_data, role="STUDENT")
        user.set_password(password)
        user.save()
        GroupStudent.objects.create(group=group, student=user)
        # ✅ auto-create chat thread between teacher and student
        MessageThread.objects.get_or_create(teacher=request.user, student=user)
        return user


class HomeworkSerializer(serializers.ModelSerializer):
    submissions_count = serializers.SerializerMethodField()

    class Meta:
        model = Homework
        fields = (
            "id",
            "group",
            "teacher",
            "title",
            "description",
            "link",
            "attachment",
            "due_date",
            "created_at",
            "submissions_count",
        )

    def get_submissions_count(self, obj):
        return obj.submissions.count()


class HomeworkCreateSerializer(serializers.ModelSerializer):
    # ✅ create paytida group_number yuboriladi
    group_number = serializers.IntegerField(write_only=True)

    class Meta:
        model = Homework
        fields = ("id", "group_number", "title", "description", "link", "attachment", "due_date")


class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    student_info = TeacherInfoSerializer(source="student", read_only=True)
    graded_by_info = TeacherInfoSerializer(source="graded_by", read_only=True)

    class Meta:
        model = HomeworkSubmission
        fields = (
            "id",
            "homework",
            "student_info",
            "text_answer",
            "file",
            "submitted_at",
            "grade",
            "teacher_comment",
            "graded_by_info",
            "graded_at",
        )


class HomeworkSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkSubmission
        fields = ("id", "text_answer", "file")


class HomeworkGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkSubmission
        fields = ("grade", "teacher_comment")

    def validate_grade(self, value):
        if value is None:
            return value
        if not (1 <= int(value) <= 5):
            raise serializers.ValidationError("grade must be 1..5")
        return value
