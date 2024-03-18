import os

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .forms import AddEventForm, AddPaymentForm, AddCommentForm
from users.models import Theme, CustomUser
from base.models import Event, Payment, Comment
from base.tasks import send_email_participants_wanted
from circles.models import Circle
from circles.forms import AddCircleForm

@login_required(login_url='/log_in')
def index(request):
    '''Home page.'''
    context = request.user.get_events_involved_in()
    context.update(request.user.get_overview(Event.objects.filter(archived=False)))
    return render(request, "home.html", context)

@login_required(login_url='/log_in')
def events(request):
    '''Event page.'''
    all = Event.objects.filter(archived=False).exclude(celebrant=request.user)
    context = request.user.get_eligible_events(all)
    return render(request, "events.html", context)

@login_required(login_url='/log_in')
def event(request):
    '''Event page.'''
    try:
        event = Event.objects.filter(archived=False).get(pk=request.GET['id'])
        if event.celebrant and event.celebrant.id == request.user.id:
            # Make sure no-one can access events created for them
            raise Event.DoesNotExist
        context = {'event': event, 'payments': event.get_all_payments(),
                   'currency': Payment.currency,
                   'participants': event.participants.all().order_by('first_name', 'last_name')}
        return render(request, "event.html", context)
    except KeyError:
        return redirect(events)
    except Event.DoesNotExist:
        return redirect(events)

@login_required(login_url='/log_in')
def users(request):
    '''Users page.'''
    context = request.user.get_all_other_users()
    return render(request, "users.html", context)

@login_required(login_url='/log_in')
def circles(request):
    '''Circles page.'''
    circles = {
        'my_circles': [circle for circle in Circle.objects.all() if request.user in circle.users.all()],
        'other_circles': [circle for circle in Circle.objects.all() if request.user not in circle.users.all()]
    }
    return render(request, "circles.html", circles)

@login_required(login_url='/log_in')
def join_circle(request):
    '''Join a circle.'''
    circle = get_object_or_404(Circle, pk=request.GET['id'])
    circle.users.add(request.user)
    return redirect(circles)

@login_required(login_url='/log_in')
def leave_circle(request):
    '''Leave a circle.'''
    circle = get_object_or_404(Circle, pk=request.GET['id'])
    circle.users.remove(request.user)
    if not len(circle.users.all()):
        circle.delete()
    return redirect(circles)

@login_required(login_url='/log_in')
def add_circle(request):
    '''Add a new circle.'''
    context = {
        'type': 'add'
    }
    if request.method == 'POST':
        form = AddCircleForm(request.POST)
        context['errors'] = form.errors
        if form.is_valid():
            circle = form.save()
            circle.users.add(request.user)
            return redirect(circles)
    return render(request, 'add_edit_circle.html', context)

@login_required(login_url='/log_in')
def edit_circle(request):
    '''Edit a circle.'''
    circle = get_object_or_404(Circle, pk=request.GET['id'])
    context = {
        'type': 'edit',
        'circle': circle
    }
    if request.method == 'POST':
        form = AddCircleForm(request.POST, instance=circle)
        context['errors'] = form.errors
        if form.is_valid():
            form.save()
            return redirect(circles)
    return render(request, 'add_edit_circle.html', context)

@login_required(login_url='/log_in')
def add_event(request):
    '''Add an event page.'''
    context = {
        'users': CustomUser.objects.all().exclude(is_superuser=True).exclude(is_active=False),
        'type': 'add'
    }
    if request.method == 'POST':
        form = AddEventForm(request.POST)
        participants = request.POST.getlist('participants')
        context['participants'] = list(map(int, participants))
        context['errors'] = form.errors
        if form.is_valid():
            form.save()
            return redirect(events)
    return render(request, 'add_edit_event.html', context)

@login_required(login_url='/log_in')
def delete_event(request):
    '''Delete an event page.'''
    event = get_object_or_404(Event, pk=request.GET['id'])
    # No access to this view if not requested by the host
    if not event.host or event.host != request.user:
         return redirect('/event?id={}'.format(event.pk))
    event.delete()
    return redirect(events)

