from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User

# Registration View
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        if username and password and role:
            user = User.objects.create_user(username=username, password=password, role=role)
            user.save()
            return redirect('login')
    return render(request, 'authority/registration.html')

# Login View
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        user = authenticate(request, username=username, password=password, role=role)
        if user is not None and user.role == role:
            login(request, user, role)
            if request.user.role == 'student':
                return render(request, 'student/student_dashboard.html')
            elif request.user.role == 'teacher':
                return render(request, 'home/teacher_dashboard.html')
            elif request.user.role == 'admin':
                users = User.objects.all()
                return render(request, 'admin/admin_dashboard.html', {'users': users})
            return redirect('dashboard')
    return render(request, 'authority/login.html')

# Logout View
def user_logout(request):
    logout(request)
    return redirect('login')

# # Dashboard View
# @login_required
# def dashboard(request):
#     print(request.user.role)
#     if request.user.role == 'student':
#         return render(request, 'student/student_dashboard.html')
#     elif request.user.role == 'teacher':
#         return render(request, 'home/teacher_dashboard.html')
#     elif request.user.role == 'admin':
#         users = User.objects.all()
#         return render(request, 'admin/admin_dashboard.html', {'users': users})

@login_required
def users(request):
    return redirect('users')