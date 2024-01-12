from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsContributorOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        """Permission for /endpoint/{id}"""
        if request.method in SAFE_METHODS:
            return request.user.contributor in obj.contributors.all()
        else:
            return request.user.contributor == obj.author
