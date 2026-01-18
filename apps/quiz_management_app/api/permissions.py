"""
Custom DRF permissions for the quiz management API.

This module contains object-level access control rules for quizzes.
"""

from rest_framework.permissions import BasePermission


class IsQuizOwner(BasePermission):
    """
    Object-level permission that allows access only to the owner of a quiz.

    If the quiz belongs to a different user, access is denied with HTTP 403.
    """

    message = "You do not have permission to access this quiz."

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Return True if the requesting user owns the given quiz object.
        """
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)