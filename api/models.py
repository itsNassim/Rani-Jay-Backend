from django.db import models
from django.contrib.auth.models import AbstractUser

from .managers import *


#-----------------------------------------------------------------------------#
#----------------------------------User Model---------------------------------#
#-----------------------------------------------------------------------------#

class ServiceType(models.TextChoices):
    ADSL = "ADSL", "ADSL"
    FTTH = "FTTH", "FTTH"


class UserType(models.TextChoices):
    SIMPLE = "SIMPLE", "Simple user"
    COMPANY = "COMPANY", "Company"


class User(AbstractUser):
    # Already provided by AbstractUser:
    # username, first_name, last_name, email, password, is_staff, is_superuser ...

    client_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Algeria Telecom client / account number"
    )
    fix_phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Landline / fixed phone number"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Mobile phone number"
    )
    address = models.CharField(max_length=255, blank=True)

    service_type = models.CharField(
        max_length=10,
        choices=ServiceType.choices,
        default=ServiceType.ADSL,
    )

    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.SIMPLE,
        help_text="Simple user or company"
    )

    # Optional: for soft delete / tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # If you want email to be the main identifier:
    email = models.EmailField(unique=True)
    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["client_number"]
    objects = UserManager()  

    def __str__(self):
        return f"{self.email} ({self.client_number})"

#-----------------------------------------------------------------------------#
#-----------------------------Complaint Model---------------------------------#
#-----------------------------------------------------------------------------#
class ComplaintType(models.TextChoices):
    INTERNET_DOWN = "INTERNET_DOWN", "No internet"
    SLOW_SPEED = "SLOW_SPEED", "Slow speed"
    PHONE_ISSUE = "PHONE_ISSUE", "Phone issue"
    BILLING = "BILLING", "Billing / invoice"
    OTHER = "OTHER", "Other"


class ComplaintStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    RESOLVED = "RESOLVED", "Resolved"
    # OPEN = "OPEN", "Open"
    # CLOSED = "CLOSED", "Closed"
    # REJECTED = "REJECTED", "Rejected"

class ComplaintServiceType(models.TextChoices):
    ADSL = "ADSL", "ADSL"
    FTTH = "FTTH", "FTTH"
    PHONE = "PHONE", "Fixed Phone"



def complaint_photo_upload_path(instance, filename):
    # e.g. complaints/123/filename.jpg
    return f"complaints/{instance.id or 'new'}/{filename}"


class Complaint(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="complaints"
    )

    complaint_type = models.CharField(
        max_length=30,
        choices=ComplaintType.choices,
        default=ComplaintType.INTERNET_DOWN,
    )

    description = models.TextField()

    # one photo for now; you can change to a separate Attachment model later
    photo = models.ImageField(
        upload_to=complaint_photo_upload_path,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)   # your "time"
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=20,
        choices=ComplaintStatus.choices,
        default=ComplaintStatus.IN_PROGRESS,
    )


    service_type = models.CharField(
        max_length=20,
        choices=ComplaintServiceType.choices,
        default=ComplaintServiceType.ADSL,
    )

    # Optional reference number to show to the user
    reference_code = models.CharField(
        max_length=20,
        blank=True,
        unique=True,
        help_text="Ticket number shown to the client"
    )

    def generate_reference_code(self):
        import uuid

        return "AT" + str(uuid.uuid4()).split("-")[0].upper()
    
    def save(self, *args, **kwargs):
        # Generate code only when complaint is first created
        if not self.reference_code:
            self.reference_code = self.generate_reference_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.id} - {self.complaint_type} - {self.status}"
