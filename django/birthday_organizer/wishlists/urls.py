from django.urls import path, re_path
from wishlists import views


urlpatterns = [
    path('wishlist', views.wishlist),
    re_path('wishlist/activate/(?P<wishlist_item>\d+)', views.activate_wishlist_item),
    re_path('wishlist/deactivate/(?P<wishlist_item>\d+)', views.deactivate_wishlist_item),
    re_path('wishlist/edit/(?P<wishlist_item>\d+)', views.edit_wishlist_item),
    re_path('wishlist/delete/(?P<wishlist_item>\d+)', views.delete_wishlist_item),
    re_path('event/(?P<event>\d+)/select_wishlist/(?P<wishlist_item>\d+)', views.select_wishlist_for_event),
    re_path('event/(?P<event>\d+)/unselect_wishlist/(?P<wishlist_item>\d+)', views.unselect_wishlist_for_event),
]
