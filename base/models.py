from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
import uuid



# Custom user manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("authority", "Authority"),
        ("stakeholder", "Stakeholder"),
        ("citizen", "Citizen"),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    # Authority/Stakeholder fields
    designation = models.CharField(max_length=100, blank=True, null=True)
    organization = models.CharField(max_length=100, blank=True, null=True)
    # Citizen field
    national_id = models.CharField(max_length=20, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'role']

    objects = UserManager()

    def __str__(self):
        return f"{self.get_role_display()}: {self.email}"




class Location(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.CharField(max_length=100)
    geom = gis_models.GeometryField()  # Accepts LINESTRING or POLYGON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Location: ({self.city})"



class Work(models.Model):
    TAG_CHOICES = [
        ("Emergency", "Emergency"),
        ("Regular", "Regular"),
    ]
    STATUS_CHOICES = [
        ("ProposedByAdmin", "ProposedByAdmin"),
        ("ProposedByStakeholder", "ProposedByStakeholder"),
        ("Declined", "Declined"),
        ("Planned", "Planned"),
        ("Ongoing", "Ongoing"),
        ("Completed", "Completed"),
    ]
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stakeholder = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    tag = models.CharField(max_length=20, choices=TAG_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    estimated_time = models.DurationField(help_text="Estimated time required for completion")
    proposed_start_date = models.DateField()
    proposed_end_date = models.DateField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    conflicts = models.ManyToManyField('self', null=True, blank=True, default=None)  # Self-referential ManyToManyField to indicate conflicts

    def __str__(self):
        return f"Work: {self.name} at {self.location.name if self.location else 'N/A'}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.location and self.location.geom:
            conflicts_qs = Work.objects.exclude(pk=self.pk).filter(location__geom__intersects=self.location.geom)
            self.conflicts.set(conflicts_qs)


class Notice(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ordinance_no = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notices_notice')
    attached_file = models.FileField(upload_to='notices/', blank=True, null=True)

    def __str__(self):
        return f"Notice: {self.name} ({self.ordinance_no})"



class Notification(models.Model):
    GENRE_CHOICES = [
        ("Info", "Info"),
        ("Warning", "Warning"),
        ("Alert", "Alert"),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_created')
    created_for = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_received')
    related_work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)

    def __str__(self):
        return f"Notification: {self.genre} ({self.uuid})"


class Feedback(models.Model):
    FEELING_CHOICES = [
        ("Excellent", "Excellent"),
        ("Good", "Good"),
        ("Average", "Average"),
        ("Poor", "Poor"),
        ("Terrible", "Terrible"),
    ]
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_created')
    details = models.TextField(blank=True)
    feeling = models.CharField(max_length=20, choices=FEELING_CHOICES)
    related_work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='feedback', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Feedback: {self.feeling} by {self.created_by.email}"
    

class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ("WorkProgress", "WorkProgress"),
        ("Issue", "Issue"),
        ("Suggestion", "Suggestion"),
    ]

    STATUS_CHOICES = [
        ("Open", "Open"),
        ("InProgress", "InProgress"),
        ("Resolved", "Resolved"),
        ("Closed", "Closed"),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_created')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    related_work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)

    def __str__(self):
        return f"Report: {self.report_type} by {self.created_by.email}"