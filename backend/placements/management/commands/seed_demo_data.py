"""
Fills the database with a small, realistic demo set so the dashboards and both reports
are not empty the first time you open them:

  * 5 companies  (3 approved on different dates, 1 pending, 1 rejected with a reason)
  * 8 jobs
  * 10 students
  * ~25 applications in mixed statuses (applied / shortlisted / selected / rejected)

Safe to run many times - it never creates duplicates.

Demo logins (change/delete these before showing real data):
  admin                     / admin1234        (or ADMIN_USERNAME / ADMIN_PASSWORD env vars)
  students  ananya, ... etc / Student@123
  companies infosys, ... etc/ Company@123
"""
import os
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from placements.models import Application, CompanyProfile, Job, StudentProfile, User

STUDENT_PASSWORD = 'Student@123'
COMPANY_PASSWORD = 'Company@123'

STUDENTS = [
    # username, full name, roll no, branch, cgpa
    ('ananya', 'Ananya Iyer', '21CS001', 'CSE', '8.9'),
    ('karthik', 'Karthik Raman', '21CS002', 'CSE', '8.2'),
    ('divya', 'Divya Lakshmi', '21CS003', 'CSE', '7.6'),
    ('rahul', 'Rahul Menon', '21IT001', 'IT', '8.4'),
    ('meena', 'Meena Sundaram', '21IT002', 'IT', '7.1'),
    ('arjun', 'Arjun Prakash', '21EC001', 'ECE', '8.0'),
    ('sneha', 'Sneha Nair', '21EC002', 'ECE', '6.8'),
    ('vikram', 'Vikram Selvam', '21ME001', 'MECH', '7.4'),
    ('priya', 'Priya Dharshini', '21CS004', 'CSE', '9.1'),
    ('suresh', 'Suresh Kumar', '21IT003', 'IT', '6.5'),
]

# username, company name, website, description, hr, status, days_ago_reviewed, reason
COMPANIES = [
    ('infosys', 'Infosys', 'https://www.infosys.com', 'Global leader in digital services and consulting.',
     'Ramesh Babu', 'approved', 20, ''),
    ('zoho', 'Zoho Corporation', 'https://www.zoho.com', 'Chennai-based software products company.',
     'Lavanya S', 'approved', 12, ''),
    ('tcs', 'TCS', 'https://www.tcs.com', 'IT services, consulting and business solutions.',
     'Anand K', 'approved', 5, ''),
    ('nextgen', 'NextGen Startups', 'https://example.com', 'Early-stage product startup.',
     'Kavya R', 'pending', None, ''),
    ('quickhire', 'QuickHire Staffing', 'https://example.com', 'Staffing and recruitment agency.',
     'Mohan D', 'rejected', 3,
     'Not a direct employer - we only accept companies that hire for their own openings.'),
]

# company username, title, branches, min cgpa, package, location, description
JOBS = [
    ('infosys', 'Systems Engineer', 'CSE,IT,ECE', '6.0', '3.6 LPA', 'Chennai', 'Develop and test enterprise software for global clients.'),
    ('infosys', 'Power Programmer', 'CSE,IT', '8.0', '9 LPA', 'Bengaluru', 'Work on complex, high-performance engineering problems.'),
    ('zoho', 'Software Developer', 'CSE,IT', '7.0', '7 LPA', 'Chennai', 'Build features for Zoho products used by millions.'),
    ('zoho', 'Member Technical Staff - QA', '', '6.5', '5 LPA', 'Chennai', 'Own quality for Zoho product releases.'),
    ('tcs', 'Assistant System Engineer', 'CSE,IT,ECE,MECH', '6.0', '3.4 LPA', 'Chennai', 'Entry-level role across IT services projects.'),
    ('tcs', 'Digital Developer', 'CSE,IT', '7.5', '7 LPA', 'Hyderabad', 'Digital transformation projects with modern stacks.'),
    ('infosys', 'Operations Trainee', '', '0', '3 LPA', 'Chennai', 'Business operations and process support.'),
]

