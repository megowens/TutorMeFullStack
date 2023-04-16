from django.contrib.auth import login, get_user_model, logout
from django.db.models.functions import Concat
from django.shortcuts import redirect, render, get_object_or_404
from django.template import loader
from django.views.generic import CreateView, ListView
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
import requests
from django.db.models import CharField, Value as V
import calendar
from calendar import HTMLCalendar

from .forms import StudentSignUpForm, TutorSignUpForm, addClassForm, UpdateTutorProfileForm, TutoringSessionForm, \
    UpdateStudentProfileForm, SendRequestForm, findTutorForm
from .models import User, Student, Tutor, TutorClasses, TutoringSession, TutoringRequest


def addclass(request):
    department = ""
    catalog_number = ""
    message = ""
    if request.method == 'POST':
        formData = request.POST
        form = addClassForm()
        department = (formData["department"]).upper()
        catalog_number = formData["catalog_number"]
        urlQuery = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1232&subject=' + department + '&catalog_nbr=' + catalog_number
        response = requests.get(urlQuery)
        sisjsonTotal = response.json()
        if len(sisjsonTotal) == 0:
            message = "is not a valid course in Spring 2023"
        else:
            sisjson = sisjsonTotal[0]
            department = sisjson["subject"]
            catalog_number = sisjson["catalog_nbr"]
            classes = department + catalog_number
            n = request.user
            n.classes = n.classes + "\n" + classes
            n.save()
            # t = TutorClasses(user=n)
            # t.save()
            # request.user.classlist.add(t)
            # tutor = Tutor.objects.filter().first()
            # tutor.classes = tutor.classes + classes + "\n"
            # tutor.save()
            message = "is a valid course in Spring 2023"
            user = get_user_model()
            all_users = User.objects.all()
            print(all_users)
            print(request.user.classes)
            print(request.user)
    else:
        form = addClassForm()
    return render(request, 'addclass.html',
                  {'form': form, 'department': department, 'catalog_number': catalog_number, 'message': message})


class StudentSignUpView(CreateView):
    model = Student
    form_class = StudentSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('student_home')


class TutorSignUpView(CreateView):
    model = User
    form_class = TutorSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'tutor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('tutor_home')


def student_home(request):
    tutors = Tutor.objects.all()
    user = request.user
    student = user.student
    name = student.name
    year = student.year
    tutor_requests = TutoringRequest.objects.filter(student=student)
    print(user.is_student)
    context = {'tutors': tutors, 'name': name, 'year': year, 'tutor_requests': tutor_requests}
    # template = loader.get_template('student/home.html')
    return render(request, 'student/home.html', context)


def edit_tutor_profile(request):
    template = 'tutor/profile.html'
    tutor = request.user.tutor
    message = ''
    if request.method == 'POST':
        profile_form = UpdateTutorProfileForm(request.POST, request.FILES, instance=tutor)
        if profile_form.is_valid():
            profile_form.save()
            print(tutor.name)
            message = 'Your profile is updated successfully'
    else:
        profile_form = UpdateTutorProfileForm(instance=tutor)
    return render(request, template, {'profile_form': profile_form, 'message': message})


def edit_student_profile(request):
    template = 'student/profile.html'
    student = request.user.student
    message = ''
    if request.method == 'POST':
        profile_form = UpdateStudentProfileForm(request.POST, request.FILES, instance=student)
        if profile_form.is_valid():
            profile_form.save()
            print(student.name)
            message = 'Your profile is updated successfully'
    else:
        profile_form = UpdateStudentProfileForm(instance=student)
    return render(request, template, {'profile_form': profile_form, 'message': message})

def find_tutor(request):
    department = ""
    catalog_number = ""
    message = " "
    listOfTutors = []
    template = 'student/find_tutor.html'
    if request.method == 'POST':
        formData = request.POST
        form = findTutorForm()
        department = (formData["department"]).upper()
        catalog_number = formData["catalog_number"]
        classStudent = department + catalog_number #turn into one string
        users = User.objects.all()
        classData = " "
        matches = 0
        for user in users:
            if(user.is_tutor):
                tutorClassString = user.classes
                classData = tutorClassString.split("\n")
            #need to parse classData for classStudent, if match and need to print the tutor
            #check a long string for another string contained within it
            #string.split method? make actual list type
                if classStudent in classData:
                    tutorName = user.tutor.name
                    tutorYear = user.tutor.year
                    tutorClasses = user.classes
                    tutorHourly = user.tutor.hourly_rate
                    toPrint = '\nName: ' + tutorName + " Year: " + tutorYear + " Classes taken: " + tutorClasses + " Hourly Rate: " + str(tutorHourly)
                    listOfTutors.append(user)
                    matches += 1
            
        message = "Number of tutors found for " + classStudent + " are: " + str(matches)

    else:
        form = findTutorForm()
    # get something from data table (json equivalent), parse it, change existing variable if match is made (an array), add that variable to message
    return render(request, 'find_tutor.html',
                  {'form': form, 'department': department, 'catalog_number': catalog_number, 'message': message, 'tutorList': listOfTutors})



def tutor_home(request):
    user = request.user
    tutor = user.tutor
    name = tutor.name
    year = tutor.year
    hourly_rate = tutor.hourly_rate
    tutoring_sessions = TutoringSession.objects.filter(tutor=tutor)
    context = {'name': name, 'year': year, 'hourly_rate': hourly_rate, 'sessions': tutoring_sessions}
    print(tutor)
    print(tutoring_sessions)
    return render(request, 'tutor/home.html', context)


# Process and create a tutoring session
def createsession(request):
    template = 'tutor/createsession.html'
    tutor = request.user.tutor
    message = ''
    if request.method == 'POST':
        tutoring_form = TutoringSessionForm(request.POST, request.FILES)
        if tutoring_form.is_valid():
            tutoring_session = tutoring_form.save(commit=False)
            tutoring_session.tutor = tutor
            tutoring_session.save()
            print(tutor)
            print(tutoring_form.errors)
            message = 'Your session was created successfully'
    else:
        tutoring_form = TutoringSessionForm()
    return render(request, template, {'tutoring_form': tutoring_form, 'message': message})


def send_request(request, tutor):
    uid = User.objects.get(username=tutor)
    tutor = uid.tutor
    name = tutor.name
    tutor_username = tutor.user.username
    tutoring_sessions = TutoringSession.objects.filter(tutor=tutor).order_by('date')
    print(tutoring_sessions)
    if request.method == "POST":
        form = SendRequestForm(request.POST, request.FILES)
        if form.is_valid():
            tutor_request = form.save(commit=False)
            tutor_request.student = request.user.student
            tutor_request.session = TutoringSession.objects.get(pk=request.POST['session_id'])
            tutor_request.save()
            print(tutor_request.session.date)
    else:
        form = SendRequestForm(initial={'student': request.user.student, 'session': tutoring_sessions.first().id})
    return render(request, 'student/request.html', {'name': name,
                                                    'sessions': tutoring_sessions,
                                                    'username': tutor_username,
                                                    'form': form})


def pending_requests(request):
    template = 'tutor/pending_requests.html'
    tutor = request.user.tutor
    tutoring_requests = TutoringRequest.objects.filter(session__tutor=tutor, status=False)
    return render(request, template, {'requests': tutoring_requests})
