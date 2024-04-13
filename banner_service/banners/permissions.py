from rest_framework import permissions

class AdminTokenPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.META.get('HTTP_TOKEN') == 'admin_token'

class UserTokenPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.META.get('HTTP_TOKEN') == 'user_token'
