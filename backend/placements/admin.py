from django.contrib import admin
from .models import User, StudentProfile, CompanyProfile, Job, Application


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role',)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'roll_number', 'branch', 'cgpa', 'is_placed')
    list_filter = ('branch', 'is_placed')
    search_fields = ('full_name', 'roll_number')


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'approval_status', 'reviewed_on', 'reviewed_by')
    list_filter = ('approval_status',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'package', 'deadline', 'is_active')
    list_filter = ('is_active',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'status', 'applied_on', 'phone')
    list_filter = ('status',)
