from django import template

register = template.Library()

@register.filter
def has_group(user, group_name):
    """
    Check if a user belongs to a specific group or is a superuser
    Usage: {% if user|has_group:"group_name" %}...{% endif %}
    """
    if user.is_superuser:
        return True
    return user.groups.filter(name=group_name).exists()