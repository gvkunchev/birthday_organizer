from django import template
from django.conf import settings
from users.models import CustomUser

register = template.Library()


@register.filter('active')
def active(collection):
    """Filter collection based on its active field."""
    result = []
    for item in collection:
        if item.active:
            result.append(item)
    return result

@register.filter('get_value_from_dict')
def get_value_from_dict(dict_data, key):
    """Usage example {{ your_dict|get_value_from_dict:your_key }}"""
    if key:
        return dict_data.get(key)

@register.simple_tag
def version_variable(prefix='?'):
    """project version to append to static file URLs."""
    version_to_str = "_".join(map(str, settings.VERSION))
    return f"{prefix}version={version_to_str}"

@register.simple_tag
def comment_liked_by(comment, user):
    """Check if comment is liked by a user."""
    return comment.likes.filter(id=user.id).exists()

@register.simple_tag
def get_all_likes_for_comment(comment):
    """Get the names for all people that liked a comment."""
    all_users = []
    for user in comment.likes.values():
        all_users.append(CustomUser.objects.get(id=user['id']).full_name)
    if not len(all_users):
        return ''
    elif len(all_users) > 1:
        user_list_as_str = ', '.join(all_users[:-1])
        user_list_as_str = f'{user_list_as_str} and {all_users[-1]}'
        return f'{user_list_as_str} like this comment'
    else:
        user_list_as_str = ', '.join(all_users)
        return f'{user_list_as_str} likes this comment'