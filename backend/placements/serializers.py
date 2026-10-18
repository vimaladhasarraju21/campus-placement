from django.db import transaction
from rest_framework import serializers
from .models import User, StudentProfile, CompanyProfile, Job, Application


# --- Auth -------------------------------------------------------------------
class StudentRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    full_name = serializers.CharField()
    roll_number = serializers.CharField()
    branch = serializers.CharField()
    graduation_year = serializers.IntegerField()
    cgpa = serializers.DecimalField(max_digits=4, decimal_places=2)
    phone = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password'],
                email=validated_data.get('email', ''),
                role=User.ROLE_STUDENT,
            )
            profile = StudentProfile.objects.create(
                user=user,
                full_name=validated_data['full_name'],
                roll_number=validated_data['roll_number'],
                branch=validated_data['branch'],
                graduation_year=validated_data['graduation_year'],
                cgpa=validated_data['cgpa'],
                phone=validated_data.get('phone', ''),
            )
        return profile


class CompanyRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    company_name = serializers.CharField()
    website = serializers.URLField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    hr_contact_name = serializers.CharField(required=False, allow_blank=True)
    hr_contact_phone = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password'],
                email=validated_data.get('email', ''),
                role=User.ROLE_COMPANY,
            )
            profile = CompanyProfile.objects.create(
                user=user,
                company_name=validated_data['company_name'],
                website=validated_data.get('website', ''),
                description=validated_data.get('description', ''),
                hr_contact_name=validated_data.get('hr_contact_name', ''),
                hr_contact_phone=validated_data.get('hr_contact_phone', ''),
            )
        return profile


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role')


# --- Profiles -----------------------------------------------------------
class StudentProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = StudentProfile
        fields = (
            'id', 'username', 'full_name', 'roll_number', 'branch', 'graduation_year',
            'cgpa', 'phone', 'resume_link', 'skills', 'is_placed',
        )
        read_only_fields = ('id', 'roll_number', 'is_placed')


class CompanyProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    is_approved = serializers.BooleanField(read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True, default=None)

    class Meta:
        model = CompanyProfile
        fields = (
            'id', 'username', 'company_name', 'website', 'description',
            'hr_contact_name', 'hr_contact_phone',
            'approval_status', 'is_approved', 'reviewed_on', 'reviewed_by_name',
            'rejection_reason', 'registered_on',
        )
        read_only_fields = (
            'id', 'approval_status', 'is_approved', 'reviewed_on', 'reviewed_by_name',
            'rejection_reason', 'registered_on',
        )


# --- Jobs & Applications -------------------------------------------------
class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    applicant_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = (
            'id', 'company', 'company_name', 'title', 'description', 'eligible_branches',
            'min_cgpa', 'package', 'location', 'deadline', 'posted_on', 'is_active',
            'applicant_count',
        )
        read_only_fields = ('id', 'company', 'company_name', 'posted_on', 'applicant_count')

    def get_applicant_count(self, obj):
        return obj.applications.count()


class ApplyFormSerializer(serializers.Serializer):
    """The simple apply form a student fills in."""
    phone = serializers.CharField(max_length=15)
    resume_link = serializers.URLField()
    cover_note = serializers.CharField(required=False, allow_blank=True)


class ApplicationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    roll_number = serializers.CharField(source='student.roll_number', read_only=True)
    cgpa = serializers.DecimalField(source='student.cgpa', max_digits=4, decimal_places=2, read_only=True)
    branch = serializers.CharField(source='student.branch', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company.company_name', read_only=True)

    class Meta:
        model = Application
        fields = (
            'id', 'student', 'student_name', 'roll_number', 'cgpa', 'branch',
            'phone', 'resume_link', 'cover_note',
            'job', 'job_title', 'company_name', 'status', 'applied_on',
        )
        read_only_fields = ('id', 'student', 'applied_on')
