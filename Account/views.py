from datetime import datetime, timedelta
import os
import cv2
from django.utils import timezone
import numpy as np
from PIL import Image
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Department, Section, Semester, Course, Student, Attendance


def attendance_form(request):
    departments = Department.objects.all()
    sections = Section.objects.all()
    semesters = Semester.objects.all()
    courses = Course.objects.all()

    students = None

    if request.method == 'POST':
        department_id = request.POST.get('department')
        section_id = request.POST.get('section')
        semester_id = request.POST.get('semester')
        course_id = request.POST.get('course')

        students = Student.objects.filter(
            department_id=department_id,
            section_id=section_id,
            semester_id=semester_id,
            courses__id=course_id
        )
        # Check if date is provided in the form
        date_str = request.POST.get('date')
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()

            selected_students = request.POST.getlist('attendance[]')

            students = Student.objects.filter(id__in=selected_students)
            if students:
                for student in students:
                    Attendance.objects.create(
                        student=student,
                        section=student.section,
                        semester=student.semester,
                        department=student.department,
                        course_id=course_id,
                        date=date,
                        present=True
                    )
                messages.success(request, 'Attendance taken successfully.')
                return redirect('take_attendance')
            else:
                messages.error(request, 'No students selected for attendance.')

    return render(request, 'Student/take_attendance.html', {
        'departments': departments,
        'sections': sections,
        'semesters': semesters,
        'courses': courses,
        'students': students,
    })


def attendance_for_students(request):
    if request.method == 'POST':
        department_id = request.POST.get('department')
        course_id = request.POST.get('course')
        semester_id = request.POST.get('semester')
        Section_id = request.POST.get('Section')
        selected_date = request.POST.get('date')

        department = Department.objects.get(pk=department_id)
        course = Course.objects.get(pk=course_id)
        semester = Semester.objects.get(pk=semester_id)
        section = Section.objects.get(pk=Section_id)

        students = Student.objects.filter(
            department=department,
            semester=semester,
            courses__in=[course_id],
            section=section
        )

        attendance_data = []

        for student in students:
            recent_attendances = Attendance.objects.filter(
                student=student,
                date__gte=timezone.datetime.strptime(selected_date, "%Y-%m"),
                date__lt=timezone.datetime.strptime(selected_date, "%Y-%m") + timedelta(days=31),
            )

            attended_days = set(attendance.date.day for attendance in recent_attendances)
            missed_days = 31 - len(attended_days)  # Calculate missed days
            attendance_data.append({
                'student': student,
                'attended_days': attended_days,
                'missed_days': missed_days,
            })

        # Pass department, semester, and session to the template
        context = {
            'students': attendance_data,
            'department_name': department.name,
            'semester_name': semester.name
        }

        return render(request, 'Student/attendance_for_students.html', context)

    departments = Department.objects.all()
    courses = Course.objects.all()
    semesters = Semester.objects.all()
    section = Section.objects.all()

    return render(request, 'Student/attendance_input_form.html', {
        'departments': departments,
        'courses': courses,
        'semesters': semesters,
        'sections': section
    })


def add_student_data(request):
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
    return render(request, 'face_recog/photo_train.html', context)


def generate_dataset(request, id):
    try:
        # Fetch student from the database
        student = Student.objects.get(id=id)  # You may need to adjust this based on your logic

        # Open the camera and capture images
        face_classifier = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

        def face_cropped(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray, 1.3, 5)

            if not os.path.exists("dataset"):
                os.makedirs("dataset")

            for (x, y, w, h) in faces:
                face_cropped = img[y:y + h, x:x + w]
                return face_cropped

        cap = cv2.VideoCapture(0)
        img_id = 0
        while True:
            ret, my_frame = cap.read()
            if face_cropped(my_frame) is not None:
                img_id += 1
                face = cv2.resize(face_cropped(my_frame), (450, 450))
                face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                file_name_path = f"dataset/user.{student.Roll}.{img_id}.jpg"
                cv2.imwrite(file_name_path, face)
                cv2.putText(face, str(img_id), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 2)
                cv2.imshow("Cropped Face", face)

            if cv2.waitKey(1) == 13 or int(img_id) == 20:
                break

        cap.release()
        cv2.destroyAllWindows()

        messages.success(request, "Image capture completed")
        return redirect('admin_desh')

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('admin_desh')


@csrf_exempt
def train_dataset(request):
    data_dir = "dataset"
    path = [os.path.join(data_dir, file) for file in os.listdir(data_dir)]
    faces = []
    ids = []

    for image in path:
        try:
            id = int(os.path.split(image)[1].split('.')[1])
        except ValueError:
            print(f"Skipping invalid file name: {image}")
            continue

        img = Image.open(image).convert('L')  # Convert to Gray Scale Image
        image_np = np.array(img, 'uint8')

        faces.append(image_np)
        ids.append(id)

    ids = np.array(ids)

    # Train the dataset
    recognizer = cv2.face.LBPHFaceRecognizer.create()
    recognizer.train(faces, ids)

    # Save the recognizer
    recognizer.save("classifier.xml")
    messages.success(request, "Image Train Done")
    return redirect('admin_desh')


def show_course_selection(request):
    courses = Course.objects.all()
    departments = Department.objects.all()
    semesters = Semester.objects.all()
    sections = Section.objects.all()

    # Initialize students with an empty queryset
    students = Student.objects.none()

    if request.method == 'POST':
        course_code = request.POST.get('courseCode')
        department_id = request.POST.get('department')
        section_id = request.POST.get('section')
        semester_id = request.POST.get('semester')

        # Filter students based on department, section, and semester
        if department_id and section_id and semester_id:
            students = Student.objects.filter(department=department_id, section=section_id, semester=semester_id)

        # Call function if course code is provided
        if course_code:
            recognize_faces_and_mark_attendance(course_code)

    context = {
        'courses': courses,
        'departments': departments,
        'sections': sections,
        'students': students,
        'semesters': semesters,
    }
    return render(request, 'face_recog/Face_attand_take.html', context)


@csrf_exempt
def recognize_faces_and_mark_attendance(course_code):
    face_classifier = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("classifier.xml")

    recognition_results = []  # Keep track of recognition results for all students

    try:
        selected_course = Course.objects.get(code=course_code)
    except Course.DoesNotExist:
        return JsonResponse({'error': 'Invalid course ID'})

    # Open the camera
    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:
        # Read each frame from the camera
        ret, frame = video_capture.read()

        if not ret:
            print("Error reading frame from the camera.")
            break

        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_classifier.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            # Extract the face region
            face = gray[y:y + h, x:x + w]

            # Perform face recognition
            label, confidence = recognizer.predict(face)

            if confidence < 100:
                mark_attendance(label, selected_course)  # Pass the selected course
                recognition_results.append({
                    'student_id': label,
                    'confidence': confidence,
                    'message': 'Recognition and attendance marked successfully'
                })

        # Display the frame with rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow('Video', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all windows
    video_capture.release()
    cv2.destroyAllWindows()

    # Return JsonResponse or redirect based on the recognition_results
    return JsonResponse({'results': recognition_results})


def mark_attendance(Roll, course):
    current_date = datetime.now().date()
    student = Student.objects.get(Roll=Roll)
    print('print student', student)

    try:
        # Get or create attendance for the student and selected course
        attendance, created = Attendance.objects.get_or_create(
            student=student,
            section=student.section,
            semester=student.semester,
            department=student.department,
            course=course,  # Use the selected course
            date=current_date
        )

        # Mark the attendance as present
        attendance.present = True
        attendance.save()
    except Exception as e:
        print(f"Error marking attendance: {e}")
