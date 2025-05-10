from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Register your models here.

# 扩展 UserAdmin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'date_joined', 'last_login', 'is_active', 'is_staff', 'is_cloud_member')
    list_filter = ('is_active', 'is_staff', 'is_cloud_member')
    fieldsets = UserAdmin.fieldsets + (
        ('云栈权限', {'fields': ('is_cloud_member',)}),
    )

# 重新注册 User 模型
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
