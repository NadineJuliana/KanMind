from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    DestroyAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from boards_app.models import Board
from tasks_app.models import Task, Comment
from .permissions import CanDeleteTask, IsTaskBoardMember, IsCommentAuthor
from .serializers import (
    TaskCreateUpdateSerializer,
    TaskOutputSerializer,
    CommentCreateSerializer,
    CommentOutputSerializer,
)


class AssignedToMeTaskListView(ListAPIView):
    """
    Returns tasks assigned to the authenticated user.
    """

    serializer_class = TaskOutputSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class ReviewingTaskListView(ListAPIView):
    """
    Returns tasks where the authenticated user is the reviewer.
    """

    serializer_class = TaskOutputSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class TaskCreateView(CreateAPIView):
    """
    Handles creating tasks inside boards.
    """

    serializer_class = TaskCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        board_id = request.data.get("board")

        if not self._is_board_member(board_id, request.user):
            return Response(
                {"detail": "You must be a board member."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        data = TaskOutputSerializer(task).data
        return Response(data, status=status.HTTP_201_CREATED)

    def _is_board_member(self, board_id, user):
        """
        Checks whether a user owns or belongs to a board.
        """
        
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return False

        return board.owner == user or board.members.filter(id=user.id).exists()


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    """
    Handles updating and deleting a single task.
    """

    queryset = Task.objects.all()
    serializer_class = TaskCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMember, CanDeleteTask]
    lookup_url_kwarg = "task_id"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TaskOutputSerializer
        return TaskCreateUpdateSerializer

    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(
            task,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        data = TaskOutputSerializer(task).data
        return Response(data, status=status.HTTP_200_OK)
    

class CommentListCreateView(ListAPIView, CreateAPIView):
    """
    Handles listing and creating comments for a task.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task = self._get_task()
        self._check_board_access(task)
        return task.comments.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateSerializer
        return CommentOutputSerializer

    def create(self, request, *args, **kwargs):
        task = self._get_task()
        self._check_board_access(task)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = serializer.save(
            task=task,
            author=request.user,
        )

        data = CommentOutputSerializer(comment).data
        return Response(data, status=status.HTTP_201_CREATED)

    def _get_task(self):
        return get_object_or_404(
            Task,
            id=self.kwargs["task_id"],
        )

    def _check_board_access(self, task):
        """
        Ensures that the user can access the task's board.
        """
        
        user = self.request.user
        is_owner = task.board.owner == user
        is_member = task.board.members.filter(id=user.id).exists()

        if not is_owner and not is_member:
            self.permission_denied(self.request)


class CommentDeleteView(DestroyAPIView):
    """
    Handles deleting a comment by its author.
    """

    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        return Comment.objects.filter(
            task_id=self.kwargs["task_id"],
        )