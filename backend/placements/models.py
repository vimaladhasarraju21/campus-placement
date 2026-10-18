from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user with a role. Every account is one of student/company/admin."""
    ROLE_STUDENT = 'student'
    ROLE_COMPANY = 'company'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = (
        (ROLE_STUDENT, 'Student'),
        (ROLE_COMPANY, 'Company'),
        (ROLE_ADMIN, 'Placement Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f'{self.username} ({self.role})'


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=150)
    roll_number = models.CharField(max_length=50, unique=True)
    branch = models.CharField(max_length=100)
    graduation_year = models.IntegerField(default=2026)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    phone = models.CharField(max_length=15, blank=True)
    resume_link = models.URLField(blank=True)
    skills = models.TextField(blank=True, help_text='Comma separated, e.g. Python, SQL, React')
    is_placed = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class CompanyProfile(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    APPROVAL_CHOICES = (
        (STATUS_PENDING, 'Pending review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=150)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    hr_contact_name = models.CharField(max_length=150, blank=True)
    hr_contact_phone = models.CharField(max_length=15, blank=True)

    # --- Approval workflow (a company can't post jobs until approved) ---
    approval_status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default=STATUS_PENDING)
    reviewed_on = models.DateTimeField(null=True, blank=True, help_text='Date/time the admin approved or rejected.')
    reviewed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_companies'
    )
    rejection_reason = models.TextField(blank=True)
    registered_on = models.DateTimeField(auto_now_add=True)

    @property
    def is_approved(self):
        return self.approval_status == self.STATUS_APPROVED

    def __str__(self):
        return self.company_name


class Job(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    eligible_branches = models.CharField(
        max_length=300, help_text='Comma separated, e.g. CSE,IT,ECE. Leave blank for all branches.'
    )
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    package = models.CharField(max_length=100, help_text='e.g. 6 LPA')
    location = models.CharField(max_length=150, blank=True)
    deadline = models.DateField()
    posted_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.title} - {self.company.company_name}'


class Application(models.Model):
    STATUS_APPLIED = 'applied'
    STATUS_SHORTLISTED = 'shortlisted'
    STATUS_SELECTED = 'selected'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = (
        (STATUS_APPLIED, 'Applied'),
        (STATUS_SHORTLISTED, 'Shortlisted'),
        (STATUS_SELECTED, 'Selected'),
        (STATUS_REJECTED, 'Rejected'),
    )
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_APPLIED)
    applied_on = models.DateTimeField(auto_now_add=True)

    # Filled in by the student on the apply form
    phone = models.CharField(max_length=15, blank=True)
    resume_link = models.URLField(blank=True)
    cover_note = models.TextField(blank=True, help_text='Why the student is interested in this role.')

    class Meta:
        unique_together = ('student', 'job')

    def __str__(self):
        return f'{self.student.full_name} -> {self.job.title} ({self.status})'
