from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.views import logout_then_login



# Create your views here.
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect("admin_dashboard")
        else:
                messages.error(request, "Need admin credentials to access this page.")
                
    return render(request, "admin_login.html")

def admin_logout(request):
    logout(request)
    return redirect("admin_login")


def index(request):

    return render (request , 'index.html')

def career(request):

    return render (request , 'career.html')

import os
from django.shortcuts import render, redirect
from .models import JobApplication, ExtractDetails
from .resume_parser import process_resume, extract_filtered_details_with_gemini  # Import resume parsing functions
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages



def job_application_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        resume_file = request.FILES.get('resume')  # Get uploaded file


        send_mail(
            subject=f"Application Confirmation - {subject}",
            message=f"""Dear {name},

            Thank you for applying for the {subject} position at Company Name. 

            We’ve received your application and our team is currently reviewing your profile. If your qualifications match our requirements, we’ll be in touch soon to discuss the next steps. 

            In the meantime, if you have any questions, please feel free to reach out to us at support@companyname.com.

            We appreciate your interest in joining our team and wish you the best of luck in the hiring process.

            Best regards,  
            Recruitment Team  
            DataRevel
            www.Datareveal.com  
            """,
                from_email='shihabameen386@gmail.com',
                recipient_list=[email],
                fail_silently=False,
            )

        print(f'data: name={name},email = {email},sub = {subject},resume={resume_file}')

        if not (name and email and subject and resume_file):
            return render(request, 'career.html', {'error': 'All fields are required!'})

        # Save job application
        job_application = JobApplication(
            name=name,
            email=email,
            subject=subject,
            resume=resume_file,
            message=message
        )
        job_application.save()

        # Process the uploaded resume
        resume_path = os.path.join("media/resumes", resume_file.name)
        print(f"Processing resume: {resume_path}")

        with open(resume_path, "wb+") as destination:
            for chunk in resume_file.chunks():
                destination.write(chunk)

        # Extract text and details from the resume
        extracted_text = process_resume(resume_path)
        if extracted_text:
            extracted_details = extract_filtered_details_with_gemini(extracted_text)
            # Convert extracted text to dictionary
            details_dict = {}
            lines = extracted_details.split("\n")
            for line in lines:
                if "**Full Name:**" in line:
                    details_dict["Full Name"] = line.replace("**Full Name:**", "").strip()
                elif "**Total Experience:**" in line:
                    details_dict["Total Experience"] = line.replace("**Total Experience:**", "").strip()
                elif "**Key Skills:**" in line:
                    details_dict["Key Skills"] = line.replace("**Key Skills:**", "").strip()
                elif "**Degree:**" in line:
                    details_dict["Degree"] = line.replace("**Degree:**", "").strip()
                elif "**Additional Qualification:**" in line:
                    details_dict["Additional Qualification"] = line.replace("**Additional Qualification:**", "").strip()
                elif "**Location:**" in line:
                    details_dict["Location"] = line.replace("**Location:**", "").strip()

            print(f"Parsed details: {details_dict}")  # Debugging output
            
            print(f"Extracted details: {extracted_details}")


            # Save extracted details in ExtractDetails model
            ExtractDetails.objects.create(
                resume=job_application,
                full_name=details_dict.get("Full Name", "Not Found"),
                total_experience=details_dict.get("Total Experience", "Not Found"),
                key_skills=details_dict.get("Key Skills", "Not Found"),
                degree=details_dict.get("Degree", "Not Found"),
                additional_qualification=details_dict.get("Additional Qualification", ""),
                location=details_dict.get("Location", "Not Found"),
            )

            # return render(request, 'job_applications.html', {'success': 'Application submitted successfully!'})
            messages.success(request, "Application sent successfully! Check your email for confirmation.")
        else:
            messages.error(request, "The Application is not Submitted")
    applications = JobApplication.objects.all().order_by('-submitted_at')  # Latest applications first
    return render(request, 'career.html')




# def register(request):
#     if request.method == "POST":
#         print('-----------------------cddd')
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         subject = request.POST.get('subject')
#         message = request.POST.get('message')
#         resume = request.FILES.get('resume')  # Handling uploaded file
        
