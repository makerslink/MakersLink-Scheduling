from django import template
register = template.Library()

@register.filter(name='is_participant')
def is_participant(user, eventInstance):
    user_id = int(user.id)
    return eventInstance.participants.filter(id=user_id).exists() # check if relationship exists
