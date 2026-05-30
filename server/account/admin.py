from django.contrib import admin

from account.models import Connection, Profile, Token


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'first_name', 'balance', 'bonus_balance']
    actions = []
    search_fields = ['user__username', 'email']


admin.site.register(Profile, ProfileAdmin)


class TokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'key', 'is_active', 'created_at']
    readonly_fields = ['created_at', 'user', 'key']
    ordering = ('-created_at',)


admin.site.register(Token, TokenAdmin)


class ConnectionAdmin(admin.ModelAdmin):
    list_display = ['channel_name', 'user']
    list_filter = ['created_at']
    readonly_fields = ('channel_name', 'created_at')


admin.site.register(Connection, ConnectionAdmin)
