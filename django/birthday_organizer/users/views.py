from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash,
                                 get_user_model)
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.http import HttpResponse
from .forms import SignUpForm, EditPersonalInformationForm
from .models import Theme
from .tokens import account_activation_token
from base.email import Email

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
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your Birthday Organizer account.'
            message = render_to_string('email_template.html', {
                            'user': user.full_name,
                            'domain': current_site.domain,
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'token': account_activation_token.make_token(user),
                        })
            email = form.cleaned_data.get('email')
            Email().send_email([email], mail_subject, message)
            return render(request, 'activate.html')
        return render(request, 'signup.html', {'errors': form.errors})
    else:
        return render(request, 'signup.html')

def activate(request):
    User = get_user_model()
    try:
        uidb64 = request.GET['uidb64']
        token = request.GET['token']
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'activated.html')
    else:
        return HttpResponse('Activation link is invalid!')
