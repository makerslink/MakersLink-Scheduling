from django.contrib import admin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

def make_approved(modeladmin, request, queryset):
    queryset.update(is_active=True, is_registration_complete=True)
make_approved.short_description = "Mark selected users as approved"

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('email', 'slackId', 'is_active', 'is_registration_complete')    
    actions = [make_approved]
