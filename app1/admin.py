from django.contrib import admin

from .models import JobApplication,ExtractDetails



@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'resume', 'submitted_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('subject', 'submitted_at')


@admin.register(ExtractDetails)
class ExtractDetailsAdmin(admin.ModelAdmin):
    list_display = ("full_name", "total_experience", "key_skills", "degree", "location")
    search_fields = ("full_name", "total_experience", "key_skills", "degree", "location")
    list_filter = ("total_experience", "degree", "location")