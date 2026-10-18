from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, StudentProfile, CompanyProfile, Job, Application
from .serializers import (
    StudentRegisterSerializer, CompanyRegisterSerializer, MeSerializer,
    StudentProfileSerializer, CompanyProfileSerializer, JobSerializer, ApplicationSerializer,
    ApplyFormSerializer,
)
from .permissions import IsStudent, IsCompany, IsPlacementAdmin


def tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


# --- AUTH ---------------------------------------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def register_student(request):
    serializer = StudentRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    profile = serializer.save()
    return Response(
        {'user': MeSerializer(profile.user).data, 'tokens': tokens_for_user(profile.user)},
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def register_company(request):
    serializer = CompanyRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    profile = serializer.save()
    return Response(
        {'user': MeSerializer(profile.user).data, 'tokens': tokens_for_user(profile.user)},
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    data = MeSerializer(request.user).data
    if request.user.role == User.ROLE_STUDENT:
        try:
            data['profile'] = StudentProfileSerializer(request.user.student_profile).data
        except StudentProfile.DoesNotExist:
            data['profile'] = None
    elif request.user.role == User.ROLE_COMPANY:
        try:
            data['profile'] = CompanyProfileSerializer(request.user.company_profile).data
        except CompanyProfile.DoesNotExist:
            data['profile'] = None
    return Response(data)


# --- STUDENT PROFILE ------------------------------------------------------
class MyStudentProfileView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        profile = get_object_or_404(StudentProfile, user=request.user)
        return Response(StudentProfileSerializer(profile).data)

    def put(self, request):
        profile = get_object_or_404(StudentProfile, user=request.user)
        serializer = StudentProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# --- COMPANY PROFILE ------------------------------------------------------
class MyCompanyProfileView(APIView):
    permission_classes = [IsCompany]

    def get(self, request):
        profile = get_object_or_404(CompanyProfile, user=request.user)
        return Response(CompanyProfileSerializer(profile).data)

    def put(self, request):
        profile = get_object_or_404(CompanyProfile, user=request.user)
        serializer = CompanyProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# --- JOBS -----------------------------------------------------------------
class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Job.objects.select_related('company').all().order_by('-posted_on')
        if user.role == User.ROLE_COMPANY:
            return qs.filter(company__user=user)
        if user.role == User.ROLE_STUDENT:
            return qs.filter(is_active=True, company__approval_status=CompanyProfile.STATUS_APPROVED)
        return qs  # admin sees everything

    def perform_create(self, serializer):
        if self.request.user.role != User.ROLE_COMPANY:
            raise PermissionDenied('Only companies can post jobs.')
        company = get_object_or_404(CompanyProfile, user=self.request.user)
        if not company.is_approved:
            raise PermissionDenied('Your company account is not approved yet, so you cannot post jobs.')
        serializer.save(company=company)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Job.objects.select_related('company').all()
        if user.role == User.ROLE_COMPANY:
            return qs.filter(company__user=user)
        return qs

    def check_permissions(self, request):
        super().check_permissions(request)
        # Only the owning company may edit/delete a job (its queryset is already limited to its own jobs).
        if request.method not in ('GET', 'HEAD', 'OPTIONS') and request.user.role != User.ROLE_COMPANY:
            raise PermissionDenied('Only the company that posted a job can change it.')


def _eligibility(profile, job):
    """Returns (is_eligible, reason_if_not)."""
    branches = [b.strip().upper() for b in job.eligible_branches.split(',') if b.strip()]
    if branches and profile.branch.strip().upper() not in branches:
        return False, 'Your branch is not eligible for this role.'
    if profile.cgpa < job.min_cgpa:
        return False, f'Minimum CGPA {job.min_cgpa} required.'
    if job.deadline < timezone.localdate():
        return False, 'Application deadline has passed.'
    return True, ''


@api_view(['GET'])
@permission_classes([IsStudent])
def eligible_jobs(request):
    """Jobs the logged-in student actually qualifies for, based on branch + CGPA."""
    profile = get_object_or_404(StudentProfile, user=request.user)
    jobs = Job.objects.filter(
        is_active=True, company__approval_status=CompanyProfile.STATUS_APPROVED
    ).select_related('company')
    result = [j for j in jobs if _eligibility(profile, j)[0]]
    return Response(JobSerializer(result, many=True).data)


@api_view(['GET'])
@permission_classes([IsStudent])
def company_board(request):
    """Student home page: one card per APPROVED company, with its open roles."""
    profile = get_object_or_404(StudentProfile, user=request.user)
    my_apps = {a.job_id: a.status for a in Application.objects.filter(student=profile)}
    companies = CompanyProfile.objects.filter(approval_status=CompanyProfile.STATUS_APPROVED).order_by('company_name')
    cards = []
    for c in companies:
        roles = []
        for job in c.jobs.filter(is_active=True).order_by('-posted_on'):
            ok, reason = _eligibility(profile, job)
            roles.append({
                'id': job.id, 'title': job.title, 'description': job.description,
                'package': job.package, 'location': job.location, 'min_cgpa': str(job.min_cgpa),
                'eligible_branches': job.eligible_branches or 'All branches',
                'deadline': job.deadline, 'eligible': ok, 'not_eligible_reason': reason,
                'application_status': my_apps.get(job.id),
            })
        cards.append({
            'id': c.id, 'company_name': c.company_name, 'website': c.website,
            'description': c.description, 'roles': roles,
        })
    return Response({'student': {'full_name': profile.full_name, 'phone': profile.phone,
                                 'resume_link': profile.resume_link}, 'companies': cards})


# --- APPLICATIONS ----------------------------------------------------------
@api_view(['POST'])
@permission_classes([IsStudent])
def apply_to_job(request, job_id):
    profile = get_object_or_404(StudentProfile, user=request.user)
    job = get_object_or_404(
        Job, id=job_id, is_active=True, company__approval_status=CompanyProfile.STATUS_APPROVED
    )

    form = ApplyFormSerializer(data=request.data)
    form.is_valid(raise_exception=True)

    ok, reason = _eligibility(profile, job)
    if not ok:
        return Response({'detail': reason}, status=400)
    if Application.objects.filter(student=profile, job=job).exists():
        return Response({'detail': 'You have already applied to this job.'}, status=400)

    data = form.validated_data
    application = Application.objects.create(
        student=profile, job=job,
        phone=data['phone'], resume_link=data['resume_link'], cover_note=data.get('cover_note', ''),
    )
    # Remember contact details on the profile so the next form is pre-filled.
    changed = False
    if not profile.resume_link:
        profile.resume_link, changed = data['resume_link'], True
    if not profile.phone:
        profile.phone, changed = data['phone'], True
    if changed:
        profile.save()
    return Response(ApplicationSerializer(application).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsStudent])
def my_applications(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    apps = Application.objects.filter(student=profile).select_related('job', 'job__company')
    return Response(ApplicationSerializer(apps, many=True).data)


@api_view(['GET'])
@permission_classes([IsCompany])
def applicants_for_job(request, job_id):
    company = get_object_or_404(CompanyProfile, user=request.user)
    job = get_object_or_404(Job, id=job_id, company=company)
    apps = Application.objects.filter(job=job).select_related('student', 'job')
    return Response(ApplicationSerializer(apps, many=True).data)


@api_view(['PATCH'])
@permission_classes([IsCompany])
def update_application_status(request, application_id):
    company = get_object_or_404(CompanyProfile, user=request.user)
    if not company.is_approved:
        return Response({'detail': 'Your company is not approved.'}, status=403)
    application = get_object_or_404(Application, id=application_id, job__company=company)
    new_status = request.data.get('status')
    valid_statuses = dict(Application.STATUS_CHOICES).keys()
    if new_status not in valid_statuses:
        return Response({'detail': 'Invalid status.'}, status=400)
    application.status = new_status
    application.save()
    # A student counts as placed while at least one application is "selected".
    student = application.student
    student.is_placed = student.applications.filter(status=Application.STATUS_SELECTED).exists()
    student.save()
    return Response(ApplicationSerializer(application).data)


@api_view(['GET'])
@permission_classes([IsCompany])
def company_dashboard(request):
    """Company home: approval status, and (once approved) how many people applied."""
    company = get_object_or_404(CompanyProfile, user=request.user)
    data = {
        'company_name': company.company_name,
        'approval_status': company.approval_status,
        'reviewed_on': company.reviewed_on,
        'rejection_reason': company.rejection_reason if company.approval_status == 'rejected' else '',
    }
    if company.is_approved:
        apps = Application.objects.filter(job__company=company)
        by_status = {s: apps.filter(status=s).count() for s, _ in Application.STATUS_CHOICES}
        data.update({
            'total_applicants': apps.values('student').distinct().count(),
            'total_applications': apps.count(),
            'by_status': by_status,
            'jobs': [
                {'id': j.id, 'title': j.title, 'applicants': j.applications.count()}
                for j in company.jobs.all().order_by('-posted_on')
            ],
        })
    return Response(data)


# --- ADMIN (PLACEMENT CELL) ------------------------------------------------
@api_view(['GET'])
@permission_classes([IsPlacementAdmin])
def admin_students(request):
    students = StudentProfile.objects.all().order_by('full_name')
    return Response(StudentProfileSerializer(students, many=True).data)


@api_view(['GET'])
@permission_classes([IsPlacementAdmin])
def admin_companies(request):
    companies = CompanyProfile.objects.all().order_by('company_name')
    return Response(CompanyProfileSerializer(companies, many=True).data)


@api_view(['PATCH'])
@permission_classes([IsPlacementAdmin])
def review_company(request, company_id):
    """Admin approves or rejects a company. Rejection needs a reason. The date is stored."""
    company = get_object_or_404(CompanyProfile, id=company_id)
    decision = request.data.get('decision')
    if decision not in ('approved', 'rejected'):
        return Response({'detail': "decision must be 'approved' or 'rejected'."}, status=400)
    reason = (request.data.get('reason') or '').strip()
    if decision == 'rejected' and not reason:
        return Response({'detail': 'Please give a reason for rejecting the company.'}, status=400)

    company.approval_status = decision
    company.reviewed_on = timezone.now()
    company.reviewed_by = request.user
    company.rejection_reason = reason if decision == 'rejected' else ''
    company.save()
    return Response(CompanyProfileSerializer(company).data)


@api_view(['GET'])
@permission_classes([IsPlacementAdmin])
def admin_jobs(request):
    jobs = Job.objects.select_related('company').all().order_by('-posted_on')
    return Response(JobSerializer(jobs, many=True).data)


@api_view(['GET'])
@permission_classes([IsPlacementAdmin])
def placement_stats(request):
    total_students = StudentProfile.objects.count()
    placed_students = StudentProfile.objects.filter(is_placed=True).count()
    total_companies = CompanyProfile.objects.filter(approval_status=CompanyProfile.STATUS_APPROVED).count()
    total_jobs = Job.objects.count()
    total_applications = Application.objects.count()
    selected = Application.objects.filter(status=Application.STATUS_SELECTED).count()

    branch_breakdown = {}
    for s in StudentProfile.objects.all():
        branch_breakdown.setdefault(s.branch, {'total': 0, 'placed': 0})
        branch_breakdown[s.branch]['total'] += 1
        if s.is_placed:
            branch_breakdown[s.branch]['placed'] += 1

    return Response({
        'total_students': total_students,
        'placed_students': placed_students,
        'placement_rate': round((placed_students / total_students) * 100, 1) if total_students else 0,
        'total_companies': total_companies,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'total_selected': selected,
        'branch_breakdown': branch_breakdown,
    })
