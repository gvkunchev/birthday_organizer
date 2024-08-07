from django.contrib.auth.models import Group
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    ordering = ('email',)
    search_fields = ('email',)
    filter_horizontal = ()
    list_display = ('first_name', 'last_name', 'email', 'birthdate', 'is_active')
    fieldsets = (
            (None, {
                "fields": (
                    ('email', 'first_name', 'last_name', 'birthdate', 'theme',
                     'iban', 'revolut', 'is_active', 'allow_alerts')
                ),
            }),
        )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name',
                       'birthdate', 'password1', 'password2',
                       'iban', 'revolut', 'is_active', 'allow_alerts')
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(Group)
