from django.contrib import admin
from .models import User, Location, Work, Notice, Notification, Feedback, Report


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ("uuid", "email", "name", "role", "designation", "organization", "national_id", "phone_number", "city", "created_at", "updated_at", "is_active")
	search_fields = ("email", "name", "role", "designation", "organization", "national_id", "phone_number", "city")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
	list_display = ("uuid", "city", "geom", "created_at", "updated_at")
	search_fields = ("city",)


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
	list_display = ("uuid", "stakeholder", "location", "name", "tag", "status", "estimated_time", "proposed_start_date", "proposed_end_date", "start_date", "end_date", "budget", "created_at", "updated_at")
	search_fields = ("name", "details", "tag", "status")


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
	list_display = ("uuid", "ordinance_no", "name", "created_by", "created_at", "updated_at")
	search_fields = ("name", "ordinance_no", "details", "created_by__email", "created_by__name")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ("uuid", "genre", "is_read", "created_by", "created_for", "details", "created_at", "updated_at")
	search_fields = ("created_by__email", "created_by__name", "details")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
	list_display = ("uuid", "created_by", "feeling", "details", "related_work", "created_at", "updated_at")
	search_fields = ("created_by__email", "created_by__name", "feeling", "details", "related_work__name")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
	list_display = ("uuid", "created_by", "report_type", "details", "status", "related_work", "created_at", "updated_at")
	search_fields = ("created_by__email", "created_by__name", "report_type", "details", "status", "related_work__name")