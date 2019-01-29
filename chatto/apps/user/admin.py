from django.contrib import admin

# Register your models here.
from .models import User


class UserAdmin(admin.ModelAdmin):
    fields = ('username', 'email', 'last_login', 'avatar', 'roles')
    list_display = ('id', 'username', 'email', 'is_superuser', 'roles', 'last_login')


admin.site.register(User, UserAdmin)
