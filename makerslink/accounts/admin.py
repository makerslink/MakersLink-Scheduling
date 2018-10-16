from django.contrib import admin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('email', 'slackId', 'is_active', 'is_registration_complete')    
    actions = ['make_approved']
    
    def make_approved(self, request, queryset):
        rows_updated = queryset.update(is_active=True, is_registration_complete=True)
        if rows_updated == 1:
            message_bit = "1 host was"
        else:
            message_bit = "%s hosts were" % rows_updated
        self.message_user(request, "%s successfully approved." % message_bit)
    make_approved.short_description = "Mark selected users as approved"
