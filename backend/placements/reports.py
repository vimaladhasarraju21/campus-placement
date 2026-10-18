"""
The two admin reports.

  1. Overall report   -> every company: approval status + date, jobs, how many students applied,
                         and who they are (company -> students mapping).
  2. Student report   -> every student and what they have applied for (student -> companies mapping).

Both are computed live from the database, so anything users do in the app (register, apply,
get shortlisted/selected, companies approved/rejected) shows up the next time the report is opened.
Add ?export=csv to download either report as a CSV file.
"""
import csv

from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Application, CompanyProfile, StudentProfile, Job
from .permissions import IsPlacementAdmin


def _dt(value, fmt='%d %b %Y'):
    """Format a date/datetime in local (IST) time; blank if None."""
    if not value:
        return ''
    if hasattr(value, 'tzinfo') and value.tzinfo is not None:
        value = timezone.localtime(value)
    return value.strftime(fmt)


def _csv_response(filename, header, rows):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(header)
    writer.writerows(rows)
    return response


# ---------------------------------------------------------------------------
# Report 1: overall / company-wise
# ---------------------------------------------------------------------------
def build_overall_report():
    companies = CompanyProfile.objects.select_related('reviewed_by').order_by('company_name')
    apps = (
        Application.objects
        .select_related('student', 'job', 'job__company')
        .order_by('-applied_on')
    )
    apps_by_company = {}
    for a in apps:
        apps_by_company.setdefault(a.job.company_id, []).append(a)

    company_rows = []
    for c in companies:
        c_apps = apps_by_company.get(c.id, [])
        counts = {s: sum(1 for a in c_apps if a.status == s) for s, _ in Application.STATUS_CHOICES}
        company_rows.append({
            'id': c.id,
            'company_name': c.company_name,
            'approval_status': c.approval_status,
            'registered_on': c.registered_on,
            'reviewed_on': c.reviewed_on,
            'reviewed_by': c.reviewed_by.username if c.reviewed_by else None,
            'rejection_reason': c.rejection_reason,
            'jobs_posted': c.jobs.count(),
            'total_applicants': len({a.student_id for a in c_apps}),
            'total_applications': len(c_apps),
            'applied': counts['applied'],
            'shortlisted': counts['shortlisted'],
            'selected': counts['selected'],
            'rejected': counts['rejected'],
            'applicants': [
                {
                    'student_name': a.student.full_name,
                    'roll_number': a.student.roll_number,
                    'branch': a.student.branch,
                    'cgpa': str(a.student.cgpa),
                    'job_title': a.job.title,
                    'status': a.status,
                    'applied_on': a.applied_on,
                }
                for a in c_apps
            ],
        })

    total_students = StudentProfile.objects.count()
    placed = StudentProfile.objects.filter(is_placed=True).count()
    branch = {}
    for s in StudentProfile.objects.all():
        b = branch.setdefault(s.branch, {'total': 0, 'placed': 0})
        b['total'] += 1
        b['placed'] += 1 if s.is_placed else 0

    summary = {
        'total_students': total_students,
        'placed_students': placed,
        'placement_rate': round(placed / total_students * 100, 1) if total_students else 0,
        'companies_total': len(company_rows),
        'companies_approved': sum(1 for r in company_rows if r['approval_status'] == 'approved'),
        'companies_pending': sum(1 for r in company_rows if r['approval_status'] == 'pending'),
        'companies_rejected': sum(1 for r in company_rows if r['approval_status'] == 'rejected'),
        'total_jobs': Job.objects.count(),
        'total_applications': apps.count(),
        'applications_by_status': {s: apps.filter(status=s).count() for s, _ in Application.STATUS_CHOICES},
    }
    return {
        'generated_on': _dt(timezone.now(), '%d %b %Y, %I:%M %p'),
        'summary': summary,
        'branch_breakdown': branch,
        'companies': company_rows,
    }


@api_view(['GET'])
@permission_classes([IsPlacementAdmin])
def overall_report(request):
    report = build_overall_report()
    if request.query_params.get('export') == 'csv':
        header = ['Company', 'Approval status', 'Approved/Reviewed on', 'Reviewed by', 'Rejection reason',
                  'Role applied for', 'Student', 'Roll no.', 'Branch', 'CGPA', 'Application status', 'Applied on']
        rows = []
        for c in report['companies']:
            base = [c['company_name'], c['approval_status'], _dt(c['reviewed_on']),
                    c['reviewed_by'] or '', c['rejection_reason']]
            if not c['applicants']:
                rows.append(base + ['', '', '', '', '', '', ''])
            for a in c['applicants']:
                rows.append(base + [a['job_title'], a['student_name'], a['roll_number'], a['branch'],
                                    a['cgpa'], a['status'], _dt(a['applied_on'])])
        return _csv_response('overall_placement_report.csv', header, rows)
    return Response(report)


# ---------------------------------------------------------------------------
# Report 2: student-wise (who applied where)
# ---------------------------------------------------------------------------
def build_student_report():
    students = StudentProfile.objects.order_by('full_name')
    apps = Application.objects.select_related('job', 'job__company').order_by('-applied_on')
    apps_by_student = {}
    for a in apps:
        apps_by_student.setdefault(a.student_id, []).append(a)

    rows = []
    for s in students:
        s_apps = apps_by_student.get(s.id, [])
        rows.append({
            'id': s.id,
            'full_name': s.full_name,
            'roll_number': s.roll_number,
            'branch': s.branch,
            'cgpa': str(s.cgpa),
            'graduation_year': s.graduation_year,
            'is_placed': s.is_placed,
            'total_applications': len(s_apps),
            'applications': [
                {
                    'company_name': a.job.company.company_name,
                    'job_title': a.job.title,
                    'package': a.job.package,
                    'status': a.status,
                    'applied_on': a.applied_on,
                }
                for a in s_apps
            ],
        })
    return {
        'generated_on': _dt(timezone.now(), '%d %b %Y, %I:%M %p'),
        'summary': {
            'total_students': len(rows),
            'students_applied': sum(1 for r in rows if r['total_applications']),
            'students_not_applied': sum(1 for r in rows if not r['total_applications']),
            'placed_students': sum(1 for r in rows if r['is_placed']),
        },
        'students': rows,
    }


@api_view(['GET'])
@permission_classes([IsPlacementAdmin])
def student_report(request):
    report = build_student_report()
    if request.query_params.get('export') == 'csv':
        header = ['Student', 'Roll no.', 'Branch', 'CGPA', 'Placed?', 'Company applied to',
                  'Role', 'Package', 'Application status', 'Applied on']
        rows = []
        for s in report['students']:
            base = [s['full_name'], s['roll_number'], s['branch'], s['cgpa'], 'Yes' if s['is_placed'] else 'No']
            if not s['applications']:
                rows.append(base + ['(has not applied yet)', '', '', '', ''])
            for a in s['applications']:
                rows.append(base + [a['company_name'], a['job_title'], a['package'], a['status'],
                                    _dt(a['applied_on'])])
        return _csv_response('student_applications_report.csv', header, rows)
    return Response(report)
