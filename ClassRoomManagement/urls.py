"""
URL configuration for ClassRoomManagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Teacher.views import *
from Account.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Login_teacher, name='Login_teacher'),
    path('teacher_dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('Login_admin/', Login_admin, name='Login_admin'),
    path('admin_desh/', admin_desh, name='admin_desh'),
    path('teacher_logout/', teacher_logout, name='teacher_logout'),
    path('student-details/', student_details, name='student_details'),
    path('take-attendance/', take_attendance, name='take_attendance'),
    path('take-show_course_selection/', show_course_selection, name='show_course_selection'),
    path('attendance-list/', attendance_list, name='attendance_list'),
    path('count-present-students/', count_present_students, name='count_present_students'),
    path('manual-attendance-system/', manual_attendance_system, name='manual_attendance_system'),
    path('update_student/<int:id>/', update_student, name='update_student'),
    path('student/<int:student_id>/delete/', delete_student, name='delete_student'),
    path('attendance/', attendance_form, name='take_attendance'),
    path('attendance_input/', attendance_for_students, name='attendance_input'),
    path('generate-dataset/<int:id>/', generate_dataset, name='generate_dataset'),
    path('add_student_data/', add_student_data, name='add_student_data'),
    path('train_dataset/', train_dataset, name='train_dataset'),
    path('recognize-faces-and-mark-attendance/', recognize_faces_and_mark_attendance,
         name='recognize_faces_and_mark_attendance'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
