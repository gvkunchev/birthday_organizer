from django.contrib import admin

from .models import WishlistItem

class WishlistItemAdmin(admin.ModelAdmin):
    model = WishlistItem
    ordering = ('owner', 'title', 'description', 'active')
    search_fields = ('owner', 'title', 'description')
    filter_horizontal = ()
    list_display = ('owner', 'title', 'active')
    list_filter = ('owner', 'active')
    fieldsets = (
            (None, {
                "fields": (
                    ('owner', 'title', 'description', 'active')
                ),
            }),
        )
    add_fieldsets = (
        (None, {
            'fields': ('owner', 'title', 'description', 'active')
        }),
    )


admin.site.register(WishlistItem, WishlistItemAdmin)
