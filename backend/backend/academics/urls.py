from django.urls import path

from .views import (
    AdminCreateTeacherView,
    TeacherDashboardView,
    TeacherContactsView,
    TeacherCreateStudentView,
    TeacherHomeworkCreateView,
    TeacherHomeworkListView,
    TeacherHomeworkSubmissionsView,
    TeacherGradeSubmissionView,
    StudentDashboardView,
    StudentHomeworkListView,
    StudentHomeworkSubmitView,
    StudentMySubmissionsView,
    HomeworkAttachmentDownloadView,
    SubmissionFileDownloadView,
)

urlpatterns = [
    # dashboards
    path("teacher/dashboard/", TeacherDashboardView.as_view()),
    path("teacher/contacts/", TeacherContactsView.as_view()),
    path("student/dashboard/", StudentDashboardView.as_view()),

    # admin
    path("admin/teachers/", AdminCreateTeacherView.as_view()),

    # teacher: create student + homeworks
    path("teacher/students/", TeacherCreateStudentView.as_view()),
    path("teacher/homeworks/", TeacherHomeworkListView.as_view()),
    path("teacher/homeworks/create/", TeacherHomeworkCreateView.as_view()),
    path("teacher/homeworks/<int:homework_id>/submissions/", TeacherHomeworkSubmissionsView.as_view()),
    path("teacher/submissions/<int:submission_id>/grade/", TeacherGradeSubmissionView.as_view()),

    # student: homeworks
    path("student/homeworks/", StudentHomeworkListView.as_view()),
    path("student/homeworks/<int:homework_id>/submit/", StudentHomeworkSubmitView.as_view()),
    path("student/submissions/", StudentMySubmissionsView.as_view()),

    # downloads
    path("files/homeworks/<int:homework_id>/attachment/", HomeworkAttachmentDownloadView.as_view()),
    path("files/submissions/<int:submission_id>/file/", SubmissionFileDownloadView.as_view()),
]
