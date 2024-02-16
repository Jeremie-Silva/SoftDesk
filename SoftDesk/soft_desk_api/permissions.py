from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Project, Issue, Comment


class IsContributorOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        """Permission for /endpoint/{id}"""
        if request.method in SAFE_METHODS:
            if isinstance(obj, Project):
                return request.user.contributor in obj.contributors.all()
            if isinstance(obj, Issue):
                return request.user.contributor in obj.project.contributors.all()
            if isinstance(obj, Comment):
                return request.user.contributor in obj.issue.project.contributors.all()
        else:
            return request.user.contributor == obj.author


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return obj.user == request.user
