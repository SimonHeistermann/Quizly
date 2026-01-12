from rest_framework.permissions import BasePermission


class IsQuizOwner(BasePermission):
    """
    Object-level permission: only the owner of a quiz can access it.
    Returns 403 if the quiz belongs to someone else.
    """

    message = "You do not have permission to access this quiz."

    def has_object_permission(self, request, view, obj) -> bool:
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)