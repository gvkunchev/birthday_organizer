from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import SignUpForm, EditPersonalInformationForm
from .models import Theme
from portal.views import index


@login_required(login_url='/log_in')
def update_personal_info(request):
    '''Update personal info and load user's settings.'''
    form = EditPersonalInformationForm(request.POST, instance=request.user)
    context = {'errors': form.errors, 'themes': Theme.choices}
    if form.is_valid():
        form.save()
        context.update({'personal_form_message': 'Successfully updated.'})
    return render(request, 'settings.html', context)

@login_required(login_url='/log_in')
def update_password(request):
    '''Update password and load user's settings.'''
    form = PasswordChangeForm(request.user, request.POST)
    context = {'errors': form.errors, 'themes': Theme.choices}
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        context.update({'password_form_message': 'Successfully updated.'})
    return render(request, 'settings.html', context)

def log_in(request):
    '''Login page.'''
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is None:
            return render(request, "login.html",
                          {'errors': 'Wrong credentials.'})
        else:
            login(request, user)
            try:
                return redirect(request.GET['next'])
            except KeyError:
                return redirect(index)
    else:
        return render(request, "login.html")

def log_out(request):
    '''Logout page.'''
    logout(request)
    return redirect(index)

def signup(request):
    '''Sign up page.'''
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect(index)
        return render(request, 'signup.html', {'errors': form.errors})
    else:
        return render(request, 'signup.html')