#         # Save form data to the database (optional)
#         # Example: Application.objects.create(name=name, email=email, subject=subject, message=message, resume=resume)

#         # Sending Email
#         send_mail(
#             subject="Application Sent Successfully",
#             message=f"Dear {name},\n\nYour application for {subject} has been received successfully.\n\nBest Regards,\nCompany Name",
#             from_email='careers.reveal@gmail.com',
#             recipient_list=[email],
#             fail_silently=False,
#         )

#         messages.success(request, "Application sent successfully! Check your email for confirmation.")
#         return redirect('register')

#     return render(request, 'register.html')



from django.shortcuts import render
from .models import JobApplication, ExtractDetails



def admin_dashboard(request):
    # Get total number of applicants
    total_applicants = JobApplication.objects.count()
    
    # Get all extracted details (resumes) and order by latest applications
    candidates = ExtractDetails.objects.all().order_by('-resume__submitted_at')

    # Filtering based on search queries
    query = request.GET.get('q')
    if query:
        candidates = candidates.filter(
            full_name__icontains=query
        ) | candidates.filter(
            key_skills__icontains=query
        ) | candidates.filter(
            degree__icontains=query
        ) | candidates.filter(
            total_experience__icontains=query
        ) | candidates.filter(
            location__icontains=query
        )

    return render(request, 'admin_dashboard.html', {
        'total_applicants': total_applicants, 
        'candidates': candidates
    })




from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache



def manage_job_applications(request):
    applications = JobApplication.objects.all().order_by('-submitted_at')  # Latest applications first

    return render(request, 'manage_applications.html', {
        'applications': applications
    })


from django.shortcuts import render
from .models import ExtractDetails

from django.shortcuts import render
from .models import ExtractDetails

import re

import re

import re

def parse_experience(experience_str):
    """
    Extracts the numerical experience in years from a given string.
    Example Inputs:
    - "0-1 years" -> 0  (Fresher)
    - "1 year 5 months" -> 1
    - "5+ years" -> 5
    - "Fresher" -> 0
    """
    if not experience_str:
        return 0  # Default for empty values

    experience_str = experience_str.lower().strip()

    if "0-1" in experience_str or "fresher" in experience_str:
        return 0  # Treat "0-1 years" as Fresher (0 experience)

    # Extract the first number in the string (years of experience)
    match = re.search(r'(\d+)', experience_str)
    if match:
        return int(match.group(1))  # Return the extracted numeric value
    return 0  # Default to 0 if no match is found



import re
from django.shortcuts import render
from .models import ExtractDetails

# Standardized Degree Mapping
DEGREE_MAPPING = {
    "bachelor of science": "BSc",
    "master of science": "MSc",
    "be": "B.E",
    "btech": "B.Tech",
    "mtech": "M.Tech",
    "mca": "MCA",
    "mba": "MBA",
    "b tech": "B.Tech",
    "b.tech": "B.Tech",
    "m.sc": "MSc",
    "b.sc": "BSc",
    "bachelor science": "BSc",
    "master science": "MSc"
}

def normalize_degree(degree):
    """Normalize the extracted degree into a standard format (e.g., 'B.Tech')."""
    if degree:
        degree = degree.lower().strip()  # Convert to lowercase and remove extra spaces
        degree = re.sub(r"\.", "", degree)  # Remove dots (e.g., 'B.Tech' → 'BTech')
        degree = re.sub(r"\s+", " ", degree)  # Normalize spaces

        # Match against predefined degree names
        for key, value in DEGREE_MAPPING.items():
            if key in degree:
                return value  # Return standardized name (e.g., 'B.Tech')
    return degree  # Return as-is if no match is found

from django.shortcuts import render, get_object_or_404, redirect
from .models import ExtractDetails, SelectedCandidate
# from .utils import normalize_degree, parse_experience  # Assuming you have these utilities

