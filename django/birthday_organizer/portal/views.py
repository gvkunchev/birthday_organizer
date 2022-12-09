from calendar import WEDNESDAY
import re
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .forms import (SignUpForm, EditPersonalInformationForm, AddEventForm,
                    AddPaymentForm, AddCommentForm)
from .models import Theme, Event, CustomUser, Payment

@login_required(login_url='/log_in')
def index(request):
    '''Home page.'''
    context = request.user.get_events_involved_in()
    return render(request, "home.html", context)

@login_required(login_url='/log_in')
def events(request):
    '''Event page.'''
    context = request.user.get_eligible_events()
    return render(request, "events.html", context)

@login_required(login_url='/log_in')
def event(request):
    '''Event page.'''
    try:
        event = Event.objects.get(pk=request.GET['id'])
        if event.celebrant and event.celebrant.id == request.user.id:
            # Make sure no-one can access events created for them
            raise Event.DoesNotExist
        context = {'event': event, 'payments': event.get_all_payments(),
                   'currency': Payment.currency}
        return render(request, "event.html", context)
    except KeyError:
        return redirect(events)
    except Event.DoesNotExist:
        context = Event()
        return render(request, "event.html", context)

@login_required(login_url='/log_in')
def users(request):
    '''Users page.'''
    context = request.user.get_all_other_users()
    return render(request, "users.html", context)

@login_required(login_url='/log_in')
def add_event(request):
    '''Add an event page.'''
    context = {
        'users': CustomUser.objects.all(),
        'type': 'add'
    }
    if request.method == 'POST':
        form = AddEventForm(request.POST)
        participants = request.POST.getlist('participants')
        context['participants'] = list(map(int, participants))
        context['errors'] = form.errors
        if form.is_valid():
            form.save()
    return render(request, 'add_edit_event.html', context)

@login_required(login_url='/log_in')
def edit_event(request):
    '''Add an event page.'''
    context = {
        'users': CustomUser.objects.all(),
        'type': 'edit'
    }
    event = get_object_or_404(Event, pk=request.GET['id'])
    # No access to this view if not requested by the host
    if not event.host or event.host != request.user:
        return redirect(events)
    if request.method == 'POST':
        form = AddEventForm(request.POST, instance=event)
        participants = request.POST.getlist('participants')
        context['participants'] = list(map(int, participants))
        context['errors'] = form.errors
        if form.is_valid():
            form.save()
            return redirect('/event?id={}'.format(event.pk))
    else:
        event = Event.objects.get(pk=request.GET['id'])
        context['event'] = event
    return render(request, 'add_edit_event.html', context)


@login_required(login_url='/log_in')
def join_event(request):
    '''Join to an event.'''
    req_event = get_object_or_404(Event, pk=request.GET['id'])
    eligible_events = request.user.get_eligible_events()['other_events']
    eligible_events_ids = [x.pk for x in eligible_events]
    if req_event.pk not in eligible_events_ids:
        return redirect(events)
    else:
        req_event.participants.add(request.user)
        req_event.save()
        return redirect('/event?id={}'.format(req_event.pk))

@login_required(login_url='/log_in')
def add_payment(request):
    '''Add payment.'''
    try:
        form = AddPaymentForm(request.POST)
        event = Event.objects.get(pk=request.POST['event'])
        if str(request.user.id) != request.POST['user']:
            raise Event.DoesNotExist
        if not event.eligible_for_actions(request.user):
            raise Event.DoesNotExist
        if form.is_valid():
            form.save()
            context = {'event': event, 'payments': event.get_all_payments(),
                       'currency': Payment.currency}
            content = render_to_string("event_participants.html",
                                       context, request=request)
            return JsonResponse({'result': 'success', 'content': content})
    except (KeyError, Event.DoesNotExist):
        return JsonResponse({'result':'error', 'details': 'Invalid request'})

@login_required(login_url='/log_in')
def get_total(request):
    '''Get total amount for an event.'''
    try:
        event = Event.objects.get(pk=request.POST['event'])
        if not event.eligible_for_actions(request.user):
            raise Event.DoesNotExist
        return JsonResponse({'result': 'success',
                             'content': event.get_total_money})
    except (KeyError, Event.DoesNotExist):
        return JsonResponse({'result':'error', 'details': 'Invalid request'})

@login_required(login_url='/log_in')
def toggle_payment(request):
    '''Toggle payment confirmation.'''
    try:
        payment = Payment.objects.get(pk=request.POST['payment'])
        event = payment.event
        if not event.host:
            raise Event.DoesNotExist
        if request.user != event.host:
            raise Event.DoesNotExist
        payment.confirmed = bool(int(request.POST['status']))
        payment.save()
        return JsonResponse({'result': 'success'})
    except (ValueError, KeyError, Event.DoesNotExist):
        return JsonResponse({'result':'error', 'details': 'Invalid request'})

@login_required(login_url='/log_in')
def remove_payment(request):
    '''Remove payment.'''
    try:
        payment = Payment.objects.get(pk=request.POST['payment'])
        payment.delete()
        event = payment.event
        context = {'event': event, 'payments': event.get_all_payments(),
                   'currency': Payment.currency}
        content = render_to_string("event_participants.html",
                                   context, request=request)
        return JsonResponse({'result': 'success', 'content': content})
    except (ValueError, KeyError):
        return JsonResponse({'result':'error', 'details': 'Invalid request'})

@login_required(login_url='/log_in')
def add_comment(request):
    '''Add a comment to an event.'''
    try:
        event = Event.objects.get(pk=request.POST['event'])
        if not event.eligible_for_actions(request.user):
            raise Event.DoesNotExist
        if str(request.user.id) != request.POST['user']:
            raise Event.DoesNotExist
        form = AddCommentForm(request.POST)
        if form.is_valid():
            form.save()
            context = {'event': event}
            content = render_to_string("event_comments.html",
                                       context, request=request)
            return JsonResponse({'result': 'success', 'content': content})
    except (ValueError, KeyError, Event.DoesNotExist):
        return JsonResponse({'result':'error', 'details': 'Invalid request'})

@login_required(login_url='/log_in')
def settings(request):
    '''User's settings page.'''
    context = {'themes': Theme.choices}
    return render(request, "settings.html", context)


'''User authorization specifics'''


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
