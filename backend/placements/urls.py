from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views, reports

urlpatterns = [
    # Auth
    path('auth/register/student/', views.register_student),
    path('auth/register/company/', views.register_company),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/me/', views.me),

    # Profiles
    path('students/me/', views.MyStudentProfileView.as_view()),
    path('companies/me/', views.MyCompanyProfileView.as_view()),
    path('companies/dashboard/', views.company_dashboard),

    # Jobs
    path('jobs/', views.JobListCreateView.as_view()),
    path('jobs/<int:pk>/', views.JobDetailView.as_view()),
    path('jobs/eligible/', views.eligible_jobs),
    path('student/board/', views.company_board),
    path('jobs/<int:job_id>/apply/', views.apply_to_job),
    path('jobs/<int:job_id>/applicants/', views.applicants_for_job),

    # Applications
    path('applications/mine/', views.my_applications),
    path('applications/<int:application_id>/status/', views.update_application_status),

    # Admin / placement cell
    path('admin/students/', views.admin_students),
    path('admin/companies/', views.admin_companies),
    path('admin/companies/<int:company_id>/review/', views.review_company),
    path('admin/jobs/', views.admin_jobs),
    path('admin/stats/', views.placement_stats),

    # The two reports (add ?export=csv to download)
    path('admin/reports/overall/', reports.overall_report),
    path('admin/reports/students/', reports.student_report),
]
