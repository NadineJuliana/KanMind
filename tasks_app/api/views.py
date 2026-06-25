from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from boards_app.models import Board
from tasks_app.models import Task, Comment
from .permissions import CanDeleteTask, IsTaskBoardMember, IsCommentAuthor
from .serializers import (
    CommentCreateSerializer,
    CommentOutputSerializer,
    TaskCreateUpdateSerializer,
    TaskOutputSerializer,
)


class AssignedToMeTaskListView(ListAPIView):
    """
    Returns tasks assigned to the authenticated user.
    """

    serializer_class = TaskOutputSerializer

    def get_queryset(self):
        """
        Returns all tasks assigned to the authenticated user.
        """

        return Task.objects.filter(assignee=self.request.user)


class ReviewingTaskListView(ListAPIView):
    """
    Returns tasks where the authenticated user is the reviewer.
    """

    serializer_class = TaskOutputSerializer

    def get_queryset(self):
        """
        Returns all tasks where the authenticated user is assigned as reviewer.
        """

        return Task.objects.filter(reviewer=self.request.user)


class TaskCreateView(CreateAPIView):
    """
    Handles creating tasks inside boards.
    """

    serializer_class = TaskCreateUpdateSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates a task for a board if the authenticated user has board access.
        """

        board = get_object_or_404(Board, id=request.data.get("board"))

        if not self._has_board_access(board, request.user):
            return Response(
                {"detail": "You must be a board member."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        data = TaskOutputSerializer(task).data
        return Response(data, status=status.HTTP_201_CREATED)

    def _has_board_access(self, board, user):
        """
        Checks whether a user owns or belongs to a board.
        """

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
        """
        Returns the output serializer for GET requests and the create/update
        serializer for write requests.
        """

        if self.request.method == "GET":
            return TaskOutputSerializer
        return TaskCreateUpdateSerializer

    def partial_update(self, request, *args, **kwargs):
        """
        Partially updates a task and returns the updated task data.
        """

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

    def get_queryset(self):
        """
        Returns all comments belonging to the selected task after checking
        board access.
        """

        task = self._get_task()
        self._check_board_access(task)
        return task.comments.all()

    def get_serializer_class(self):
        """
        Returns the create serializer for POST requests and the output
        serializer for read requests.
        """

        if self.request.method == "POST":
            return CommentCreateSerializer
        return CommentOutputSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates a comment for the selected task if the authenticated user
        has board access.
        """

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
        """
        Returns the task matching the task ID from the URL.
        """

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
        """
        Returns comments belonging to the selected task.
        """

        return Comment.objects.filter(
            task_id=self.kwargs["task_id"],
        )