def search_candidates(request):
    candidates = None  # Default: No candidates displayed

    # --- Handle Selection ---
    if request.method == "POST":
        candidate_id = request.POST.get("candidate_id")
        candidate = get_object_or_404(ExtractDetails, id=candidate_id)
        SelectedCandidate.objects.get_or_create(candidate=candidate)
        return redirect('search_candidates')  # Replace with your URL name

    # --- Filtering Logic ---
    name_query = request.GET.get('name', '').strip()
    location_query = request.GET.get('location', '').strip()
    experience_query = request.GET.get('experience', '').strip()
    skills_query = request.GET.get('skills', '').strip()
    degree_query = request.GET.get('degree', '').strip()

    normalized_degree_query = normalize_degree(degree_query)

    if name_query or location_query or experience_query or skills_query or degree_query:
        candidates = ExtractDetails.objects.all()

        if name_query:
            candidates = candidates.filter(full_name__icontains=name_query)
        if location_query:
            candidates = candidates.filter(location__icontains=location_query)
        if skills_query:
            candidates = candidates.filter(key_skills__icontains=skills_query)

        if degree_query:
            degree_variations = [normalized_degree_query]
            for key, value in DEGREE_MAPPING.items():
                if value == normalized_degree_query:
                    degree_variations.append(key)
            candidates = candidates.filter(degree__iregex=r"|".join(degree_variations))

        if experience_query:
            try:
                exp_value = int(experience_query)
                filtered_candidates = []
                for candidate in candidates:
                    candidate_exp = parse_experience(candidate.total_experience)
                    if exp_value == 0:
                        if candidate_exp == 0:
                            filtered_candidates.append(candidate)
                    else:
                        if candidate_exp >= exp_value:
                            filtered_candidates.append(candidate)
                candidates = filtered_candidates
            except ValueError:
                pass

    # --- Get Selected Candidates ---
    selected_candidates = SelectedCandidate.objects.all()

    return render(request, 'search_candidates.html', {
        'candidates': candidates,
        'selected_candidates': selected_candidates,
        'name_query': name_query,
        'location_query': location_query,
        'experience_query': experience_query,
        'skills_query': skills_query,
        'degree_query': degree_query,
    })

def selected_candidates_view(request):
    selected_candidates = SelectedCandidate.objects.select_related('candidate')
    
    candidate_application_map = {}
    for sc in selected_candidates:
        application = JobApplication.objects.filter(extractdetails=sc.candidate).first()
        candidate_application_map[sc.id] = application.id if application else None

    return render(request, 'selected_candidates.html', {
        'selected_candidates': selected_candidates,
        'application_ids': candidate_application_map,
    })

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import ExtractDetails

from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from .models import ExtractDetails

def send_shortlist_email(request, candidate_id):
    candidate = get_object_or_404(ExtractDetails, id=candidate_id)

    # If already sent, stop here
    if candidate.email_sent:
        messages.warning(request, f"Shortlist email has already been sent to {candidate.full_name}.")
        return redirect('candidate_detail', pk=candidate.id)

    # Send the email
    subject = "📢 You're Shortlisted for the Next Round - DataRevel"
    message = f"""Dear {candidate.full_name},

Congratulations! 🎉

Your profile has been *shortlisted* for the next phase of the selection process at **DataRevel**.

Our team was impressed with your qualifications and experience, and we look forward to speaking with you soon. A member of our recruitment team will reach out to you shortly with further steps.

If you have any questions, please feel free to contact us at support@datarevel.com.

Warm regards,  
Recruitment Team  
DataRevel  
🌐 www.datarevel.com
"""

    send_mail(
        subject=subject,
        message=message,
        from_email='shihabameen386@gmail.com',
        recipient_list=[candidate.resume.email],
        fail_silently=False,
    )

    # Mark as sent
    candidate.email_sent = True
    candidate.save()

    messages.success(request, f"Shortlist email sent to {candidate.full_name}.")
    return redirect('candidate_detail', pk=candidate.id)


