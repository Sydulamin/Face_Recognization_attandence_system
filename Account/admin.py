from django.contrib import admin
from .models import *


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'department']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_id', 'section', 'department', 'semester', 'email', 'contact_no', 'gender',
                    'date_of_birth', 'address', 'blood_group', 'photo_samples_status']
    filter_horizontal = ['courses']  # For the courses field


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['teacher_id', 'name', 'email', 'phone_no', 'department']


@admin.register(AssignTeacher)
class AssignTeacherAdmin(admin.ModelAdmin):
    list_display = ['course', 'teacher']
