from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import WishlistItem
from .forms import WishlistItemForm
from base.models import Event

@login_required(login_url='/log_in')
def wishlist(request):
    '''Wishlist page.'''
    if request.method == 'GET':
        context = {
            'wishlist_items': request.user.get_wishlist_items()
        }
        return render(request, "wishlist.html", context)
    else:
        data = request.POST.dict()
        data.update({'owner': request.user})
        form = WishlistItemForm(data)
        if form.is_valid():
            form.save()
        context = {
            'wishlist_items': request.user.get_wishlist_items(),
            'errors': form.errors
        }
        return render(request, "wishlist.html", context)


@login_required(login_url='/log_in')
def activate_wishlist_item(request, wishlist_item):
    """Activate a wishlist item."""
    try:
        wishlist = WishlistItem.objects.get(pk=wishlist_item)
        if wishlist.owner.pk != request.user.pk:
            raise Exception('No access.')
        wishlist.active = True
        wishlist.save()
    except:
        pass # Disregard and simply reload
    context = {
        'wishlist_items': request.user.get_wishlist_items()
    }
    return render(request, "wishlist.html", context)


@login_required(login_url='/log_in')
def deactivate_wishlist_item(request, wishlist_item):
    """Deactivate a wishlist item."""
    try:
        wishlist = WishlistItem.objects.get(pk=wishlist_item)
        if wishlist.owner.pk != request.user.pk:
            raise Exception('No access.')
        wishlist.active = False
        wishlist.save()
    except:
        pass # Disregard and simply reload
    context = {
        'wishlist_items': request.user.get_wishlist_items()
    }
    return render(request, "wishlist.html", context)


@login_required(login_url='/log_in')
def edit_wishlist_item(request, wishlist_item):
    """Edit a wishlist item."""
    try:
        wishlist = WishlistItem.objects.get(pk=wishlist_item)
        if wishlist.owner.pk != request.user.pk:
            raise Exception('No access.')
    except:
        # Go back to wishlist page
        context = {
            'wishlist_items': request.user.get_wishlist_items()
        }
        return render(request, "wishlist.html", context)
    if request.method == 'GET':
        context = {
            'wishlist_item': wishlist
        }
        return render(request, "edit_wishlist.html", context)
    elif request.method == 'POST':
        data = request.POST.dict()
        data.update({'owner': request.user})
        form = WishlistItemForm(data, instance=wishlist)
        if form.is_valid():
            form.save()
            context = {
                'wishlist_items': request.user.get_wishlist_items()
            }
            return render(request, "wishlist.html", context)
        else:
            context = {
                'wishlist_item': wishlist,
                'errors': form.errors
            }
            return render(request, "edit_wishlist.html", context)


@login_required(login_url='/log_in')
def delete_wishlist_item(request, wishlist_item):
    """Delete a wishlist item."""
    try:
        wishlist = WishlistItem.objects.get(pk=wishlist_item)
        if wishlist.owner.pk != request.user.pk:
            raise Exception('No access.')
        wishlist.delete()
    except:
        pass # Disregard access errors
    context = {
        'wishlist_items': request.user.get_wishlist_items()
    }
    return render(request, "wishlist.html", context)


@login_required(login_url='/log_in')
def select_wishlist_for_event(request, event, wishlist_item):
    """Select a wishlist item for an event."""
    try:
        wishlist_obj = WishlistItem.objects.get(pk=wishlist_item)
        event_obj = Event.objects.get(pk=event)
        if request.user.pk != event_obj.host.pk:
            raise Exception('Access error')
        event_obj.wishlist_item.add(wishlist_obj)
        event_obj.save()
    except:
        pass # Disregard access errors and simply reload the event page
    return redirect(f'/event?id={event_obj.pk}')

@login_required(login_url='/log_in')
def unselect_wishlist_for_event(request, event, wishlist_item):
    """Unselect a wishlist item for an event."""
    try:
        wishlist_obj = WishlistItem.objects.get(pk=wishlist_item)
        event_obj = Event.objects.get(pk=event)
        if request.user.pk != event_obj.host.pk:
            raise Exception('Access error')
        event_obj.wishlist_item.remove(wishlist_obj)
        event_obj.save()
    except:
        pass # Disregard access errors and simply reload the event page
    return redirect(f'/event?id={event_obj.pk}')
