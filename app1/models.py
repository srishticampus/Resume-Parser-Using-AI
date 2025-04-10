from django.db import models

# Create your models here.

from django.db import models

class JobApplication(models.Model):
    SUBJECT_CHOICES = [
        ('Information Technology', 'Information Technology'),
        ('Software Development', 'Software Development'),
        ('Human Resources (HR)', 'Human Resources (HR)'),
        ('Marketing & Advertising', 'Marketing & Advertising'),
        ('Sales & Business Development', 'Sales & Business Development'),
        ('Customer Support', 'Customer Support'),
        ('Creative & Design', 'Creative & Design'),
    ]

    name = models.CharField(max_length=100,unique=True)
    email = models.EmailField(unique=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    message = models.TextField()

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    


class ExtractDetails(models.Model):
    resume = models.ForeignKey(JobApplication, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    total_experience = models.CharField(max_length=50)  # Example: "7 years 7 months"
    key_skills = models.TextField()  # Stores multiple skills as a text
    degree = models.CharField(max_length=255)  # Example: "BE in Electronics and Communication"
    additional_qualification = models.CharField(max_length=255, null=True, blank=True)  # Example: "Diploma in Embedded System"
    location = models.TextField()  # Can store address as a long string
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

class SelectedCandidate(models.Model):
    candidate = models.ForeignKey(ExtractDetails, on_delete=models.CASCADE)
    selected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.candidate.full_name