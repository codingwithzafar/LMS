from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse, Http404
import os

from users.permissions import IsAdmin, IsTeacher, IsStudent
from .models import Group, GroupStudent, Homework, HomeworkSubmission
from django.utils import timezone

from .serializers import (
    GroupSerializer,
    GroupForStudentSerializer,
    CreateTeacherSerializer,
    CreateStudentSerializer,
    HomeworkSerializer,
    HomeworkCreateSerializer,
    HomeworkSubmissionSerializer,
    HomeworkSubmitSerializer,
    HomeworkGradeSerializer,
    ContactSerializer,
)

User = get_user_model()


def _download_file(file_field, filename: str | None = None):
    """Return a secure download response for a FileField."""
    if not file_field:
        raise Http404("File not found")

    path = getattr(file_field, "path", None)
    if not path or not os.path.exists(path):
        raise Http404("File not found")

    resp = FileResponse(open(path, "rb"), as_attachment=True)
    if filename:
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


# -------------------------
# ADMIN
# -------------------------
class AdminCreateTeacherView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = CreateTeacherSerializer


# -------------------------
# TEACHER
# -------------------------
class TeacherDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        groups = (
            Group.objects.filter(teacher=request.user, is_active=True)
            .prefetch_related("schedules", "members")
            .order_by("group_number", "name")
        )
        return Response(
            {
                "teacher": {"id": request.user.id, "full_name": request.user.full_name, "username": request.user.username},
                "groups": GroupSerializer(groups, many=True).data,
            }
        )


class TeacherContactsView(APIView):
    """Teacher: o'z gruppasidagi o'quvchilar ro'yxati (chat contacts)."""

    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        # active students in teacher's active groups
        student_ids = GroupStudent.objects.filter(
            group__teacher=request.user, is_active=True, group__is_active=True
        ).values_list("student_id", flat=True).distinct()

        qs = User.objects.filter(id__in=student_ids, role="STUDENT").order_by("full_name", "username")
        return Response(ContactSerializer(qs, many=True).data)


class TeacherCreateStudentView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = CreateStudentSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


# --- TEACHER: create homework (link + zip/file) ---
class TeacherHomeworkCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = HomeworkCreateSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        group_number = int(serializer.validated_data.pop("group_number"))
        group = Group.objects.filter(teacher=self.request.user, group_number=group_number, is_active=True).first()
        if not group:
            raise PermissionDenied("Group number noto‘g‘ri yoki bu group sizniki emas.")
        serializer.save(teacher=self.request.user, group=group)


class TeacherHomeworkListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = HomeworkSerializer

    def get_queryset(self):
        return Homework.objects.filter(teacher=self.request.user).order_by("-created_at")


class TeacherHomeworkSubmissionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = HomeworkSubmissionSerializer

    def get_queryset(self):
        homework_id = self.kwargs["homework_id"]
        hw = Homework.objects.filter(id=homework_id, teacher=self.request.user).first()
        if not hw:
            raise PermissionDenied("Not your homework.")
        return HomeworkSubmission.objects.filter(homework=hw).order_by("-submitted_at")


class TeacherGradeSubmissionView(APIView):
    """Teacher: submissionga 1-5 baho va izoh yozadi."""

    permission_classes = [IsAuthenticated, IsTeacher]

    def patch(self, request, submission_id):
        sub = HomeworkSubmission.objects.select_related("homework", "homework__group").filter(id=submission_id).first()
        if not sub:
            raise ValidationError("Submission not found.")

        # faqat o'z homeworklariga baho qo'ya oladi
        if sub.homework.teacher_id != request.user.id:
            raise PermissionDenied("Not your homework.")

        ser = HomeworkGradeSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)

        if "grade" in ser.validated_data:
            sub.grade = ser.validated_data.get("grade")
        if "teacher_comment" in ser.validated_data:
            sub.teacher_comment = ser.validated_data.get("teacher_comment", "")

        sub.graded_by = request.user
        sub.graded_at = timezone.now()
        sub.save()

        return Response(HomeworkSubmissionSerializer(sub).data)


