from django.contrib import admin

from .models import JobApplication,ExtractDetails,SelectedCandidate



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


@admin.register(SelectedCandidate)
class SelectedCandidateAdmin(admin.ModelAdmin):
    list_display = ("candidate", "selected_at")
    search_fields = ("candidate__full_name",)
    list_filter = ("selected_at",)