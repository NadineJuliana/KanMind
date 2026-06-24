from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBoardOwnerOrMember(BasePermission):
    """
    Allows access only to board owners or board members.
    """

    def has_object_permission(self, request, view, obj):
        is_owner = obj.owner == request.user
        is_member = obj.members.filter(id=request.user.id).exists()

        return is_owner or is_member


class IsBoardOwnerForDelete(BasePermission):
    """
    Allows deleting a board only for the board owner.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.method == "DELETE":
            return obj.owner == request.user

        return True