class TeacherHomeworkSubmissionGradeView(generics.UpdateAPIView):
    """Teacher baho + komment qo'yishi (1-5)."""

    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = HomeworkGradeSerializer

    def get_queryset(self):
        # only submissions for my homeworks
        return HomeworkSubmission.objects.filter(homework__teacher=self.request.user)

    def perform_update(self, serializer):
        serializer.save(graded_by=self.request.user, graded_at=timezone.now())


# -------------------------
# STUDENT
# -------------------------
class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        group_ids = GroupStudent.objects.filter(student=request.user, is_active=True).values_list("group_id", flat=True)
        groups = Group.objects.filter(id__in=group_ids, is_active=True).prefetch_related("schedules").select_related("teacher")
        return Response(
            {
                "student": {"id": request.user.id, "full_name": request.user.full_name, "username": request.user.username},
                "groups": GroupForStudentSerializer(groups, many=True).data,
            }
        )


class StudentHomeworkListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = HomeworkSerializer

    def get_queryset(self):
        group_ids = GroupStudent.objects.filter(student=self.request.user, is_active=True).values_list("group_id", flat=True)
        return Homework.objects.filter(group_id__in=group_ids).order_by("-created_at")


class StudentHomeworkSubmitView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = HomeworkSubmitSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        homework_id = self.kwargs["homework_id"]
        hw = Homework.objects.select_related("group").filter(id=homework_id).first()
        if not hw:
            raise ValidationError("Homework not found.")

        allowed = GroupStudent.objects.filter(group=hw.group, student=self.request.user, is_active=True).exists()
        if not allowed:
            raise PermissionDenied("You are not in this group.")

        if HomeworkSubmission.objects.filter(homework=hw, student=self.request.user).exists():
            raise ValidationError("You already submitted this homework.")

        serializer.save(homework=hw, student=self.request.user)


class StudentMySubmissionsView(generics.ListAPIView):
    """Student: o'zi topshirgan vazifalar (grade/izoh bilan)."""

    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = HomeworkSubmissionSerializer

    def get_queryset(self):
        return HomeworkSubmission.objects.filter(student=self.request.user).select_related(
            "homework", "graded_by", "student"
        ).order_by("-submitted_at")


# -------------------------
# FILE DOWNLOADS (Teacher <-> Student)
# -------------------------
class HomeworkAttachmentDownloadView(APIView):
    """Download teacher's homework attachment.

    - Teacher can download own homework attachment
    - Student can download if they are an active member of the homework group
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, homework_id):
        hw = Homework.objects.select_related("group", "teacher").filter(id=homework_id).first()
        if not hw:
            raise Http404("Homework not found")

        # teacher: ok
        if request.user.role == "TEACHER" and hw.teacher_id == request.user.id:
            return _download_file(hw.attachment, filename=os.path.basename(hw.attachment.name))

        # student: must be in the group
        if request.user.role == "STUDENT":
            allowed = GroupStudent.objects.filter(group=hw.group, student=request.user, is_active=True).exists()
            if not allowed:
                raise PermissionDenied("You are not in this group.")
            return _download_file(hw.attachment, filename=os.path.basename(hw.attachment.name))

        raise PermissionDenied("You don't have permission to download this file.")


class SubmissionFileDownloadView(APIView):
    """Download student's submission file.

    - Teacher can download submission file if submission belongs to their homework
    - Student can download own submission file
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, submission_id):
        sub = (
            HomeworkSubmission.objects.select_related("homework", "homework__teacher", "student")
            .filter(id=submission_id)
            .first()
        )
        if not sub:
            raise Http404("Submission not found")

        # teacher: only own homework
        if request.user.role == "TEACHER" and sub.homework.teacher_id == request.user.id:
            return _download_file(sub.file, filename=os.path.basename(sub.file.name))

        # student: only own
        if request.user.role == "STUDENT" and sub.student_id == request.user.id:
            return _download_file(sub.file, filename=os.path.basename(sub.file.name))

        raise PermissionDenied("You don't have permission to download this file.")
