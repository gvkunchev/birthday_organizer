from django.contrib import admin
from .models import Event, Payment, Comment
from .forms import CommentAdminForm


class EventAdmin(admin.ModelAdmin):
    model = Event
    ordering = ('date', 'archived')
    search_fields = ('date', 'name',)
    filter_horizontal = ()
    list_display = ('name', 'date', 'celebrant', 'host')
    list_filter = ('archived', )
    fieldsets = (
            (None, {
                "fields": (
                    ('name', 'date', 'celebrant', 'host', 'participants', 'archived')
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
    list_filter = ('confirmed', )
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
    list_filter = ('alert_sent', )
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


admin.site.register(Event, EventAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Comment, CommentAdmin)
