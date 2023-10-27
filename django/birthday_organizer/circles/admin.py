from django.contrib import admin

from .models import Circle


class CircleAdmin(admin.ModelAdmin):
    model = Circle
    ordering = ('name',)
    search_fields = ('name', 'users')
    filter_horizontal = ()
    list_display = ('name', )
    fieldsets = (
            (None, {
                "fields": (
                    ('name', 'users')
                ),
            }),
        )
    add_fieldsets = (
            (None, {
                "fields": (
                    ('name', 'users')
                ),
            }),
    )


admin.site.register(Circle, CircleAdmin)
