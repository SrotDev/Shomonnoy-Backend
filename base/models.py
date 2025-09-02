from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid

class BaseUser(models.Model):
    """Abstract user base (no superuser fields)"""

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # store hashed password
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)



class Authority(BaseUser):
    designation = models.CharField(max_length=100)  # e.g., Mayor, Ward Commissioner
    organization = models.CharField(max_length=100)  # e.g., City Corporation, LGED, DMP

    def __str__(self):
        return f"Authority: {self.email}"



class Stakeholder(BaseUser):
    designation = models.CharField(max_length=100)  # e.g., Manager, Engineer
    organization = models.CharField(max_length=100)  # e.g., WASA, DESCO, etc.

    def __str__(self):
        return f"Stakeholder: {self.email}"



class Citizen(BaseUser):
    national_id = models.CharField(max_length=20)

    def __str__(self):
        return f"Citizen: {self.email}"
