from rest_framework.permissions import BasePermission


class IsTaskBoardMember(BasePermission):
    """
    Allows access only to users who own the board or are board members.
    """

    def has_object_permission(self, request, view, obj):
        is_owner = obj.board.owner == request.user
        is_member = obj.board.members.filter(id=request.user.id).exists()

        return is_owner or is_member


class CanDeleteTask(BasePermission):
    """
    Allows deleting a task only for the creator or the board owner.
    """

    def has_object_permission(self, request, view, obj):
        if request.method != "DELETE":
            return True

        is_creator = obj.created_by == request.user
        is_board_owner = obj.board.owner == request.user

        return is_creator or is_board_owner