@login_required(login_url='/log_in')
def edit_event(request):
    '''Add an event page.'''
    context = {
        'users': CustomUser.objects.all().exclude(is_superuser=True).exclude(is_active=False),
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
        event = Event.objects.filter(archived=False).get(pk=request.GET['id'])
        context['event'] = event
    return render(request, 'add_edit_event.html', context)


@login_required(login_url='/log_in')
def join_event(request):
    '''Join to an event.'''
    req_event = get_object_or_404(Event, pk=request.GET['id'])
    all = Event.objects.filter(archived=False).exclude(celebrant=request.user)
    eligible_events = request.user.get_eligible_events(all)['other_events']
    eligible_events_ids = [x.pk for x in eligible_events]
    if req_event.pk not in eligible_events_ids:
        return redirect(events)
    else:
        req_event.participants.add(request.user)
        req_event.save()
        return redirect('/event?id={}'.format(req_event.pk))

@login_required(login_url='/log_in')
def leave_event(request):
    '''Leave to an event.'''
    req_event = get_object_or_404(Event, pk=request.GET['id'])
    try:
        req_event.participants.remove(request.user)
        req_event.save()
    except:
        pass # User not part of the event - nothing to do
    return redirect('/event?id={}'.format(req_event.pk))

@login_required(login_url='/log_in')
def become_host(request):
    '''Become a host to an event.'''
    req_event = get_object_or_404(Event, pk=request.GET['id'])
    all = Event.objects.filter(archived=False).exclude(celebrant=request.user)
    eligible_events = request.user.get_eligible_events(all)['participated_events']
    eligible_events_ids = [x.pk for x in eligible_events]
    if req_event.pk not in eligible_events_ids:
        return redirect(events)
    else:
        req_event.host = request.user
        req_event.save()
        return redirect('/event?id={}'.format(req_event.pk))

@login_required(login_url='/log_in')
def participants_wanted(request):
    '''Send email, asking for more participants.'''
    event = get_object_or_404(Event, pk=request.GET['id'])
    if request.user != event.host:
        raise Event.DoesNotExist
    if os.environ.get('BIRTHDAY_ORGANIZER_ENV') == 'prd':
        send_email_participants_wanted.delay(event.pk)
    else:
        send_email_participants_wanted(event.pk)
    return redirect('/event?id={}'.format(event.pk))

@login_required(login_url='/log_in')
def add_payment(request):
    '''Add payment.'''
    try:
        data = request.POST.dict()
        data['added_by_host'] = False
        event = Event.objects.filter(archived=False).get(pk=request.POST['event'])
        if str(request.user.id) != request.POST['user']:
            data['added_by_host'] = True
            if request.user != event.host:
                # Payment can be done only for the logged in user, unless
                # they are the host - host can add payments for all participants
                raise Event.DoesNotExist
        form = AddPaymentForm(data)
        if not event.eligible_for_actions(request.user):
            raise Event.DoesNotExist
        if form.is_valid():
            form.save()
            context = {'event': event, 'payments': event.get_all_payments(),
                       'currency': Payment.currency,
                       'participants': event.participants.all().order_by('first_name', 'last_name')}
            content = render_to_string("event_participants.html",
                                       context, request=request)
            return JsonResponse({'result': 'success', 'content': content})
    except (KeyError, Event.DoesNotExist):
        return JsonResponse({'result':'error', 'details': 'Invalid request'})

@login_required(login_url='/log_in')
def get_total(request):
    '''Get total amount for an event.'''
    try:
        event = Event.objects.filter(archived=False).get(pk=request.POST['event'])
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
def toggle_like(request):
    '''Toggle comment like.'''
    try:
        comment = Comment.objects.get(pk=request.POST['comment'])
        event = Event.objects.get(pk=request.POST['event'])
        if bool(int(request.POST['status'])):
            comment.likes.add(request.user)
        else:
            comment.likes.remove(request.user)
        comment.save()
        context = {'event': event}
        content = render_to_string("event_comments.html",
                                    context, request=request)
        return JsonResponse({'result': 'success', 'content': content})
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
                   'currency': Payment.currency,
                   'participants': event.participants.all().order_by('first_name', 'last_name')}
        content = render_to_string("event_participants.html",
                                   context, request=request)
        return JsonResponse({'result': 'success', 'content': content})
    except (ValueError, KeyError):
        return JsonResponse({'result':'error', 'details': 'Invalid request'})

@login_required(login_url='/log_in')
def add_comment(request):
    '''Add a comment to an event.'''
    try:
        event = Event.objects.filter(archived=False).get(pk=request.POST['event'])
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
def edit_comment(request):
    '''Edit a comment.'''
    try:
        comment = Comment.objects.get(pk=request.POST['comment'])
        event = Event.objects.get(pk=request.POST['event'])
        if request.user.id != comment.user.id:
            raise Event.DoesNotExist
        comment.content = request.POST['content']
        comment.save()
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

@login_required(login_url='/log_in')
def change_theme(request):
    '''Change user theme.'''
    try:
        user = CustomUser.objects.get(id=request.user.id)
        user.theme = request.POST['theme']
        user.save()
        return JsonResponse({'result': 'success'})
    except (ValueError, KeyError, CustomUser.DoesNotExist):
        return JsonResponse({'result':'error'})