def delete_selected_candidate(request, selected_candidate_id):
    if request.method == 'POST':
        candidate = get_object_or_404(SelectedCandidate, id=selected_candidate_id)
        candidate.delete()
        messages.success(request, "Candidate has been deleted successfully.")
    return redirect('selected_candidates')

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
@csrf_exempt
def select_candidate_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        candidate_id = data.get('candidate_id')

        if candidate_id:
            candidate = get_object_or_404(ExtractDetails, id=candidate_id)

            if SelectedCandidate.objects.filter(candidate=candidate).exists():
                return JsonResponse({'success': False, 'message': 'Candidate already selected.'})

            SelectedCandidate.objects.create(candidate=candidate)
            return JsonResponse({'success': True, 'message': 'Candidate selected successfully.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})

from django.shortcuts import render
from django.db.models import Count
from .models import JobApplication, ExtractDetails
import matplotlib.pyplot as plt
import io
import urllib, base64
from django.conf import settings
def generate_pie_chart(data, title,filename):
    labels = list(data.keys())
    sizes = list(data.values())
    chart_path = os.path.join(settings.MEDIA_ROOT, filename)

    # Delete the old chart if it exists
    if os.path.exists(chart_path):
        os.remove(chart_path)
    # plt.figure(figsize=(2, 1))
    plt.pie(sizes, autopct='%1.1f%%', startangle=140, colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
    plt.axis('equal')
    plt.legend(loc = 'lower right',labels=labels)
    plt.title(title)

    plt.savefig(chart_path)

    return settings.MEDIA_URL + filename  # Return the URL to the new chart

def analytics_dashboard(request):
    # Total Job Applications
    total_applicants = JobApplication.objects.count()

    # Popular Job Fields
    job_fields = JobApplication.objects.values('subject').annotate(count=Count('subject')).order_by('-count')
    job_field_dict = {entry['subject']: entry['count'] for entry in job_fields}
    print(job_field_dict)
    # Top Locations
    top_locations = ExtractDetails.objects.values('location').annotate(count=Count('location')).order_by('-count')[:5]
    location_dict = {entry['location']: entry['count'] for entry in top_locations}

    # Average Experience Calculation
    experiences = ExtractDetails.objects.values_list('total_experience', flat=True)
    total_months = 0
    valid_experience_entries = 0

    # for exp in experiences:
    #     parts = exp.split()
    #     if len(parts) >= 2 and parts[1] in ['years', 'year']:
    #         total_months += int(parts[0]) * 12
    #     if len(parts) >= 4 and parts[3] in ['months', 'month']:
    #         total_months += int(parts[2])

    # average_experience = f"{total_months // 12} years, {total_months % 12} months" if total_months > 0 else "N/A"

    # Most Common Skills
    skill_list = ExtractDetails.objects.values_list('key_skills', flat=True)
    skill_dict = {}
    for skills in skill_list:
        for skill in skills.split(','):
            skill = skill.strip()
            if skill:
                skill_dict[skill] = skill_dict.get(skill, 0) + 1
    sorted_skills = dict(sorted(skill_dict.items(), key=lambda item: item[1], reverse=True)[:5])

    # Candidates per Degree
    degree_counts = ExtractDetails.objects.values('degree').annotate(count=Count('degree')).order_by('-count')
    degree_dict = {entry['degree']: entry['count'] for entry in degree_counts}

    # Generate Pie Charts
    job_field_chart = generate_pie_chart(job_field_dict, "Popular Job Fields", "job_field_chart.png")
    # location_chart = generate_pie_chart(location_dict, "Top Candidate Locations")

    context = {
        'total_applicants': total_applicants,
        # 'average_experience': average_experience,
        'job_field_chart': job_field_chart,
        # 'location_chart': location_chart,
        'sorted_skills': sorted_skills,
        'degree_dict': degree_dict
    }

    return render(request, 'analytics_dashboard.html', context)


from django.shortcuts import render, get_object_or_404
from .models import JobApplication

def view_application(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    return render(request, 'view_application.html', {'application': application})


def candidate_detail(request, pk):
    candidate = get_object_or_404(ExtractDetails, pk=pk)
    return render(request, 'candidate_detail.html', {'candidate': candidate})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import JobApplication

def delete_application(request, application_id):
    if request.method == 'DELETE':
        application = get_object_or_404(JobApplication, id=application_id)
        application.delete()
        return JsonResponse({'message': 'Application deleted successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)
