from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Extra", {"fields": ("role", "full_name")}),
    )
    list_display = ("username", "full_name", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
