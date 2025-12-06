from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Complaint


# --------------------------------------------------------------------------- #
#                                Custom User Admin                            #
# --------------------------------------------------------------------------- #

class UserAdmin(BaseUserAdmin):
    # You removed username -> must override everything related to username
    ordering = ["email"]
    list_display = (
        "email",
        "client_number",
        "first_name",
        "last_name",
        "phone_number",
        "service_type",
        "user_type",
        "is_active",
        "is_staff",
    )

    list_filter = ("service_type", "user_type", "is_staff", "is_superuser", "is_active")

    search_fields = ("email", "client_number", "first_name", "last_name", "phone_number")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {
            "fields": (
                "client_number",
                "first_name",
                "last_name",
                "phone_number",
                "fix_phone_number",
                "address",
                "service_type",
                "user_type",
            )
        }),
        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        (_("Important dates"), {"fields": ("last_login",)}),
    )

    # For create form
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "client_number",
                "password1",
                "password2",
                "service_type",
                "user_type",
                "is_staff",
                "is_superuser",
            ),
        }),
    )


admin.site.register(User, UserAdmin)


# --------------------------------------------------------------------------- #
#                                Complaint Admin                              #
# --------------------------------------------------------------------------- #

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reference_code",
        "user",
        "complaint_type",
        "service_type",
        "status",
        "created_at",
    )

    search_fields = ("reference_code", "user__email", "user__client_number")
    list_filter = ("complaint_type", "service_type", "status", "created_at")
    
    readonly_fields = ("reference_code", "created_at", "updated_at")

