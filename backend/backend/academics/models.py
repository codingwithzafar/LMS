from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Group(models.Model):
    name = models.CharField(max_length=120)
    # ✅ teacher uchun qulay raqam (101, 102, ...)
    group_number = models.PositiveIntegerField(default=1)

    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teaching_groups",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "group_number"],
                name="uniq_teacher_group_number",
            )
        ]

    def __str__(self):
        tn = getattr(self, "teacher_id", None)
        # teacher bo'lmasa ham ko'rinishi uchun
        return f"{self.group_number} - {self.name}"


class GroupSchedule(models.Model):
    DAYS = [(0, "Mon"), (1, "Tue"), (2, "Wed"), (3, "Thu"), (4, "Fri"), (5, "Sat"), (6, "Sun")]
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.IntegerField(choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.group} {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class GroupStudent(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="members")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_groups")
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("group", "student")

    def __str__(self):
        return f"{self.group} -> {self.student}"


class Homework(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="homeworks")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="homeworks_created")

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # ✅ link + zip/file
    link = models.URLField(blank=True)
    attachment = models.FileField(upload_to="homework_attachments/", null=True, blank=True)

    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.group} - {self.title}"


class HomeworkSubmission(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="homework_submissions")

    text_answer = models.TextField(blank=True)
    file = models.FileField(upload_to="submissions/", null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # ✅ teacher baholashi
    grade = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5
    teacher_comment = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="graded_submissions",
    )
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("homework", "student")

    def __str__(self):
        return f"{self.homework} -> {self.student}"
