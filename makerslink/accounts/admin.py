from django.contrib import admin
from .models import User

def make_approved(modeladmin, request, queryset):
    queryset.update(is_active=True, is_registration_complete=True)
make_approved.short_description = "Mark selected users as approved"

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'slackId', 'is_active', 'is_registration_complete')    
    actions = [make_approved]