# (student username, company username, job title, status) - days ago spread automatically
APPLICATIONS = [
    ('ananya', 'infosys', 'Systems Engineer', 'selected'),
    ('ananya', 'zoho', 'Software Developer', 'shortlisted'),
    ('ananya', 'tcs', 'Digital Developer', 'applied'),
    ('karthik', 'infosys', 'Systems Engineer', 'shortlisted'),
    ('karthik', 'zoho', 'Software Developer', 'rejected'),
    ('karthik', 'tcs', 'Assistant System Engineer', 'applied'),
    ('divya', 'infosys', 'Systems Engineer', 'applied'),
    ('divya', 'zoho', 'Member Technical Staff - QA', 'shortlisted'),
    ('rahul', 'zoho', 'Software Developer', 'selected'),
    ('rahul', 'infosys', 'Systems Engineer', 'rejected'),
    ('rahul', 'tcs', 'Digital Developer', 'shortlisted'),
    ('meena', 'tcs', 'Assistant System Engineer', 'applied'),
    ('meena', 'infosys', 'Operations Trainee', 'applied'),
    ('arjun', 'infosys', 'Systems Engineer', 'applied'),
    ('arjun', 'tcs', 'Assistant System Engineer', 'selected'),
    ('sneha', 'tcs', 'Assistant System Engineer', 'applied'),
    ('vikram', 'tcs', 'Assistant System Engineer', 'rejected'),
    ('priya', 'infosys', 'Power Programmer', 'shortlisted'),
    ('priya', 'zoho', 'Software Developer', 'selected'),
    ('priya', 'tcs', 'Digital Developer', 'applied'),
    # suresh and sneha(partly) intentionally have few/no applications so the student report shows that too
]


class Command(BaseCommand):
    help = 'Creates demo companies, students, jobs and applications (idempotent).'

    def handle(self, *args, **options):
        now = timezone.now()

        # --- admin (the person who approves companies) ---
        admin_name = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin1234')
        admin, created = User.objects.get_or_create(
            username=admin_name, defaults={'role': User.ROLE_ADMIN, 'is_staff': True}
        )
        if created:
            admin.set_password(admin_pass)
            admin.save()
            self.stdout.write(f'Created placement admin "{admin_name}".')

        # --- companies ---
        companies = {}
        for uname, name, site, desc, hr, status, days, reason in COMPANIES:
            user, created = User.objects.get_or_create(
                username=uname, defaults={'role': User.ROLE_COMPANY, 'email': f'hr@{uname}.example.com'}
            )
            if created:
                user.set_password(COMPANY_PASSWORD)
                user.save()
            profile, p_created = CompanyProfile.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': name, 'website': site, 'description': desc,
                    'hr_contact_name': hr, 'hr_contact_phone': '9876500000',
                },
            )
            if p_created:
                profile.approval_status = status
                if status != 'pending':
                    profile.reviewed_on = now - timedelta(days=days)
                    profile.reviewed_by = admin
                    profile.rejection_reason = reason
                profile.save()
            companies[uname] = profile

        # --- jobs ---
        jobs = {}
        for cuname, title, branches, cgpa, package, location, desc in JOBS:
            company = companies[cuname]
            job, _ = Job.objects.get_or_create(
                company=company, title=title,
                defaults={
                    'description': desc, 'eligible_branches': branches, 'min_cgpa': Decimal(cgpa),
                    'package': package, 'location': location,
                    'deadline': (now + timedelta(days=45)).date(),
                },
            )
            jobs[(cuname, title)] = job

        # --- students ---
        students = {}
        for uname, full_name, roll, branch, cgpa in STUDENTS:
            user, created = User.objects.get_or_create(
                username=uname, defaults={'role': User.ROLE_STUDENT, 'email': f'{uname}@college.example.com'}
            )
            if created:
                user.set_password(STUDENT_PASSWORD)
                user.save()
            profile, _ = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': full_name, 'roll_number': roll, 'branch': branch,
                    'graduation_year': 2026, 'cgpa': Decimal(cgpa), 'phone': '9876543210',
                    'resume_link': f'https://drive.google.com/demo-resume-{uname}',
                },
            )
            students[uname] = profile

        # --- applications ---
        made = 0
        for i, (suname, cuname, title, status) in enumerate(APPLICATIONS):
            student, job = students[suname], jobs[(cuname, title)]
            app, created = Application.objects.get_or_create(
                student=student, job=job,
                defaults={
                    'status': status, 'phone': student.phone, 'resume_link': student.resume_link,
                    'cover_note': f'I am keen to join {job.company.company_name} as {title}.',
                },
            )
            if created:
                made += 1
                # spread the application dates over the last ~3 weeks
                Application.objects.filter(pk=app.pk).update(applied_on=now - timedelta(days=(i * 2) % 21 + 1))
        # keep "placed" in sync with selected applications
        for s in students.values():
            s.is_placed = s.applications.filter(status=Application.STATUS_SELECTED).exists()
            s.save()

        self.stdout.write(self.style.SUCCESS(
            f'Demo data ready: {len(companies)} companies, {len(jobs)} jobs, '
            f'{len(students)} students, {made} new applications.'
        ))
