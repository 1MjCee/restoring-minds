from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Agent, Task, Crew

def login_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        User = get_user_model()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            error = "Invalid email or password."
        else:
            user = authenticate(request, username=user.email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                error = "Invalid email or password."

    return render(request, 'login.html', {'error': error})

@login_required
def dashboard_view(request):
    total_agents = Agent.objects.count()
    total_tasks = Task.objects.count()
    total_crews = Crew.objects.count() 

    context = {
        'total_agents': total_agents,
        'total_tasks': total_tasks,
        'total_crews': total_crews,
    } 

    return render(request, 'dashboard.html', context=context)

def logout_view(request):
    logout(request)
    return redirect('login')