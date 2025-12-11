from django.contrib import admin
from .models import AuthToken, PasswordResetToken, LoginHistory


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_active', 'last_used', 'ip_address')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__email', 'token', 'ip_address')
    readonly_fields = ('token', 'refresh_token', 'created_at', 'last_used')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Token Details', {
            'fields': ('token', 'refresh_token', 'expires_at', 'refresh_expires_at', 'is_active')
        }),
        ('Device Information', {
            'fields': ('device_info', 'ip_address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_used')
        }),
    )

    def has_add_permission(self, request):
        return False


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_used', 'used_at')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__email', 'token')
    readonly_fields = ('token', 'created_at', 'used_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Token Details', {
            'fields': ('token', 'expires_at', 'is_used', 'used_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

    def has_add_permission(self, request):
        return False


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time', 'ip_address', 'success', 'device_info')
    list_filter = ('success', 'login_time')
    search_fields = ('user__username', 'user__email', 'ip_address', 'device_info')
    readonly_fields = ('user', 'login_time', 'logout_time', 'ip_address', 'device_info', 
                       'user_agent', 'success', 'failure_reason')
    date_hierarchy = 'login_time'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Login Details', {
            'fields': ('login_time', 'logout_time', 'success', 'failure_reason')
        }),
        ('Device Information', {
            'fields': ('ip_address', 'device_info', 'user_agent')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
