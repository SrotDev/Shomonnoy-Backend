
from django.contrib import admin
from .models import Authority, Stakeholder, Citizen

@admin.register(Authority)
class AuthorityAdmin(admin.ModelAdmin):
	list_display = ("uuid", "email", "name", "designation", "organization", "phone_number", "city", "created_at", "updated_at", "is_active")
	search_fields = ("email", "name", "designation", "organization", "phone_number", "city")

@admin.register(Stakeholder)
class StakeholderAdmin(admin.ModelAdmin):
	list_display = ("uuid", "email", "name", "designation", "organization", "phone_number", "city", "created_at", "updated_at", "is_active")
	search_fields = ("email", "name", "designation", "organization", "phone_number", "city")

@admin.register(Citizen)
class CitizenAdmin(admin.ModelAdmin):
	list_display = ("uuid", "email", "name", "national_id", "phone_number", "city", "created_at", "updated_at", "is_active")
	search_fields = ("email", "name", "national_id", "phone_number", "city")
