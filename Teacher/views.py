from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Account.models import *


def Login_teacher(request):
    if request.user.is_authenticated:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        name = request.POST.get('id')
        password = request.POST.get('pass')

        user = authenticate(request, username=name, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('teacher_dashboard')
    return render(request, 'Auth/login.html')


def Login_admin(request):
    if request.method == 'POST':
        name = request.POST.get('id')
        password = request.POST.get('pass')

        user = authenticate(request, username=name, password=password)
        if user:
            login(request, user)
            return redirect('admin_desh')
        else:
            messages.success(request, 'This is not Admin Account.')
            return redirect('Login_admin')
    return render(request, 'Auth/admin_login.html')


def admin_desh(request):
    return render(request, 'face_recog/Student_face_Recog_portal.html', locals())


@login_required
def teacher_dashboard(request):
    user = request.user
    if user.is_authenticated:
        try:
            prof = Teacher.objects.get(teacher_id=user)
        except:
            messages.success(request, 'No Teacher Profile Found.')
            return redirect('Login_teacher')

    return render(request, 'Auth/teacher_dashboard.html', locals())


def teacher_logout(request):
    logout(request)
    messages.success(request, 'Logout successful.')
    return redirect('Login_teacher')


def student_details(request):
    departments = Department.objects.all()
    semesters = Semester.objects.all()
    sections = Section.objects.all()
    students = []

    if 'department_id' in request.GET and 'section_id' in request.GET:
        department_id = request.GET['department_id']
        section_id = request.GET['section_id']

        if department_id and section_id:
            students = Student.objects.filter(department_id=department_id, section_id=section_id)

    context = {
        'departments': departments,
        'sections': sections,
        'students': students,
        'semesters': semesters,
    }
    return render(request, 'Student/students_details.html', context)


def take_attendance(request):
    # Replace this with your actual logic for taking attendance
    return render(request, 'take_attendance.html')


def attendance_list(request):
    # Replace this with your actual logic for displaying attendance list
    return render(request, 'attendance_list.html')


def count_present_students(request):
    # Replace this with your actual logic for counting present students
    return render(request, 'count_present_students.html')


def manual_attendance_system(request):
    # Replace this with your actual logic for the manual attendance system
    return render(request, 'manual_attendance_system.html')


def update_student(request, id):
    student = Student.objects.get(id=id)
    student_courses = student.courses.all()
    sections = Section.objects.all()
    department = Department.objects.all()
    semester = Semester.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        student_id = request.POST.get('stu_id')
        print(student_id)
        section_id = request.POST.get('section')
        if section_id:
            sectionN = Section.objects.get(pk=section_id)
        department_id = request.POST.get('department')
        if department_id:
            departmentN = Department.objects.get(pk=department_id)
        semester_id = request.POST.get('semester')
        if semester_id:
            semesterN = Semester.objects.get(pk=semester_id)
        courses = request.POST.getlist('courses')
        email = request.POST.get('email')
        photo = request.FILES.get('photo')
        blood_group = request.POST.get('blood_group')
        address = request.POST.get('address')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        contact_no = request.POST.get('contact_no')

        if name:
            student.name = name
            student.student_id = student_id
            student.section = sectionN
            student.department = departmentN
            student.semester = semesterN
            student.email = email
            student.blood_group = blood_group
            student.address = address
            student.date_of_birth = date_of_birth
            student.gender = gender
            student.contact_no = contact_no

            student.save()

            student.courses.set(courses)

            if photo:
                student.photo = photo
                student.save()
    context = {
        'student': student,
        'student_courses': student_courses,
        'sections': sections,
        'departments': department,
        'semesters': semester,
    }
    return render(request, 'Student/update_student.html', context)


def delete_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        student.delete()
        return redirect('student_details')
    return redirect('student_details')
