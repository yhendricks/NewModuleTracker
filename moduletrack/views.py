from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.contrib.admin.utils import NestedObjects
from django.db import connection
import operator


def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Check if this is the first user, if so make them a superuser
            if User.objects.count() == 1:  # This is the first user
                user.is_superuser = True
                user.is_staff = True
                user.save()
            
            # Add user to management groups if they exist
            pcb_group, created = Group.objects.get_or_create(name='mng_pcb_type')
            user.groups.add(pcb_group)
            
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('home')  # Redirect to home after logout