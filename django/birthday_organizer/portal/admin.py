from django.contrib.auth.models import Group
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Event, Payment, Comment
from .forms import CommentAdminForm

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    ordering = ('email',)
    search_fields = ('email',)
    filter_horizontal = ()
    list_display = ('first_name', 'last_name', 'email', 'birthdate')
    fieldsets = (
            (None, {
                "fields": (
                    ('email', 'first_name', 'last_name', 'birthdate', 'theme',
                     'iban', 'revolut')
                ),
            }),
        )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name',
                       'birthdate', 'password1', 'password2',
                       'iban', 'revolut')
        }),
    )


class EventAdmin(admin.ModelAdmin):
    model = Event
    ordering = ('date',)
    search_fields = ('date', 'name',)
    filter_horizontal = ()
    list_display = ('name', 'date', 'celebrant', 'host')
    list_filter = ()
    fieldsets = (
            (None, {
                "fields": (
                    ('name', 'date', 'celebrant', 'host', 'participants')
                ),
            }),
        )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'date', 'celebrant', 'host', 'participants')
        }),
    )


class PaymentAdmin(admin.ModelAdmin):
    model = Payment
    ordering = ('user',)
    search_fields = ('user__first_name', 'user__last_name', 'event__name')
    filter_horizontal = ()
    list_display = ('event', 'user', 'amount', 'confirmed')
    list_filter = ()
    fieldsets = (
            (None, {
                "fields": (
                    ('event', 'user', 'amount', 'confirmed')
                ),
            }),
        )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('event', 'user', 'amount', 'confirmed')
        }),
    )


class CommentAdmin(admin.ModelAdmin):
    model = Comment
    ordering = ('event', 'user')
    search_fields = ('event__first_name', 'user__last_name', 'event__name')
    filter_horizontal = ()
    list_display = ('event', 'timestamp', 'user')
    list_filter = ()
    form = CommentAdminForm
    readonly_fields=('timestamp',)
    fieldsets = (
            (None, {
                "fields": (
                    ('event', 'timestamp', 'user', 'content')
                ),
            }),
        )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('event', 'user', 'content')
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.unregister(Group)
