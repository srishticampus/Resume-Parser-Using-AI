from django.urls import path

from  . import views
from .views import job_application_view,admin_dashboard,manage_job_applications,search_candidates,analytics_dashboard

urlpatterns =[
    path('',views.index,name='home'),
    path('career/',views.career,name='poda'),
    path('register/', views.job_application_view, name='register'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-applications/', manage_job_applications, name='manage_applications'),
    path('search-candidates/', search_candidates, name='search_candidates'),
    path('analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('view-application/<int:application_id>/', views.view_application, name='view_application'),
    path("login/", views.admin_login, name="admin_login"),
    path("logout/", views.admin_logout, name="admin_logout"),




]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
